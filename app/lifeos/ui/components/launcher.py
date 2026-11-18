
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QListWidget,
    QVBoxLayout,
)


class AppLauncher(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("LIFE Launcher")
        self.resize(430, 410)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        title = QLabel("Applications")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Find an app...")
        layout.addWidget(self.search)

        self.apps = QListWidget()
        self.apps.addItems(["Overview", "Notes", "Files", "Settings"])
        layout.addWidget(self.apps)

        self.search.textChanged.connect(self.filter_apps)
        self.apps.itemActivated.connect(self.launch_app)
        self.apps.itemClicked.connect(self.launch_app)

    def filter_apps(self, text):
        for index in range(self.apps.count()):
            item = self.apps.item(index)
            item.setHidden(text.lower() not in item.text().lower())

    def launch_app(self, item):
        destination = {
            "Overview": 0,
            "Notes": 1,
            "Files": 2,
            "Settings": 3,
        }[item.text()]

        self.parent().navigate(destination)
        self.accept()
