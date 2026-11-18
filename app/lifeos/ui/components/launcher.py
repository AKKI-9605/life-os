"""LIFE OS searchable application launcher."""

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QVBoxLayout,
)

from lifeos.icons import icon_path
from lifeos.ui.components.navigation import PAGES


class AppLauncher(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("LIFE Launcher")
        self.resize(460, 450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        title = QLabel("Find your flow.")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel(
            "Everything you need, one search away."
        )
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search LIFE applications..."
        )
        layout.addWidget(self.search)

        self.apps = QListWidget()
        self.apps.setIconSize(QSize(24, 24))

        theme = "light"
        if parent is not None:
            theme = getattr(parent, "active_theme", "light")

        for name, icon_name in PAGES:
            item = QListWidgetItem(name)
            item.setIcon(
                QIcon(str(icon_path(icon_name, theme)))
            )
            self.apps.addItem(item)

        layout.addWidget(self.apps)

        self.search.textChanged.connect(
            self.filter_apps
        )
        self.apps.itemActivated.connect(
            self.launch_app
        )
        self.apps.itemClicked.connect(
            self.launch_app
        )

        self.search.setFocus()

    def filter_apps(self, text):
        query = text.strip().lower()

        for index in range(self.apps.count()):
            item = self.apps.item(index)
            item.setHidden(
                query not in item.text().lower()
            )

    def launch_app(self, item):
        destinations = {
            name: index
            for index, (name, _) in enumerate(PAGES)
        }

        self.parent().navigate(
            destinations[item.text()]
        )
        self.accept()
