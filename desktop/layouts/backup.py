"""Backup native desktop configuration without modifying it."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATHS = {
    "life-lite": [
        ".config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml",
        ".config/xfce4/panel",
    ],
    "life-standard": [
        ".config/plasma-org.kde.plasma.desktop-appletsrc",
        ".config/plasmashellrc",
    ],
}


def backup_layout(home: Path, edition: str) -> Path:
    if edition not in CONFIG_PATHS:
        raise ValueError(f"Unknown edition: {edition}")

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    destination = (
        home / ".local" / "state" / "lifeos"
        / "layout-backups" / stamp
    )

    destination.mkdir(parents=True, exist_ok=False)

    copied = []

    for relative in CONFIG_PATHS[edition]:
        source = home / relative

        if not source.exists() or source.is_symlink():
            continue

        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)

        if source.is_dir():
            shutil.copytree(
                source,
                target,
                symlinks=True,
            )
        elif source.is_file():
            shutil.copy2(source, target)
        else:
            continue

        copied.append(relative)

    manifest = {
        "edition": edition,
        "created_utc": stamp,
        "files": copied,
        "version": 1,
    }

    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    return destination
