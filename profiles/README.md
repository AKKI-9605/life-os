# LIFE OS — Archiso Profiles

LIFE OS will use Archiso to generate bootable installation media.

## Editions

- **LIFE Lite:** XFCE-based environment for basic computing and lower-resource hardware.
- **LIFE Standard:** KDE Plasma-based environment for everyday student use.
- **LIFE Gaming:** a future optional gaming-focused package configuration based on LIFE Standard; not a separate launch profile yet.

## Build architecture

The first release targets x86_64 systems. Profiles must be copied from the official Archiso `releng` profile on a supported Arch Linux build host. This preserves upstream bootloader and live-system configuration before LIFE OS customizations are introduced.

Do not manually create empty bootloader configuration directories or copy profile files from unrelated tutorials. No profile is build-ready until it is complete and validated on a supported Arch Linux build host.

## Planned profile contents

- `airootfs/` — files installed into the live environment
- `efiboot/`, `syslinux/`, `grub/` — upstream boot configuration, retained as appropriate
- `packages.x86_64` — packages included in the image
- `pacman.conf` — package repository configuration
- `profiledef.sh` — Archiso profile metadata
