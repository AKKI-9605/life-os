"""LIFE OS M19 — XDG desktop integration."""
from __future__ import annotations

import argparse
import os
import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

APPS = HOME / ".local/share/applications"
BIN = HOME / ".local/bin"
AUTOSTART = HOME / ".config/autostart"
BACKUPS = HOME / ".local/share/lifeos/backups"
ASSETS = ROOT / "desktop/assets"

APPLICATIONS = {
    "lifeos-desktop": (
        "LIFE OS Desktop",
        "scripts/life_desktop_m18.py",
        "LIFE OS desktop shell and apps",
    ),
    "lifeos-classic": (
        "LIFE OS Classic",
        "scripts/life_desktop_m14.py",
        "Earlier LIFE OS visual desktop",
    ),
}


def save_file(path: Path, content: str, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.read_text() == content:
        print("UNCHANGED", path)
        return

    if path.exists():
        BACKUPS.mkdir(parents=True, exist_ok=True)
        target = BACKUPS / (path.name + ".m19-backup")
        if not target.exists():
            shutil.copy2(path, target)

    path.write_text(content, encoding="utf-8")

    if executable:
        path.chmod(
            path.stat().st_mode | stat.S_IXUSR
        )

    print("INSTALLED", path)


def wrapper(script: str):
    return f"""#!/usr/bin/env bash
set -e

cd "{ROOT}"
source "{ROOT}/.venv/bin/activate"

export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1

if [ -z "${{DISPLAY:-}}" ]; then
    export DISPLAY=:98
fi

exec python -u "{ROOT / script}"
"""


def desktop_entry(name, launcher, description, icon=""):
    icon_line = f"Icon={icon}\n" if icon else ""

    return f"""[Desktop Entry]
Type=Application
Version=1.0
Name={name}
Comment={description}
Exec={launcher}
{icon_line}Terminal=false
Categories=Utility;System;
StartupNotify=true
"""


def install():
    missing = []

    for _, (_, script, _) in APPLICATIONS.items():
        if not (ROOT / script).exists():
            missing.append(script)

    if missing:
        raise SystemExit(
            "Missing required LIFE scripts:\n"
            + "\n".join(missing)
        )

    icon = ASSETS / "icons/light/home.svg"
    icon_path = str(icon) if icon.exists() else ""

    for key, (name, script, description) in APPLICATIONS.items():
        launcher = BIN / key

        save_file(
            launcher,
            wrapper(script),
            executable=True
        )

        save_file(
            APPS / f"{key}.desktop",
            desktop_entry(
                name,
                str(launcher),
                description,
                icon_path
            )
        )

    print("\nLIFE OS XDG launchers installed.")
    print("They can be used by compatible Linux app menus.")
    print("They do not replace the existing LIFE shell.")


def wallpaper():
    candidates = [
        ASSETS / "wallpapers/blue-horizon.svg",
        ASSETS / "wallpapers/morning-haze.svg",
    ]

    source = next(
        (path for path in candidates if path.exists()),
        None
    )

    if not source:
        print("No wallpaper asset found.")
        return

    print("Wallpaper:", source)

    # XFCE wallpaper settings require a running XFCE session.
    # KDE wallpaper tools require an active Plasma session.
    desktop = os.environ.get(
        "XDG_CURRENT_DESKTOP", "Unknown"
    )

    print("Current desktop environment:", desktop)

    if "XFCE" in desktop.upper():
        print(
            "XFCE detected. Wallpaper can be applied "
            "through xfconf-query in a later session setup."
        )
    elif "KDE" in desktop.upper():
        print(
            "Plasma detected. Wallpaper can be applied "
            "through its desktop configuration."
        )
    else:
        print(
            "Using a non-KDE/XFCE session. "
            "No wallpaper configuration changed."
        )


def autostart():
    launcher = BIN / "lifeos-desktop"

    if not launcher.exists():
        raise SystemExit(
            "Install launchers before enabling autostart."
        )

    save_file(
        AUTOSTART / "lifeos-desktop.desktop",
        desktop_entry(
            "LIFE OS Desktop Startup",
            str(launcher),
            "Start LIFE OS in a graphical session"
        ) + "X-GNOME-Autostart-enabled=true\n"
    )

    print("Autostart installed for compatible sessions.")


def status():
    print("\n===== LIFE OS M19 =====")
    print("Repository:", ROOT)
    print("Display:", os.environ.get("DISPLAY", "unset"))
    print(
        "Desktop:",
        os.environ.get("XDG_CURRENT_DESKTOP", "unset")
    )

    for program in (
        "openbox", "xfce4-session",
        "plasmashell", "x11vnc", "websockify"
    ):
        print(
            f"{program:18}",
            shutil.which(program) or "not installed"
        )

    for key in APPLICATIONS:
        entry = APPS / f"{key}.desktop"
        print(
            f"{key:18}",
            "installed" if entry.exists() else "missing"
        )

    print(
        "KDE and XFCE session integration: "
        "not yet activated"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--autostart",
        action="store_true",
        help="Opt in to graphical-session autostart"
    )
    parser.add_argument(
        "--status-only",
        action="store_true"
    )

    args = parser.parse_args()

    if not args.status_only:
        install()
        wallpaper()

        if args.autostart:
            autostart()

    status()


if __name__ == "__main__":
    main()
