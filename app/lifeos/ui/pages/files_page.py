from pathlib import Path

from PySide6.QtCore import QDir, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileSystemModel, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeView, QVBoxLayout, QWidget,
)


class FilesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_path = Path.home()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(12)

        title = QLabel("Files")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel("Browse your Linux workspace.")
        description.setObjectName("muted")
        layout.addWidget(description)

        controls = QHBoxLayout()

        home = QPushButton("Home")
        home.clicked.connect(lambda: self.go_to(Path.home()))
        controls.addWidget(home)

        up = QPushButton("Up")
        up.clicked.connect(self.go_up)
        controls.addWidget(up)

        self.path_input = QLineEdit()
        self.path_input.returnPressed.connect(self.go_to_input)
        controls.addWidget(self.path_input, 1)

        layout.addLayout(controls)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter files in this folder...")
        self.search.textChanged.connect(self.filter_rows)
        layout.addWidget(self.search)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(QDir.rootPath())

        self.view = QTreeView()
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)
        self.view.doubleClicked.connect(self.open_item)
        self.view.clicked.connect(self.describe_item)
        layout.addWidget(self.view, 1)

        self.status = QLabel("")
        self.status.setObjectName("muted")
        layout.addWidget(self.status)

        self.go_to(self.current_path)

    def go_to(self, path):
        path = Path(path).expanduser()

        if not path.is_dir():
            self.status.setText("Folder not found.")
            return

        self.current_path = path.resolve()
        self.path_input.setText(str(self.current_path))
        self.view.setRootIndex(
            self.model.index(str(self.current_path))
        )
        self.filter_rows(self.search.text())
        self.status.setText(str(self.current_path))

    def go_up(self):
        self.go_to(self.current_path.parent)

    def go_to_input(self):
        self.go_to(self.path_input.text())

    def filter_rows(self, text):
        root = self.view.rootIndex()
        for row in range(self.model.rowCount(root)):
            index = self.model.index(row, 0, root)
            name = self.model.fileName(index)
            visible = text.lower() in name.lower()
            self.view.setRowHidden(row, root, not visible)

    def describe_item(self, index):
        path = Path(self.model.filePath(index))
        kind = "Folder" if path.is_dir() else "File"
        self.status.setText(f"{kind}  /  {path.name}")

    def open_item(self, index):
        path = Path(self.model.filePath(index))

        if path.is_dir():
            self.go_to(path)
        else:
            if not QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(path))
            ):
                self.status.setText(
                    "No application available to open this file."
                )
