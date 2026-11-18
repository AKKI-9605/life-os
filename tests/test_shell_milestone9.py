import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from lifeos.ui.components.navigation import PAGES
from lifeos.ui.main_window import LifeOSWindow


@pytest.fixture
def app():
    instance = QApplication.instance()
    return instance or QApplication([])


def test_navigation_has_five_pages():
    assert [name for name, _ in PAGES] == [
        "Overview",
        "Notes",
        "Files",
        "Settings",
        "Appearance",
    ]


def test_native_shell_integrates_appearance(
    app, tmp_path, monkeypatch
):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / ".local/share"))

    window = LifeOSWindow(app)

    assert window.pages.count() == 5
    assert len(window.sidebar.button_group.buttons()) == 5

    window.navigate(4)

    assert window.pages.currentIndex() == 4
    assert window.appearance_page is not None

    window.close()


def test_navigation_to_files(app, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / ".local/share"))

    window = LifeOSWindow(app)

    window.navigate(2)

    assert window.pages.currentWidget() is window.files_page

    window.close()


def test_shell_theme_change(app, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / ".local/share"))

    window = LifeOSWindow(app)

    window.change_theme("dark")
    assert window.active_theme == "dark"

    window.change_theme("light")
    assert window.active_theme == "light"

    window.close()
