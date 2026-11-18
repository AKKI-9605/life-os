"""Reusable LIFE OS visual assets."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ICONS_ROOT = PROJECT_ROOT / "desktop/assets/icons"
WALLPAPERS_ROOT = PROJECT_ROOT / "desktop/assets/wallpapers"

ICON_NAMES = (
    "files",
    "notes",
    "appearance",
    "music",
    "pictures",
    "calendar",
    "terminal",
    "settings",
    "launcher",
    "home",
)


def icon_path(name, theme="light"):
    if name not in ICON_NAMES:
        raise ValueError(f"Unknown LIFE OS icon: {name}")
    if theme not in ("light", "dark"):
        raise ValueError(f"Unknown icon theme: {theme}")

    return ICONS_ROOT / theme / f"{name}.svg"


def wallpaper_path(name):
    from lifeos.appearance import WALLPAPERS

    if name not in WALLPAPERS:
        raise ValueError(f"Unknown wallpaper: {name}")

    return WALLPAPERS_ROOT / f"{name}.svg"
