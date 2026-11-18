"""Small, native PySide6 utilities for LIFE OS."""
from __future__ import annotations
import os
import platform
import time
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QScrollArea, QHBoxLayout)


class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LIFE Clock')
        self.resize(480, 270)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        self.time_text = QLabel()
        self.time_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_text.setStyleSheet('font-size: 48px; font-weight: 700;')
        self.date_text = QLabel()
        self.date_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.time_text)
        layout.addWidget(self.date_text)
        layout.addStretch()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    def refresh(self):
        now = datetime.now()
        self.time_text.setText(now.strftime('%H:%M:%S'))
        self.date_text.setText(now.strftime('%A, %d %B %Y'))


class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LIFE System Monitor')
        self.resize(540, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        self.header = QLabel('System overview')
        self.header.setStyleSheet('font-size: 22px; font-weight: 700')
        self.details = QLabel()
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.header)
        layout.addWidget(self.details)
        layout.addStretch()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(3000)
        self.refresh()

    def refresh(self):
        mem = 'Unavailable'
        try:
            stats = {}
            for line in Path('/proc/meminfo').read_text().splitlines():
                parts = line.replace(':', ' ').split()
                if parts and parts[0] in ('MemTotal','MemAvailable'):
                    stats[parts[0]] = int(parts[1]) / (1024*1024)
            total = stats.get('MemTotal')
            available = stats.get('MemAvailable')
            if total is not None and available is not None:
                mem = f'{total-available:.2f} / {total:.2f} GiB used'
        except OSError:
            pass
        self.details.setText(f'Operating system: {platform.system()} {platform.release()}\n'
                             f'Processor architecture: {platform.machine()}\n'
                             f'CPU cores available: {os.cpu_count() or "Unknown"}\n'
                             f'Memory: {mem}\n\n'
                             'Statistics reflect the Codespaces container, not your Mac.')


class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LIFE Image Viewer')
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        browse = QPushButton('Open image…')
        browse.clicked.connect(self.open_image)
        layout.addWidget(browse)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.picture = QLabel('Open a PNG, JPEG, BMP, or WebP image')
        self.picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.picture)
        layout.addWidget(self.scroll)
        self.current_pixmap = None

    def open_image(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Open image', str(Path.home()),
                                             'Images (*.png *.jpg *.jpeg *.bmp *.webp)')
        if not name:
            return
        pixmap = QPixmap(name)
        if pixmap.isNull():
            self.picture.setText('Unable to open this image')
            return
        self.current_pixmap = pixmap
        self.setWindowTitle(f'LIFE Image Viewer — {Path(name).name}')
        self.render_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap is not None:
            self.render_image()

    def render_image(self):
        size = self.scroll.viewport().size()
        if size.width() > 10 and size.height() > 10:
            self.picture.setPixmap(self.current_pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
