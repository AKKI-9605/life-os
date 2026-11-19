#!/usr/bin/env python3
"""LIFE OS M41–45: XFCE live-ISO boot integration."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "iso/overlays/life-lite"
EDITIONS = ROOT / "iso/editions.json"
WORKFLOW = ROOT / ".github/workflows/build-life-lite.yml"
WRAPPER = ROOT / "scripts/prepare_iso_m45.py"

EXTRA_PACKAGES = (
    "xorg-server",
    "xorg-xauth",
    "xf86-input-libinput",
    "mesa",
    "xfce4-session",
)


def write(relative, content, executable=False):
    path = OVERLAY / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    if executable:
        path.chmod(0o755)

    print("CREATED", path.relative_to(ROOT))


def configure_packages():
    data = json.loads(EDITIONS.read_text())

    lite = data["life-lite"]
    packages = lite["packages"]

    for package in EXTRA_PACKAGES:
        if package not in packages:
            packages.append(package)

    EDITIONS.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8"
    )

    print("XFCE graphics packages configured")


def build_live_setup():
    write(
        "usr/local/sbin/life-live-user-setup",
        """#!/usr/bin/env bash
set -euo pipefail

# Temporary user for the LIFE Lite live ISO.
# This is NOT a permanent installed-system account.

if ! getent group autologin >/dev/null; then
    groupadd --system autologin
fi

if ! id life >/dev/null 2>&1; then
    useradd \
        --create-home \
        --shell /bin/bash \
        --groups autologin \
        life
else
    usermod -aG autologin life
fi

# Ensure the live desktop has its own user home.
install -d -o life -g life /home/life

echo "LIFE Lite live user ready"
""",
        executable=True,
    )

    write(
        "usr/lib/systemd/system/life-live-user.service",
        """[Unit]
Description=LIFE Lite live-session user setup
Before=display-manager.service
After=systemd-user-sessions.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/life-live-user-setup
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
""",
    )

    write(
        "etc/systemd/system/lightdm.service.d/20-life-user.conf",
        """[Unit]
Requires=life-live-user.service
After=life-live-user.service
""",
    )

    write(
        "etc/lightdm/lightdm.conf.d/50-life-lite.conf",
        """# LIFE Lite LIVE IMAGE ONLY
# Permanent installations must use normal account setup.

