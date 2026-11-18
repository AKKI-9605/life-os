#!/usr/bin/env python3
"""LIFE OS layout switcher CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))

from layouts.engine import (
    LAYOUTS,
    load_preference,
    layout_plan,
    save_preference,
)
from layouts.render import render


def main():
    parser = argparse.ArgumentParser(
        description="LIFE OS Desktop Layout Manager"
    )

    parser.add_argument(
        "command",
        choices=["list", "preview", "generate", "select", "current"],
    )

    parser.add_argument(
        "--edition",
        choices=["life-lite", "life-standard"],
        default="life-lite",
    )

    parser.add_argument(
        "--layout",
        default="flow",
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
    )

    args = parser.parse_args()

    if args.command == "list":
        print(json.dumps(LAYOUTS, indent=2))
        return

    if args.command == "current":
        print(json.dumps(load_preference(args.home), indent=2))
        return

    if args.command == "preview":
        print(
            json.dumps(
                layout_plan(args.edition, args.layout),
                indent=2,
            )
        )
        return

    if args.command == "generate":
        output = render(args.edition, args.layout)

        if args.output:
            args.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            args.output.write_text(output)
            print(f"Generated: {args.output}")
        else:
            print(output)

        return

    if args.command == "select":
        path = save_preference(
            args.home,
            args.edition,
            args.layout,
        )
        print(f"Saved LIFE layout preference: {path}")
        print("Desktop panels have not been changed.")


if __name__ == "__main__":
    main()
