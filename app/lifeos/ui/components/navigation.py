
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)


class NavigationSidebar(QFrame):
    page_selected = Signal(int)
    launcher_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(212)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 18)
        layout.setSpacing(8)

        brand = QLabel("LIFE")
        brand.setObjectName("brand")
        layout.addWidget(brand)

        subtitle = QLabel("YOUR DESKTOP, YOUR WAY")
        subtitle.setObjectName("eyebrow")
        layout.addWidget(subtitle)
        layout.addSpacing(32)

        section = QLabel("WORKSPACE")
        section.setObjectName("eyebrow")
        layout.addWidget(section)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = {}

        for index, name in enumerate(("Overview", "Notes", "Files", "Settings")):
            button = QPushButton(name)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            button.setMinimumHeight(42)
            self.button_group.addButton(button, index)
            self.buttons[name] = button
            layout.addWidget(button)

        self.button_group.idClicked.connect(self.page_selected.emit)
        self.set_active_page(0)
        layout.addStretch()

        launcher = QPushButton("Open launcher")
        launcher.setObjectName("launcherButton")
        launcher.clicked.connect(self.launcher_requested.emit)
        layout.addWidget(launcher)

        footer = QLabel("LIFE OS  /  DEVELOPMENT")
        footer.setObjectName("eyebrow")
        layout.addWidget(footer)

    def set_active_page(self, index):
        button = self.button_group.button(index)
        if button:
            button.setChecked(True)
