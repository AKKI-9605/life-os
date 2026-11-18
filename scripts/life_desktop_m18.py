"""LIFE OS M18 — Desktop Control Suite."""

import json
import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QLineEdit,
    QTabWidget, QWidget, QComboBox, QMessageBox,
    QProgressBar, QCheckBox
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import life_desktop_m17 as m17


CONFIG_DIR = Path.home() / ".config" / "lifeos"
CONFIG_FILE = CONFIG_DIR / "desktop-m18.json"
SCREENSHOTS = Path.home() / "Pictures" / "LIFE OS"


def load_preferences():
    defaults = {
        "workspace": 1,
        "search_limit": 1500,
        "confirm_close": True
    }
    try:
        saved = json.loads(CONFIG_FILE.read_text())
        if isinstance(saved, dict):
            defaults.update(saved)
    except (OSError, ValueError):
        pass
    return defaults


def save_preferences(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )


def format_size(value):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
        value /= 1024


def panel_button(text, callback):
    button = QPushButton(text)
    button.clicked.connect(callback)
    return button


class ControlSuite(QDialog):
    def __init__(self, desktop):
        super().__init__(desktop)

        self.desktop = desktop
        self.setWindowTitle("LIFE · Desktop Control Suite")
        self.resize(760, 570)
        self.setMinimumSize(600, 440)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 20)

        heading = QLabel("✦  LIFE Control Suite")
        heading.setObjectName("suiteHeading")
        outer.addWidget(heading)

        subtitle = QLabel(
            "Your workspaces, windows, files and system."
        )
        outer.addWidget(subtitle)

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs)

        self.build_workspaces()
        self.build_search()
        self.build_system()
        self.build_gallery()
        self.build_preferences()

        self.setStyleSheet("""
            QDialog {
                background: #F5F8FD;
                color: #263B55;
            }
            QLabel#suiteHeading {
                font-size: 23px;
                font-weight: 700;
            }
            QLabel {
                color: #344A64;
                font-size: 12px;
            }
            QTabWidget::pane {
                background: #FFFFFF;
                border: 1px solid #D9E5F1;
                border-radius: 12px;
                padding: 8px;
            }
            QTabBar::tab {
                background: #EAF1F9;
                padding: 11px 14px;
                border-radius: 7px;
                margin-right: 4px;
                color: #37506B;
            }
            QTabBar::tab:selected {
                background: #AFCFEF;
                color: #1F3651;
            }
            QPushButton {
                background: #DFECFA;
                color: #263E59;
                border: 1px solid #D0E0EF;
                border-radius: 10px;
                padding: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #C7DEF5;
            }
            QListWidget, QLineEdit, QComboBox {
                background: white;
                color: #283E59;
                border: 1px solid #D4E2EF;
                border-radius: 9px;
                padding: 9px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background: #D7E9FB;
                color: #213954;
            }
            QProgressBar {
                border: 0;
                background: #E4ECF5;
                color: #243C57;
                min-height: 17px;
                border-radius: 7px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #90BCE4;
                border-radius: 7px;
            }
        """)

    def make_tab(self, name):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(11)
        self.tabs.addTab(page, name)
        return layout

    def section(self, layout, text):
        label = QLabel(text)
        label.setStyleSheet(
            "font-size:15px;font-weight:700;"
            "padding-top:6px;"
        )
        layout.addWidget(label)

    def build_workspaces(self):
        layout = self.make_tab("Workspaces")

        self.section(layout, "Three independent workspaces")

        workspace_row = QHBoxLayout()

        for number in (1, 2, 3):
            workspace_row.addWidget(
                panel_button(
                    f"Workspace {number}",
                    lambda n=number:
                        self.desktop.switch_workspace(n)
                )
            )

        layout.addLayout(workspace_row)

        self.workspace_info = QLabel()
        layout.addWidget(self.workspace_info)

        self.section(layout, "Open windows")

        self.window_list = QListWidget()
        self.window_list.itemDoubleClicked.connect(
            lambda *_: self.activate_selected()
        )
        layout.addWidget(self.window_list)

        actions = QHBoxLayout()

        actions.addWidget(
            panel_button(
                "Focus",
                self.activate_selected
            )
        )
        actions.addWidget(
            panel_button(
                "Move to workspace",
                self.move_selected
            )
        )
        actions.addWidget(
            panel_button(
                "Arrange grid",
                self.desktop.grid_windows
            )
        )

        layout.addLayout(actions)

        self.target_workspace = QComboBox()
        self.target_workspace.addItems([
            "Workspace 1",
            "Workspace 2",
            "Workspace 3"
        ])
        layout.addWidget(self.target_workspace)

        layout.addWidget(
            panel_button(
                "Refresh windows",
                self.refresh_windows
            )
        )

    def refresh_windows(self):
        self.window_list.clear()
        self.window_refs = []

        active = self.desktop.m18_workspace

        self.workspace_info.setText(
            f"Current workspace: {active}"
        )

        for window in self.desktop.mdi.subWindowList():
            number = self.desktop.window_workspace(window)

            title = window.windowTitle() or "Untitled"

            prefix = "●" if number == active else "○"

            self.window_list.addItem(
                f"{prefix}  {title}  ·  Workspace {number}"
            )
            self.window_refs.append(window)

    def selected_window(self):
        index = self.window_list.currentRow()
        if 0 <= index < len(self.window_refs):
            window = self.window_refs[index]
            if window in self.desktop.mdi.subWindowList():
                return window
        return None

    def activate_selected(self):
        window = self.selected_window()

        if window is None:
            return

        number = self.desktop.window_workspace(window)
        self.desktop.switch_workspace(number)

        window.showNormal()
        self.desktop.mdi.setActiveSubWindow(window)
        window.raise_()
        self.refresh_windows()

    def move_selected(self):
        window = self.selected_window()

        if window is None:
            return

        number = self.target_workspace.currentIndex() + 1
        self.desktop.m18_assignments[id(window)] = number

        if number != self.desktop.m18_workspace:
            window.hide()
        else:
            window.showNormal()

        self.desktop.refresh_tasks()
        self.refresh_windows()

    def build_search(self):
        layout = self.make_tab("File Search")

        self.section(layout, "Find files in your home folders")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Enter part of a filename..."
        )
        self.search_input.returnPressed.connect(
            self.find_files
        )
        layout.addWidget(self.search_input)

        layout.addWidget(
            panel_button(
                "Search files",
                self.find_files
            )
        )

        self.search_status = QLabel(
            "Searches Documents, Downloads and Pictures."
        )
        layout.addWidget(self.search_status)

        self.file_results = QListWidget()
        self.file_results.itemDoubleClicked.connect(
            self.open_result
        )
        layout.addWidget(self.file_results)

        layout.addWidget(
            panel_button(
                "Open selected file",
                lambda: self.open_result()
            )
        )

    def find_files(self):
        query = self.search_input.text().strip().casefold()

        self.file_results.clear()
        self.found_files = []

        if not query:
            self.search_status.setText(
                "Enter a filename to search."
            )
            return

        roots = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures"
        ]

        examined = 0
        max_files = 1500
        max_results = 80

        for root in roots:
            if not root.is_dir():
                continue

            for directory, folders, filenames in os.walk(root):
                folders[:] = [
                    name for name in folders
                    if not name.startswith(".")
                ]

                for filename in filenames:
                    examined += 1

                    if query in filename.casefold():
                        path = Path(directory) / filename

                        self.found_files.append(path)
                        self.file_results.addItem(
                            str(path)
                        )

                    if (
                        examined >= max_files
                        or len(self.found_files) >= max_results
                    ):
                        break

                if (
                    examined >= max_files
                    or len(self.found_files) >= max_results
                ):
                    break

            if (
                examined >= max_files
                or len(self.found_files) >= max_results
            ):
                break

        self.search_status.setText(
            f"{len(self.found_files)} results · "
            f"{examined} files examined"
        )

    def open_result(self, *_):
        index = self.file_results.currentRow()

        if not 0 <= index < len(self.found_files):
            return

        path = self.found_files[index]

        if path.exists():
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(path))
            )

    def build_system(self):
        layout = self.make_tab("System")

        self.section(layout, "System resources")

        self.system_details = QLabel()
        layout.addWidget(self.system_details)

        self.ram_bar = QProgressBar()
        self.disk_bar = QProgressBar()

        layout.addWidget(QLabel("Memory usage"))
        layout.addWidget(self.ram_bar)

        layout.addWidget(QLabel("Disk usage"))
        layout.addWidget(self.disk_bar)

        layout.addWidget(
            panel_button(
                "Refresh system information",
                self.refresh_system
            )
        )

        layout.addStretch()

    def refresh_system(self):
        usage, used, total = m17.memory_info()

        self.ram_bar.setValue(round(usage))

        disk = shutil.disk_usage(Path.home())

        disk_used = disk.total - disk.free
        disk_percent = (
            disk_used / disk.total * 100
            if disk.total else 0
        )

        self.disk_bar.setValue(round(disk_percent))

        process_ram = m17.process_memory()

        self.system_details.setText(
            "LIFE OS desktop session\n\n"
            f"CPU cores: {os.cpu_count() or 'Unknown'}\n"
            f"System RAM: {used:.2f} / {total:.2f} GiB\n"
            f"LIFE process RAM: {process_ram:.0f} MiB\n"
            f"Disk used: {format_size(disk_used)}\n"
            f"Disk total: {format_size(disk.total)}\n"
            f"Open app windows: "
            f"{len(self.desktop.mdi.subWindowList())}"
        )

    def build_gallery(self):
        layout = self.make_tab("Screenshots")

        self.section(layout, "Your LIFE OS screenshots")

        self.gallery = QListWidget()
        self.gallery.itemDoubleClicked.connect(
            lambda *_: self.open_screenshot()
        )
        layout.addWidget(self.gallery)

        row = QHBoxLayout()

        row.addWidget(
            panel_button(
                "Refresh gallery",
                self.refresh_gallery
            )
        )
        row.addWidget(
            panel_button(
                "View screenshot",
                self.open_screenshot
            )
        )
        row.addWidget(
            panel_button(
                "Capture desktop",
                self.desktop.screenshot
            )
        )

        layout.addLayout(row)

    def refresh_gallery(self):
        SCREENSHOTS.mkdir(
            parents=True,
            exist_ok=True
        )

        self.gallery_files = sorted(
            SCREENSHOTS.glob("*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:100]

        self.gallery.clear()

        for path in self.gallery_files:
            self.gallery.addItem(path.name)

    def open_screenshot(self):
        index = self.gallery.currentRow()

        if 0 <= index < len(self.gallery_files):
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    str(self.gallery_files[index])
                )
            )

    def build_preferences(self):
        layout = self.make_tab("Preferences")

        self.section(layout, "Desktop preferences")

        self.preference_info = QLabel(
            "Settings are stored locally in your "
            "LIFE OS configuration folder."
        )
        self.preference_info.setWordWrap(True)
        layout.addWidget(self.preference_info)

        self.confirm_checkbox = QCheckBox(
            "Confirm before closing all app windows"
        )
        self.confirm_checkbox.setChecked(
            bool(
                self.desktop.m18_preferences.get(
                    "confirm_close", True
                )
            )
        )
        layout.addWidget(self.confirm_checkbox)

        layout.addWidget(
            panel_button(
                "Save preferences",
                self.save_settings
            )
        )

        layout.addStretch()

    def save_settings(self):
        prefs = self.desktop.m18_preferences

        prefs["confirm_close"] = (
            self.confirm_checkbox.isChecked()
        )

        prefs["workspace"] = (
            self.desktop.m18_workspace
        )

        save_preferences(prefs)

        QMessageBox.information(
            self,
            "LIFE OS",
            "Desktop preferences saved."
        )

    def open_tab(self, index):
        self.refresh_windows()
        self.refresh_system()
        self.refresh_gallery()
        self.tabs.setCurrentIndex(index)

        self.show()
        self.raise_()
        self.activateWindow()


