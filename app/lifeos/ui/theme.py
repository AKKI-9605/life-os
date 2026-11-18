from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


LIGHT_PALETTE = {
    "window": "#F5F6FA",
    "surface": "#FFFFFF",
    "text": "#202431",
    "muted": "#737B8C",
    "accent": "#6487E8",
    "border": "#E5E8F0",
}

DARK_PALETTE = {
    "window": "#171A22",
    "surface": "#222633",
    "text": "#F1F3F8",
    "muted": "#A0A8B8",
    "accent": "#83A4FF",
    "border": "#343A49",
}


def apply_theme(app: QApplication, theme: str) -> None:
    if theme not in ("light", "dark", "system"):
        raise ValueError(f"Unsupported theme: {theme}")

    if theme == "system":
        theme = (
            "dark"
            if app.styleHints().colorScheme() == Qt.ColorScheme.Dark
            else "light"
        )

    colors = DARK_PALETTE if theme == "dark" else LIGHT_PALETTE

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["window"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["window"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["surface"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)
