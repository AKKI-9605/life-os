"""LIFE OS M16: Custom native app windows."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMdiSubWindow
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import life_desktop_m15 as m15

base = m15.m14.base


class WindowHeader(QFrame):
    def __init__(self, title, subwindow, desktop):
        super().__init__()
        self.subwindow = subwindow
        self.desktop = desktop
        self.drag_origin = None

        self.setObjectName("lifeWindowHeader")
        self.setFixedHeight(51)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 5, 10, 5)
        layout.setSpacing(8)

        symbol = QLabel("✦")
        symbol.setObjectName("windowSymbol")
        layout.addWidget(symbol)

        title_label = QLabel(title)
        title_label.setObjectName("windowCaption")
        layout.addWidget(title_label)

        layout.addStretch()

        for label, action, kind in (
            ("−", subwindow.showMinimized, "min"),
            ("□", self.toggle_maximize, "max"),
            ("×", subwindow.close, "close"),
        ):
            button = QPushButton(label)
            button.setObjectName("windowControl")
            button.setProperty("kind", kind)
            button.setFixedSize(32, 30)
            button.setToolTip({
                "min": "Minimize",
                "max": "Maximize or restore",
                "close": "Close window"
            }[kind])
            button.clicked.connect(action)
            layout.addWidget(button)

    def toggle_maximize(self):
        if self.subwindow.isMaximized():
            self.subwindow.showNormal()
        else:
            self.subwindow.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_origin = (
                event.globalPosition().toPoint()
                - self.subwindow.pos()
            )
            self.desktop.mdi.setActiveSubWindow(
                self.subwindow
            )
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_origin is not None
            and event.buttons() & Qt.MouseButton.LeftButton
            and not self.subwindow.isMaximized()
        ):
            position = (
                event.globalPosition().toPoint()
                - self.drag_origin
            )
            area = self.desktop.mdi.viewport()
            x = max(
                0,
                min(position.x(), area.width() - 100)
            )
            y = max(
                0,
                min(position.y(), area.height() - 45)
            )
            self.subwindow.move(x, y)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_origin = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize()
        event.accept()


class Desktop16(m15.Desktop15):
    def __init__(self, app):
        super().__init__(app)
        self.setWindowTitle(
            "LIFE OS · Desktop M16"
        )
        self.setMinimumSize(920, 600)

    def window_style(self):
        theme = base.THEMES[self.theme]

        dark = theme["dark"]

        surface = "#25334D" if dark else "#F8FAFF"
        border = "#526783" if dark else "#C8D9E9"
        hover = "#3B5070" if dark else "#E6EFF9"
        ink = "#F4F7FF" if dark else "#243952"
        subtitle = "#C1D0E2" if dark else "#637A91"

        return f"""
        QWidget#lifeWindowSurface {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 13px;
        }}
        QFrame#lifeWindowHeader {{
            background: {surface};
            border: none;
            border-bottom: 1px solid {border};
            border-top-left-radius: 13px;
            border-top-right-radius: 13px;
        }}
        QLabel#windowSymbol {{
            color: {theme['hill2']};
            font-size: 19px;
            font-weight: bold;
        }}
        QLabel#windowCaption {{
            color: {ink};
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton#windowControl {{
            background: transparent;
            color: {subtitle};
            border: none;
            border-radius: 9px;
            font-size: 18px;
            padding: 0;
        }}
        QPushButton#windowControl:hover {{
            background: {hover};
            color: {ink};
        }}
        QPushButton#windowControl[kind="close"]:hover {{
            background: #D85A67;
            color: white;
        }}
        QWidget#lifeAppContent {{
            background: {surface};
            border: none;
            color: {ink};
        }}
        """

    def apply_theme(self, name):
        super().apply_theme(name)

        if hasattr(self, "open_windows"):
            for sub in self.open_windows.values():
                shell = sub.widget()
                if shell is not None:
                    shell.setStyleSheet(
                        self.window_style()
                    )

    def launch(self, name):
        if name == "LIFE Notes":
            return super().launch(name)

        self.hide_drawer()

        if not base.APPS_READY:
            self.show_drawer(
                "error",
                "Apps unavailable",
                base.IMPORT_FAILURE
            )
            return

        existing = self.open_windows.get(name)

        if existing in self.mdi.subWindowList():
            existing.showNormal()
            existing.show()
            self.mdi.setActiveSubWindow(existing)
            existing.raise_()
            self.refresh_tasks()
            return

        mapping = {
            "Explorer": base.FileBrowser,
            "Writer": base.TextEditor,
            "Calendar": base.Calendar,
            "Calculator": base.Calculator,
            "Clock": base.Clock,
            "System Monitor": base.SystemMonitor,
            "Image Viewer": base.ImageViewer,
        }

        klass = mapping.get(name)

        if klass is None:
            return

        try:
            content = klass()
            content.setWindowFlags(Qt.WindowType.Widget)
            content.setMinimumSize(280, 220)
            content.setObjectName("lifeAppContent")

            sub = QMdiSubWindow()
            sub.setWindowFlags(
                Qt.WindowType.SubWindow
                | Qt.WindowType.FramelessWindowHint
            )
            sub.setAttribute(
                Qt.WidgetAttribute.WA_DeleteOnClose
            )
            sub.setWindowTitle("LIFE · " + name)

            shell = QWidget()
            shell.setObjectName("lifeWindowSurface")

            layout = QVBoxLayout(shell)
            layout.setContentsMargins(1, 1, 1, 1)
            layout.setSpacing(0)

            header = WindowHeader(name, sub, self)

            layout.addWidget(header)
            layout.addWidget(content, 1)

            sub.setWidget(shell)
            self.mdi.addSubWindow(sub)

            sub.resize(
                min(820, max(450, self.mdi.width() - 95)),
                min(580, max(350, self.mdi.height() - 95))
            )

            count = len(self.mdi.subWindowList())

            sub.move(
                45 + (count * 31) % 160,
                36 + (count * 25) % 115
            )

            self.open_windows[name] = sub

            def remove_window(*_):
                if self.open_windows.get(name) is sub:
                    self.open_windows.pop(name, None)

            sub.destroyed.connect(remove_window)

            shell.setStyleSheet(self.window_style())

            sub.show()
            self.mdi.setActiveSubWindow(sub)

            self.welcome.hide()
            self.refresh_tasks()

        except Exception as exc:
            self.show_drawer(
                "error",
                "Unable to open app",
                f"{name}: {exc}"
            )


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS M16")

    m15.m14.base.Wallpaper = m15.m14.CachedWallpaper

    desktop = Desktop16(app)

    print(
        "LIFE OS M16 ready — custom app windows",
        flush=True
    )

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
