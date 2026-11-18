#!/usr/bin/env python3
"""Prepare a LIFE OS Archiso profile on an Arch Linux build host."""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "iso" / "editions.json"


def load_editions():
    editions = json.loads(CONFIG.read_text())
    for name, edition in editions.items():
        assert name.startswith("life-")
        assert edition["packages"]
        assert edition["display_manager"] in ("lightdm", "sddm")
        assert len(edition["packages"]) == len(set(edition["packages"]))
    return editions


def prepare(edition_name, archiso_root, destination):
    editions = load_editions()

    if edition_name not in editions:
        raise ValueError(f"Unknown edition: {edition_name}")

    source = archiso_root / "configs" / "releng"

    if not (source / "profiledef.sh").is_file():
        raise FileNotFoundError(
            "Archiso releng profile not found. "
            "Use an Arch Linux host with archiso installed."
        )

    if destination.exists():
        raise FileExistsError(
            f"{destination} already exists. "
            "Remove it manually if you intend to regenerate."
        )

    shutil.copytree(source, destination, symlinks=True)

    edition = editions[edition_name]
    # Ship LIFE Layout with the live operating system.
    # No desktop configuration is automatically applied.
    life_root = destination / "airootfs/usr/share/lifeos"
    life_root.mkdir(parents=True, exist_ok=True)

    shutil.copytree(
        ROOT / "desktop",
        life_root / "desktop",
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    scripts_dir = life_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(
        ROOT / "scripts/life_layout.py",
        scripts_dir / "life_layout.py",
    )

    bin_dir = destination / "airootfs/usr/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launcher = bin_dir / "life-layout"
    launcher.write_text(
        "#!/bin/sh\\n"
        "exec /usr/bin/python "
        "/usr/share/lifeos/scripts/life_layout.py "
        "\\\"$@\\\"\\n"
    )
    launcher.chmod(0o755)

    packages_file = destination / "packages.x86_64"

    existing = packages_file.read_text().splitlines()
    additions = [
        package
        for package in edition["packages"]
        if package not in existing
    ]

    packages_file.write_text(
        "\n".join(existing + additions) + "\n"
    )

    profile = destination / "profiledef.sh"
    content = profile.read_text()

    import re
    content, count = re.subn(
        r'^iso_name=.*$',
        f'iso_name="{edition_name}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    if count != 1:
        raise RuntimeError("Could not set ISO name")

    profile.write_text(content)

    print(f"Prepared: {edition_name}")
    print(f"Desktop: {edition['desktop']}")
    print(f"Profile: {destination}")
    print(f"Additional packages: {len(additions)}")
    print("Status: profile prepared; graphical login not configured.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "edition",
        choices=load_editions().keys(),
    )
    parser.add_argument(
        "--archiso-root",
        type=Path,
        default=Path("/usr/share/archiso"),
    )
    parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args()
    destination = args.output or (
        ROOT / "out" / "profiles" / args.edition
    )

    try:
        prepare(
            args.edition,
            args.archiso_root,
            destination,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
