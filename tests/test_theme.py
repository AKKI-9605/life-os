import pytest

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from lifeos.ui.theme import apply_theme


def get_app():
    return QApplication.instance() or QApplication([])


def test_light_theme():
    app = get_app()
    apply_theme(app, "light")

    color = app.palette().color(QPalette.ColorRole.Window)
    assert color.name() == "#f5f6fa"


def test_dark_theme():
    app = get_app()
    apply_theme(app, "dark")

    color = app.palette().color(QPalette.ColorRole.Window)
    assert color.name() == "#171a22"


def test_invalid_theme():
    app = get_app()

    with pytest.raises(ValueError):
        apply_theme(app, "invalid")
