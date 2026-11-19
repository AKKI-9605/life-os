#!/usr/bin/env python3
"""Prepare the ArchISO profile and integrate LIFE Lite assets."""

from pathlib import Path
import importlib.util
import inspect
import sys

from life_iso_m36_40 import copy_overlay

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/prepare_iso.py"

spec = importlib.util.spec_from_file_location(
    "life_original_prepare_iso", SOURCE
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

original_prepare = module.prepare


def integrated_prepare(*args, **kwargs):
    signature = inspect.signature(original_prepare)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()

    result = original_prepare(*args, **kwargs)

    edition = str(
        bound.arguments.get("edition_name", "")
    ).lower()

    destination = bound.arguments.get("destination")

    if destination is None:
        raise RuntimeError(
            "Original ISO preparer did not expose destination"
        )

    # Other editions retain their original preparation behavior.
    if "lite" in edition:
        copy_overlay(Path(destination))

    return result


module.prepare = integrated_prepare


if __name__ == "__main__":
    raise SystemExit(module.main())
