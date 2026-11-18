"""Appearance preferences for LIFE OS."""

import json
from pathlib import Path

WALLPAPERS = {
    "morning-haze": "Morning Haze",
    "blue-horizon": "Blue Horizon",
    "deep-night": "Deep Night",
}

THEMES = ("light", "dark")

DEFAULTS = {
    "theme": "light",
    "wallpaper": "morning-haze",
    "version": 1,
}


def appearance_path(home=None):
    home = Path(home) if home else Path.home()
    return home / ".config" / "lifeos" / "appearance.json"


def validate(data):
    if data["theme"] not in THEMES:
        raise ValueError("Invalid LIFE OS appearance theme")
    if data["wallpaper"] not in WALLPAPERS:
        raise ValueError("Invalid LIFE OS wallpaper")


def load_appearance(home=None):
    path = appearance_path(home)
    if not path.exists():
        return DEFAULTS.copy()

    try:
        values = json.loads(path.read_text())
        result = DEFAULTS | {
            k: values[k]
            for k in DEFAULTS
            if k in values
        }
        validate(result)
        return result
    except (OSError, ValueError, TypeError, KeyError):
        return DEFAULTS.copy()


def save_appearance(theme, wallpaper, home=None):
    data = {
        "theme": theme,
        "wallpaper": wallpaper,
        "version": 1,
    }
    validate(data)

    path = appearance_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)

    return path
