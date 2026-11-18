from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QHBoxLayout,
    QWidget,
)

from lifeos.core.settings import Settings
from lifeos.ui.theme import apply_theme
from lifeos.ui.components.navigation import NavigationSidebar
from lifeos.ui.pages.dashboard import DashboardPage
from lifeos.ui.pages.notes import NotesPage


class LifeOSWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.settings = Settings()

        apply_theme(self.app, self.settings.get_theme())

        self.setWindowTitle("LIFE OS")
        self.resize(1120, 740)
        self.setMinimumSize(800, 560)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        self.sidebar = NavigationSidebar()

        self.pages = QStackedWidget()
        self.notes = NotesPage()
        self.dashboard = DashboardPage(self.notes.db)

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.notes)

        self.sidebar.page_selected.connect(self.navigate)
        self.dashboard.note_selected.connect(self.open_dashboard_note)
        self.dashboard.notes_requested.connect(lambda: self.navigate(1))

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages, 1)

        self.setCentralWidget(root)

        self.setStyleSheet("""
            * {
                font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
            }

            QMainWindow, QWidget {
                background: palette(window);
                color: palette(window-text);
            }

            QFrame#sidebar {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }

            QLabel#brand {
                font-size: 21px;
                font-weight: 750;
                padding: 8px 4px;
            }

            QLabel#eyebrow {
                color: palette(mid);
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
            }

            QLabel#pageTitle {
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#muted {
                color: palette(mid);
                font-size: 13px;
            }

            QPushButton {
                background: transparent;
                border: none;
                border-radius: 7px;
                padding: 10px 12px;
                text-align: left;
            }

            QPushButton:hover {
                background: palette(alternate-base);
            }

            QPushButton:checked {
                background: palette(highlight);
                color: palette(highlighted-text);
            }

            QLineEdit, QTextEdit, QListWidget {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 7px;
                padding: 9px;
            }

            QListWidget::item {
                padding: 9px;
            }

            QListWidget::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)

    def navigate(self, index: int):
        self.pages.setCurrentIndex(index)
        if index == 0:
            self.dashboard.refresh()

    def open_dashboard_note(self, note_id: int):
        self.navigate(1)
        self.notes.open_note(note_id)

    def closeEvent(self, event):
        self.notes.db.close()
        super().closeEvent(event)

    def confirm_delete(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Delete note",
            "Delete this note permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes
