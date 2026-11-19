#!/usr/bin/env python3
"""LIFE OS M31–35: distribution overlay + rootfs staging + tests."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "iso/overlays/life-lite"
MANIFEST = ROOT / "iso/life-lite-manifest.json"

WALLPAPERS = {
    "horizon": "blue-horizon.svg",
    "morning": "morning-haze.svg",
    "midnight": "deep-night.svg",
}


def write(path, text, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)
    print("CREATED:", path.relative_to(ROOT))


def build():
    print("\n🍉 LIFE OS M31–35 — BUILDING OVERLAY")

    # M31 — Distribution wallpapers
    wall_dir = OVERLAY / "usr/share/backgrounds/lifeos"
    wall_dir.mkdir(parents=True, exist_ok=True)

    for name, filename in WALLPAPERS.items():
        source = ROOT / "desktop/assets/wallpapers" / filename
        if not source.is_file():
            raise RuntimeError(f"Missing wallpaper: {source}")

        destination = wall_dir / f"life-{name}.svg"
        shutil.copy2(source, destination)
        print("WALLPAPER:", destination.relative_to(ROOT))

    # M32 — First-login configuration
    setup = OVERLAY / "usr/local/bin/life-lite-first-login"

    write(setup, r'''#!/usr/bin/env bash
set -eu

# LIFE Lite — initial XFCE appearance setup
MARKER="$HOME/.config/lifeos/lite-first-login-v1"
WALL="/usr/share/backgrounds/lifeos/life-horizon.svg"

[ -f "$MARKER" ] && exit 0
[ -f "$WALL" ] || exit 0

command -v xfconf-query >/dev/null 2>&1 || exit 0

# Wait for XFCE to initialize the desktop channel.
PROPERTIES=""

for attempt in 1 2 3 4 5 6 7 8 9 10; do
    PROPERTIES="$(
        xfconf-query -c xfce4-desktop -lv 2>/dev/null |
        awk '$1 ~ /\/last-image$/ {print $1}'
    )"

    [ -n "$PROPERTIES" ] && break
    sleep 2
done

# Do not mark complete if the desktop isn't initialized.
[ -n "$PROPERTIES" ] || exit 0

SUCCESS=0

while IFS= read -r property; do
    [ -n "$property" ] || continue

    if xfconf-query -c xfce4-desktop \
        -p "$property" -s "$WALL"; then

        SUCCESS=1

        style="${property%/last-image}/image-style"

        xfconf-query -c xfce4-desktop \
            -p "$style" --create -t int -s 5 \
            >/dev/null 2>&1 || \
        xfconf-query -c xfce4-desktop \
            -p "$style" -s 5 >/dev/null 2>&1 || true
    fi
done <<EOF
$PROPERTIES
EOF

[ "$SUCCESS" -eq 1 ] || exit 0

# Use an installed light GTK theme.
if [ -d /usr/share/themes/Adwaita ]; then
    xfconf-query -c xsettings \
        -p /Net/ThemeName \
        --create -t string -s Adwaita \
        >/dev/null 2>&1 || \
    xfconf-query -c xsettings \
        -p /Net/ThemeName -s Adwaita \
        >/dev/null 2>&1 || true
fi

mkdir -p "$HOME/.config/lifeos"
touch "$MARKER"

echo "LIFE Lite first-login configuration complete"
''', executable=True)

    # Native XFCE session autostart
    write(
        OVERLAY / "etc/xdg/autostart/life-lite-first-login.desktop",
        """[Desktop Entry]
Version=1.0
Type=Application
Name=LIFE Lite First Login
Comment=Initialize LIFE Lite appearance
Exec=/usr/local/bin/life-lite-first-login
TryExec=/usr/local/bin/life-lite-first-login
OnlyShowIn=XFCE;
Terminal=false
StartupNotify=false
""",
    )

    # M33 — LIFE system information utility
    write(
        OVERLAY / "usr/local/bin/life-about",
        r'''#!/usr/bin/env bash
printf '\nLIFE OS — Lite Edition\n'
printf 'Desktop: XFCE\n'
printf 'Development milestone: 35\n'
printf 'Base system: '
if [ -r /etc/os-release ]; then
    . /etc/os-release
    printf '%s\n' "${PRETTY_NAME:-Linux}"
else
    printf 'Linux\n'
fi
printf '\n'
''',
        executable=True,
    )

    write(
        OVERLAY / "usr/share/applications/life-about.desktop",
        """[Desktop Entry]