class Desktop18(m17.Desktop17):
    def __init__(self, app):
        super().__init__(app)

        self.setWindowTitle(
            "LIFE OS · Desktop M18"
        )

        self.m18_preferences = load_preferences()
        self.m18_workspace = 1
        self.m18_assignments = {}

        for window in self.mdi.subWindowList():
            self.m18_assignments[id(window)] = 1

        self.m18_suite = ControlSuite(self)

        self.m18_shortcuts = []

        bindings = [
            ("Ctrl+Alt+W", lambda: self.m18_suite.open_tab(0)),
            ("Ctrl+Alt+F", lambda: self.m18_suite.open_tab(1)),
            ("Ctrl+Alt+I", lambda: self.m18_suite.open_tab(2)),
            ("Ctrl+Alt+G", lambda: self.m18_suite.open_tab(3)),
            ("Ctrl+Alt+1", lambda: self.switch_workspace(1)),
            ("Ctrl+Alt+2", lambda: self.switch_workspace(2)),
            ("Ctrl+Alt+3", lambda: self.switch_workspace(3)),
        ]

        for keys, callback in bindings:
            shortcut = QShortcut(
                QKeySequence(keys), self
            )
            shortcut.activated.connect(callback)
            self.m18_shortcuts.append(shortcut)

        self.m18_button = QPushButton(
            "✦ Control Suite", self
        )
        self.m18_button.clicked.connect(
            lambda: self.m18_suite.open_tab(0)
        )

        self.m18_button.setStyleSheet("""
            QPushButton {
                background: #E8F2FE;
                color: #274563;
                border: 1px solid #B9D1E9;
                border-radius: 12px;
                padding: 11px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #CFE5FA;
            }
        """)

        self.m18_button.adjustSize()
        self.position_control_button()
        self.m18_button.show()
        self.m18_button.raise_()

    def position_control_button(self):
        if not hasattr(self, "m18_button"):
            return

        button = self.m18_button
        button.move(
            max(10, self.width() - button.width() - 20),
            65
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_control_button()

    def window_workspace(self, window):
        return self.m18_assignments.get(
            id(window), 1
        )

    def switch_workspace(self, number):
        if number not in (1, 2, 3):
            return

        self.m18_workspace = number

        for window in self.mdi.subWindowList():
            assigned = self.window_workspace(window)

            if assigned == number:
                window.show()
            else:
                window.hide()

        self.m18_preferences["workspace"] = number
        save_preferences(self.m18_preferences)

        self.refresh_tasks()

        if hasattr(self, "m18_suite"):
            self.m18_suite.refresh_windows()

    def launch(self, name):
        previous = {
            id(window)
            for window in self.mdi.subWindowList()
        }

        result = super().launch(name)

        for window in self.mdi.subWindowList():
            if id(window) not in previous:
                self.m18_assignments[
                    id(window)
                ] = self.m18_workspace

        return result

    def closeEvent(self, event):
        prefs = self.m18_preferences
        prefs["workspace"] = self.m18_workspace
        save_preferences(prefs)

        super().closeEvent(event)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS M18")

    m17.m16.m15.m14.base.Wallpaper = (
        m17.m16.m15.m14.CachedWallpaper
    )

    desktop = Desktop18(app)

    print("LIFE OS M18 — Control Suite ready", flush=True)
    print("Ctrl+Alt+W : Workspaces", flush=True)
    print("Ctrl+Alt+F : File search", flush=True)
    print("Ctrl+Alt+I : System Center", flush=True)
    print("Ctrl+Alt+G : Screenshot Gallery", flush=True)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
