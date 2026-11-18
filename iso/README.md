# LIFE OS ISO infrastructure

Target architecture: x86-64.

Editions:
- LIFE Lite: XFCE
- LIFE Standard: KDE Plasma

The profiles are derived from Archiso's official releng profile.

On an Arch Linux build host with archiso installed:

    python scripts/prepare_iso.py life-lite
    python scripts/prepare_iso.py life-standard

This only prepares build profiles. It does not create bootable
images or configure automatic graphical login.

Remaining work:
- Configure graphical sessions and live user accounts.
- Configure branding, permissions and services.
- Integrate LIFE applications.
- Build images using mkarchiso.
- Test booting, networking, installation and persistence.
- Validate hardware requirements.
