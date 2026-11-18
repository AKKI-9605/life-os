
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QLabel, QVBoxLayout, QWidget,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, current_theme="system", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(14)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel("Make LIFE feel like yours.")
        description.setObjectName("muted")
        layout.addWidget(description)
        layout.addSpacing(26)

        appearance = QLabel("APPEARANCE")
        appearance.setObjectName("eyebrow")
        layout.addWidget(appearance)

        layout.addWidget(QLabel("Color mode"))

        self.theme_selector = QComboBox()
        self.theme_selector.addItem("Follow system", "system")
        self.theme_selector.addItem("Light", "light")
        self.theme_selector.addItem("Dark", "dark")

        index = self.theme_selector.findData(current_theme)
        self.theme_selector.setCurrentIndex(max(index, 0))
        self.theme_selector.setMaximumWidth(300)
        layout.addWidget(self.theme_selector)

        self.theme_selector.currentIndexChanged.connect(self.change_theme)

        layout.addSpacing(26)

        about = QLabel("ABOUT")
        about.setObjectName("eyebrow")
        layout.addWidget(about)

        layout.addWidget(QLabel("LIFE OS — development prototype"))

        info = QLabel(
            "The current workspace is a PySide6 application. "
            "Desktop integration and system applications are in development."
        )
        info.setWordWrap(True)
        info.setObjectName("muted")
        layout.addWidget(info)

        layout.addStretch()

    def change_theme(self, index):
        theme = self.theme_selector.itemData(index)
        if theme:
            self.theme_changed.emit(theme)
