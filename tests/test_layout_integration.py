import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))

from layouts.backup import backup_layout
from layouts.engine import load_preference


def test_xfce_backup(tmp_path):
    home = tmp_path / "home"
    config = (
        home
        / ".config/xfce4/xfconf/xfce-perchannel-xml"
        / "xfce4-panel.xml"
    )
    config.parent.mkdir(parents=True)
    config.write_text("<channel />")

    destination = backup_layout(home, "life-lite")

    assert (
        destination
        / ".config/xfce4/xfconf/xfce-perchannel-xml"
        / "xfce4-panel.xml"
    ).read_text() == "<channel />"

    assert config.read_text() == "<channel />"


def test_plasma_backup(tmp_path):
    home = tmp_path / "home"
    config = (
        home
        / ".config/plasma-org.kde.plasma.desktop-appletsrc"
    )
    config.parent.mkdir(parents=True)
    config.write_text("[Containments]\n")

    destination = backup_layout(home, "life-standard")

    assert (
        destination
        / ".config/plasma-org.kde.plasma.desktop-appletsrc"
    ).read_text() == "[Containments]\n"


def test_missing_configuration_is_safe(tmp_path):
    destination = backup_layout(tmp_path, "life-lite")
    manifest = json.loads(
        (destination / "manifest.json").read_text()
    )
    assert manifest["files"] == []


def test_cli_backup(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/life_layout.py"),
            "backup",
            "--edition",
            "life-lite",
            "--home",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Desktop backup created" in result.stdout


def test_backup_does_not_change_layout_preference(tmp_path):
    backup_layout(tmp_path, "life-lite")
    assert load_preference(tmp_path) is None


def test_both_editions_include_python():
    editions = json.loads(
        (ROOT / "iso/editions.json").read_text()
    )
    for edition in editions.values():
        assert "python" in edition["packages"]


def test_archiso_integration_code_present():
    code = (
        ROOT / "scripts/prepare_iso.py"
    ).read_text()
    assert "life-layout" in code
    assert "life_layout.py" in code


def test_prepare_iso_with_mock_releng(tmp_path):
    releng = tmp_path / "archiso" / "configs" / "releng"
    releng.mkdir(parents=True)

    (releng / "profiledef.sh").write_text(
        'iso_name="archlinux"\n'
    )
    (releng / "packages.x86_64").write_text(
        "base\nlinux\n"
    )

    output = tmp_path / "profile"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/prepare_iso.py"),
            "life-lite",
            "--archiso-root",
            str(tmp_path / "archiso"),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    launcher = output / "airootfs/usr/bin/life-layout"
    assert launcher.exists()
    assert launcher.stat().st_mode & 0o111

    assert (
        output
        / "airootfs/usr/share/lifeos/desktop/layouts/engine.py"
    ).exists()
