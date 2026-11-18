import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))

import pytest

from layouts.engine import (
    load_preference,
    layout_plan,
    save_preference,
)
from layouts.render import render


@pytest.mark.parametrize(
    "edition,desktop",
    [
        ("life-lite", "xfce"),
        ("life-standard", "plasma"),
    ],
)
def test_flow_supported_by_both_editions(edition, desktop):
    plan = layout_plan(edition, "flow")
    assert plan["desktop"] == desktop
    assert plan["top_panel"]
    assert plan["dock"]


def test_unknown_layout_rejected():
    with pytest.raises(ValueError):
        layout_plan("life-lite", "unknown")


def test_unknown_edition_rejected():
    with pytest.raises(ValueError):
        layout_plan("unknown", "flow")


def test_preference_persistence(tmp_path):
    save_preference(tmp_path, "life-lite", "flow")
    assert load_preference(tmp_path) == {
        "edition": "life-lite",
        "layout": "flow",
        "version": 1,
    }


def test_no_preference_returns_none(tmp_path):
    assert load_preference(tmp_path) is None


def test_xfce_script():
    script = render("life-lite", "flow")
    assert "xfconf-query" in script
    assert "panel-1" in script
    assert "panel-2" in script


def test_plasma_script():
    script = render("life-standard", "flow")
    assert "new Panel()" in script
    assert 'top.location = "top"' in script
    assert 'dock.location = "bottom"' in script


def test_cli_preview():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/life_layout.py"),
            "preview",
            "--edition",
            "life-standard",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["desktop"] == "plasma"


def test_cli_select(tmp_path):
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/life_layout.py"),
            "select",
            "--edition",
            "life-lite",
            "--home",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert load_preference(tmp_path)["layout"] == "flow"
