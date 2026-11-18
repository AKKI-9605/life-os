"""LIFE OS M13 — standalone native visual shell (PySide6/X11).

No GitHub/network access, no writes to user settings, notes, or repository content.
Open existing LIFE OS Notes via the existing native main window.
"""
from __future__ import annotations

import math
import os
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSize, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QLinearGradient, QRadialGradient, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMdiArea, QMdiSubWindow, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget
)

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

try:
    from life_apps import Calculator, TextEditor, Calendar, FileBrowser
    from life_extra_apps import Clock, SystemMonitor, ImageViewer
    from lifeos.ui.main_window import LifeOSWindow
    APPS_READY = True
    IMPORT_FAILURE = ""
except Exception as exc:
    APPS_READY = False
    IMPORT_FAILURE = str(exc)

THEMES = {
    "Horizon": dict(top="#9CC9E5", mid="#E4D8DF", bottom="#F6D9C0", hill1="#A7BACD", hill2="#7E9EB6", hill3="#536F92", ink="#243951", glass="#F7FAFF", muted="#596B82", accent="#D7E9F9", dark=False),
    "Blush": dict(top="#E9C3CB", mid="#F5E0DA", bottom="#EFE5D7", hill1="#DEC4CB", hill2="#B9A1B7", hill3="#927F9E", ink="#493C52", glass="#FFF9F7", muted="#76657A", accent="#F4DCE7", dark=False),
    "Midnight": dict(top="#132039", mid="#2B3859", bottom="#6C648A", hill1="#536183", hill2="#354A6E", hill3="#1D3053", ink="#EDF3FF", glass="#283651", muted="#B9C7E1", accent="#445C83", dark=True),
}

APP_DEFS = [
    ("Explorer", "Browse your folders", "▣", "FileBrowser"),
    ("Writer", "Text and code editor", "✎", "TextEditor"),
    ("Calendar", "Your dates and plans", "▦", "Calendar"),
    ("Calculator", "Numbers, made simple", "▤", "Calculator"),
    ("Clock", "Time and focus", "◷", "Clock"),
    ("System Monitor", "CPU and memory", "◈", "SystemMonitor"),
    ("Image Viewer", "View local images", "▧", "ImageViewer"),
    ("LIFE Notes", "Your existing saved notes", "✦", "LifeOSWindow"),
]


def button(text, callback, obj="control", minheight=42):
    widget = QPushButton(text)
    widget.setObjectName(obj)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.setMinimumHeight(minheight)
    widget.clicked.connect(callback)
    return widget


class Wallpaper(QWidget):
    """Vector wallpaper is painted directly; no full-screen blur or video GPU load."""
    def __init__(self):
        super().__init__()
        self.theme = "Horizon"
        self.setObjectName("wallpaper")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if not w or not h:
            return
        t = THEMES[self.theme]
        sky = QLinearGradient(0, 0, w * .35, h)
        for at, key in ((0, "top"), (.57, "mid"), (1, "bottom")):
            sky.setColorAt(at, QColor(t[key]))
        p.fillRect(self.rect(), sky)
        p.setPen(Qt.PenStyle.NoPen)
        orb = QRadialGradient(QPointF(w * .74, h * .23), min(w, h) * .14)
        orb.setColorAt(0, QColor(255, 252, 238, 230))
        orb.setColorAt(.35, QColor(255, 244, 222, 185))
        orb.setColorAt(1, QColor(255, 241, 215, 0))
        p.setBrush(orb)
        r = min(w, h) * .14
        p.drawEllipse(QPointF(w * .74, h * .23), r, r)
        for idx, color in enumerate((t["hill1"], t["hill2"], t["hill3"])):
            y = h * (.59 + idx * .13)
            path = QPainterPath(QPointF(0, h))
            path.lineTo(0, y + 28)
            path.cubicTo(w * .16, y - h * .20, w * .31, y + h * .11, w * .52, y - 23)
            path.cubicTo(w * .69, y - h * .16, w * .85, y + h * .08, w, y - 50)
            path.lineTo(w, h)
            path.closeSubpath()
            p.fillPath(path, QColor(color))
        p.end()


