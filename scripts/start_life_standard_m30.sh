#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="/workspaces/life-os"
cd "$ROOT"

echo "======================================"
echo "  LIFE OS STANDARD — M27–M30"
echo "  Real KDE Plasma Desktop"
echo "======================================"

# Keep LIFE Standard separate from LIFE Lite.
export DISPLAY=:96
export XDG_CURRENT_DESKTOP=KDE
export XDG_SESSION_DESKTOP=KDE
export XDG_SESSION_TYPE=x11
export KDE_SESSION_VERSION=5
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QUICK_BACKEND=software

export XDG_CONFIG_HOME="$HOME/.config/lifeos-standard"
mkdir -p "$XDG_CONFIG_HOME"

RUNTIME="/tmp/life-standard-runtime-$(id -u)"
mkdir -p "$RUNTIME"
chmod 700 "$RUNTIME"
export XDG_RUNTIME_DIR="$RUNTIME"

mkdir -p \
  "$ROOT/desktop/life-standard" \
  "$HOME/.local/share/lifeos/wallpapers"

# ======================================
# M27 — INSTALL REAL KDE PLASMA
# ======================================

echo ""
echo "[M27] Checking KDE components..."

if ! command -v startplasma-x11 >/dev/null 2>&1; then

    echo "Refreshing package lists..."
    sudo apt-get update

    echo "Installing minimal KDE Plasma..."
    sudo DEBIAN_FRONTEND=noninteractive \
      apt-get install -y --no-install-recommends \
      plasma-desktop \
      plasma-workspace \
      kwin-x11 \
      dolphin \
      systemsettings \
      breeze-icon-theme \
      dbus-x11

fi

if ! command -v startplasma-x11 >/dev/null 2>&1; then
    echo "ERROR: KDE Plasma executable not found."
    exit 1
fi

echo "KDE Plasma installed."

# ======================================
# M28 — ORIGINAL LIFE WALLPAPER
# ======================================

echo ""
echo "[M28] Preparing LIFE Standard wallpaper..."

if [ -f "$ROOT/.venv/bin/activate" ]; then
    source "$ROOT/.venv/bin/activate"

    QT_QPA_PLATFORM=offscreen python - <<'PY'
from pathlib import Path

from PySide6.QtCore import QRectF
from PySide6.QtGui import (
    QImage, QPainter, QColor
)
from PySide6.QtSvg import QSvgRenderer

root = Path("/workspaces/life-os")
source = root / "desktop/assets/wallpapers/blue-horizon.svg"
target = Path.home() / ".local/share/lifeos/wallpapers/life-standard.png"

if not source.exists():
    print("Wallpaper source unavailable")
else:
    renderer = QSvgRenderer(str(source))

    if renderer.isValid():
        image = QImage(
            1440, 900,
            QImage.Format.Format_ARGB32
        )
        image.fill(QColor("#DCEAF5"))

        painter = QPainter(image)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        renderer.render(
            painter, QRectF(0, 0, 1440, 900)
        )
        painter.end()

        if image.save(str(target)):
            print("Wallpaper prepared:", target)
PY
fi

# ======================================
# M29 — START ISOLATED KDE SESSION
# ======================================

echo ""
echo "[M29] Starting LIFE Standard display..."

if ! DISPLAY=:96 xdpyinfo >/dev/null 2>&1; then

    nohup Xvfb :96 \
      -screen 0 1440x900x24 \
      -nolisten tcp \
      >/tmp/life-standard-xvfb.log 2>&1 \
      </dev/null &

    sleep 3
fi

if ! DISPLAY=:96 xdpyinfo >/dev/null 2>&1; then
    echo "ERROR: X11 display :96 did not start."
    exit 1
fi

echo "Display :96 is ready."

SESSION_PID_FILE="/tmp/life-standard-session-$(id -u).pid"

SESSION_RUNNING=0

if [ -f "$SESSION_PID_FILE" ]; then
    OLD_PID="$(cat "$SESSION_PID_FILE")"

    if kill -0 "$OLD_PID" 2>/dev/null; then
        SESSION_RUNNING=1
    fi
fi

if [ "$SESSION_RUNNING" -eq 0 ]; then

    echo "Starting native KDE Plasma session..."

    # KDE is launched in a separate DBus session.
    nohup dbus-run-session -- \
      startplasma-x11 \
      >/tmp/life-standard-plasma.log 2>&1 \
      </dev/null &

    echo "$!" > "$SESSION_PID_FILE"

    sleep 8

fi

# ======================================
# M30 — noVNC ACCESS
# ======================================

echo ""
echo "[M30] Starting remote desktop..."

if ! ss -ltn | grep -q ':5903 '; then

    x11vnc \
      -display :96 \
      -localhost \
      -nopw \
      -forever \
      -shared \
      -rfbport 5903 \
      -bg \
      -o /tmp/life-standard-vnc.log

fi

if ! ss -ltn | grep -q ':6083 '; then

    nohup websockify \
      --web=/usr/share/novnc/ \
      6083 localhost:5903 \
      >/tmp/life-standard-web.log 2>&1 \
      </dev/null &

fi

# ======================================
# VERIFY
# ======================================

echo ""
echo "======================================"
echo "  LIFE STANDARD — STATUS"
echo "======================================"

echo "Plasma:"
command -v startplasma-x11

echo ""
echo "Display:"
DISPLAY=:96 xdpyinfo >/dev/null 2>&1 \
  && echo "X11 READY"

echo ""
echo "Processes:"
pgrep -af 'startplasma-x11|plasmashell|kwin_x11' || true

echo ""
echo "Ports:"
ss -ltn | grep -E ':5903 |:6083 ' || true

echo ""
echo "Wallpaper prepared:"
ls -lh \
  "$HOME/.local/share/lifeos/wallpapers/life-standard.png" \
  2>/dev/null || true

echo ""
echo "🍉 Open Codespaces port 6083"
echo "Set the port visibility to PRIVATE."
echo ""
echo "If Plasma does not appear:"
echo "tail -60 /tmp/life-standard-plasma.log"
echo ""
echo "Existing LIFE Lite and Notes data were not modified."
