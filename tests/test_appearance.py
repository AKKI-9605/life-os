from pathlib import Path
import xml.etree.ElementTree as ET

from lifeos.appearance import (
    WALLPAPERS,
    load_appearance,
    save_appearance
)

ROOT = Path(__file__).resolve().parents[1]


def test_wallpaper_assets_exist():
    for wallpaper in WALLPAPERS:
        path = (
            ROOT / "desktop/assets/wallpapers"
            / f"{wallpaper}.svg"
        )
        assert path.exists()
        ET.parse(path)


def test_defaults(tmp_path):
    data = load_appearance(tmp_path)
    assert data["theme"] == "light"
    assert data["wallpaper"] == "morning-haze"


def test_save_and_reload(tmp_path):
    save_appearance(
        "dark", "deep-night", tmp_path
    )
    data = load_appearance(tmp_path)
    assert data["theme"] == "dark"
    assert data["wallpaper"] == "deep-night"


def test_invalid_selection(tmp_path):
    try:
        save_appearance(
            "invalid", "deep-night", tmp_path
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid themes must be rejected"
        )
