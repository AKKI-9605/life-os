"""LIFE OS M12: a dock, app drawer, search, system panel and original native shell.

Runs inside an existing X11 Codespaces session. No repository or user-data writes.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize, QRectF, QPointF
from PySide6.QtGui import QAction, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QDockWidget, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QScrollArea, QSizePolicy, QStackedWidget,
    QToolButton, QVBoxLayout, QWidget,
)

# The M11 native apps are reused; nothing is reimplemented or overwritten.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from life_apps import Calculator, TextEditor, Calendar, FileBrowser
from life_extra_apps import Clock, SystemMonitor, ImageViewer
from lifeos.ui.main_window import LifeOSWindow

PALETTES = {
    "morning": {"bg": "#F4F5F8", "panel": "#FFFFFF", "ink": "#253954", "muted": "#74829A", "line": "#DFE5F0", "accent": "#C6DFF7", "accent_ink": "#214B74"},
    "evening": {"bg": "#182437", "panel": "#263550", "ink": "#F4F6FF", "muted": "#B2BED3", "line": "#435473", "accent": "#526E99", "accent_ink": "#FFFFFF"},
}

APPS = [
    ("Calculator", "Arithmetic and quick numbers", "▦", Calculator),
    ("Writer", "Notes, plain text and code", "✎", TextEditor),
    ("Calendar", "Browse dates and months", "▤", Calendar),
    ("Explorer", "Navigate your files", "▣", FileBrowser),
    ("Clock", "Time and date", "◷", Clock),
    ("System Monitor", "Check system resources", "◫", SystemMonitor),
    ("Image Viewer", "Open images", "▧", ImageViewer),
]


def style_for(mode: str) -> str:
    p = PALETTES[mode]
    return f"""
    QWidget#LifeChrome {{ background:{p['bg']}; color:{p['ink']}; font-family:'DejaVu Sans'; font-size:13px; }}
    QWidget#LifePanel, QFrame#LifePanel {{ background:{p['panel']}; border:1px solid {p['line']}; border-radius:17px; }}
    QFrame#LifePanel QLabel {{ background:transparent; border:0px; }}
    QLabel#LifeTitle {{ font-size:23px; font-weight:750; color:{p['ink']}; background:transparent; }}
    QLabel#LifeSub {{ color:{p['muted']}; background:transparent; }}
    QLineEdit#LifeSearch {{ background:{p['panel']}; border:1px solid {p['line']}; border-radius:14px; padding:11px 15px; color:{p['ink']}; }}
    QPushButton#LifeControl {{ background:{p['panel']}; border:1px solid {p['line']}; border-radius:14px; padding:12px; color:{p['ink']}; text-align:left; }}
    QPushButton#LifeControl:hover {{ background:{p['accent']}; color:{p['accent_ink']}; }}
    QPushButton#LifeAccent {{ background:{p['accent']}; border:0; border-radius:14px; padding:13px; font-weight:700; color:{p['accent_ink']}; }}
    QPushButton#LifeAccent:hover {{ border:1px solid {p['accent_ink']}; }}
    QDockWidget#LifeDock {{ color:{p['ink']}; font-weight:700; }}
    QDockWidget#LifeDock::title {{ text-align:left; padding:8px; background:{p['panel']}; }}
    """


class Landscape(QWidget):
    """Tiny original painted landscape; no image fetching or animations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(145)
        self.setMaximumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.mode = "morning"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        gradient = QLinearGradient(r.topLeft(), r.bottomLeft())
        if self.mode == "evening":
            gradient.setColorAt(0, QColor("#294365"))
            gradient.setColorAt(1, QColor("#6F82A2"))
            hills = ["#526887", "#354D6B", "#223C59"]
            sun = QColor("#E5D9CF")
        else:
            gradient.setColorAt(0, QColor("#C8E4F8"))
            gradient.setColorAt(1, QColor("#FFE6D8"))
            hills = ["#C8DCE2", "#A9C4D7", "#819FB9"]
            sun = QColor("#FFF8E8")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(r, gradient)
        painter.setBrush(sun)
        painter.drawEllipse(QPointF(r.width()*.79, r.height()*.31), 31, 31)
        for idx, color in enumerate(hills):
            path = QPainterPath()
            base = r.height() * (.57 + idx * .12)
            path.moveTo(0, r.height())
            path.lineTo(0, base + 12)
            path.cubicTo(r.width()*.20, base-45, r.width()*.31, base+30, r.width()*.47, base-12)
            path.cubicTo(r.width()*.65, base-50, r.width()*.8, base+37, r.width(), base-18)
            path.lineTo(r.width(),r.height())
            path.closeSubpath()
            painter.fillPath(path, QColor(color))
        painter.end()


