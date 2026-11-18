"""Native desktop layout planning for LIFE OS."""

from __future__ import annotations

import json
from pathlib import Path

LAYOUTS = {
    "flow": {
        "name": "LIFE Flow",
        "description": "A calm workspace with a top bar and bottom dock.",
        "supported_editions": ["life-lite", "life-standard"],
    }
}

EDITIONS = {
    "life-lite": "xfce",
    "life-standard": "plasma",
}


def validate(edition: str, layout: str) -> None:
    if edition not in EDITIONS:
        raise ValueError(f"Unsupported edition: {edition}")
    if layout not in LAYOUTS:
        raise ValueError(f"Unsupported layout: {layout}")
    if edition not in LAYOUTS[layout]["supported_editions"]:
        raise ValueError(f"{layout} is unavailable for {edition}")


def state_path(home: Path) -> Path:
    return home / ".config" / "lifeos" / "desktop-layout.json"


def save_preference(
    home: Path,
    edition: str,
    layout: str,
) -> Path:
    validate(edition, layout)

    path = state_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            {
                "edition": edition,
                "layout": layout,
                "version": 1,
            },
            indent=2,
        ) + "\n"
    )

    return path


def load_preference(home: Path) -> dict | None:
    path = state_path(home)

    if not path.exists():
        return None

    data = json.loads(path.read_text())
    validate(data["edition"], data["layout"])
    return data


def layout_plan(edition: str, layout: str) -> dict:
    validate(edition, layout)

    if edition == "life-lite":
        return {
            "edition": edition,
            "layout": layout,
            "desktop": "xfce",
            "top_panel": {
                "position": "top",
                "size": 30,
                "items": [
                    "applicationsmenu",
                    "separator",
                    "tasklist",
                    "clock",
                ],
            },
            "dock": {
                "position": "bottom",
                "size": 48,
                "items": [
                    "launcher",
                    "tasklist",
                ],
            },
        }

    return {
        "edition": edition,
        "layout": layout,
        "desktop": "plasma",
        "top_panel": {
            "location": "top",
            "height": 32,
            "widgets": [
                "org.kde.plasma.kickoff",
                "org.kde.plasma.panelspacer",
                "org.kde.plasma.systemtray",
                "org.kde.plasma.digitalclock",
            ],
        },
        "dock": {
            "location": "bottom",
            "height": 52,
            "widgets": [
                "org.kde.plasma.icontasks",
            ],
        },
    }
