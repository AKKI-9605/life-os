import sqlite3

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lifeos.storage import list_notes


class DashboardPage(QWidget):
    note_selected = Signal(int)
    notes_requested = Signal()

    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(14)

        eyebrow = QLabel("LIFE OS / WORKSPACE")
        eyebrow.setObjectName("eyebrow")
        layout.addWidget(eyebrow)

        title = QLabel("Your space.")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel("Pick up where you left off.")
        description.setObjectName("muted")
        layout.addWidget(description)

        layout.addSpacing(24)

        recent_title = QLabel("Recent notes")
        layout.addWidget(recent_title)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(300)
        self.recent_list.setSpacing(5)
        self.recent_list.itemClicked.connect(self.open_recent)
        layout.addWidget(self.recent_list)

        self.open_notes_button = QPushButton("Open Notes")
        self.open_notes_button.clicked.connect(self.notes_requested.emit)
        layout.addWidget(self.open_notes_button)

        layout.addStretch()
        self.refresh()

    def refresh(self):
        self.recent_list.clear()
        notes = list_notes(self.db)[:5]

        if not notes:
            item = QListWidgetItem("No notes yet. Start with a thought.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recent_list.addItem(item)
            return

        for note in notes:
            preview = " ".join(note["body"].split())[:75]
            label = note["title"]

            if preview:
                label += f"\n{preview}"

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, note["id"])
            self.recent_list.addItem(item)

    def open_recent(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id is not None:
            self.note_selected.emit(note_id)
