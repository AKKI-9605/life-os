"""LIFE OS Milestone 10: standalone native apps, Qt/PySide6.
Run: python scripts/life_apps.py
No writes to existing LIFE OS Notes or configuration.
"""
from __future__ import annotations

import ast
import calendar
import operator
import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QCalendarWidget, QComboBox, QDialog, QFileDialog, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QMainWindow, QMessageBox, QPushButton, QPlainTextEdit, QSpinBox,
    QStackedWidget, QToolBar, QVBoxLayout, QWidget,
)

STYLE = """
QWidget { font-family: 'DejaVu Sans'; font-size: 13px; background: #F7F5F2; color: #26334B; }
QMainWindow, QDialog { background: #F7F5F2; }
QLabel#headline { font-size: 24px; font-weight: 700; color: #283E61; }
QLabel#subtitle { font-size: 12px; color: #69778C; }
QPushButton { border: 1px solid #D9DFE8; border-radius: 12px; padding: 11px 15px; background: white; }
QPushButton:hover { background: #EAF1FA; border-color: #AAC6E7; }
QPushButton#primary { background: #C5DDF5; color: #203955; border: none; font-weight: 700; }
QLineEdit, QPlainTextEdit, QListWidget, QCalendarWidget, QComboBox, QSpinBox { background: #FFFFFF; border: 1px solid #DDE4EF; border-radius: 10px; padding: 8px; selection-background-color: #B8D4F1; }
QFrame#card { background: #FFFFFF; border: 1px solid #E1E6EF; border-radius: 16px; }
QFrame#card QLabel { background: transparent; }
"""


def heading(title: str, subtitle: str) -> QVBoxLayout:
    top = QVBoxLayout()
    label = QLabel(title)
    label.setObjectName("headline")
    sub = QLabel(subtitle)
    sub.setObjectName("subtitle")
    top.addWidget(label)
    top.addWidget(sub)
    top.addSpacing(12)
    return top


