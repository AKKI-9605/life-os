
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

LIGHT_PALETTE = {
    "window": "#F5F3EF",
    "surface": "#FFFFFF",
    "text": "#27313B",
    "muted": "#737F89",
    "accent": "#587B91",
    "border": "#DDDCD7",
}

DARK_PALETTE = {
    "window": "#202630",
    "surface": "#29313D",
    "text": "#F1F1EE",
    "muted": "#A6B0BB",
    "accent": "#8CB6CE",
    "border": "#414B57",
}


def resolved_theme(app, theme):
    if theme == "system":
        return (
            "dark"
            if app.styleHints().colorScheme() == Qt.ColorScheme.Dark
            else "light"
        )
    return theme


def apply_theme(app: QApplication, theme: str) -> None:
    if theme not in ("light", "dark", "system"):
        raise ValueError(f"Unsupported theme: {theme}")

    colors = DARK_PALETTE if resolved_theme(app, theme) == "dark" else LIGHT_PALETTE

    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: colors["window"],
        QPalette.ColorRole.WindowText: colors["text"],
        QPalette.ColorRole.Base: colors["surface"],
        QPalette.ColorRole.AlternateBase: colors["window"],
        QPalette.ColorRole.Text: colors["text"],
        QPalette.ColorRole.Button: colors["surface"],
        QPalette.ColorRole.ButtonText: colors["text"],
        QPalette.ColorRole.Highlight: colors["accent"],
        QPalette.ColorRole.HighlightedText: "#FFFFFF" if resolved_theme(app, theme) == "light" else "#18222B",
        QPalette.ColorRole.Mid: colors["border"],
        QPalette.ColorRole.PlaceholderText: colors["muted"],
    }

    for role, value in roles.items():
        palette.setColor(role, QColor(value))

    app.setPalette(palette)


def shell_stylesheet(app, theme):
    dark = resolved_theme(app, theme) == "dark"
    c = DARK_PALETTE if dark else LIGHT_PALETTE
    hover = "#354150" if dark else "#EBF0F2"
    selected = "#364F60" if dark else "#DFEAF0"
    selected_text = "#EAF4FA" if dark else "#29495C"

    return """
    QWidget {
        background: %(window)s;
        color: %(text)s;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px;
    }

    QFrame#sidebar, QFrame#toolbar {
        background: %(surface)s;
        border: 1px solid %(border)s;
        border-radius: 13px;
    }

    QLabel {
        background: transparent;
        border: none;
    }

    QLabel#brand {
        font-size: 27px;
        font-weight: 800;
        letter-spacing: 2px;
    }

    QLabel#eyebrow {
        font-size: 10px;
        font-weight: 700;
        color: %(muted)s;
    }

    QLabel#pageTitle {
        font-size: 30px;
        font-weight: 700;
    }

    QLabel#muted {
        color: %(muted)s;
    }

    QPushButton {
        background: %(surface)s;
        color: %(text)s;
        border: 1px solid %(border)s;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
    }

    QPushButton:hover {
        background: %(hover)s;
    }

    QPushButton#navigationButton {
        background: transparent;
        border: none;
        text-align: left;
        padding: 12px 14px;
        font-weight: 500;
    }

    QPushButton#navigationButton:hover {
        background: %(hover)s;
    }

    QPushButton#navigationButton:checked {
        background: %(selected)s;
        color: %(selected_text)s;
        font-weight: 700;
    }

    QPushButton#launcherButton {
        background: %(selected)s;
        color: %(selected_text)s;
        font-weight: 700;
        border: none;
    }

    QLineEdit, QTextEdit, QListWidget, QComboBox {
        background: %(surface)s;
        color: %(text)s;
        border: 1px solid %(border)s;
        border-radius: 9px;
        padding: 10px;
        selection-background-color: %(accent)s;
    }

    QLineEdit#noteTitle {
        font-size: 22px;
        font-weight: 700;
        padding: 14px;
    }

    QListWidget::item {
        padding: 12px;
        border-radius: 6px;
    }

    QListWidget::item:hover {
        background: %(hover)s;
    }

    QListWidget::item:selected {
        background: %(selected)s;
        color: %(selected_text)s;
    }

    QComboBox QAbstractItemView {
        background: %(surface)s;
        color: %(text)s;
        selection-background-color: %(selected)s;
        selection-color: %(selected_text)s;
    }
    """ % {
        **c,
        "hover": hover,
        "selected": selected,
        "selected_text": selected_text,
    }
