import xml.etree.ElementTree as ET

import pytest

from lifeos.icons import (
    ICON_NAMES,
    icon_path,
    wallpaper_path,
)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_icon_collections(theme):
    for name in ICON_NAMES:
        path = icon_path(name, theme)
        assert path.exists(), str(path)
        ET.parse(path)


@pytest.mark.parametrize(
    "name",
    ["morning-haze", "blue-horizon", "deep-night"],
)
def test_wallpaper_collection(name):
    path = wallpaper_path(name)
    assert path.exists()
    ET.parse(path)


def test_unknown_icon_rejected():
    with pytest.raises(ValueError):
        icon_path("unknown")


def test_unknown_wallpaper_rejected():
    with pytest.raises(ValueError):
        wallpaper_path("unknown")
