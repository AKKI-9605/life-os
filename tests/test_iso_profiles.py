import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_editions_exist():
    data = json.loads(
        (ROOT / "iso" / "editions.json").read_text()
    )
    assert set(data) == {"life-lite", "life-standard"}


def test_desktop_packages():
    data = json.loads(
        (ROOT / "iso" / "editions.json").read_text()
    )
    assert "xfce4" in data["life-lite"]["packages"]
    assert "plasma-meta" in data["life-standard"]["packages"]


def test_package_lists_are_unique():
    data = json.loads(
        (ROOT / "iso" / "editions.json").read_text()
    )
    for edition in data.values():
        packages = edition["packages"]
        assert len(packages) == len(set(packages))
