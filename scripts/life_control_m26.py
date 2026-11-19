"""LIFE Lite M24–26: native XFCE Control Center."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QComboBox,
    QProgressBar, QFrame, QMessageBox, QSpinBox,
    QGridLayout, QTextEdit
)

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

WALL_DIR = HOME / ".local/share/lifeos/wallpapers"
BACKUP_DIR = HOME / ".local/share/lifeos/backups"
PICTURES = HOME / "Pictures/LIFE OS"

WALLPAPERS = {
    "Horizon": "blue-horizon.svg",
    "Morning Haze": "morning-haze.svg",
    "Midnight": "deep-night.svg",
}


def run(*args):
    result = subprocess.run(
        list(map(str, args)),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def xf_get(channel, prop):
    status, out, _ = run(
        "xfconf-query", "-c", channel, "-p", prop
    )
    return out if status == 0 else None


def xf_set(channel, prop, value, kind="int"):
    args = [
        "xfconf-query", "-c", channel,
        "-p", prop
    ]

    if xf_get(channel, prop) is None:
        args += ["--create", "-t", kind]

    args += ["-s", str(value)]

    status, out, err = run(*args)
    if status != 0:
        raise RuntimeError(err or out or "XFCE setting failed")


def make_wallpapers():
    WALL_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for name, filename in WALLPAPERS.items():
        source = ROOT / "desktop/assets/wallpapers" / filename
        destination = WALL_DIR / (
            "life-" + filename.replace(".svg", ".png")
        )

        if not source.is_file():
            continue

        if not destination.exists():
            renderer = QSvgRenderer(str(source))
            if not renderer.isValid():
                continue

            image = QImage(
                1440, 900,
                QImage.Format.Format_ARGB32
            )
            image.fill(QColor("#E5EFF8"))

            painter = QPainter(image)
            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing
            )
            renderer.render(
                painter, QRectF(0, 0, 1440, 900)
            )
            painter.end()

            if not image.save(str(destination)):
                continue

        results[name] = destination

    return results


def apply_wallpaper(path):
    status, output, error = run(
        "xfconf-query", "-c", "xfce4-desktop", "-lv"
    )

    if status != 0:
        raise RuntimeError(
            error or "XFCE desktop settings unavailable"
        )

    properties = []

    for line in output.splitlines():
        parts = line.split(maxsplit=1)

        if parts and parts[0].endswith("/last-image"):
            properties.append(parts[0])

    if not properties:
        raise RuntimeError(
            "No XFCE wallpaper properties found. "
            "Open Desktop Settings once, then retry."
        )

    for prop in properties:
        xf_set(
            "xfce4-desktop", prop,
            str(path), "string"
        )

        style = prop.rsplit("/", 1)[0] + "/image-style"
        xf_set("xfce4-desktop", style, 5)

    run("xfdesktop", "--reload")


def system_memory():
    values = {}

    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.split()[0])

        total = values["MemTotal"] * 1024
        available = values["MemAvailable"] * 1024
        used = total - available

        return total, used
    except (OSError, KeyError, ValueError):
        return 0, 0


def cpu_sample():
    try:
        data = Path("/proc/stat").read_text().splitlines()[0]
        values = [int(x) for x in data.split()[1:]]
        idle = values[3] + values[4]
        total = sum(values)
        return total, idle
    except (OSError, IndexError, ValueError):
        return 0, 0


def gb(value):
    return f"{value / (1024 ** 3):.2f} GiB"


class LifeControl(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LIFE · Control Center")
        self.resize(960, 680)
        self.setMinimumSize(780, 540)

        self.wallpapers = make_wallpapers()
        self.last_cpu = cpu_sample()

        self.build_ui()
        self.refresh_system()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_system)
        self.timer.start(3000)

    def build_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #F5F8FD;
                color: #263B55;
                font-family: sans-serif;
                font-size: 13px;
            }

            QLabel#heading {
                font-size: 28px;
                font-weight: 700;
                color: #253A55;
            }

            QLabel#subtitle {
                color: #73879F;
                font-size: 13px;
            }

            QLabel#section {
                font-size: 18px;
                font-weight: 700;
                padding: 5px 0;
            }

            QTabWidget::pane {
                border: 1px solid #D9E4F0;
                border-radius: 14px;
                background: #FFFFFF;
                padding: 12px;
            }

            QTabBar::tab {
                background: #E8F0F9;
                color: #4D6680;
                padding: 12px 18px;
                margin: 3px;
                border-radius: 10px;
            }

            QTabBar::tab:selected {
                background: #CFE3F7;
                color: #244361;
                font-weight: 700;
            }

            QPushButton {
                background: #E1EEFB;
                color: #284967;
                border: 1px solid #CBDCEC;
                border-radius: 11px;
                padding: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #C5DFF8;
            }

            QComboBox, QSpinBox, QTextEdit {
                background: #FFFFFF;
                border: 1px solid #CDDDEB;
                border-radius: 10px;
                padding: 9px;
            }

            QProgressBar {
                background: #E6EDF5;
                border: 0;
                border-radius: 7px;
                height: 20px;
                text-align: center;
                color: #23415F;
            }

            QProgressBar::chunk {
                background: #91BCE2;
                border-radius: 7px;
            }

            QFrame#separator {
                background: #DFE8F2;
                max-height: 1px;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(14)

        heading = QLabel("✦ LIFE Control Center")
        heading.setObjectName("heading")
        main.addWidget(heading)

        subtitle = QLabel(
            "Your desktop. Your atmosphere. Your space."
        )
        subtitle.setObjectName("subtitle")
        main.addWidget(subtitle)

        self.tabs = QTabWidget()
        main.addWidget(self.tabs, 1)

        self.build_appearance()
        self.build_desktop()
        self.build_system()
        self.build_tools()
        self.build_about()

        self.status = QLabel("LIFE Lite · Ready")
        self.status.setObjectName("subtitle")
        main.addWidget(self.status)

    def page(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(15)
        self.tabs.addTab(widget, title)
        return layout

    def heading(self, layout, title, description=None):
        label = QLabel(title)
        label.setObjectName("section")
        layout.addWidget(label)

        if description:
            detail = QLabel(description)
            detail.setWordWrap(True)
            detail.setObjectName("subtitle")
            layout.addWidget(detail)

    def button(self, title, callback):
        button = QPushButton(title)
        button.clicked.connect(callback)
        return button

    def report(self, message):
        self.status.setText(message)

    def failure(self, title, error):
        QMessageBox.warning(self, title, str(error))
        self.report(f"{title}: {error}")

    # -----------------------------------
    # M24: Appearance
    # -----------------------------------

    def build_appearance(self):
        layout = self.page("Appearance")

        self.heading(
            layout,
            "Wallpaper Studio",
            "Choose one of LIFE OS's original wallpapers."
        )

        self.wallpaper_choice = QComboBox()
        self.wallpaper_choice.addItems(
            list(self.wallpapers)
        )

        layout.addWidget(self.wallpaper_choice)

        self.wall_preview = QLabel()
        self.wall_preview.setMinimumHeight(210)
        self.wall_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wall_preview.setStyleSheet(
            "background:#E0EBF5;"
            "border-radius:14px;"
            "padding:10px;"
        )
        layout.addWidget(self.wall_preview, 1)

        self.wallpaper_choice.currentTextChanged.connect(
            self.update_wallpaper_preview
        )
        self.update_wallpaper_preview()

        layout.addWidget(
            self.button(
                "Apply LIFE Wallpaper",
                self.change_wallpaper
            )
        )

        self.heading(
            layout,
            "Native appearance",
            "Edit XFCE window appearance and desktop settings."
        )

        row = QHBoxLayout()
        row.addWidget(
            self.button(
                "XFCE Appearance",
                lambda: self.launch("xfce4-appearance-settings")
            )
        )
        row.addWidget(
            self.button(
                "Desktop Settings",
                lambda: self.launch("xfdesktop-settings")
            )
        )
        layout.addLayout(row)

    def update_wallpaper_preview(self, *_):
        path = self.wallpapers.get(
            self.wallpaper_choice.currentText()
        )

        if not path:
            self.wall_preview.setText(
                "Wallpaper preview unavailable"
            )
            return

        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            self.wall_preview.setText("Preview unavailable")
        else:
            self.wall_preview.setPixmap(
                pixmap.scaled(
                    600, 290,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

    def change_wallpaper(self):
        name = self.wallpaper_choice.currentText()
        path = self.wallpapers.get(name)

        if not path:
            return

        try:
            apply_wallpaper(path)
            self.report(f"Wallpaper applied: {name}")
        except Exception as error:
            self.failure("Wallpaper", error)

    # -----------------------------------
    # M25: Desktop panels
    # -----------------------------------

    def build_desktop(self):
        layout = self.page("Desktop")

        self.heading(
            layout,
            "LIFE Panel Studio",
            "Control the real XFCE top bar and bottom dock."
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)

        self.top_size = QSpinBox()
        self.top_size.setRange(25, 70)
        self.top_size.setSuffix(" px")
        self.top_size.setValue(
            self.current_panel_size(1, 36)
        )

        self.dock_size = QSpinBox()
        self.dock_size.setRange(35, 95)
        self.dock_size.setSuffix(" px")
        self.dock_size.setValue(
            self.current_panel_size(2, 55)
        )

        grid.addWidget(QLabel("Top bar height"), 0, 0)
        grid.addWidget(self.top_size, 0, 1)

        grid.addWidget(QLabel("Dock height"), 1, 0)
        grid.addWidget(self.dock_size, 1, 1)

        layout.addLayout(grid)

        layout.addWidget(
            self.button(
                "Apply Panel Sizes",
                self.apply_panel_sizes
            )
        )

        self.heading(
            layout,
            "Desktop controls",
            "Open native XFCE utilities."
        )

        controls = QGridLayout()

        commands = [
            ("Panel Preferences", "xfce4-panel", "--preferences"),
            ("Window Manager", "xfwm4-settings"),
            ("Keyboard Settings", "xfce4-keyboard-settings"),
            ("Display Settings", "xfce4-display-settings"),
        ]

        for index, command in enumerate(commands):
            title, *args = command

            controls.addWidget(
                self.button(
                    title,
                    lambda a=args: self.launch(*a)
                ),
                index // 2,
                index % 2
            )

        layout.addLayout(controls)
        layout.addStretch()

    def current_panel_size(self, panel, default):
        value = xf_get(
            "xfce4-panel",
            f"/panels/panel-{panel}/size"
        )
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def apply_panel_sizes(self):
        try:
            xf_set(
                "xfce4-panel",
                "/panels/panel-1/size",
                self.top_size.value(),
                "uint"
            )
            xf_set(
                "xfce4-panel",
                "/panels/panel-2/size",
                self.dock_size.value(),
                "uint"
            )
            self.report("XFCE panels updated.")
        except Exception as error:
            self.failure("Panel settings", error)

    # -----------------------------------
    # M26: System Monitor
    # -----------------------------------

    def build_system(self):
        layout = self.page("System")

        self.heading(
            layout,
            "LIFE System Monitor",
            "Live information from your Codespaces Linux session."
        )

        self.cpu_info = QLabel("CPU usage: measuring...")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)

        self.ram_info = QLabel("Memory")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)

        self.disk_info = QLabel("Disk")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)

        for label, bar in (
            (self.cpu_info, self.cpu_bar),
            (self.ram_info, self.ram_bar),
            (self.disk_info, self.disk_bar)
        ):
            layout.addWidget(label)
            layout.addWidget(bar)

        self.session_info = QLabel()
        self.session_info.setWordWrap(True)
        layout.addWidget(self.session_info)

        layout.addWidget(
            self.button(
                "Refresh Now",
                self.refresh_system
            )
        )

        layout.addStretch()

    def refresh_system(self):
        total, used = system_memory()

        if total:
            percent = round(used / total * 100)
            self.ram_bar.setValue(percent)
            self.ram_info.setText(
                f"Memory: {gb(used)} / {gb(total)}"
            )

        disk = shutil.disk_usage(HOME)
        disk_used = disk.total - disk.free

        disk_percent = (
            round(disk_used / disk.total * 100)
            if disk.total else 0
        )
        self.disk_bar.setValue(disk_percent)

        self.disk_info.setText(
            f"Disk: {gb(disk_used)} / {gb(disk.total)}"
        )

        now_cpu = cpu_sample()

        delta_total = now_cpu[0] - self.last_cpu[0]
        delta_idle = now_cpu[1] - self.last_cpu[1]

        if delta_total > 0:
            cpu_percent = round(
                100 * (1 - delta_idle / delta_total)
            )
            cpu_percent = max(0, min(100, cpu_percent))
            self.cpu_bar.setValue(cpu_percent)
            self.cpu_info.setText(
                f"CPU usage: {cpu_percent}%"
            )

        self.last_cpu = now_cpu

        self.session_info.setText(
            f"Display: {os.environ.get('DISPLAY', 'Unknown')}\n"
            f"Desktop: XFCE (LIFE Lite)\n"
            f"Logical CPU cores: {os.cpu_count() or 0}\n"
            "Environment: GitHub Codespaces"
        )

    # -----------------------------------
    # Utilities
    # -----------------------------------

    def build_tools(self):
        layout = self.page("Tools")

        self.heading(
            layout,
            "LIFE Utilities",
            "Native tools, useful shortcuts and screenshots."
        )

        tools = [
            ("Open File Manager", ("thunar",)),
            ("Open Applications", ("xfce4-appfinder",)),
            ("Open Terminal", ("xfce4-terminal",)),
            ("Open LIFE App Center", (
                str(HOME / ".local/bin/life-lite-apps"),
            )),
        ]

        grid = QGridLayout()

        for index, (title, command) in enumerate(tools):
            grid.addWidget(
                self.button(
                    title,
                    lambda c=command: self.launch(*c)
                ),
                index // 2,
                index % 2
            )

        layout.addLayout(grid)

        self.heading(layout, "Desktop screenshot")

        layout.addWidget(
            self.button(
                "Capture Desktop Screenshot",
                self.screenshot
            )
        )

        layout.addWidget(
            self.button(
                "Open Screenshot Folder",
                lambda: self.launch("thunar", str(PICTURES))
            )
        )

        layout.addStretch()

    def screenshot(self):
        PICTURES.mkdir(
            parents=True, exist_ok=True
        )

        screen = QApplication.primaryScreen()

        if screen is None:
            self.failure("Screenshot", "No screen detected")
            return

        destination = PICTURES / (
            "life-lite-"
            + datetime.now().strftime("%Y%m%d-%H%M%S")
            + ".png"
        )

        if screen.grabWindow(0).save(str(destination)):
            self.report(
                f"Screenshot saved: {destination.name}"
            )
        else:
            self.failure(
                "Screenshot",
                "Could not capture the desktop"
            )

    def launch(self, *command):
        if not command:
            return

        executable = shutil.which(command[0])

        if not executable:
            self.failure(
                "Application unavailable",
                command[0]
            )
            return

        try:
            subprocess.Popen(
                [executable, *command[1:]],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.report("Opened: " + command[0])
        except OSError as error:
            self.failure("Launch failed", error)

    def build_about(self):
        layout = self.page("About")

        self.heading(
            layout,
            "LIFE OS — Lite Edition"
        )

        text = QLabel(
            "A personal, customizable Linux desktop project.\n\n"
            "Foundation: XFCE on Debian (development environment)\n"
            "Target: Arch-based LIFE OS\n"
            "Interface: native Linux desktop\n"
            "Current milestone: M24–M26\n\n"
            "LIFE OS is still under development. "
            "This is an XFCE integration prototype, "
            "not a complete standalone distribution."
        )

        text.setWordWrap(True)
        text.setStyleSheet(
            "font-size:14px;line-height:1.5;"
        )
        layout.addWidget(text)

        layout.addStretch()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LIFE Control Center")

    window = LifeControl()
    window.show()

    print("LIFE M24–26 Control Center running", flush=True)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