def safe_calculate(expression: str) -> float | int:
    """Only arithmetic is accepted; never eval arbitrary Python."""
    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
    }

    def walk(node, depth=0):
        if depth > 18:
            raise ValueError("Expression too complex")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 1e12:
                raise ValueError("Number too large")
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = walk(node.operand, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            left, right = walk(node.left, depth + 1), walk(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("Exponent too large")
            result = ops[type(node.op)](left, right)
            if abs(result) > 1e18:
                raise ValueError("Result too large")
            return result
        raise ValueError("Only arithmetic is supported")

    if not expression.strip() or len(expression) > 180:
        raise ValueError("Enter a shorter expression")
    return walk(ast.parse(expression, mode="eval").body)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE Calculator")
        self.resize(390, 510)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.addLayout(heading("Calculator", "Simple, safe everyday maths"))
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setMinimumHeight(57)
        self.display.setPlaceholderText("0")
        self.display.returnPressed.connect(self.calculate)
        root.addWidget(self.display)
        grid = QGridLayout()
        for r, row in enumerate((
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("C", "0", ".", "+"),
            ("(", ")", "%", "="),
        )):
            for c, value in enumerate(row):
                b = QPushButton(value)
                b.setMinimumHeight(54)
                if value == "=":
                    b.setObjectName("primary")
                b.clicked.connect(lambda checked=False, x=value: self.press(x))
                grid.addWidget(b, r, c)
        root.addLayout(grid)
        self.status = QLabel("Ready")
        self.status.setObjectName("subtitle")
        root.addWidget(self.status)

    def press(self, value):
        if value == "C":
            self.display.clear()
            self.status.setText("Ready")
        elif value == "=":
            self.calculate()
        else:
            self.display.insert(value)

    def calculate(self):
        try:
            value = safe_calculate(self.display.text())
            self.display.setText(str(value))
            self.status.setText("Calculated")
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
            self.status.setText(str(exc))


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE Writer — Untitled")
        self.resize(850, 600)
        self.path: Path | None = None
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Start writing...")
        self.setCentralWidget(self.editor)
        toolbar = QToolBar("File")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        for label, callback, shortcut in (
            ("New", self.new_file, "Ctrl+N"),
            ("Open", self.open_file, "Ctrl+O"),
            ("Save", self.save_file, "Ctrl+S"),
            ("Save As", self.save_as, "Ctrl+Shift+S"),
        ):
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            toolbar.addAction(action)
        self.statusBar().showMessage("Local text editor • .txt, .md, .py and other plain-text files")
        self.editor.document().modificationChanged.connect(self._set_title)

    def _set_title(self, _modified=False):
        name = self.path.name if self.path else "Untitled"
        dirty = " *" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"LIFE Writer — {name}{dirty}")

    def _confirm_discard(self) -> bool:
        if not self.editor.document().isModified():
            return True
        result = QMessageBox.question(self, "Unsaved work", "Discard unsaved changes?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        return result == QMessageBox.StandardButton.Yes

    def new_file(self):
        if self._confirm_discard():
            self.editor.clear()
            self.path = None
            self.editor.document().setModified(False)
            self._set_title()

    def open_file(self):
        if not self._confirm_discard():
            return
        filename, _ = QFileDialog.getOpenFileName(self, "Open text file", str(Path.home()))
        if not filename:
            return
        try:
            content = Path(filename).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, "Open failed", str(exc))
            return
        self.editor.setPlainText(content)
        self.path = Path(filename)
        self.editor.document().setModified(False)
        self._set_title()

    def save_file(self):
        if self.path is None:
            return self.save_as()
        try:
            self.path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            return False
        self.editor.document().setModified(False)
        self._set_title()
        self.statusBar().showMessage(f"Saved {self.path}", 5000)
        return True

    def save_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save text file", str(self.path or (Path.home() / "Untitled.txt")))
        if filename:
            previous_path = self.path
            self.path = Path(filename)
            if not self.save_file():
                self.path = previous_path
                return False
            return True
        return False

    def closeEvent(self, event):
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()


class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE Calendar")
        self.resize(780, 620)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.addLayout(heading("Calendar", "Plan your month at a glance"))
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        root.addWidget(self.calendar, 1)
        self.selected = QLabel()
        self.selected.setObjectName("subtitle")
        root.addWidget(self.selected)
        self.calendar.selectionChanged.connect(self.update_selected)
        self.update_selected()

    def update_selected(self):
        self.selected.setText("Selected: " + self.calendar.selectedDate().toString("dddd, d MMMM yyyy"))


class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE Explorer")
        self.resize(850, 590)
        self.directory = Path.home()
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.addLayout(heading("Explorer", "Browse local files and folders"))
        bar = QHBoxLayout()
        back = QPushButton("Up")
        back.clicked.connect(lambda: self.navigate(self.directory.parent))
        bar.addWidget(back)
        home = QPushButton("Home")
        home.clicked.connect(lambda: self.navigate(Path.home()))
        bar.addWidget(home)
        self.location = QLineEdit()
        self.location.returnPressed.connect(lambda: self.navigate(Path(self.location.text()).expanduser()))
        bar.addWidget(self.location, 1)
        root.addLayout(bar)
        self.items = QListWidget()
        self.items.itemDoubleClicked.connect(self.open_item)
        root.addWidget(self.items, 1)
        self.info = QLabel()
        self.info.setObjectName("subtitle")
        root.addWidget(self.info)
        self.navigate(self.directory)

    def navigate(self, directory: Path):
        directory = directory.expanduser()
        if not directory.is_dir():
            self.info.setText("Not a folder")
            return
        try:
            children = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))
        except OSError as exc:
            self.info.setText(str(exc))
            return
        self.directory = directory
        self.location.setText(str(directory))
        self.items.clear()
        for child in children:
            item_label = ("📁 " if child.is_dir() else "📄 ") + child.name
            self.items.addItem(item_label)
        self.info.setText(f"{len(children)} items • Double-click a folder to open it")

    def open_item(self, item):
        name = item.text()[2:]
        target = self.directory / name
        if target.is_dir():
            self.navigate(target)
        else:
            self.info.setText(f"File: {target.name} • Open in LIFE Writer using File → Open")


class AppCenter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIFE OS — App Center")
        self.resize(790, 560)
        self.windows = []
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.addLayout(heading("LIFE App Center", "Your native desktop apps, all in one place"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps...")
        self.search.textChanged.connect(self.filter_apps)
        root.addWidget(self.search)
        self.entries = [
            ("✦  LIFE Calculator", "Calculator", Calculator),
            ("✎  LIFE Writer", "Writer Text Editor", TextEditor),
            ("▦  LIFE Calendar", "Calendar", Calendar),
            ("▣  LIFE Explorer", "Explorer File Browser", FileBrowser),
        ]
        self.buttons = []
        grid = QGridLayout()
        for i, (label, keywords, klass) in enumerate(self.entries):
            button = QPushButton(label)
            button.setMinimumHeight(105)
            button.clicked.connect(lambda checked=False, k=klass: self.launch(k))
            grid.addWidget(button, i // 2, i % 2)
            self.buttons.append(button)
        root.addLayout(grid)
        root.addStretch(1)
        footer = QLabel("Milestone 10 • Local-first • No online services required")
        footer.setObjectName("subtitle")
        root.addWidget(footer)

    def filter_apps(self, term):
        for (label, keywords, _), button in zip(self.entries, self.buttons):
            button.setVisible(term.casefold() in (label + " " + keywords).casefold())

    def launch(self, klass):
        window = klass()
        self.windows.append(window)
        window.destroyed.connect(lambda: self.windows.remove(window) if window in self.windows else None)
        window.show()
        window.raise_()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE OS Apps")
    app.setStyleSheet(STYLE)
    window = AppCenter()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
