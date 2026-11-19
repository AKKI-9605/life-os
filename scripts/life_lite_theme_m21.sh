#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/life-os
source .venv/bin/activate

export DISPLAY=:97
export QT_QPA_PLATFORM=offscreen

echo "🍉 LIFE Lite — Visual Identity M21"

mkdir -p \
  "$HOME/.local/share/lifeos/wallpapers" \
  "$HOME/.local/bin" \
  "$HOME/.local/share/applications" \
  "$HOME/Desktop" \
  "$HOME/.config/lifeos/backups"

# 1. Render our existing original wallpaper to PNG.
python - <<'PY'
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

root = Path("/workspaces/life-os")
source = root / "desktop/assets/wallpapers/blue-horizon.svg"
output = Path.home() / ".local/share/lifeos/wallpapers/life-horizon.png"

if not source.exists():
    raise SystemExit(f"Missing wallpaper: {source}")

renderer = QSvgRenderer(str(source))
if not renderer.isValid():
    raise SystemExit("Wallpaper SVG could not be rendered")

image = QImage(1440, 900, QImage.Format.Format_ARGB32)
image.fill(QColor("#DCEAF5"))

painter = QPainter(image)
painter.setRenderHint(QPainter.RenderHint.Antialiasing)
renderer.render(painter)
painter.end()

if not image.save(str(output), "PNG"):
    raise SystemExit("Could not save wallpaper")

print("✅ Original LIFE wallpaper ready:", output)
PY

# 2. Find the DBus session belonging to XFCE.
SESSION_PID="$(pgrep -u "$(id -u)" -x xfce4-session | head -1 || true)"

if [ -n "$SESSION_PID" ] && [ -r "/proc/$SESSION_PID/environ" ]; then
    BUS="$(
      tr '\0' '\n' < "/proc/$SESSION_PID/environ" |
      sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p' |
      head -1
    )"

    if [ -n "$BUS" ]; then
        export DBUS_SESSION_BUS_ADDRESS="$BUS"
    fi
fi

WALL="$HOME/.local/share/lifeos/wallpapers/life-horizon.png"

# 3. Back up and configure the XFCE wallpaper.
if xfconf-query -c xfce4-desktop -lv \
    > "$HOME/.config/lifeos/backups/xfce-desktop-before-m21.txt" \
    2>/dev/null; then

    echo "✅ XFCE configuration accessible"

    mapfile -t PROPS < <(
      xfconf-query -c xfce4-desktop -lv |
      awk '$1 ~ /\/last-image$/ {print $1}'
    )

    if [ "${#PROPS[@]}" -eq 0 ]; then
        PROPS=(
          "/backdrop/screen0/monitor0/workspace0/last-image"
        )
    fi

    for PROP in "${PROPS[@]}"; do
        xfconf-query -c xfce4-desktop \
          -p "$PROP" \
          --create -t string -s "$WALL" \
          2>/dev/null || \
        xfconf-query -c xfce4-desktop \
          -p "$PROP" -s "$WALL" || true

        STYLE_PROP="${PROP%/last-image}/image-style"

        xfconf-query -c xfce4-desktop \
          -p "$STYLE_PROP" \
          --create -t int -s 5 \
          2>/dev/null || true
    done

    xfconf-query -c xsettings \
      -p /Net/ThemeName \
      --create -t string -s Adwaita \
      2>/dev/null || true

    xfconf-query -c xsettings \
      -p /Net/IconThemeName \
      --create -t string -s Adwaita \
      2>/dev/null || true
else
    echo "⚠️ XFCE configuration unavailable; wallpaper file still saved."
fi

# 4. Create a native LIFE App Center launcher.
cat > "$HOME/.local/bin/life-lite-apps" <<'APP'
#!/usr/bin/env bash
cd /workspaces/life-os
source .venv/bin/activate

export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1

exec python -u scripts/life_apps.py
APP

chmod +x "$HOME/.local/bin/life-lite-apps"

ICON="/workspaces/life-os/desktop/assets/icons/light/launcher.svg"

cat > "$HOME/.local/share/applications/life-lite-apps.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LIFE App Center
Comment=Native applications for LIFE Lite
Exec=$HOME/.local/bin/life-lite-apps
Icon=$ICON
Terminal=false
Categories=Utility;
StartupNotify=true
EOF

cp "$HOME/.local/share/applications/life-lite-apps.desktop" \
   "$HOME/Desktop/LIFE App Center.desktop"

chmod +x "$HOME/Desktop/LIFE App Center.desktop"

# 5. Refresh the desktop.
DISPLAY=:97 xfdesktop --reload 2>/dev/null || true

echo ""
echo "=================================="
echo "  LIFE Lite M21 setup complete"
echo "=================================="
echo "Wallpaper: $WALL"
echo "App Center: LIFE App Center"
echo "Desktop: XFCE on :97"
echo "Browser: port 6082"
echo ""
echo "No Notes database or project source files were deleted."
