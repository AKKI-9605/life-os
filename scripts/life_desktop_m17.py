"""LIFE OS M17 — Performance and desktop controls."""

import os
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout,
    QLabel, QPushButton, QProgressBar
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import life_desktop_m16 as m16


def memory_info():
    info = {}

    try:
        with open("/proc/meminfo") as file:
            for line in file:
                name, value = line.split(":", 1)
                info[name] = int(value.strip().split()[0])

        total = info.get("MemTotal", 1)
        available = info.get("MemAvailable", total)
        used = total - available

        return used / total * 100, used / 1048576, total / 1048576
    except (OSError, ValueError, IndexError):
        return 0, 0, 0


def process_memory():
    try:
        with open("/proc/self/status") as file:
            for line in file:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        pass

    return 0


class PerformanceCenter(QDialog):
    def __init__(self, desktop):
        super().__init__(desktop)

        self.desktop = desktop
        self.setWindowTitle("LIFE · Performance Center")
        self.resize(430, 330)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 22, 25, 22)
        layout.setSpacing(14)

        heading = QLabel("✦ LIFE Performance Center")
        heading.setStyleSheet(
            "font-size:20px;font-weight:700;"
        )
        layout.addWidget(heading)

        self.cpu_label = QLabel()
        self.memory_label = QLabel()
        self.process_label = QLabel()
        self.windows_label = QLabel()
        self.load_label = QLabel()

        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)

        for widget in (
            self.cpu_label,
            self.load_label,
            self.memory_label,
            self.memory_bar,
            self.process_label,
            self.windows_label
        ):
            layout.addWidget(widget)

        button = QPushButton("Refresh now")
        button.clicked.connect(self.refresh)
        layout.addWidget(button)

        self.setStyleSheet("""
            QDialog {
                background:#F7F9FD;
                color:#263B55;
            }
            QLabel {
                font-size:13px;
            }
            QPushButton {
                background:#DCECFB;
                border:0;
                border-radius:10px;
                padding:11px;
                color:#253C59;
            }
            QProgressBar {
                background:#DFE7F0;
                border:0;
                border-radius:7px;
                min-height:14px;
                text-align:center;
            }
            QProgressBar::chunk {
                background:#8BB8DC;
                border-radius:7px;
            }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        self.timer.start(3000)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def refresh(self):
        usage, used, total = memory_info()

        self.memory_label.setText(
            f"System RAM: {used:.1f} / {total:.1f} GiB"
        )
        self.memory_bar.setValue(round(usage))

        try:
            load = os.getloadavg()
            self.load_label.setText(
                f"Load average: {load[0]:.2f} / "
                f"{load[1]:.2f} / {load[2]:.2f}"
            )
        except OSError:
            self.load_label.setText("Load unavailable")

        self.cpu_label.setText(
            f"Logical CPU count: {os.cpu_count() or 'Unknown'}"
        )

        self.process_label.setText(
            f"LIFE process RAM: {process_memory():.0f} MiB"
        )

        self.windows_label.setText(
            f"Open LIFE app windows: "
            f"{len(self.desktop.mdi.subWindowList())}"
        )


class Desktop17(m16.Desktop16):
    def __init__(self, app):
        super().__init__(app)

        self.setWindowTitle("LIFE OS · Desktop M17")

        self.performance_center = PerformanceCenter(self)
        self.hidden_desktop_windows = []
        self._last_task_state = None

        self.m17_shortcuts = []

        shortcuts = [
            ("Ctrl+Shift+P", self.open_performance),
            ("Ctrl+Alt+D", self.toggle_desktop),
            ("Ctrl+Alt+T", self.next_theme),
        ]

        for keys, action in shortcuts:
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.activated.connect(action)
            self.m17_shortcuts.append(shortcut)

    def open_performance(self):
        self.performance_center.show()
        self.performance_center.raise_()
        self.performance_center.activateWindow()

    def toggle_desktop(self):
        windows = self.mdi.subWindowList()

        if self.hidden_desktop_windows:
            for window in self.hidden_desktop_windows:
                if window in self.mdi.subWindowList():
                    window.showNormal()

            self.hidden_desktop_windows = []
        else:
            self.hidden_desktop_windows = [
                window for window in windows
                if window.isVisible()
                and not window.isMinimized()
            ]

            for window in self.hidden_desktop_windows:
                window.showMinimized()

        self.refresh_tasks()

    def next_theme(self):
        themes = list(m16.base.THEMES)

        current = themes.index(self.theme) \
            if self.theme in themes else -1

        self.apply_theme(
            themes[(current + 1) % len(themes)]
        )

    def refresh_tasks(self, *args):
        if not hasattr(self, "mdi"):
            return

        windows = self.mdi.subWindowList()
        active = self.mdi.activeSubWindow()

        state = (
            tuple(id(w) for w in windows),
            id(active) if active else None,
            tuple(w.isMinimized() for w in windows)
        )

        if state == getattr(self, "_last_task_state", None):
            return

        self._last_task_state = state
        super().refresh_tasks(*args)


def main():
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        print("WARNING: Offscreen rendering is enabled.")

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS M17")

    m16.m15.m14.base.Wallpaper = (
        m16.m15.m14.CachedWallpaper
    )

    desktop = Desktop17(app)

    print("LIFE OS M17 started", flush=True)
    print("Ctrl+Shift+P : Performance Center", flush=True)
    print("Ctrl+Alt+D   : Show desktop", flush=True)
    print("Ctrl+Alt+T   : Switch theme", flush=True)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
