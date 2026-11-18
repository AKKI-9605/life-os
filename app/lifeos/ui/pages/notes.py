from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lifeos.storage import connect, list_notes, save_note, delete_note


class NotesPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.db = connect()
        self.current_note_id = None

        root = QHBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(24)

        sidebar = QVBoxLayout()
        sidebar.setSpacing(12)

        heading = QLabel("Notes")
        heading.setObjectName("pageTitle")
        sidebar.addWidget(heading)

        self.note_list = QListWidget()
        self.note_list.currentRowChanged.connect(self.load_selected_note)
        sidebar.addWidget(self.note_list)

        new_button = QPushButton("New note")
        new_button.clicked.connect(self.new_note)
        sidebar.addWidget(new_button)

        editor = QVBoxLayout()
        editor.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Untitled note")
        self.title_input.setObjectName("noteTitle")
        editor.addWidget(self.title_input)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Start writing...")
        editor.addWidget(self.body_input)

        actions = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_current_note)
        actions.addWidget(save_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.remove_current_note)
        actions.addWidget(delete_button)

        editor.addLayout(actions)

        root.addLayout(sidebar, 1)
        root.addLayout(editor, 2)

        self.refresh_notes()

    def refresh_notes(self, select_id=None):
        self.note_list.blockSignals(True)
        self.note_list.clear()

        self.notes = list_notes(self.db)

        selected_row = -1
        for index, note in enumerate(self.notes):
            self.note_list.addItem(note["title"])
            if note["id"] == select_id:
                selected_row = index

        self.note_list.blockSignals(False)

        if selected_row >= 0:
            self.note_list.setCurrentRow(selected_row)
        elif self.notes:
            self.note_list.setCurrentRow(0)
        else:
            self.current_note_id = None
            self.title_input.clear()
            self.body_input.clear()

    def load_selected_note(self, row):
        if row < 0 or row >= len(self.notes):
            return

        note = self.notes[row]
        self.current_note_id = note["id"]
        self.title_input.setText(note["title"])
        self.body_input.setPlainText(note["body"])

    def new_note(self):
        self.current_note_id = None
        self.note_list.clearSelection()
        self.title_input.clear()
        self.body_input.clear()
        self.title_input.setFocus()

    def save_current_note(self):
        note_id = save_note(
            self.db,
            self.title_input.text(),
            self.body_input.toPlainText(),
            self.current_note_id,
        )
        self.refresh_notes(select_id=note_id)

    def remove_current_note(self):
        if self.current_note_id is None:
            return

        if not self.window().confirm_delete():
            return

        delete_note(self.db, self.current_note_id)
        self.current_note_id = None
        self.refresh_notes()

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
