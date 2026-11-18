"""LIFE OS M15 — Desktop Experience."""

import sys
import math
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QBrush, QColor
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel,
    QLineEdit, QListWidget, QMessageBox
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import life_desktop_m14 as m14


class CommandPalette(QDialog):
    def __init__(self, desktop):
        super().__init__(desktop)
        self.desktop = desktop
        self.setWindowTitle("LIFE · Command Center")
        self.setMinimumSize(470, 440)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 22)
        layout.setSpacing(12)

        heading = QLabel("✦  What would you like to do?")
        heading.setObjectName("paletteHeading")
        layout.addWidget(heading)

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search apps, commands or themes…"
        )
        layout.addWidget(self.search)

        self.listing = QListWidget()
        layout.addWidget(self.listing)

        self.commands = []

        for name, *_ in m14.base.APP_DEFS:
            self.commands.append((
                f"Open  ·  {name}",
                lambda n=name: desktop.launch(n)
            ))

        self.commands.extend([
            ("Desktop · Home", desktop.go_home),
            ("Windows · Side by side", desktop.side_by_side),
            ("Windows · Grid layout", desktop.grid_windows),
            ("Windows · Window Studio", desktop.show_windows),
            ("Display · Fullscreen", desktop.toggle_fullscreen),
            ("Display · Screenshot", desktop.screenshot),
            ("Settings · Control Center", desktop.show_settings),
        ])

        for theme in m14.base.THEMES:
            self.commands.append((
                f"Theme · {theme}",
                lambda n=theme: desktop.apply_theme(n)
            ))

        self.search.textChanged.connect(self.filter_commands)
        self.search.returnPressed.connect(self.run_selected)
        self.listing.itemActivated.connect(
            lambda *_: self.run_selected()
        )

        self.setStyleSheet("""
            QDialog {
                background: #F7F9FF;
                color: #263B55;
            }
            QLabel#paletteHeading {
                font-size: 20px;
                font-weight: 700;
                padding: 8px;
            }
            QLineEdit {
                background: white;
                border: 1px solid #BDD1E3;
                border-radius: 12px;
                padding: 12px;
            }
            QListWidget {
                background: white;
                border: 1px solid #D9E6F0;
                border-radius: 14px;
                padding: 9px;
                outline: 0;
            }
            QListWidget::item {
                padding: 11px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #DCECFB;
                color: #213954;
            }
        """)

        self.filter_commands("")

    def filter_commands(self, query):
        self.filtered = [
            (name, action)
            for name, action in self.commands
            if query.casefold() in name.casefold()
        ]
        self.listing.clear()
        self.listing.addItems(
            [name for name, _ in self.filtered]
        )
        if self.filtered:
            self.listing.setCurrentRow(0)

    def run_selected(self):
        index = self.listing.currentRow()
        if 0 <= index < len(self.filtered):
            action = self.filtered[index][1]
            self.hide()
            action()

    def open_palette(self):
        self.search.clear()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search.setFocus()


class Desktop15(m14.Desktop14):
    def __init__(self, app):
        super().__init__(app)
        self.setWindowTitle("LIFE OS · Desktop M15")

        self.command_palette = CommandPalette(self)

        shortcuts = [
            ("Ctrl+K", self.command_palette.open_palette),
            ("F11", self.toggle_fullscreen),
            ("Ctrl+Shift+S", self.screenshot),
            ("Ctrl+Shift+G", self.grid_windows),
            ("Ctrl+Shift+2", self.side_by_side),
        ]

        self.m15_shortcuts = []

        for keys, action in shortcuts:
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.activated.connect(action)
            self.m15_shortcuts.append(shortcut)

        QTimer.singleShot(0, self.add_command_button)

    def add_command_button(self):
        bars = self.findChildren(m14.QFrame, "chrome")
        if not bars:
            return

        layout = bars[0].layout()
        if layout:
            button = m14.base.button(
                "⌘ Commands",
                self.command_palette.open_palette,
                "topButton"
            )
            layout.insertWidget(
                min(6, layout.count()),
                button
            )

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def available_windows(self):
        return [
            window
            for window in self.mdi.subWindowList()
            if not window.isHidden()
        ]

    def grid_windows(self):
        windows = self.available_windows()

        if not windows:
            self.show_launcher()
            return

        columns = math.ceil(math.sqrt(len(windows)))
        rows = math.ceil(len(windows) / columns)

        area = self.mdi.viewport()
        width = max(220, (area.width() - 18) // columns)
        height = max(180, (area.height() - 18) // rows)

        for index, window in enumerate(windows):
            window.showNormal()
            col = index % columns
            row = index // columns

            window.setGeometry(
                6 + col * width,
                6 + row * height,
                width - 6,
                height - 6
            )

        self.refresh_tasks()

    def side_by_side(self):
        windows = self.available_windows()

        if not windows:
            self.show_launcher()
            return

        area = self.mdi.viewport()
        width = max(
            250,
            (area.width() - 12) // len(windows)
        )

        for index, window in enumerate(windows):
            window.showNormal()
            window.setGeometry(
                6 + width * index,
                6,
                width - 8,
                max(210, area.height() - 12)
            )

        self.refresh_tasks()

    def screenshot(self):
        folder = Path.home() / "Pictures" / "LIFE OS"
        folder.mkdir(parents=True, exist_ok=True)

        filename = (
            "life-desktop-"
            + datetime.now().strftime("%Y%m%d-%H%M%S")
            + ".png"
        )
        path = folder / filename

        if self.grab().save(str(path), "PNG"):
            self.events.append((
                "Screenshot saved",
                str(path)
            ))
            self.show_notifications()
        else:
            QMessageBox.warning(
                self,
                "Screenshot",
                "Could not save screenshot."
            )


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS Desktop M15")

    m14.base.Wallpaper = m14.CachedWallpaper

    desktop = Desktop15(app)

    # Preserve the transparent desktop and solid app windows.
    desktop.mdi.setBackground(
        QBrush(QColor(0, 0, 0, 0))
    )
    desktop.mdi.setAutoFillBackground(False)
    desktop.mdi.viewport().setAutoFillBackground(False)
    desktop.mdi.viewport().setStyleSheet(
        "QMdiArea { background: transparent; }"
        "QMdiSubWindow { background: #F7F9FD; }"
        "QMdiSubWindow > QWidget { background: #F7F9FD; }"
    )

    print("LIFE OS M15 ready", flush=True)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
