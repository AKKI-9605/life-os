"""LIFE OS milestone 11: one-process desktop with native app launcher.
Run from repository: DISPLAY=:98 QT_QPA_PLATFORM=xcb python scripts/life_desktop.py
Does not change Notes, appearance preferences or existing LIFE OS source.
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar

sys.path.insert(0, str(Path(__file__).resolve().parent))
from life_apps import AppCenter, STYLE
from life_extra_apps import Clock, SystemMonitor, ImageViewer
from lifeos.ui.main_window import LifeOSWindow


def main() -> int:
    if os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
        raise SystemExit('Qt is set to offscreen: use QT_QPA_PLATFORM=xcb for noVNC')
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName('LIFE OS')
    window = LifeOSWindow(app)
    center = AppCenter()
    center.setStyleSheet(STYLE)
    center.entries.extend([
        ('◷  LIFE Clock', 'Clock Time Date', Clock),
        ('▤  System Monitor', 'System RAM CPU Memory Monitor', SystemMonitor),
        ('▧  Image Viewer', 'Image Pictures Photos Viewer', ImageViewer),
    ])
    # Regenerate the App Center grid so all seven apps are searchable.
    grid = center.layout().itemAt(2).layout()
    from PySide6.QtWidgets import QPushButton
    for i, (label, keywords, klass) in enumerate(center.entries[4:], start=4):
        button = QPushButton(label)
        button.setMinimumHeight(72)
        button.clicked.connect(lambda checked=False, k=klass: center.launch(k))
        grid.addWidget(button, i // 2, i % 2)
        center.buttons.append(button)
    # Speed: keep the App Center dormant until requested, in the same Qt process.
    def open_apps():
        center.show()
        center.raise_()
        center.activateWindow()
    if isinstance(window, QMainWindow):
        toolbar = QToolBar('LIFE Apps')
        toolbar.setMovable(False)
        action = QAction('✦ Apps', window)
        action.setToolTip('Open LIFE App Center (Ctrl+Space)')
        action.triggered.connect(open_apps)
        toolbar.addAction(action)
        window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
    shortcut = QShortcut(QKeySequence('Ctrl+Space'), window)
    shortcut.activated.connect(open_apps)
    window._life_center = center
    window._life_apps_shortcut = shortcut
    window.show()
    print('LIFE OS M11 ready — click ✦ Apps or press Ctrl+Space', flush=True)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