def labeled_button(label: str, callback, accent=False) -> QPushButton:
    button = QPushButton(label)
    button.setObjectName("LifeAccent" if accent else "LifeControl")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.clicked.connect(callback)
    return button


class LifeDesktop12:
    def __init__(self, app: QApplication):
        self.app = app
        self.window = LifeOSWindow(app)  # Keeps existing Notes/Files/Settings untouched.
        self.window.setWindowTitle("LIFE OS • Desktop")
        self.windows = []
        self.mode = "morning"
        self.panel = None
        self.dock = None
        self._timer = QTimer(self.window)
        self._timer.timeout.connect(self.update_clock)
        self._timer.start(30000)
        self.build_dock()
        self.make_shortcuts()
        self.apply_mode("morning")
        self.window.show()
        self.update_clock()

    def make_shortcuts(self):
        for keys, action in (
            ("Ctrl+Space", self.show_apps),
            ("Ctrl+Shift+P", self.show_quick_settings),
            ("Ctrl+Shift+D", self.show_home),
            ("Esc", self.hide_panel),
        ):
            shortcut = QShortcut(QKeySequence(keys), self.window)
            shortcut.activated.connect(action)
            # Parent owns the shortcuts for the full application lifetime.

    def build_dock(self):
        self.dock = QDockWidget("LIFE Dock", self.window)
        self.dock.setObjectName("LifeDock")
        self.dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        bar = QWidget()
        bar.setObjectName("LifeChrome")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 9, 14, 9)
        layout.setSpacing(10)
        layout.addWidget(labeled_button("◈  Home", self.show_home, True))
        layout.addWidget(labeled_button("▦  All Apps", self.show_apps))
        layout.addWidget(labeled_button("▣  Files", lambda: self.open_app(FileBrowser)))
        layout.addWidget(labeled_button("✎  Writer", lambda: self.open_app(TextEditor)))
        layout.addWidget(labeled_button("◷  Clock", lambda: self.open_app(Clock)))
        layout.addStretch()
        self.clock = QLabel()
        self.clock.setObjectName("LifeSub")
        layout.addWidget(self.clock)
        layout.addWidget(labeled_button("⚙  Controls", self.show_quick_settings))
        self.dock.setWidget(bar)
        self.window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock)

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%a %d %b · %H:%M"))

    def open_app(self, klass):
        for widget in list(self.windows):
            if isinstance(widget, klass):
                widget.show()
                widget.raise_()
                widget.activateWindow()
                self.hide_panel()
                return
        widget = klass()
        widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        widget.destroyed.connect(lambda: self.windows.remove(widget) if widget in self.windows else None)
        self.windows.append(widget)
        widget.show()
        self.hide_panel()

    def show_panel(self, title: str, subtitle: str):
        self.hide_panel()
        self.panel = QDockWidget(title, self.window)
        self.panel.setObjectName("LifeDock")
        self.panel.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.panel.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.panel.setMinimumWidth(360)
        self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.panel)
        host = QWidget()
        host.setObjectName("LifeChrome")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        heading = QLabel(title)
        heading.setObjectName("LifeTitle")
        layout.addWidget(heading)
        sub = QLabel(subtitle)
        sub.setObjectName("LifeSub")
        sub.setWordWrap(True)
        layout.addWidget(sub)
        self.panel.setWidget(host)
        self.panel.setStyleSheet(style_for(self.mode))
        return layout

    def hide_panel(self):
        if self.panel is not None:
            previous = self.panel
            self.panel = None
            self.window.removeDockWidget(previous)
            previous.deleteLater()

    def show_home(self):
        layout = self.show_panel("A place to focus", "LIFE Desktop · Your space, your pace")
        scene = Landscape()
        scene.mode = self.mode
        layout.addWidget(scene)
        title = QLabel("Make room for what matters.")
        title.setObjectName("LifeTitle")
        title.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(labeled_button("Explore all apps", self.show_apps, True))
        layout.addWidget(labeled_button("Open LIFE Writer", lambda: self.open_app(TextEditor)))
        layout.addWidget(labeled_button("Open Explorer", lambda: self.open_app(FileBrowser)))
        layout.addWidget(labeled_button("Quick settings", self.show_quick_settings))
        layout.addStretch()

    def show_apps(self):
        layout = self.show_panel("App Library", "Search and launch a native application")
        search = QLineEdit()
        search.setObjectName("LifeSearch")
        search.setPlaceholderText("Search apps…  (Ctrl+Space)")
        layout.addWidget(search)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        host.setObjectName("LifeChrome")
        grid = QGridLayout(host)
        grid.setSpacing(10)
        buttons = []
        for index, (name, description, icon, klass) in enumerate(APPS):
            button = labeled_button(f"{icon}  {name}\n     {description}", lambda checked=False, k=klass: self.open_app(k))
            button.setMinimumHeight(72)
            grid.addWidget(button, index // 2, index % 2)
            buttons.append((name, description, button))
        grid.setRowStretch((len(APPS)+1)//2, 1)
        scroll.setWidget(host)
        layout.addWidget(scroll, 1)

        def filter_apps(query):
            needle = query.strip().casefold()
            for name, description, button in buttons:
                button.setVisible(needle in (name + " " + description).casefold())
        search.textChanged.connect(filter_apps)
        search.setFocus()

    def show_quick_settings(self):
        layout = self.show_panel("Quick Settings", "Desktop appearance and navigation")
        layout.addWidget(labeled_button("☀  Morning haze", lambda: self.apply_mode("morning"), True))
        layout.addWidget(labeled_button("☾  Deep evening", lambda: self.apply_mode("evening")))
        layout.addWidget(labeled_button("◈  Home", self.show_home))
        layout.addWidget(labeled_button("▦  Application library", self.show_apps))
        label = QLabel("Desktop shortcuts\nCtrl+Space  ·  Apps\nCtrl+Shift+P  ·  Controls\nCtrl+Shift+D  ·  Home\nEsc  ·  Close panel")
        label.setObjectName("LifeSub")
        label.setWordWrap(True)
        layout.addWidget(label)
        note = QLabel("Appearance here changes LIFE Dock panels only; system Wi-Fi and brightness aren't simulated.")
        note.setObjectName("LifeSub")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()

    def apply_mode(self, mode: str):
        if mode not in PALETTES:
            raise ValueError(mode)
        self.mode = mode
        self.dock.widget().setStyleSheet(style_for(mode))
        if self.panel is not None:
            self.panel.widget().setStyleSheet(style_for(mode))
            self.panel.setStyleSheet(style_for(mode))
            for scene in self.panel.findChildren(Landscape):
                scene.mode = mode
                scene.update()


def main() -> int:
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        print("Launching with Qt offscreen: UI will not be visible in noVNC.", flush=True)
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE Desktop")
    desktop = LifeDesktop12(app)
    print("LIFE OS M12 ready · dock + app library + quick settings", flush=True)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
