"""LIFE OS Appearance application."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea,
    QFrame, QSizePolicy
)

from lifeos.appearance import (
    WALLPAPERS, load_appearance, save_appearance
)


ASSETS = (
    Path(__file__).resolve().parents[4]
    / "desktop/assets/wallpapers"
)


class WallpaperCard(QFrame):
    def __init__(self, key, title, path, callback):
        super().__init__()
        self.key = key
        self.setObjectName("wallpaperCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(9)

        self.preview = QSvgWidget(str(path))
        self.preview.setFixedHeight(115)
        self.preview.setMinimumWidth(170)
        layout.addWidget(self.preview)

        self.button = QPushButton(title)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.clicked.connect(
            lambda: callback(self.key)
        )
        layout.addWidget(self.button)

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class AppearancePage(QWidget):
    appearance_applied = Signal(str, str)
    def __init__(self, parent=None):
        super().__init__(parent)

        settings = load_appearance()
        self.selected_theme = settings["theme"]
        self.selected_wallpaper = settings["wallpaper"]

        self.setWindowTitle("LIFE Appearance")
        self.resize(920, 720)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)

        body = QVBoxLayout(page)
        body.setContentsMargins(36, 30, 36, 30)
        body.setSpacing(18)

        eyebrow = QLabel("PERSONALIZATION  /  LIFE OS")
        eyebrow.setObjectName("eyebrow")
        body.addWidget(eyebrow)

        title = QLabel("Make LIFE yours.")
        title.setObjectName("appearanceTitle")
        body.addWidget(title)

        subtitle = QLabel(
            "Your desktop should feel like a place you want to be."
        )
        subtitle.setObjectName("muted")
        body.addWidget(subtitle)

        self.hero = QSvgWidget()
        self.hero.setMinimumHeight(230)
        self.hero.setMaximumHeight(320)
        self.hero.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        body.addWidget(self.hero)

        wallpaper_title = QLabel("Desktop wallpaper")
        wallpaper_title.setObjectName("sectionTitle")
        body.addWidget(wallpaper_title)

        wallpaper_hint = QLabel(
            "Original artwork designed for LIFE OS."
        )
        wallpaper_hint.setObjectName("muted")
        body.addWidget(wallpaper_hint)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)

        self.cards = {}

        for index, (key, name) in enumerate(WALLPAPERS.items()):
            card = WallpaperCard(
                key, name,
                ASSETS / f"{key}.svg",
                self.choose_wallpaper
            )
            self.cards[key] = card
            cards_layout.addWidget(
                card, index // 3, index % 3
            )

        body.addLayout(cards_layout)

        theme_title = QLabel("Appearance")
        theme_title.setObjectName("sectionTitle")
        body.addWidget(theme_title)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(12)

        self.light_button = QPushButton("☀  Warm Light")
        self.dark_button = QPushButton("☾  Deep Night")

        for button in (
            self.light_button, self.dark_button
        ):
            button.setMinimumHeight(46)
            button.setCursor(Qt.PointingHandCursor)
            theme_row.addWidget(button)

        self.light_button.clicked.connect(
            lambda: self.choose_theme("light")
        )
        self.dark_button.clicked.connect(
            lambda: self.choose_theme("dark")
        )

        body.addLayout(theme_row)

        footer = QHBoxLayout()

        self.status = QLabel("Appearance preferences")
        self.status.setObjectName("muted")
        footer.addWidget(self.status)

        footer.addStretch()

        self.save_button = QPushButton("Apply appearance")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setMinimumHeight(44)
        self.save_button.clicked.connect(self.apply_changes)
        footer.addWidget(self.save_button)

        body.addLayout(footer)
        body.addStretch()

        self.refresh()

    def choose_wallpaper(self, key):
        self.selected_wallpaper = key
        self.refresh()

    def choose_theme(self, theme):
        self.selected_theme = theme
        self.refresh()

    def refresh(self):
        path = ASSETS / f"{self.selected_wallpaper}.svg"
        self.hero.load(str(path))

        for key, card in self.cards.items():
            card.set_selected(
                key == self.selected_wallpaper
            )

        self.light_button.setProperty(
            "selected", self.selected_theme == "light"
        )
        self.dark_button.setProperty(
            "selected", self.selected_theme == "dark"
        )

        for button in (
            self.light_button, self.dark_button
        ):
            button.style().unpolish(button)
            button.style().polish(button)

        self.apply_stylesheet()

    def apply_stylesheet(self):
        dark = self.selected_theme == "dark"

        bg = "#182535" if dark else "#F7F8F6"
        surface = "#25374B" if dark else "#FFFFFF"
        text = "#EDF4F9" if dark else "#293B4C"
        muted = "#B3C5D3" if dark else "#788995"
        border = "#425A70" if dark else "#DEE7E9"
        selected = "#42617B" if dark else "#D8E9F0"
        accent = "#85B9D8" if dark else "#537E9C"
        contrast = "#102335" if dark else "#FFFFFF"

        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                color: {text};
                font-family: 'Inter', 'Arial', sans-serif;
                font-size: 13px;
            }}
            QScrollArea {{
                border: none;
            }}
            QLabel#eyebrow {{
                color: {accent};
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel#appearanceTitle {{
                font-size: 30px;
                font-weight: 700;
            }}
            QLabel#sectionTitle {{
                font-size: 18px;
                font-weight: 650;
            }}
            QLabel#muted {{
                color: {muted};
            }}
            QFrame#wallpaperCard {{
                background: {surface};
                border: 1px solid {border};
                border-radius: 15px;
            }}
            QFrame#wallpaperCard[selected="true"] {{
                background: {selected};
                border: 2px solid {accent};
            }}
            QPushButton {{
                background: {surface};
                color: {text};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 10px 15px;
            }}
            QPushButton:hover {{
                border-color: {accent};
            }}
            QPushButton[selected="true"] {{
                background: {selected};
                border-color: {accent};
            }}
            QPushButton#primaryButton {{
                background: {accent};
                color: {contrast};
                font-weight: 700;
                border: none;
                padding: 11px 22px;
            }}
        """)

    def apply_changes(self):
        path = save_appearance(
            self.selected_theme,
            self.selected_wallpaper
        )
        self.status.setText(
            f"Saved: {WALLPAPERS[self.selected_wallpaper]}"
        )
        print(f"LIFE Appearance saved: {path}")
        self.appearance_applied.emit(
            self.selected_theme,
            self.selected_wallpaper,
        )
