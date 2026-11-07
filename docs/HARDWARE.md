# LIFE OS — Hardware Targets

These are initial design targets, not verified minimum requirements. Do not advertise them as supported specifications until measured on physical hardware.

| Resource | Lite | Standard | Gaming |
|---|---:|---:|---:|
| RAM | 2 GB experimental | 4 GB target | 8 GB+ target |
| Storage | 12 GB experimental | 32 GB+ target | 64 GB+ target |
| CPU | x86_64 | x86_64 | x86_64 |
| Desktop | XFCE | KDE Plasma | KDE Plasma |

## LIFE Lite priorities

- Basic web browsing
- Notes and documents
- Lecture playback
- Low background memory usage

## LIFE Standard priorities

- Student productivity
- Everyday multitasking
- Multimedia
- General-purpose applications

## LIFE Gaming priorities

- Steam availability
- Proton compatibility
- Minecraft compatibility information
- Graphics driver guidance

Game compatibility depends on the individual game, graphics hardware, drivers, and anti-cheat support.

## Validation plan

Before publishing hardware requirements, record:

- RAM usage after a clean boot
- Installed storage footprint
- Boot time and shutdown behavior
- Idle CPU usage and background services
- Live-session stability
- Wi-Fi, audio, graphics, suspend, and input-device compatibility

All requirements must be validated on physical hardware before release.
