import pytest

from lifeos.core.settings import Settings


def test_default_theme(tmp_path):
    settings = Settings(tmp_path / "settings.json")
    assert settings.get_theme() == "system"


def test_theme_persistence(tmp_path):
    config_file = tmp_path / "settings.json"

    settings = Settings(config_file)
    settings.set_theme("dark")

    restored = Settings(config_file)
    assert restored.get_theme() == "dark"


def test_invalid_theme(tmp_path):
    settings = Settings(tmp_path / "settings.json")

    with pytest.raises(ValueError):
        settings.set_theme("invalid")
