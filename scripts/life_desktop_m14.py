"""LIFE OS Milestone 14 — polished native shell extension of Milestone 13.

No network, repository writes, or access to Notes storage. Persist only visual
preferences in ~/.config/lifeos/desktop-m14.json.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QRadialGradient, QPixmap, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget, QScrollArea
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import life_desktop_m13 as base

PREFS = Path.home() / '.config' / 'lifeos' / 'desktop-m14.json'
base.THEMES.update({
    'Sage': dict(top='#BFD8CC', mid='#EBE9DD', bottom='#FAEAD4', hill1='#B7C7B4', hill2='#92AC9E', hill3='#648C83', ink='#253F39', glass='#FAFFF8', muted='#557267', accent='#D8E9DB', dark=False),
    'Aurora': dict(top='#1B2749', mid='#38436D', bottom='#927D9A', hill1='#536C89', hill2='#3E5475', hill3='#263B64', ink='#F5F3FF', glass='#2D375A', muted='#C9C8E5', accent='#536991', dark=True),
})


def read_prefs():
    try:
        data = json.loads(PREFS.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def save_prefs(data):
    PREFS.parent.mkdir(parents=True, exist_ok=True)
    temporary = PREFS.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temporary.replace(PREFS)


class CachedWallpaper(base.Wallpaper):
    """Paint the landscape once per size/theme instead of on every exposure."""
    def __init__(self):
        super().__init__()
        self._cache = None
        self._cache_key = None

    def paintEvent(self, event):
        if self.width() < 2 or self.height() < 2:
            return
        key = (self.width(), self.height(), self.theme)
        if self._cache_key != key:
            self._cache_key = key
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w, h = self.width(), self.height()
            t = base.THEMES[self.theme]
            sky = QLinearGradient(0, 0, w*.22, h)
            sky.setColorAt(0, QColor(t['top']))
            sky.setColorAt(.58, QColor(t['mid']))
            sky.setColorAt(1, QColor(t['bottom']))
            painter.fillRect(pixmap.rect(), sky)
            painter.setPen(Qt.PenStyle.NoPen)
            glow = QRadialGradient(QPointF(w*.74, h*.25), min(w, h)*.25)
            glow.setColorAt(0, QColor(255, 245, 216, 215))
            glow.setColorAt(.30, QColor(255, 245, 216, 105))
            glow.setColorAt(1, QColor(255, 245, 216, 0))
            painter.setBrush(glow)
            rr = min(w,h)*.25
            painter.drawEllipse(QPointF(w*.74,h*.25),rr,rr)
            for index, c in enumerate((t['hill1'], t['hill2'], t['hill3'])):
                y = h*(.58+index*.14)
                path = QPainterPath(QPointF(0,h))
                path.lineTo(0,y+35)
                path.cubicTo(w*.21,y-h*.21,w*.37,y+h*.08,w*.55,y-25)
                path.cubicTo(w*.76,y-h*.17,w*.89,y+h*.12,w,y-60)
                path.lineTo(w,h)
                path.closeSubpath()
                painter.fillPath(path,QColor(c))
            # Gentle static grain-free constellation in dark modes.
            if t['dark']:
                painter.setBrush(QColor('#FFFFFF'))
                for x,y,r in ((.15,.18,2),(.21,.25,1),(.34,.13,2),(.49,.30,1),(.61,.15,2),(.88,.11,1),(.93,.37,2),(.4,.38,1)):
                    painter.setOpacity(.50)
                    painter.drawEllipse(QPointF(w*x,h*y),r,r)
                painter.setOpacity(1)
            painter.end()
            self._cache = pixmap
        painter = QPainter(self)
        painter.drawPixmap(0,0,self._cache)
        painter.end()


class Desktop14(base.Desktop):
    def __init__(self, app):
        self.prefs = read_prefs()
        self.focus_mode = bool(self.prefs.get('focus_mode', False))
        self.window_history = []
        self.events = [('Welcome', 'Your desktop session is ready.')]
        super().__init__(app)
        self.setWindowTitle('LIFE OS · Desktop M14')
        self.setMinimumSize(920,600)
        self.apply_theme(self.prefs.get('theme','Horizon'))
        self._make_m14_shortcuts()
        self.refresh_tasks()
        self._sync_focus()

    def _make_topbar(self):
        bar=QFrame()
        bar.setObjectName('chrome')
        bar.setFixedHeight(56)
        line=QHBoxLayout(bar)
        line.setContentsMargins(19,3,16,3)
        line.setSpacing(10)
        brand=QLabel('◈   LIFE OS')
        brand.setObjectName('brand')
        line.addWidget(brand)
        sub=QLabel('  ·  STUDIO')
        sub.setObjectName('muted')
        line.addWidget(sub)
        line.addSpacing(19)
        line.addWidget(base.button('⌕  Search',self.show_launcher,'topButton'))
        line.addWidget(base.button('▦  Library',self.show_launcher,'topButton'))
        line.addWidget(base.button('▤  Windows',self.show_windows,'topButton'))
        line.addStretch(1)
        self.date_label=QLabel('')
        self.date_label.setObjectName('topInfo')
        line.addWidget(self.date_label)
        line.addWidget(base.button('◷',self.show_notifications,'topButton'))
        line.addWidget(base.button('◉  Control Center',self.show_settings,'topButton'))
        self.vbox.addWidget(bar)

    def _make_center(self):
        super()._make_center()
        from PySide6.QtGui import QBrush, QColor
        self.mdi.setBackground(QBrush(QColor(0, 0, 0, 0)))
        self.mdi.setAutoFillBackground(False)
        self.mdi.viewport().setAutoFillBackground(False)
        self.mdi.viewport().setStyleSheet(
            "QMdiArea { background: transparent; }"
            "QMdiSubWindow { background: #F7F9FD; }"
            "QMdiSubWindow > QWidget { background: #F7F9FD; }"
        )

        self.welcome.setFixedSize(430, 212)
        title=self.welcome.findChild(QLabel,'welcomeTitle')
        if title:
            title.setText('Your space to make beautiful things happen.')
        self.atmosphere=QFrame(self.mdi.viewport())
        self.atmosphere.setObjectName('atmosphere')
        self.atmosphere.setFixedSize(230, 138)
        al=QVBoxLayout(self.atmosphere)
        al.setContentsMargins(20,15,16,14)
        self.atmosphere_tag=QLabel('LIFE  /  TODAY')
        self.atmosphere_tag.setObjectName('muted')
        self.atmosphere_time=QLabel('')
        self.atmosphere_time.setObjectName('ambientTime')
        self.atmosphere_date=QLabel('')
        self.atmosphere_date.setObjectName('muted')
        al.addWidget(self.atmosphere_tag)
        al.addWidget(self.atmosphere_time)
        al.addWidget(self.atmosphere_date)
        al.addStretch()
        self.atmosphere.show()

    def _make_dock(self):
        foot=QHBoxLayout()
        foot.addStretch(1)
        dock=QFrame()
        dock.setObjectName('dock')
        row=QHBoxLayout(dock)
        row.setContentsMargins(13,8,13,8)
        row.setSpacing(7)
        self.dock_buttons={}
        entries=[
            ('◈','Home',self.go_home), ('▦','Apps',self.show_launcher),
            ('▣','Explorer',lambda:self.launch('Explorer')),
            ('✎','Writer',lambda:self.launch('Writer')),
            ('✦','Notes',lambda:self.launch('LIFE Notes')),
            ('◷','Clock',lambda:self.launch('Clock')),
            ('▤','Windows',self.show_windows),
            ('◉','Settings',self.show_settings),
        ]
        for glyph,name,callback in entries:
            b=base.button(glyph,callback,'dockButton',49)
            b.setFixedWidth(49)
            b.setToolTip(name)
            row.addWidget(b)
            self.dock_buttons[name]=b
        self.tasks_label=QLabel('  Your desktop')
        self.tasks_label.setObjectName('taskLabel')
        row.addWidget(self.tasks_label)
        foot.addWidget(dock)
        foot.addStretch(1)
        self.vbox.addLayout(foot)

    def _make_m14_shortcuts(self):
        for key,cb in (
            ('Ctrl+Tab',self.switch_app),
            ('Ctrl+Alt+Left',lambda:self.tile_active('left')),
            ('Ctrl+Alt+Right',lambda:self.tile_active('right')),
            ('Ctrl+Alt+Up',lambda:self.tile_active('full')),
            ('Ctrl+Alt+Down',self.restore_active),
            ('Ctrl+Shift+W',self.show_windows),
        ):
            shortcut=QShortcut(QKeySequence(key),self)
            shortcut.activated.connect(cb)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'atmosphere'):
            self.atmosphere.move(max(10,self.mdi.viewport().width()-self.atmosphere.width()-20),35)

    def palette_style(self):
        t=base.THEMES[self.theme]
        extra=(
          f'QFrame#atmosphere {{ background:{t["glass"]}; border:1px solid {t["hill1"]}; border-radius:22px; }}'
          f'QLabel#ambientTime {{font-size:37px;font-weight:700;color:{t["ink"]};}}'
          f'QPushButton#dockButton[active="true"] {{background:{t["accent"]}; border-radius:14px;}}'
          f'QPushButton#miniAction {{background:{t["accent"]}; border-radius:12px; font-weight:bold;}}'
        )
        return super().palette_style()+'\n'+extra

    def apply_theme(self,name):
        if name not in base.THEMES:
            name='Horizon'
        super().apply_theme(name)
        self.prefs['theme']=name
        try:
            save_prefs(self.prefs)
        except OSError as exc:
            print('Could not save visual preference:',exc,flush=True)

    def update_clock(self):
        super().update_clock()
        if hasattr(self,'atmosphere_time'):
            now=datetime.now()
            self.atmosphere_time.setText(now.strftime('%H:%M'))
            self.atmosphere_date.setText(now.strftime('%A, %d %B'))

    def _sync_focus(self):
        if hasattr(self,'atmosphere'):
            self.atmosphere.setVisible(not self.focus_mode)
        if hasattr(self,'welcome'):
            self.welcome.setVisible(not self.focus_mode and not self.mdi.subWindowList())

    def toggle_focus(self):
        self.focus_mode=not self.focus_mode
        self.prefs['focus_mode']=self.focus_mode
        try:
            save_prefs(self.prefs)
        except OSError:
            pass
        self._sync_focus()
        self.show_settings()

    def show_settings(self):
        self.show_drawer('settings','Control Center','Personalize your LIFE desktop')
        layout=self.drawer.layout_box
        label=QLabel('DESKTOP MOOD  ·  SELECT WALLPAPER')
        label.setObjectName('muted')
        layout.addWidget(label)
        gridhost=QWidget()
        grid=QGridLayout(gridhost)
        grid.setContentsMargins(0,0,0,0)
        grid.setSpacing(9)
        for i,(name,glyph) in enumerate((('Horizon','☀'),('Blush','✿'),('Sage','❀'),('Midnight','☾'),('Aurora','✧'))):
            marker=' ✓' if name==self.theme else ''
            grid.addWidget(base.button(f'{glyph}  {name}{marker}',lambda _=False,n=name:self.apply_theme(n),'control',48),i//2,i%2)
        layout.addWidget(gridhost)
        layout.addSpacing(8)
        layout.addWidget(base.button(('✓  ' if self.focus_mode else '')+'Focus desktop (hide widgets)',self.toggle_focus,'control'))
        layout.addWidget(base.button('▤  Manage open windows',self.show_windows,'control'))
        layout.addWidget(base.button('▦  App Library',self.show_launcher,'primary'))
        info=QLabel('SHORTCUTS\nCtrl+Space  App Library\nCtrl+Shift+W  Windows\nCtrl+Tab  Switch app\nCtrl+Alt+←/→  Tile active window\nCtrl+Alt+↑  Fill desktop\nCtrl+Alt+↓  Restore window\nEsc  Close panel')
        info.setObjectName('muted')
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()

    def _active(self):
        sub=self.mdi.activeSubWindow()
        if not sub and self.mdi.subWindowList():
            sub=self.mdi.subWindowList()[-1]
        return sub

    def tile_active(self,placement):
        sub=self._active()
        if sub is None:
            self.show_windows()
            return
        sub.showNormal()
        w=max(300,self.mdi.viewport().width()-12)
        h=max(240,self.mdi.viewport().height()-12)
        if placement=='left':
            sub.setGeometry(6,6,max(260,w//2-3),h)
        elif placement=='right':
            sub.setGeometry(w//2+5,6,max(260,w//2-4),h)
        elif placement=='full':
            sub.setGeometry(6,6,w,h)
        self.mdi.setActiveSubWindow(sub)
        sub.raise_()
        self.refresh_tasks()

    def restore_active(self):
        sub=self._active()
        if sub:
            sub.showNormal()
            width=max(340,min(760,self.mdi.viewport().width()-90))
            height=max(250,min(520,self.mdi.viewport().height()-90))
            sub.resize(width,height)
            sub.move(max(10,(self.mdi.viewport().width()-width)//2),max(10,(self.mdi.viewport().height()-height)//2))
            self.mdi.setActiveSubWindow(sub)

    def switch_app(self):
        windows=[w for w in self.mdi.subWindowList() if not w.isHidden()]
        if not windows:
            self.show_launcher()
            return
        active=self.mdi.activeSubWindow()
        if active in windows:
            target=windows[(windows.index(active)+1)%len(windows)]
        else:
            target=windows[0]
        target.showNormal()
        self.mdi.setActiveSubWindow(target)
        target.raise_()

    def show_windows(self):
        self.show_drawer('windows','Window Studio','Arrange, focus and switch your apps')
        layout=self.drawer.layout_box
        active=self._active()
        if active:
            gridhost=QWidget()
            grid=QGridLayout(gridhost)
            grid.setContentsMargins(0,0,0,0)
            grid.setSpacing(7)
            for index,(title,action) in enumerate((('◧  Tile left',lambda:self.tile_active('left')),
                                                   ('◨  Tile right',lambda:self.tile_active('right')),
                                                   ('▣  Fill area',lambda:self.tile_active('full')),
                                                   ('▫  Restore',self.restore_active))):
                grid.addWidget(base.button(title,action,'control',52),index//2,index%2)
            layout.addWidget(gridhost)
        windows=self.mdi.subWindowList()
        if not windows:
            label=QLabel('No app windows open yet. Explore the library to get started.')
            label.setObjectName('muted')
            label.setWordWrap(True)
            layout.addWidget(label)
        else:
            label=QLabel(f'{len(windows)} OPEN WINDOW'+('S' if len(windows)!=1 else ''))
            label.setObjectName('muted')
            layout.addWidget(label)
            for sub in windows:
                isactive=sub==self.mdi.activeSubWindow()
                b=base.button(('●  ' if isactive else '○  ')+sub.windowTitle(),lambda _=False,s=sub:self.activate_sub(s),'control',50)
                layout.addWidget(b)
        layout.addStretch()
        layout.addWidget(base.button('▦  Open another app',self.show_launcher,'primary'))

    def activate_sub(self,sub):
        if sub in self.mdi.subWindowList():
            sub.showNormal()
            sub.show()
            self.mdi.setActiveSubWindow(sub)
            sub.raise_()
        self.hide_drawer()

    def refresh_tasks(self,*args):
        super().refresh_tasks(*args)
        if hasattr(self,'dock_buttons'):
            active=self.mdi.activeSubWindow()
            for name,b in self.dock_buttons.items():
                match=(active is not None and name in active.windowTitle())
                if name=='Home':
                    match=active is None
                b.setProperty('active',bool(match))
                b.style().unpolish(b)
                b.style().polish(b)

    def launch(self,name):
        super().launch(name)
        self.refresh_tasks()
        if hasattr(self,'atmosphere'):
            self.atmosphere.lower()  # App windows should never be covered by ambient card.

    def go_home(self):
        super().go_home()
        self._sync_focus()
        self.refresh_tasks()

    def show_notifications(self):
        self.show_drawer('notifications','Activity Center','A calm place for useful updates')
        layout=self.drawer.layout_box
        for name,detail in self.events[-5:][::-1]:
            tile=QFrame()
            tile.setObjectName('atmosphere')
            vl=QVBoxLayout(tile)
            vl.setContentsMargins(13,12,13,12)
            label=QLabel('✦  '+name)
            label.setStyleSheet('font-weight:700;')
            detailLabel=QLabel(detail)
            detailLabel.setObjectName('muted')
            detailLabel.setWordWrap(True)
            vl.addWidget(label)
            vl.addWidget(detailLabel)
            layout.addWidget(tile)
        layout.addStretch()
        layout.addWidget(base.button('▦  Explore applications',self.show_launcher,'primary'))


def main():
    if os.environ.get('QT_QPA_PLATFORM')=='offscreen':
        print('WARNING: Qt offscreen mode will not be visible in noVNC.',flush=True)
    app=QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName('LIFE OS Desktop M14')
    # Swap only the wallpaper renderer: identical artwork, cached between repaints.
    base.Wallpaper = CachedWallpaper
    desktop=Desktop14(app)
    print('LIFE OS M14 ready · desktop, windows, themes, shortcuts',flush=True)
    if not base.APPS_READY:
        print('App availability warning:',base.IMPORT_FAILURE,flush=True)
    return app.exec()


if __name__=='__main__':
    raise SystemExit(main())