Version=1.0
Type=Application
Name=About LIFE Lite
Comment=View LIFE Lite information
Exec=xfce4-terminal --hold -e /usr/local/bin/life-about
Icon=computer
Terminal=false
Categories=System;Utility;
""",
    )

    # M33 — Edition manifest
    data = {
        "name": "LIFE OS",
        "edition": "Lite",
        "milestone": 35,
        "architecture": "x86_64",
        "target_base": "Arch Linux",
        "development_base": "Debian 12",
        "desktop": "XFCE",
        "status": "distribution overlay prototype",
        "first_login": "/usr/local/bin/life-lite-first-login",
        "wallpapers": [
            f"/usr/share/backgrounds/lifeos/life-{name}.svg"
            for name in WALLPAPERS
        ],
    }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
    print("MANIFEST:", MANIFEST.relative_to(ROOT))

    # Include a copy of the edition metadata inside the image.
    write(
        OVERLAY / "usr/share/lifeos/edition.json",
        json.dumps(data, indent=2) + "\n",
    )

    print("\n✅ Overlay generated")


def stage(rootfs):
    """M34: install overlay into an existing Linux root filesystem."""
    target = Path(rootfs).expanduser().resolve()

    if not target.is_dir():
        raise RuntimeError(f"Rootfs directory missing: {target}")

    if target == Path("/"):
        raise RuntimeError("Refusing to modify the running system root")

    if target == OVERLAY or OVERLAY in target.parents:
        raise RuntimeError("Cannot stage an overlay inside itself")

    if not (target / "etc").is_dir():
        raise RuntimeError(
            "Target does not look like a Linux rootfs: missing etc/"
        )

    count = 0

    for source in OVERLAY.rglob("*"):
        if not source.is_file():
            continue

        relative = source.relative_to(OVERLAY)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.is_symlink():
            raise RuntimeError(
                f"Refusing to overwrite symlink: {destination}"
            )

        shutil.copy2(source, destination)
        count += 1

    print(f"✅ M34: Staged {count} files into {target}")


def test():
    """M35: validate generated files and rootfs installation."""
    print("\n===== M35 AUTOMATED TESTS =====")

    scripts = [
        OVERLAY / "usr/local/bin/life-lite-first-login",
        OVERLAY / "usr/local/bin/life-about",
    ]

    for script in scripts:
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        print("PASS: shell syntax", script.name)

    autostart = (
        OVERLAY /
        "etc/xdg/autostart/life-lite-first-login.desktop"
    )

    content = autostart.read_text()
    assert "[Desktop Entry]" in content
    assert "OnlyShowIn=XFCE;" in content
    assert "Exec=/usr/local/bin/life-lite-first-login" in content

    print("PASS: XFCE autostart")

    for name in WALLPAPERS:
        path = (
            OVERLAY /
            f"usr/share/backgrounds/lifeos/life-{name}.svg"
        )
        assert path.is_file()
        assert "<svg" in path.read_text()[:1000].lower()
        print("PASS: wallpaper", name)

    metadata = json.loads(MANIFEST.read_text())
    assert metadata["edition"] == "Lite"
    assert metadata["desktop"] == "XFCE"
    assert metadata["architecture"] == "x86_64"

    print("PASS: edition metadata")

    # Test actual staging into an isolated temporary rootfs.
    with tempfile.TemporaryDirectory(prefix="life-m35-") as tmp:
        rootfs = Path(tmp)
        (rootfs / "etc").mkdir()

        stage(rootfs)

        for source in OVERLAY.rglob("*"):
            if source.is_file():
                destination = (
                    rootfs / source.relative_to(OVERLAY)
                )
                assert destination.is_file()
                assert source.read_bytes() == destination.read_bytes()

        # Repeat to verify idempotent installation.
        stage(rootfs)

        print("PASS: rootfs staging")
        print("PASS: repeatable installation")

    print("\n✅ ALL M35 SMOKE TESTS PASSED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        metavar="ROOTFS",
        help="Install overlay into an existing rootfs directory",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.test_only:
        build()

    if args.stage:
        stage(args.stage)

    test()

    print("\n🍉 LIFE OS M31–35 COMPLETE")
    print("Overlay:", OVERLAY)
    print("Next: connect overlay to the actual ISO build pipeline")


if __name__ == "__main__":
    main()
