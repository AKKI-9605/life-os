#!/usr/bin/env python3
"""Validate LIFE OS edition definitions."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
editions = json.loads(
    (root / "iso" / "editions.json").read_text()
)

assert set(editions) == {"life-lite", "life-standard"}

for name, edition in editions.items():
    packages = edition["packages"]

    assert packages
    assert len(packages) == len(set(packages))
    assert "networkmanager" in packages
    assert "firefox" in packages
    assert edition["display_manager"] in packages

    print(f"PASS: {name} — {len(packages)} package entries")

print("LIFE OS edition definitions valid.")
