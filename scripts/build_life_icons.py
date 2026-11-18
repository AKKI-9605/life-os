"""Generate original, scalable LIFE OS interface icons."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "desktop/assets/icons"
OUTPUT.mkdir(parents=True, exist_ok=True)

ICONS = {
    "files": """
        <path d="M4 8V6a2 2 0 0 1 2-2h5l3 3h6a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2z"/>
        <path d="M3 11h18"/>
    """,
    "notes": """
        <rect x="5" y="3" width="14" height="18" rx="3"/>
        <path d="M9 8h6M9 12h6M9 16h4"/>
    """,
    "appearance": """
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/>
    """,
    "music": """
        <path d="M9 18V5l12-2v13"/>
        <ellipse cx="6" cy="18" rx="3" ry="2"/>
        <ellipse cx="18" cy="16" rx="3" ry="2"/>
    """,
    "pictures": """
        <rect x="3" y="4" width="18" height="16" rx="3"/>
        <circle cx="8" cy="9" r="1.5"/>
        <path d="M4 17l5-5 4 4 3-3 5 5"/>
    """,
    "calendar": """
        <rect x="3" y="5" width="18" height="16" rx="3"/>
        <path d="M7 3v4M17 3v4M3 10h18M8 14h2M14 14h2M8 18h2"/>
    """,
    "terminal": """
        <rect x="3" y="4" width="18" height="16" rx="3"/>
        <path d="M7 9l3 3-3 3M12 16h5"/>
    """,
    "settings": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 2l2 2 3-.3.7 3L21 9l-1 3 1 3-3.3 2.3-.7 3-3-.3-2 2-2-2-3 .3-.7-3L3 15l1-3-1-3 3.3-2.3.7-3 3 .3z"/>
    """,
    "launcher": """
        <rect x="3" y="3" width="7" height="7" rx="2"/>
        <rect x="14" y="3" width="7" height="7" rx="2"/>
        <rect x="3" y="14" width="7" height="7" rx="2"/>
        <rect x="14" y="14" width="7" height="7" rx="2"/>
    """,
    "home": """
        <path d="M3 11l9-8 9 8v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>
        <path d="M9 21v-8h6v8"/>
    """,
}

COLORS = {
    "light": "#527F9D",
    "dark": "#BEDDF0",
}

for theme, color in COLORS.items():
    folder = OUTPUT / theme
    folder.mkdir(parents=True, exist_ok=True)

    for name, paths in ICONS.items():
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 24 24" width="64" height="64"
fill="none" stroke="{color}" stroke-width="1.7"
stroke-linecap="round" stroke-linejoin="round">
{paths}
</svg>
"""
        (folder / f"{name}.svg").write_text(svg)

print(f"Generated {len(ICONS)} icons in 2 themes.")
