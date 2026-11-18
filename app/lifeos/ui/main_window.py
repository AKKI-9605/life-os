
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from lifeos.core.settings import Settings
from lifeos.ui.theme import apply_theme, shell_stylesheet
from lifeos.ui.components.navigation import NavigationSidebar
from lifeos.ui.components.launcher import AppLauncher
from lifeos.ui.pages.dashboard import DashboardPage
from lifeos.ui.pages.notes import NotesPage
from lifeos.ui.pages.files_page import FilesPage
from lifeos.ui.pages.settings_page import SettingsPage


class LifeOSWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.settings = Settings()

        self.setWindowTitle("LIFE OS")
        self.resize(1180, 760)
        self.setMinimumSize(850, 570)

        root = QWidget()
        outer = QHBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(16)

        self.sidebar = NavigationSidebar()
        outer.addWidget(self.sidebar)

        workspace = QVBoxLayout()
        workspace.setSpacing(14)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 8, 16, 8)

        location = QLabel("LIFE  /  WORKSPACE")
        location.setObjectName("eyebrow")
        toolbar_layout.addWidget(location)

        toolbar_layout.addStretch()

        launcher_button = QPushButton("Applications")
        launcher_button.clicked.connect(self.open_launcher)
        toolbar_layout.addWidget(launcher_button)

        workspace.addWidget(toolbar)

        self.pages = QStackedWidget()
        self.notes = NotesPage()
        self.dashboard = DashboardPage(self.notes.db)
        self.files_page = FilesPage()
        self.settings_page = SettingsPage(self.settings.get_theme())

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.notes)
        self.pages.addWidget(self.files_page)
        self.pages.addWidget(self.settings_page)

        workspace.addWidget(self.pages, 1)
        outer.addLayout(workspace, 1)

        self.setCentralWidget(root)

        self.sidebar.page_selected.connect(self.navigate)
        self.sidebar.launcher_requested.connect(self.open_launcher)
        self.dashboard.note_selected.connect(self.open_dashboard_note)
        self.dashboard.notes_requested.connect(lambda: self.navigate(1))
        self.settings_page.theme_changed.connect(self.change_theme)

        self.change_theme(self.settings.get_theme(), save=False)

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.sidebar.set_active_page(index)

        if index == 0:
            self.dashboard.refresh()

    def open_dashboard_note(self, note_id):
        self.navigate(1)
        self.notes.open_note(note_id)

    def open_launcher(self):
        launcher = AppLauncher(self)
        launcher.setStyleSheet(self.styleSheet())
        launcher.exec()

    def change_theme(self, theme, save=True):
        if save:
            self.settings.set_theme(theme)

        apply_theme(self.app, theme)
        self.setStyleSheet(shell_stylesheet(self.app, theme))

    def confirm_delete(self):
        answer = QMessageBox.question(
            self,
            "Delete note",
            "Delete this note permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def closeEvent(self, event):
        self.notes.db.close()
        super().closeEvent(event)