class Overlay(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("overlay")
        self.setMinimumWidth(350)
        self.setMaximumWidth(410)
        self.setVisible(False)
        self.layout_box = QVBoxLayout(self)
        self.layout_box.setContentsMargins(20, 19, 20, 18)
        self.layout_box.setSpacing(12)

    def clear(self):
        while self.layout_box.count():
            item = self.layout_box.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                pass

    def heading(self, title, subtitle):
        self.clear()
        h = QLabel(title)
        h.setObjectName("panelTitle")
        self.layout_box.addWidget(h)
        s = QLabel(subtitle)
        s.setObjectName("muted")
        s.setWordWrap(True)
        self.layout_box.addWidget(s)


class Desktop(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.theme = "Horizon"
        self.open_windows = {}
        self.notes_window = None
        self.drawer_type = None
        self.setWindowTitle("LIFE OS · Desktop M13")
        self.setMinimumSize(900, 590)
        self.root = Wallpaper()
        self.setCentralWidget(self.root)
        self.vbox = QVBoxLayout(self.root)
        self.vbox.setContentsMargins(24, 15, 24, 19)
        self.vbox.setSpacing(10)
        self._make_topbar()
        self._make_center()
        self._make_dock()
        self.drawer = Overlay(self.root)
        self._make_shortcuts()
        self.apply_theme("Horizon")
        self.ticker = QTimer(self)
        self.ticker.timeout.connect(self.update_clock)
        self.ticker.start(30000)
        self.update_clock()
        self.showMaximized()

    def _make_topbar(self):
        bar = QFrame()
        bar.setObjectName("chrome")
        bar.setFixedHeight(53)
        line = QHBoxLayout(bar)
        line.setContentsMargins(18, 2, 15, 2)
        line.setSpacing(10)
        brand = QLabel("◈   LIFE OS")
        brand.setObjectName("brand")
        line.addWidget(brand)
        line.addSpacing(20)
        line.addWidget(button("⌕   Search", self.show_launcher, "topButton"))
        line.addWidget(button("▦   Apps", self.show_launcher, "topButton"))
        line.addStretch()
        self.date_label = QLabel()
        self.date_label.setObjectName("topInfo")
        line.addWidget(self.date_label)
        line.addSpacing(8)
        line.addWidget(button("◷", self.show_notifications, "topButton"))
        line.addWidget(button("◉   Controls", self.show_settings, "topButton"))
        self.vbox.addWidget(bar)

    def _make_center(self):
        self.center = QWidget()
        h = QHBoxLayout(self.center)
        h.setContentsMargins(13, 18, 0, 2)
        h.setSpacing(7)
        shortcuts = QVBoxLayout()
        shortcuts.setSpacing(12)
        shortcuts.addWidget(button("▣\nExplorer", lambda: self.launch("Explorer"), "desktopIcon", 86))
        shortcuts.addWidget(button("✦\nLIFE Notes", lambda: self.launch("LIFE Notes"), "desktopIcon", 86))
        shortcuts.addWidget(button("✎\nWriter", lambda: self.launch("Writer"), "desktopIcon", 86))
        shortcuts.addWidget(button("▦\nApp Library", self.show_launcher, "desktopIcon", 86))
        shortcuts.addStretch()
        h.addLayout(shortcuts)
        self.mdi = QMdiArea()
        self.mdi.setObjectName("mdi")
        self.mdi.setFrameShape(QFrame.Shape.NoFrame)
        self.mdi.setOption(QMdiArea.AreaOption.DontMaximizeSubWindowOnActivation, True)
        self.mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.mdi.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.mdi.subWindowActivated.connect(self.refresh_tasks)
        h.addWidget(self.mdi, 1)
        self.vbox.addWidget(self.center, 1)

        self.welcome = QFrame(self.mdi.viewport())
        self.welcome.setObjectName("welcome")
        wl = QVBoxLayout(self.welcome)
        wl.setContentsMargins(22, 20, 24, 22)
        title = QLabel("A little space to make big things happen.")
        title.setObjectName("welcomeTitle")
        title.setWordWrap(True)
        wl.addWidget(title)
        note = QLabel("LIFE OS  /  Your space, your pace")
        note.setObjectName("welcomeNote")
        wl.addWidget(note)
        wl.addSpacing(8)
        wl.addWidget(button("Explore your apps   ↗", self.show_launcher, "primary"))
        self.welcome.setFixedSize(395, 185)
        self.welcome.show()

    def _make_dock(self):
        foot = QHBoxLayout()
        foot.addStretch(1)
        dock = QFrame()
        dock.setObjectName("dock")
        d = QHBoxLayout(dock)
        d.setContentsMargins(13, 8, 13, 8)
        d.setSpacing(7)
        for title, name, callback in [
            ("◈", "Home", self.go_home),
            ("▦", "Apps", self.show_launcher),
            ("▣", "Explorer", lambda: self.launch("Explorer")),
            ("✎", "Writer", lambda: self.launch("Writer")),
            ("✦", "Notes", lambda: self.launch("LIFE Notes")),
            ("◷", "Clock", lambda: self.launch("Clock")),
            ("◉", "Controls", self.show_settings),
        ]:
            b = button(title, callback, "dockButton", 48)
            b.setToolTip(name)
            b.setFixedWidth(51)
            d.addWidget(b)
        self.tasks_label = QLabel("  Desktop ready")
        self.tasks_label.setObjectName("taskLabel")
        d.addWidget(self.tasks_label)
        foot.addWidget(dock)
        foot.addStretch(1)
        self.vbox.addLayout(foot)

    def _make_shortcuts(self):
        for key, callback in (("Ctrl+Space", self.show_launcher), ("Ctrl+Shift+P", self.show_settings),
                              ("Ctrl+Shift+N", self.show_notifications), ("Ctrl+Shift+D", self.go_home),
                              ("Escape", self.hide_drawer)):
            s = QShortcut(QKeySequence(key), self)
            s.activated.connect(callback)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "drawer"):
            self.place_drawer()
        if hasattr(self, "welcome"):
            self.welcome.move(max(20, (self.mdi.viewport().width() - self.welcome.width()) // 2),
                              max(45, (self.mdi.viewport().height() - self.welcome.height()) // 3))

    def place_drawer(self):
        self.drawer.setGeometry(max(5, self.root.width() - 444), 78,
                                min(410, self.root.width() - 18),
                                max(150, self.root.height() - 166))
        self.drawer.raise_()

    def update_clock(self):
        self.date_label.setText(datetime.now().strftime("%a  %d %b   %H:%M"))

    def palette_style(self):
        t = THEMES[self.theme]
        glass, ink, muted, accent = (t[k] for k in ("glass", "ink", "muted", "accent"))
        # Solid alpha-toned surfaces stay responsive over noVNC (no expensive blur).
        glassalpha = "#F7FAFF" if not t["dark"] else "#293753"
        hover = "#E2ECF8" if not t["dark"] else "#415572"
        return f"""
            QWidget {{ font-family: 'DejaVu Sans'; color:{ink}; font-size:12px; }}
            QFrame#chrome, QFrame#dock, QFrame#overlay, QFrame#welcome {{
              background:{glassalpha}; border:1px solid {t['hill1']}; border-radius:19px; }}
            QFrame#dock {{border-radius:23px;}}
            QFrame#welcome {{border-radius:24px;}}
            QLabel {{background:transparent; border:none;}}
            QLabel#brand {{font-size:18px;font-weight:bold;}}
            QLabel#welcomeTitle {{font-size:22px;font-weight:bold;}}
            QLabel#welcomeNote, QLabel#muted, QLabel#topInfo, QLabel#taskLabel {{color:{muted};}}
            QLabel#panelTitle {{font-size:23px;font-weight:bold;}}
            QPushButton {{background:transparent; border:0; color:{ink};padding:7px;}}
            QPushButton:hover {{background:{hover};border-radius:13px;}}
            QPushButton#topButton {{padding:8px 12px;font-weight:600;}}
            QPushButton#dockButton {{font-size:22px;font-weight:bold;border-radius:14px;}}
            QPushButton#desktopIcon {{font-size:16px;font-weight:600;max-width:112px;min-width:98px;}}
            QPushButton#control, QPushButton#appTile {{background:{glassalpha};border:1px solid {t['hill1']};border-radius:14px;padding:12px;text-align:left;}}
            QPushButton#control:hover, QPushButton#appTile:hover {{background:{hover};}}
            QPushButton#primary {{background:{accent};border-radius:13px;padding:10px 16px;font-weight:bold;}}
            QLineEdit {{background:{glassalpha};border:1px solid {t['hill1']};border-radius:13px;padding:12px;color:{ink};}}
            QScrollArea, QWidget#scrollContent {{background:transparent;border:0;}}
            QMdiArea#mdi {{background:transparent;border:0;}}
            QMdiSubWindow {{background:{glassalpha};}}
        """

    def apply_theme(self, name):
        if name not in THEMES:
            return
        self.theme = name
        self.root.theme = name
        self.setStyleSheet(self.palette_style())
        self.root.update()
        if self.drawer_type == "settings":
            self.show_settings()

    def show_drawer(self, which, title, subtitle):
        self.drawer_type = which
        self.drawer.heading(title, subtitle)
        self.drawer.show()
        self.place_drawer()

    def hide_drawer(self):
        self.drawer_type = None
        self.drawer.hide()

    def show_launcher(self):
        self.show_drawer("launcher", "App Library", "Your tools, beautifully together")
        search = QLineEdit()
        search.setPlaceholderText("Search your apps…")
        self.drawer.layout_box.addWidget(search)
        area = QScrollArea()
        area.setWidgetResizable(True)
        host = QWidget()
        host.setObjectName("scrollContent")
        grid = QGridLayout(host)
        grid.setSpacing(9)
        tiles = []
        for i, (name, desc, glyph, _) in enumerate(APP_DEFS):
            tile = button(f"{glyph}   {name}\n     {desc}", lambda _=False, n=name: self.launch(n), "appTile", 76)
            grid.addWidget(tile, i // 2, i % 2)
            tiles.append((name, desc, tile))
        area.setWidget(host)
        self.drawer.layout_box.addWidget(area, 1)
        search.textChanged.connect(lambda query: [tile.setVisible(query.casefold() in (name + ' ' + desc).casefold()) for name, desc, tile in tiles])
        search.setFocus()

    def show_settings(self):
        self.show_drawer("settings", "Quick Settings", "A desktop that adapts to you")
        label = QLabel("WALLPAPER & COLOR")
        label.setObjectName("muted")
        self.drawer.layout_box.addWidget(label)
        for name, glyph in (("Horizon", "☀"), ("Blush", "✿"), ("Midnight", "☾")):
            marker = "  ✓" if name == self.theme else ""
            self.drawer.layout_box.addWidget(button(f"{glyph}   {name}{marker}", lambda _=False, n=name: self.apply_theme(n)))
        self.drawer.layout_box.addSpacing(12)
        self.drawer.layout_box.addWidget(button("▦   Open App Library", self.show_launcher, "primary"))
        info = QLabel("SHORTCUTS\nCtrl+Space    App Library\nCtrl+Shift+P  Quick Settings\nCtrl+Shift+N  Notifications\nCtrl+Shift+D  Desktop\nEsc                Close panel\n\nBrightness, Wi-Fi and volume are managed by Linux; these controls do not pretend to change hardware.")
        info.setObjectName("muted")
        info.setWordWrap(True)
        self.drawer.layout_box.addWidget(info)
        self.drawer.layout_box.addStretch()

    def show_notifications(self):
        self.show_drawer("notifications", "Notifications", "A little less noise, a lot more focus")
        title = QLabel("✦   All clear")
        title.setObjectName("panelTitle")
        self.drawer.layout_box.addWidget(title)
        message = QLabel("LIFE OS is ready. New native desktop notifications will arrive in a later milestone.")
        message.setObjectName("muted")
        message.setWordWrap(True)
        self.drawer.layout_box.addWidget(message)
        self.drawer.layout_box.addStretch()

    def go_home(self):
        self.hide_drawer()
        self.mdi.setActiveSubWindow(None)
        self.welcome.raise_()

    def refresh_tasks(self, *_):
        active = self.mdi.activeSubWindow()
        count = len(self.mdi.subWindowList())
        self.tasks_label.setText(f"  {count} open" + (f"  ·  {active.windowTitle()}" if active else ""))

    def launch(self, name):
        self.hide_drawer()
        if not APPS_READY:
            self.show_drawer("error", "Apps unavailable", f"Existing app modules couldn't load: {IMPORT_FAILURE}")
            return
        if name == "LIFE Notes":
            if self.notes_window is None:
                self.notes_window = LifeOSWindow(self.app)
                self.notes_window.setWindowTitle("LIFE OS — Notes & Settings")
                self.notes_window.destroyed.connect(lambda *_: setattr(self, "notes_window", None))
            self.notes_window.show()
            self.notes_window.raise_()
            self.notes_window.activateWindow()
            return
        if name in self.open_windows:
            sub = self.open_windows[name]
            if sub in self.mdi.subWindowList():
                sub.showNormal()
                self.mdi.setActiveSubWindow(sub)
                self.refresh_tasks()
                return
            self.open_windows.pop(name, None)
        mapping = {
            "Explorer": FileBrowser, "Writer": TextEditor, "Calendar": Calendar,
            "Calculator": Calculator, "Clock": Clock, "System Monitor": SystemMonitor,
            "Image Viewer": ImageViewer,
        }
        klass = mapping.get(name)
        if klass is None:
            return
        try:
            widget = klass()
            widget.setWindowFlags(Qt.WindowType.Widget)
            sub = self.mdi.addSubWindow(widget)
            sub.setWindowTitle("◈  " + name)
            sub.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widget.setMinimumSize(280, 220)
            sub.resize(min(780, max(420, self.mdi.width() - 90)), min(550, max(330, self.mdi.height() - 90)))
            n = len(self.open_windows)
            sub.move(45 + (n * 32) % 180, 35 + (n * 28) % 130)
            self.open_windows[name] = sub
            sub.destroyed.connect(lambda *_: self.open_windows.pop(name, None))
            sub.show()
            self.mdi.setActiveSubWindow(sub)
            self.welcome.hide()
            self.refresh_tasks()
        except Exception as exc:
            self.show_drawer("error", "App couldn't open", f"{name}: {exc}")


def main():
    if os.getenv("QT_QPA_PLATFORM") == "offscreen":
        print("WARNING: Qt offscreen is active; noVNC cannot display this window.", flush=True)
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS Desktop M13")
    app.setQuitOnLastWindowClosed(True)
    desktop = Desktop(app)
    print("LIFE OS M13 ready · native visual shell", flush=True)
    if not APPS_READY:
        print("Apps import warning:", IMPORT_FAILURE, flush=True)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
