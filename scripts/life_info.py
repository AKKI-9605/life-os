#!/usr/bin/env python3
"""Display LIFE OS development information."""

import json
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "iso/life-lite-manifest.json"

def main():
    print("\n🍉 LIFE OS — Development Information")
    print("─" * 38)

    if CONFIG.exists():
        data = json.loads(CONFIG.read_text())
        print("Edition:", data.get("edition", "LIFE Lite"))
        print("Desktop:", data.get("desktop", "XFCE"))
        print("Milestone:", data.get("milestone", "51"))

    print("Architecture:", platform.machine())
    print("Development status: Active")
    print("Next goal: ISO boot verification")
    print("─" * 38)

if __name__ == "__main__":
    main()
