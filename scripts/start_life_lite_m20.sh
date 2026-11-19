#!/usr/bin/env bash
set -e

export DISPLAY=:97
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_DESKTOP=xfce
export QT_QPA_PLATFORM=xcb
export NO_AT_BRIDGE=1

echo "🍉 Starting LIFE Lite — XFCE"

# 1. Virtual display
if ! DISPLAY=:97 xdpyinfo >/dev/null 2>&1; then
    Xvfb :97 -screen 0 1440x900x24 -nolisten tcp \
        >/tmp/life-lite-xvfb.log 2>&1 &
    sleep 2
fi

# 2. XFCE desktop session
if ! pgrep -f '^xfce4-session$' >/dev/null; then
    nohup dbus-run-session -- xfce4-session \
        >/tmp/life-lite-xfce.log 2>&1 </dev/null &
    sleep 4
fi

# 3. VNC connection
if ! ss -ltn | grep -q ':5902 '; then
    x11vnc -display :97 -localhost -nopw \
        -forever -shared -rfbport 5902 \
        -bg -o /tmp/life-lite-vnc.log
fi

# 4. Browser access
if ! ss -ltn | grep -q ':6082 '; then
    nohup websockify --web=/usr/share/novnc/ \
        6082 localhost:5902 \
        >/tmp/life-lite-web.log 2>&1 </dev/null &
fi

echo ""
echo "===== LIFE LITE STATUS ====="

DISPLAY=:97 xdpyinfo >/dev/null 2>&1 \
    && echo "✅ Display :97 ready"

pgrep -af 'xfce4-session|xfce4-panel|xfwm4|xfdesktop' || true

ss -ltn | grep -E ':5902 |:6082 ' || true

echo ""
echo "🍉 Open Codespaces port 6082"
echo "Keep port 6082 PRIVATE."
echo "If XFCE fails, see /tmp/life-lite-xfce.log"
