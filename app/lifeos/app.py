"""LIFE OS desktop companion — first runnable prototype."""
from __future__ import annotations

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QTextEdit,
    QVBoxLayout, QWidget, QLineEdit
)
from lifeos.storage import connect, list_notes, save_note, delete_note

STYLES = """
* { font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif; }
QMainWindow, QWidget#root { background: #f7f7fb; color: #20243a; }
QFrame#sidebar { background: #ffffff; border: 1px solid #ececf3; border-radius: 18px; }
QLabel#brand { font-size: 22px; font-weight: 800; color: #29314d; padding: 8px 4px; }
QLabel#eyebrow { color: #888da5; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
QLabel#headline { font-size: 29px; font-weight: 750; color: #252b43; }
QLabel#muted { color: #858aa0; font-size: 13px; }
QPushButton { background: #f0effa; color: #4e4a83; border: 0; border-radius: 11px; padding: 11px 14px; text-align: left; font-weight: 600; }
QPushButton:hover { background: #e5e3f7; }
QPushButton#primary { background: #7772c8; color: white; text-align: center; }
QPushButton#primary:hover { background: #6862b8; }
QFrame#card { background: white; border: 1px solid #ececf3; border-radius: 18px; }
QLineEdit, QTextEdit, QListWidget { background: white; border: 1px solid #e7e7ef; border-radius: 12px; padding: 10px; }
QListWidget::item { padding: 10px; border-radius: 8px; }
QListWidget::item:selected { background: #eeedfb; color: #454078; }
"""

class LifeOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE OS")
        self.resize(1120, 740)
        self.db = connect()
        self.current_note_id: int | None = None

        root = QWidget(objectName="root")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)
        self.setCentralWidget(root)

        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(210)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 18, 16, 18)
        brand = QLabel("✳  LIFE OS", objectName="brand")
        side.addWidget(brand)
        side.addSpacing(22)
        side.addWidget(QLabel("WORKSPACE", objectName="eyebrow"))
        for label, page in [("⌂   Overview", 0), ("▤   Notes", 1)]:
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, p=page: self.pages.setCurrentIndex(p))
            side.addWidget(button)
        side.addStretch()
        side.addWidget(QLabel("Made for focused days.", objectName="muted"))
        layout.addWidget(sidebar)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.make_home())
        self.pages.addWidget(self.make_notes())
        layout.addWidget(self.pages, 1)
        self.refresh_notes()

    def make_home(self) -> QWidget:
        page = QWidget()
        col = QVBoxLayout(page)
        col.setContentsMargins(18, 14, 18, 14)
        col.setSpacing(18)
        col.addWidget(QLabel("YOUR SPACE  /  OVERVIEW", objectName="eyebrow"))
        col.addWidget(QLabel("A little more room to think.", objectName="headline"))
        col.addWidget(QLabel("A calm starting point for your study, ideas, and everyday work.", objectName="muted"))

        hero = QFrame(objectName="card")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        hero_layout.addWidget(QLabel("WELCOME TO LIFE OS", objectName="eyebrow"))
        hero_layout.addWidget(QLabel("Make space for what matters.", objectName="headline"))
        hero_layout.addWidget(QLabel("Your companion is running locally. Your notes stay on this device.", objectName="muted"))
        col.addWidget(hero)

        cards = QHBoxLayout()
        for title, subtitle, action in [
            ("Notes", "Capture an idea before it disappears.", "Open notes"),
            ("Classes", "A home for subjects and resources.", "Coming soon"),
            ("Planner", "Keep the next steps in sight.", "Coming soon"),
        ]:
            card = QFrame(objectName="card")
            box = QVBoxLayout(card)
            box.setContentsMargins(18, 18, 18, 18)
            box.addWidget(QLabel(title))
            box.addWidget(QLabel(subtitle, objectName="muted"))
            btn = QPushButton(action, objectName="primary" if title == "Notes" else "")
            if title == "Notes":
                btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))
            else:
                btn.setEnabled(False)
            box.addStretch()
            box.addWidget(btn)
            cards.addWidget(card)
        col.addLayout(cards)
        col.addStretch()
        return page

    def make_notes(self) -> QWidget:
        page = QWidget()
        col = QVBoxLayout(page)
        col.setContentsMargins(18, 14, 18, 14)
        col.addWidget(QLabel("YOUR WORKSPACE  /  NOTES", objectName="eyebrow"))
        col.addWidget(QLabel("Notes", objectName="headline"))
        col.addWidget(QLabel("Private, local-first notes. No account required.", objectName="muted"))
        body = QHBoxLayout()
        self.note_list = QListWidget()
        self.note_list.setMinimumWidth(220)
        self.note_list.currentItemChanged.connect(self.load_selected_note)
        body.addWidget(self.note_list, 1)
        editor = QVBoxLayout()
        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText("Note title")
        self.note_body = QTextEdit()
        self.note_body.setPlaceholderText("Start writing…")
        editor.addWidget(self.note_title)
        editor.addWidget(self.note_body, 1)
        actions = QHBoxLayout()
        new_btn = QPushButton("New note")
        new_btn.clicked.connect(self.new_note)
        save_btn = QPushButton("Save note", objectName="primary")
        save_btn.clicked.connect(self.save_current_note)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.remove_current_note)
        actions.addWidget(new_btn)
        actions.addStretch()
        actions.addWidget(delete_btn)
        actions.addWidget(save_btn)
        editor.addLayout(actions)
        body.addLayout(editor, 3)
        col.addLayout(body, 1)
        return page

    def refresh_notes(self, select_id: int | None = None) -> None:
        self.note_list.blockSignals(True)
        self.note_list.clear()
        selected = None
        for note in list_notes(self.db):
            item = QListWidgetItem(note["title"])
            item.setData(Qt.ItemDataRole.UserRole, note["id"])
            self.note_list.addItem(item)
            if note["id"] == select_id:
                selected = item
        self.note_list.blockSignals(False)
        if selected:
            self.note_list.setCurrentItem(selected)
        elif self.note_list.count():
            self.note_list.setCurrentRow(0)
        else:
            self.new_note()

    def load_selected_note(self, current, previous=None) -> None:
        if current is None:
            return
        note_id = current.data(Qt.ItemDataRole.UserRole)
        note = self.db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if note:
            self.current_note_id = note_id
            self.note_title.setText(note["title"])
            self.note_body.setPlainText(note["body"])

    def new_note(self) -> None:
        self.current_note_id = None
        self.note_list.clearSelection()
        self.note_title.clear()
        self.note_body.clear()
        self.note_title.setFocus()

    def save_current_note(self) -> None:
        note_id = save_note(self.db, self.note_title.text(), self.note_body.toPlainText(), self.current_note_id)
        self.current_note_id = note_id
        self.refresh_notes(note_id)

    def remove_current_note(self) -> None:
        if self.current_note_id is None:
            self.new_note()
            return
        answer = QMessageBox.question(self, "Delete note", "Delete this note permanently?")
        if answer == QMessageBox.StandardButton.Yes:
            delete_note(self.db, self.current_note_id)
            self.current_note_id = None
            self.refresh_notes()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES)
    window = LifeOSWindow()
    window.show()
    return app.exec()
