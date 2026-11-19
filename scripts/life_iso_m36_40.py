#!/usr/bin/env python3
"""LIFE OS M36–40: safe ArchISO overlay integration."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "iso/overlays/life-lite"
WORKFLOW = ROOT / ".github/workflows/build-life-lite.yml"
ORIGINAL = ROOT / "scripts/prepare_iso.py"
WRAPPER = ROOT / "scripts/prepare_iso_integrated.py"


def copy_overlay(profile: Path) -> int:
    """Install LIFE files into a prepared ArchISO profile."""
    profile = profile.resolve()
    destination_root = profile / "airootfs"

    if not (profile / "profiledef.sh").is_file():
        raise RuntimeError(
            f"Not an ArchISO profile: {profile}"
        )

    if not OVERLAY.is_dir():
        raise RuntimeError("LIFE Lite overlay is missing")

    destination_root.mkdir(exist_ok=True)

    copied = 0

    for source in sorted(OVERLAY.rglob("*")):
        if source.is_symlink():
            raise RuntimeError(
                f"Overlay contains a symlink: {source}"
            )

        if not source.is_file():
            continue

        relative = source.relative_to(OVERLAY)
        target = destination_root / relative

        # Don't follow symlinks in existing destination paths.
        ancestor = target.parent

        while ancestor != profile.parent:
            if ancestor.is_symlink():
                raise RuntimeError(
                    f"Unsafe destination: {ancestor}"
                )
            if ancestor == profile:
                break
            ancestor = ancestor.parent

        if target.is_symlink():
            raise RuntimeError(
                f"Refusing to replace symlink: {target}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1

    print(f"LIFE overlay integrated: {copied} files")
    return copied


def create_wrapper():
    content = '''#!/usr/bin/env python3
"""Prepare the ArchISO profile and integrate LIFE Lite assets."""

from pathlib import Path
import importlib.util
import inspect
import sys

from life_iso_m36_40 import copy_overlay

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/prepare_iso.py"

spec = importlib.util.spec_from_file_location(
    "life_original_prepare_iso", SOURCE
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

original_prepare = module.prepare


def integrated_prepare(*args, **kwargs):
    signature = inspect.signature(original_prepare)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()

    result = original_prepare(*args, **kwargs)

    edition = str(
        bound.arguments.get("edition_name", "")
    ).lower()

    destination = bound.arguments.get("destination")

    if destination is None:
        raise RuntimeError(
            "Original ISO preparer did not expose destination"
        )

    # Other editions retain their original preparation behavior.
    if "lite" in edition:
        copy_overlay(Path(destination))

    return result


module.prepare = integrated_prepare


if __name__ == "__main__":
    raise SystemExit(module.main())
'''
    WRAPPER.write_text(content, encoding="utf-8")
    WRAPPER.chmod(0o755)
    print("Created integrated ISO preparation wrapper")


def patch_workflow():
    if not WORKFLOW.is_file():
        raise RuntimeError("Existing build workflow not found")

    old = WORKFLOW.read_text(encoding="utf-8")

    original_call = "scripts/prepare_iso.py"
    integrated_call = "scripts/prepare_iso_integrated.py"

    if integrated_call in old:
        print("Build workflow already integrated")
        return

    occurrences = old.count(original_call)

    if occurrences != 1:
        raise RuntimeError(
            "Expected exactly one original ISO preparation call "
            f"in the build workflow; found {occurrences}. "
            "No workflow changes made."
        )

    updated = old.replace(
        original_call, integrated_call, 1
    )

    # Preserve a backup outside the Git repository.
    backup = Path.home() / (
        ".local/share/lifeos/backups/"
        "build-life-lite-before-m40.yml"
    )
    backup.parent.mkdir(parents=True, exist_ok=True)

    if not backup.exists():
        backup.write_text(old, encoding="utf-8")

    WORKFLOW.write_text(updated, encoding="utf-8")
    print("Updated build-life-lite.yml")


def verify():
    print("\n===== M36–40 VALIDATION =====")

    if not ORIGINAL.is_file():
        raise RuntimeError("Original ISO preparation script missing")

    tree = ast.parse(
        ORIGINAL.read_text(encoding="utf-8")
    )

    functions = {
        node.name
        for node in tree.body
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
    }

    if not {"prepare", "main"}.issubset(functions):
        raise RuntimeError(
            "Original ISO script has an unexpected structure"
        )

    print("PASS: Original ISO preparation structure")

    for script in (
        ROOT / "scripts/life_m31_35.py",
        WRAPPER,
        Path(__file__),
    ):
        result = subprocess.run(
            ["python", "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)

    print("PASS: Python syntax")

    with tempfile.TemporaryDirectory(
        prefix="life-iso-m40-"
    ) as directory:
        profile = Path(directory) / "profile"
        profile.mkdir()
        (profile / "profiledef.sh").write_text(
            'iso_name="life-test"\n'
        )

        count = copy_overlay(profile)

        if count < 8:
            raise RuntimeError(
                f"Expected at least 8 overlay files, got {count}"
            )

        expected = profile / (
            "airootfs/usr/local/bin/"
            "life-lite-first-login"
        )

        if not expected.is_file():
            raise RuntimeError(
                "First-login script not staged"
            )

        print("PASS: ArchISO profile staging")

        original_bytes = expected.read_bytes()

        copy_overlay(profile)

        if expected.read_bytes() != original_bytes:
            raise RuntimeError(
                "Repeated staging produced different contents"
            )

        print("PASS: Repeatable profile integration")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")

    if "scripts/prepare_iso_integrated.py" not in workflow_text:
        raise RuntimeError(
            "Build workflow does not use integrated wrapper"
        )

    print("PASS: Workflow integration")
    print("\nALL M36–40 LOCAL CHECKS PASSED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-only", action="store_true"
    )
    args = parser.parse_args()

    if not args.verify_only:
        # Validate structure before editing anything.
        ast.parse(ORIGINAL.read_text(encoding="utf-8"))

        create_wrapper()
        patch_workflow()

    verify()


if __name__ == "__main__":
    main()
