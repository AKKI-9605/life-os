#!/usr/bin/env bash
set -e

cd /workspaces/life-os
source .venv/bin/activate

export DISPLAY=:98
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1

echo "🍉 Starting LIFE OS..."

# Virtual display
if ! pgrep -af '^Xvfb :98 ' >/dev/null; then
    Xvfb :98 -screen 0 1440x900x24 -nolisten tcp \
      >/tmp/life-xvfb.log 2>&1 &
    sleep 2
fi

# Window manager
if ! DISPLAY=:98 xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | grep -q 'window id'; then
    DISPLAY=:98 openbox >/tmp/life-openbox.log 2>&1 &
    sleep 1
fi

# VNC server
if ! ss -ltn | grep -q ':5901 '; then
    x11vnc -display :98 -localhost -nopw \
      -forever -shared -rfbport 5901 \
      -bg -o /tmp/life-vnc.log
fi

# Browser desktop
if ! ss -ltn | grep -q ':6081 '; then
    nohup websockify --web=/usr/share/novnc/ \
      6081 localhost:5901 \
      >/tmp/life-web.log 2>&1 </dev/null &
fi

# Main LIFE OS
if ! pgrep -af '^python .* -m lifeos$|^python -m lifeos$' >/dev/null; then
    nohup python -u -m lifeos \
      >/tmp/life-main.log 2>&1 </dev/null &
fi

# Native App Center
if [ -f scripts/life_apps.py ]; then
    if ! pgrep -af '^python .*scripts/life_apps.py$' >/dev/null; then
        nohup python -u scripts/life_apps.py \
          >/tmp/life-apps.log 2>&1 </dev/null &
    fi
fi

sleep 3

echo ""
echo "===== LIFE OS STATUS ====="
ss -ltn | grep -E ':5901 |:6081 ' || true
pgrep -af '^python .*lifeos$|^python .*life_apps.py$' || true

echo ""
echo "✅ Startup finished!"
echo "🌐 Open Codespaces port 6081"
echo "If an app is missing, check /tmp/life-main.log"
echo "or /tmp/life-apps.log"
