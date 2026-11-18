"""LIFE OS workspace navigation."""

from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)

from lifeos.icons import icon_path


PAGES = (
    ("Overview", "home"),
    ("Notes", "notes"),
    ("Files", "files"),
    ("Settings", "settings"),
    ("Appearance", "appearance"),
)


class NavigationSidebar(QFrame):
    page_selected = Signal(int)
    launcher_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(222)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 25, 16, 19)
        layout.setSpacing(9)

        brand = QLabel("LIFE")
        brand.setObjectName("brand")
        layout.addWidget(brand)

        subtitle = QLabel("YOUR SPACE. YOUR PACE.")
        subtitle.setObjectName("eyebrow")
        layout.addWidget(subtitle)
        layout.addSpacing(34)

        section = QLabel("WORKSPACE")
        section.setObjectName("eyebrow")
        layout.addWidget(section)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = {}

        for index, (name, icon_name) in enumerate(PAGES):
            button = QPushButton(name)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            button.setMinimumHeight(45)
            button.setIconSize(QSize(19, 19))
            button.setProperty("iconName", icon_name)

            self.button_group.addButton(button, index)
            self.buttons[name] = button
            layout.addWidget(button)

        self.button_group.idClicked.connect(
            self.page_selected.emit
        )

        self.set_active_page(0)
        layout.addStretch()

        self.launcher = QPushButton("  Applications")
        self.launcher.setObjectName("launcherButton")
        self.launcher.setMinimumHeight(45)
        self.launcher.setIconSize(QSize(20, 20))
        self.launcher.clicked.connect(
            self.launcher_requested.emit
        )
        layout.addWidget(self.launcher)

        layout.addSpacing(14)

        footer = QLabel("LIFE OS  /  DEVELOPMENT")
        footer.setObjectName("eyebrow")
        layout.addWidget(footer)

        self.set_icon_theme("light")

    def set_icon_theme(self, theme):
        selected = "dark" if theme == "dark" else "light"

        for button in self.buttons.values():
            icon_name = button.property("iconName")
            button.setIcon(
                QIcon(str(icon_path(icon_name, selected)))
            )

        self.launcher.setIcon(
            QIcon(str(icon_path("launcher", selected)))
        )

    def set_active_page(self, index):
        button = self.button_group.button(index)
        if button:
            button.setChecked(True)