[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=xfce
autologin-user=life
autologin-user-timeout=0
autologin-session=xfce
""",
    )

    write(
        "usr/share/xsessions/life-lite.desktop",
        """[Desktop Entry]
Name=LIFE Lite
Comment=LIFE OS XFCE desktop session
Exec=startxfce4
TryExec=startxfce4
Type=Application
DesktopNames=XFCE
""",
    )

    print("Live-session configuration created")


def ensure_link(path, target):
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_symlink():
        if path.readlink().as_posix() == target:
            return
        # This is an isolated generated ISO profile,
        # not the running Codespace.
        path.unlink()
    elif path.exists():
        raise RuntimeError(
            f"Refusing to replace regular file: {path}"
        )

    path.symlink_to(target)


def finish_profile(profile):
    """Configure startup links in a generated ArchISO profile."""

    profile = Path(profile).resolve()

    if not (profile / "profiledef.sh").is_file():
        raise RuntimeError("Invalid ArchISO profile")

    systemd = profile / "airootfs/etc/systemd/system"

    ensure_link(
        systemd / "display-manager.service",
        "/usr/lib/systemd/system/lightdm.service"
    )

    ensure_link(
        systemd / "default.target",
        "/usr/lib/systemd/system/graphical.target"
    )

    ensure_link(
        systemd / "multi-user.target.wants/life-live-user.service",
        "/usr/lib/systemd/system/life-live-user.service"
    )

    # Check that the earlier integration was actually performed.
    rootfs = profile / "airootfs"

    required = [
        "usr/local/bin/life-lite-first-login",
        "usr/local/sbin/life-live-user-setup",
        "etc/lightdm/lightdm.conf.d/50-life-lite.conf",
        "usr/lib/systemd/system/life-live-user.service",
        "usr/share/backgrounds/lifeos/life-horizon.svg",
        "etc/xdg/autostart/life-lite-first-login.desktop",
    ]

    for relative in required:
        if not (rootfs / relative).is_file():
            raise RuntimeError(
                f"Missing generated ISO file: {relative}"
            )

    packages = (
        profile / "packages.x86_64"
    ).read_text().splitlines()

    for package in (
        "lightdm",
        "lightdm-gtk-greeter",
        "xorg-server",
        "xfce4-session",
    ):
        if package not in packages:
            raise RuntimeError(
                f"Missing ISO package: {package}"
            )

    print("PASS: LIFE Lite graphical startup profile")


def create_wrapper():
    WRAPPER.write_text(
        '''#!/usr/bin/env python3
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
''',
        encoding="utf-8"
    )

    print("Created M45 ISO preparation wrapper")


def update_workflow():
    original = WORKFLOW.read_text(encoding="utf-8")

    previous = "scripts/prepare_iso_integrated.py"
    current = "scripts/prepare_iso_m45.py"

    if current in original:
        print("Workflow already updated")
        return

    if original.count(previous) != 1:
        raise RuntimeError(
            "Unexpected workflow structure; not modifying it"
        )

    WORKFLOW.write_text(
        original.replace(previous, current, 1),
        encoding="utf-8"
    )

    print("ISO build workflow updated")


def validate():
    print("\n===== M41–45 VALIDATION =====")

    data = json.loads(EDITIONS.read_text())

    packages = data["life-lite"]["packages"]

    for package in EXTRA_PACKAGES:
        assert package in packages

    print("PASS: Graphics package definitions")

    for relative in [
        "usr/local/sbin/life-live-user-setup",
        "usr/lib/systemd/system/life-live-user.service",
        "etc/lightdm/lightdm.conf.d/50-life-lite.conf",
        "usr/share/xsessions/life-lite.desktop",
    ]:
        assert (OVERLAY / relative).is_file()

    print("PASS: Live-session files")

    setup = OVERLAY / "usr/local/sbin/life-live-user-setup"

    subprocess.run(
        ["bash", "-n", str(setup)],
        check=True
    )

    subprocess.run(
        [sys.executable, "-m", "py_compile", str(WRAPPER)],
        check=True
    )

    print("PASS: Script syntax")

    # Mock ArchISO releng profile.
    # This tests integration without installing ArchISO
    # on the Debian Codespace.
    with tempfile.TemporaryDirectory(
        prefix="life-m45-"
    ) as tmp:
        temporary = Path(tmp)

        releng = temporary / "archiso/configs/releng"
        releng.mkdir(parents=True)

        (releng / "profiledef.sh").write_text(
            'iso_name="archlinux"\\n'
        )

        (releng / "packages.x86_64").write_text(
            "base\\nlinux\\n"
        )

        (releng / "airootfs/etc").mkdir(
            parents=True
        )

        output = temporary / "life-lite-profile"

        subprocess.run(
            [
                sys.executable,
                str(WRAPPER),
                "life-lite",
                "--archiso-root",
                str(temporary / "archiso"),
                "--output",
                str(output),
            ],
            check=True
        )

        finish_profile(output)

        systemd = output / (
            "airootfs/etc/systemd/system"
        )

        assert (
            systemd / "display-manager.service"
        ).is_symlink()

        assert (
            systemd / "default.target"
        ).is_symlink()

        print("PASS: LightDM activation links")
        print("PASS: XFCE live-session profile")
        print("PASS: Repeatable configuration")

    assert "scripts/prepare_iso_m45.py" in (
        WORKFLOW.read_text()
    )

    print("PASS: GitHub Actions preparation command")

    print("\nALL M41–45 LOCAL TESTS PASSED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-only",
        action="store_true"
    )
    args = parser.parse_args()

    if not args.verify_only:
        configure_packages()
        build_live_setup()
        create_wrapper()
        update_workflow()

    validate()


if __name__ == "__main__":
    main()
