#!/usr/bin/env python3
"""LIFE Lite M22 — Real XFCE panel and dock layout."""

import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ROOT = Path("/workspaces/life-os")
CONFIG = HOME / ".config/xfce4"
PANEL_FILES = CONFIG / "panel"
PANEL_XML = CONFIG / "xfconf/xfce-perchannel-xml/xfce4-panel.xml"
BACKUP_ROOT = HOME / ".local/share/lifeos/backups"
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)


def command(*args, check=True):
    result = subprocess.run(
        args,
        text=True,
        capture_output=True
    )
    if check and result.returncode:
        raise RuntimeError(
            f"{' '.join(args)}\n"
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def query(path):
    return command(
        "xfconf-query", "-c", "xfce4-panel",
        "-p", path,
        check=False
    )


def set_value(path, typ, value):
    existing = query(path)
    args = [
        "xfconf-query", "-c", "xfce4-panel",
        "-p", path
    ]
    if not existing:
        args += ["--create"]
    args += ["-t", typ, "-s", str(value)]
    command(*args)


def set_array(path, values, typ="int"):
    args = [
        "xfconf-query", "-c", "xfce4-panel",
        "-p", path, "--force-array"
    ]
    if not query(path):
        args += ["--create"]

    for value in values:
        args += ["-t", typ, "-s", str(value)]
    command(*args)


def backup():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = BACKUP_ROOT / f"xfce-panel-before-m22-{stamp}.tar.gz"

    with tarfile.open(archive, "w:gz") as tar:
        if PANEL_FILES.exists():
            tar.add(PANEL_FILES, arcname="panel")
        if PANEL_XML.exists():
            tar.add(PANEL_XML, arcname="xfce4-panel.xml")

    snapshot = BACKUP_ROOT / f"xfce-panel-before-m22-{stamp}.txt"
    snapshot.write_text(
        command(
            "xfconf-query", "-c", "xfce4-panel", "-lv",
            check=False
        ),
        encoding="utf-8"
    )
    print("Backup:", archive)
    return archive


def create_launcher(identifier, name, icon, exec_command):
    folder = PANEL_FILES / f"launcher-{identifier}"
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"life-m22-{identifier}.desktop"

    desktop = (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        f"Name={name}\n"
        f"Exec={exec_command}\n"
        f"Icon={icon}\n"
        "Terminal=false\n"
        "Categories=Utility;\n"
    )

    (folder / filename).write_text(
        desktop, encoding="utf-8"
    )

    set_value(f"/plugins/plugin-{identifier}", "string", "launcher")
    set_array(
        f"/plugins/plugin-{identifier}/items",
        [filename],
        "string"
    )


def main():
    if not shutil.which("xfconf-query"):
        raise RuntimeError("xfconf-query is missing")

    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        raise RuntimeError(
            "XFCE DBus session not detected. "
            "Run this using the M21 session environment."
        )

    print("🍉 LIFE Lite M22 starting")
    backup()

    original = command(
        "xfconf-query", "-c", "xfce4-panel", "-lv"
    )

    existing_ids = [
        int(number)
        for number in re.findall(r"/plugins/plugin-(\d+)", original)
    ]

    next_id = max(existing_ids, default=20) + 100

    def plugin(kind):
        nonlocal next_id
        identifier = next_id
        next_id += 1
        set_value(
            f"/plugins/plugin-{identifier}",
            "string", kind
        )
        return identifier

    # ===== TOP BAR =====

    menu = plugin("applicationsmenu")
    set_value(
        f"/plugins/plugin-{menu}/button-title",
        "string", "LIFE"
    )
    set_value(
        f"/plugins/plugin-{menu}/show-button-title",
        "bool", "true"
    )

    tasks = plugin("tasklist")
    set_value(
        f"/plugins/plugin-{tasks}/show-labels",
        "bool", "false"
    )

    spacer = plugin("separator")
    set_value(
        f"/plugins/plugin-{spacer}/expand",
        "bool", "true"
    )
    set_value(
        f"/plugins/plugin-{spacer}/style",
        "uint", 0
    )

    clock = plugin("clock")
    set_value(
        f"/plugins/plugin-{clock}/digital-format",
        "string", "%a %d %b  ·  %H:%M"
    )
    set_value(
        f"/plugins/plugin-{clock}/mode",
        "uint", 2
    )

    set_array(
        "/panels/panel-1/plugin-ids",
        [menu, tasks, spacer, clock]
    )

    top = "/panels/panel-1"
    set_value(top + "/position", "string", "p=6;x=0;y=0")
    set_value(top + "/size", "uint", 36)
    set_value(top + "/length", "uint", 100)
    set_value(top + "/length-adjust", "bool", "false")
    set_value(top + "/autohide-behavior", "uint", 0)
    set_value(top + "/position-locked", "bool", "true")
    set_value(top + "/background-style", "uint", 1)
    set_value(top + "/background-rgba", "string", "0.10;0.15;0.23;0.92")

    # ===== BOTTOM DOCK =====

    show_desktop = plugin("showdesktop")

    first_separator = plugin("separator")
    set_value(
        f"/plugins/plugin-{first_separator}/style",
        "uint", 1
    )

    apps_id = next_id
    next_id += 1
    create_launcher(
        apps_id,
        "LIFE Apps",
        str(ROOT / "desktop/assets/icons/light/launcher.svg"),
        str(HOME / ".local/bin/life-lite-apps")
    )

    files_id = next_id
    next_id += 1
    create_launcher(
        files_id,
        "Files",
        "system-file-manager",
        "thunar"
    )

    settings_id = next_id
    next_id += 1
    create_launcher(
        settings_id,
        "Settings",
        "preferences-system",
        "xfce4-settings-manager"
    )

    search_id = next_id
    next_id += 1
    create_launcher(
        search_id,
        "Applications",
        "system-search",
        "xfce4-appfinder"
    )

    last_separator = plugin("separator")
    set_value(
        f"/plugins/plugin-{last_separator}/style",
        "uint", 1
    )

    set_array(
        "/panels/panel-2/plugin-ids",
        [
            show_desktop,
            first_separator,
            apps_id,
            files_id,
            settings_id,
            search_id,
            last_separator
        ]
    )

    bottom = "/panels/panel-2"

    set_value(bottom + "/position", "string", "p=10;x=0;y=0")
    set_value(bottom + "/size", "uint", 55)
    set_value(bottom + "/length", "uint", 35)
    set_value(bottom + "/length-adjust", "bool", "false")
    set_value(bottom + "/autohide-behavior", "uint", 0)
    set_value(bottom + "/position-locked", "bool", "true")
    set_value(bottom + "/icon-size", "uint", 32)

    # Keep other pre-existing panels if present.
    panels = query("/panels")
    old_panel_ids = [
        int(x) for x in re.findall(r"\d+", panels)
    ]
    all_panels = list(dict.fromkeys(
        old_panel_ids + [1, 2]
    ))
    set_array("/panels", all_panels)

    print("✅ Panel configuration written")
    print("Top bar: menu, tasks, clock")
    print("Bottom dock: home, apps, files, settings, search")
    print("Restarting XFCE panel...")

    command("xfce4-panel", "--restart", check=False)

    print("✅ LIFE Lite M22 configured")
    print("Open noVNC port 6082")


if __name__ == "__main__":
    main()
