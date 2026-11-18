"""Main LIFE OS workspace."""

from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from lifeos.core.settings import Settings
from lifeos.appearance import (
    WALLPAPERS, load_appearance, save_appearance,
)
from lifeos.icons import wallpaper_path
from lifeos.ui.theme import (
    apply_theme, shell_stylesheet, resolved_theme,
)
from lifeos.ui.components.navigation import NavigationSidebar
from lifeos.ui.components.launcher import AppLauncher
from lifeos.ui.pages.dashboard import DashboardPage
from lifeos.ui.pages.notes import NotesPage
from lifeos.ui.pages.files_page import FilesPage
from lifeos.ui.pages.settings_page import SettingsPage
from lifeos.ui.pages.appearance_page import AppearancePage


class LifeOSWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.settings = Settings()
        self.appearance = load_appearance()

        initial_theme = self.settings.get_theme()
        if initial_theme == "system":
            initial_theme = self.appearance["theme"]

        self.active_theme = initial_theme

        self.setWindowTitle("LIFE OS — Your Space")
        self.resize(1280, 810)
        self.setMinimumSize(850, 570)

        root = QWidget()
        root.setObjectName("shellRoot")

        outer = QHBoxLayout(root)
        outer.setContentsMargins(17, 17, 17, 17)
        outer.setSpacing(15)

        self.sidebar = NavigationSidebar()
        outer.addWidget(self.sidebar)

        workspace = QVBoxLayout()
        workspace.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(18, 9, 18, 9)

        location = QLabel("LIFE  /  WORKSPACE")
        location.setObjectName("eyebrow")
        toolbar_layout.addWidget(location)

        toolbar_layout.addStretch()

        launcher_button = QPushButton("◈  Applications")
        launcher_button.clicked.connect(
            self.open_launcher
        )
        toolbar_layout.addWidget(launcher_button)

        workspace.addWidget(toolbar)

        self.hero_card = QFrame()
        self.hero_card.setObjectName("heroCard")

        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(13, 12, 21, 12)
        hero_layout.setSpacing(20)

        self.wallpaper_preview = QSvgWidget()
        self.wallpaper_preview.setFixedSize(226, 127)
        hero_layout.addWidget(self.wallpaper_preview)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(5)

        eyebrow = QLabel("YOUR PERSONAL WORKSPACE")
        eyebrow.setObjectName("eyebrow")
        hero_text.addWidget(eyebrow)

        greeting = QLabel("Find your flow.")
        greeting.setObjectName("heroTitle")
        hero_text.addWidget(greeting)

        self.wallpaper_label = QLabel()
        self.wallpaper_label.setObjectName("muted")
        hero_text.addWidget(self.wallpaper_label)

        hero_text.addStretch()
        hero_layout.addLayout(hero_text, 1)

        self.appearance_shortcut = QPushButton(
            "Personalize"
        )
        self.appearance_shortcut.clicked.connect(
            lambda: self.navigate(4)
        )
        hero_layout.addWidget(
            self.appearance_shortcut,
            alignment=Qt.AlignmentFlag.AlignBottom,
        )

        workspace.addWidget(self.hero_card)

        self.pages = QStackedWidget()

        self.notes = NotesPage()
        self.dashboard = DashboardPage(self.notes.db)
        self.files_page = FilesPage()
        self.settings_page = SettingsPage(initial_theme)
        self.appearance_page = AppearancePage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.notes)
        self.pages.addWidget(self.files_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.appearance_page)

        workspace.addWidget(self.pages, 1)
        outer.addLayout(workspace, 1)

        self.setCentralWidget(root)

        self.sidebar.page_selected.connect(
            self.navigate
        )
        self.sidebar.launcher_requested.connect(
            self.open_launcher
        )

        self.dashboard.note_selected.connect(
            self.open_dashboard_note
        )
        self.dashboard.notes_requested.connect(
            lambda: self.navigate(1)
        )

        self.settings_page.theme_changed.connect(
            self.change_theme
        )
        self.appearance_page.appearance_applied.connect(
            self.apply_appearance
        )

        self.change_theme(initial_theme, save=False)
        self.refresh_wallpaper()

    def navigate(self, index):
        if not 0 <= index < self.pages.count():
            return

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

    def refresh_wallpaper(self):
        selection = load_appearance()
        name = selection["wallpaper"]
        path = wallpaper_path(name)

        if path.exists():
            self.wallpaper_preview.load(str(path))

        self.wallpaper_label.setText(
            f"Current wallpaper · {WALLPAPERS[name]}"
        )

    def apply_appearance(self, theme, wallpaper):
        self.change_theme(theme)
        self.refresh_wallpaper()

    def change_theme(self, theme, save=True):
        if save:
            self.settings.set_theme(theme)

        apply_theme(self.app, theme)

        self.active_theme = resolved_theme(
            self.app, theme
        )

        self.setStyleSheet(
            shell_stylesheet(self.app, theme)
        )

        self.sidebar.set_icon_theme(
            self.active_theme
        )

        index = self.settings_page.theme_selector.findData(
            theme
        )
        if index >= 0:
            selector = self.settings_page.theme_selector
            selector.blockSignals(True)
            selector.setCurrentIndex(index)
            selector.blockSignals(False)

        if theme in ("light", "dark"):
            current = load_appearance()
            if current["theme"] != theme:
                save_appearance(
                    theme,
                    current["wallpaper"],
                )

            self.appearance_page.selected_theme = theme
            self.appearance_page.refresh()

    def confirm_delete(self):
        answer = QMessageBox.question(
            self,
            "Delete note",
            "Delete this note permanently?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def closeEvent(self, event):
        self.notes.db.close()
        super().closeEvent(event)
