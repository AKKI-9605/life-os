#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspaces/life-os
cd "$ROOT"
source .venv/bin/activate

export DISPLAY=:97
export QT_QPA_PLATFORM=offscreen

echo "🍉 LIFE Lite — Milestone 23"

CONFIG="$HOME/.config/lifeos"
BACKUP="$CONFIG/backups/m23-$(date +%Y%m%d-%H%M%S)"
WALLDIR="$HOME/.local/share/lifeos/wallpapers"
APPDIR="$HOME/.local/share/applications"
BINDIR="$HOME/.local/bin"

mkdir -p "$BACKUP" "$WALLDIR" "$APPDIR" "$BINDIR"

# Find the running XFCE session.
SESSION_PID=$(pgrep -u "$(id -u)" -x xfce4-session | head -1 || true)

if [ -z "$SESSION_PID" ]; then
    echo "XFCE is not running. Start LIFE Lite first."
    exit 1
fi

BUS=$(
  tr '\0' '\n' < "/proc/$SESSION_PID/environ" |
  sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p' |
  head -1
)

if [ -z "$BUS" ]; then
    echo "Cannot locate XFCE session DBus."
    exit 1
fi

export DBUS_SESSION_BUS_ADDRESS="$BUS"

# Back up relevant configuration.
xfconf-query -c xsettings -lv \
  > "$BACKUP/xsettings.txt" 2>/dev/null || true

xfconf-query -c xfce4-desktop -lv \
  > "$BACKUP/desktop.txt" 2>/dev/null || true

if [ -f "$HOME/.config/gtk-3.0/gtk.css" ]; then
    cp "$HOME/.config/gtk-3.0/gtk.css" \
       "$BACKUP/gtk.css"
fi

echo "✅ Settings backed up to $BACKUP"

# Generate three native PNG wallpapers.
python - <<'PY'
from pathlib import Path
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

root = Path("/workspaces/life-os")
destination = Path.home() / ".local/share/lifeos/wallpapers"

themes = {
    "horizon": "blue-horizon.svg",
    "morning": "morning-haze.svg",
    "midnight": "deep-night.svg",
}

for name, filename in themes.items():
    source = root / "desktop/assets/wallpapers" / filename

    if not source.exists():
        print("Missing:", source)
        continue

    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        print("Invalid SVG:", source)
        continue

    image = QImage(1440, 900, QImage.Format.Format_ARGB32)
    image.fill(QColor("#DCEAF5"))

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, 1440, 900))
    painter.end()

    output = destination / f"life-{name}.png"
    if image.save(str(output)):
        print("Wallpaper created:", output)
PY

# Create a wallpaper switching utility.
cat > "$BINDIR/life-wallpaper" <<'WALL'
#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-horizon}"
DIR="$HOME/.local/share/lifeos/wallpapers"
WALL="$DIR/life-$MODE.png"

if [ ! -f "$WALL" ]; then
    echo "Wallpaper unavailable: $WALL"
    exit 1
fi

export DISPLAY=:97

PID=$(pgrep -u "$(id -u)" -x xfce4-session | head -1 || true)
if [ -z "$PID" ]; then
    echo "XFCE session unavailable"
    exit 1
fi

BUS=$(
  tr '\0' '\n' < "/proc/$PID/environ" |
  sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p' |
  head -1
)

export DBUS_SESSION_BUS_ADDRESS="$BUS"

mapfile -t PROPERTIES < <(
  xfconf-query -c xfce4-desktop -lv |
  awk '$1 ~ /\/last-image$/ {print $1}'
)

if [ "${#PROPERTIES[@]}" -eq 0 ]; then
    echo "No XFCE wallpaper properties found."
    exit 1
fi

for PROP in "${PROPERTIES[@]}"; do
    xfconf-query -c xfce4-desktop \
        -p "$PROP" -s "$WALL"

    STYLE="${PROP%/last-image}/image-style"

    xfconf-query -c xfce4-desktop \
        -p "$STYLE" \
        --create -t int -s 5 2>/dev/null || \
    xfconf-query -c xfce4-desktop \
        -p "$STYLE" -s 5 2>/dev/null || true
done

xfdesktop --reload 2>/dev/null || true
echo "LIFE wallpaper applied: $MODE"
WALL

chmod +x "$BINDIR/life-wallpaper"

# Create a consistent LIFE-style GTK appearance.
mkdir -p "$HOME/.config/gtk-3.0"

cat > "$HOME/.config/gtk-3.0/gtk.css" <<'CSS'
/* LIFE Lite — Milestone 23 */

window,
dialog {
    background-color: #F6F9FD;
    color: #273B54;
}

headerbar {
    background-image: none;
    background-color: #E5EFF9;
    color: #263D57;
    border-bottom: 1px solid #CDDDEB;
}

button {
    border-radius: 9px;
}

entry,
searchentry {
    border-radius: 9px;
}

selection {
    background-color: #B6D6F2;
    color: #203B58;
}

notebook tab {
    padding: 8px 12px;
}
CSS

# Choose lightweight existing GTK/icon themes.
xfconf-query -c xsettings \
  -p /Net/ThemeName --create -t string \
  -s Adwaita 2>/dev/null || \
xfconf-query -c xsettings \
  -p /Net/ThemeName -s Adwaita

xfconf-query -c xsettings \
  -p /Net/IconThemeName --create -t string \
  -s Adwaita 2>/dev/null || \
xfconf-query -c xsettings \
  -p /Net/IconThemeName -s Adwaita

# Add wallpaper choices to the native application menu.
for MODE in horizon morning midnight; do
    cat > "$APPDIR/life-wallpaper-$MODE.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LIFE Wallpaper — ${MODE^}
Comment=Switch LIFE Lite appearance
Exec=$BINDIR/life-wallpaper $MODE
Icon=preferences-desktop-wallpaper
Terminal=false
Categories=Settings;DesktopSettings;
EOF
done

# Create an XFCE appearance launcher.
cat > "$APPDIR/life-appearance.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=LIFE Appearance
Comment=Customize LIFE Lite desktop appearance
Exec=xfce4-appearance-settings
Icon=preferences-desktop-theme
Terminal=false
Categories=Settings;DesktopSettings;
EOF

# Refresh menu data and select the default wallpaper.
if command -v update-desktop-database >/dev/null; then
    update-desktop-database "$APPDIR" 2>/dev/null || true
fi

"$BINDIR/life-wallpaper" horizon

echo ""
echo "=================================="
echo "🍉 LIFE LITE M23 INSTALLED"
echo "=================================="
echo "Themes: Horizon, Morning, Midnight"
echo "GTK styling: LIFE Light"
echo "Appearance menu: Added"
echo "Desktop menu: Refreshed"
echo "Backup: $BACKUP"
echo ""
echo "Open noVNC port 6082."
echo "Existing Notes and project files preserved."
