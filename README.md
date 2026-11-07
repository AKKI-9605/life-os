# LIFE OS

**A student-first Linux distribution built for learning, creating, and playing.**

LIFE OS is an Arch-based Linux project exploring a simple, approachable desktop that combines the visual clarity of macOS with the familiarity of Windows. The goal is to make capable Linux computing feel comfortable on everyday Intel and AMD x86-64 laptops, including older and lower-spec machines.

> **Project status:** Early development / foundation stage. LIFE OS is not yet a bootable distribution. The repository currently establishes the project direction and a first desktop-app prototype.

## Vision

- **Student-first:** a calm home for notes, classes, planning, files, and study resources.
- **Approachable:** familiar navigation, sensible defaults, and clear onboarding.
- **Lightweight:** offer a full desktop and a lighter edition for older hardware.
- **Useful offline:** core notes and library features should work without an account or network.
- **Gaming-friendly:** make supported Linux games and launchers easy to discover without promising universal compatibility.
- **Open and transparent:** documented decisions, reproducible builds, tests, and public milestones.

## Planned platform

| Area | Initial direction |
|---|---|
| Base | Arch Linux |
| Desktop | KDE Plasma (standard edition) |
| Lightweight edition | XFCE, evaluated separately |
| Installer / live image | archiso first; installer experience later |
| Package management | Pacman, with Flatpak as an optional app source |
| Student companion | Python + PySide6 |
| Local data | SQLite |
| Tests | pytest |

These are project choices to validate, not claims that all components are already integrated.

## LIFE student companion

The first software milestone is a desktop companion with these planned areas:

- **Home** — a simple overview and quick actions
- **Notes** — local-first notes
- **Classes** — subjects, lecture links, and class resources
- **Planner** — assignments and upcoming work
- **Library** — saved PDFs and learning resources
- **Dev** — coding shortcuts and developer resources
- **Hub** — curated apps, games, and useful links

## Hardware goals

The initial compatibility target is 64-bit Intel/AMD x86-64 hardware. The project will measure real memory and disk use before publishing minimum requirements. A 4 GB RAM / 12 GB storage target is an aspiration for a lightweight install, not a verified requirement; a 2 GB profile remains an experiment.

## Repository layout

```text
life-os/
├── app/                 # LIFE companion application
├── docs/                # Architecture and development notes
├── packaging/           # Early image/build configuration
├── scripts/             # Developer and validation helpers
├── tests/               # Automated tests
├── pyproject.toml       # Python project configuration
└── README.md
```

## Getting started

The app prototype targets Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m lifeos
```

If PySide6 is unavailable on your platform, install the dependencies in a supported Python environment before running the app.

## Development principles

1. Build and test the companion app before integrating it into an OS image.
2. Keep user data local by default and document where it is stored.
3. Avoid background services and telemetry unless there is a clear, documented need.
4. Test on low-spec hardware before making performance claims.
5. Keep the standard and lightweight desktop choices separate until measured.

## Roadmap

- [x] Create the project repository and define the direction
- [ ] v0.1 — runnable LIFE companion shell and local database foundation
- [ ] v0.2 — notes, subjects, and planner workflows
- [ ] v0.3 — accessibility, packaging, and automated test coverage
- [ ] v0.5 — reproducible archiso live-image experiment
- [ ] v0.8 — hardware testing, installer evaluation, and documentation
- [ ] v1.0 — first public, tested release

## Contributing

Early feedback is welcome. Please open an issue for bugs, hardware reports, feature ideas, or design proposals. Large changes should be discussed before implementation.

## License

No license has been selected yet. Until one is added, all rights are reserved by the repository owner.
