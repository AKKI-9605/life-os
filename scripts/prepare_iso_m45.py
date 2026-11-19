#!/usr/bin/env python3
"""Prepare LIFE Lite ISO with its real XFCE session."""

import argparse
import subprocess
import sys
from pathlib import Path

from life_m41_45 import finish_profile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("edition")
    parser.add_argument(
        "--archiso-root",
        type=Path,
        default=Path("/usr/share/archiso")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    output = args.output or (
        ROOT / "out/profiles" / args.edition
    )

    command = [
        sys.executable,
        str(ROOT / "scripts/prepare_iso_integrated.py"),
        args.edition,
        "--archiso-root",
        str(args.archiso_root),
        "--output",
        str(output),
    ]

    subprocess.run(command, check=True)

    if args.edition == "life-lite":
        finish_profile(output)

    print("LIFE OS ISO profile ready:", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
