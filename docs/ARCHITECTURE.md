# LIFE OS — Architecture

## Foundation

- Target architecture: x86_64 (64-bit Intel and AMD)
- Base distribution: Arch Linux
- Live image tooling: Archiso
- Package management: Pacman
- Optional application source: Flatpak

## Desktop editions

### LIFE Standard

KDE Plasma is the planned full desktop environment for everyday student use.

### LIFE Lite

XFCE is the planned lightweight desktop environment for lower-resource computers.

### LIFE Gaming

A future optional package configuration based on LIFE Standard. It is not a separate build target until the standard edition is stable.

## System components

| Component | Technology |
|---|---|
| Base system | Arch Linux |
| ISO generation | Archiso |
| Package management | Pacman |
| Optional app distribution | Flatpak |
| Companion applications | Python / PySide6 |
| Configuration scripts | Bash |
| Local application data | SQLite |
| Tests | pytest |

## Repository architecture

The existing app/ directory contains the current companion-app prototype. The planned applications/ directory is a future home for separately scoped LIFE applications. Do not duplicate or move the working prototype until the application boundaries and migration plan are agreed.

The profiles/ directory will contain edition-specific Archiso profiles. Profiles should be derived from the official Archiso releng profile on an Arch Linux build host, preserving its boot and live-system configuration before customization.

## Architecture priorities

- Modular editions with shared configuration where practical
- Minimal background services
- Reliable and understandable updates
- Hardware compatibility validated through testing
- Offline-friendly student applications
- Reproducible image builds
- Clear separation between app development and OS-image experiments

## Build-host requirement

Archiso builds should be performed on a supported Arch Linux environment. macOS is suitable for editing code and managing GitHub, but it is not the native Archiso build host.
