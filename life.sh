#!/usr/bin/env bash
set -e

cd /workspaces/life-os
source .venv/bin/activate

echo "🍉 Starting LIFE OS development..."

if [ -f scripts/start_life_lite_m20.sh ]; then
    bash scripts/start_life_lite_m20.sh
else
    echo "LIFE Lite startup script missing!"
    exit 1
fi

echo ""
echo "===== LIFE OS STATUS ====="

pgrep -af 'Xvfb|xfce4-session|xfce4-panel|xfwm4' || true

echo ""
echo "Open noVNC port 6082"
echo "LIFE Lite is the default development desktop."
