# Universe AppImage Manager

[![Build](https://github.com/ProgramingPro2/universe/actions/workflows/build.yml/badge.svg)](https://github.com/ProgramingPro2/universe/actions/workflows/build.yml)

Universe integrates AppImages into your Linux desktop and provides a GUI to run and configure them. It is a lightweight alternative to AppImageLauncher: double-click to integrate, manage apps from one window, without a heavy background daemon.

## Features

- Double-click an AppImage to integrate it (desktop shortcut, icon, menu entry)
- **Universe** manager window to browse integrated AppImages
- Per-app settings: display name, launch args, environment variables, autostart, categories, keywords
- Reads embedded AppImage update-info; optional updates via `appimageupdatetool`
- Manual AppImage file replacement from settings
- Works across major Linux desktops (XFCE, GNOME, KDE, Cinnamon, etc.)
- Packages for **amd64** and **arm64**: `.deb`, `.rpm`, and portable `.tar.gz`

## Screenshots

Add manager and open-dialog screenshots under [`docs/screenshots/`](docs/screenshots/) and embed them here before announcing publicly.

<!--
![Universe manager](docs/screenshots/manager.png)
![Open dialog](docs/screenshots/open-dialog.png)
-->

## Requirements

- Python 3.10+
- GTK 4 and libadwaita (`python3-gi`, `gir1.2-gtk-4.0`, `gir1.2-adw-1`, `libadwaita-1-0`)
- FUSE for type-2 AppImages: `libfuse2t64` (Ubuntu 24.04+) or `libfuse2` (older Debian/Ubuntu)
- `desktop-file-utils`

**Trust note:** Opening or integrating an AppImage may execute it (for example `--appimage-extract` / `--appimage-updateinfo`) to read metadata. Only integrate AppImages you trust.

Installing the package sets Universe as the default handler for AppImage MIME types.

## Install

Download the latest packages from [GitHub Releases](https://github.com/ProgramingPro2/universe/releases).

### Debian / Ubuntu (.deb)

```bash
sudo dpkg -i universe_0.1.1_amd64.deb   # or arm64
sudo apt-get install -f
```

### Fedora / RHEL (.rpm)

```bash
sudo rpm -i universe-0.1.1-1.x86_64.rpm   # or aarch64
```

### Portable tarball (.tar.gz)

```bash
tar -xzf universe_0.1.1_amd64.tar.gz
cd universe-0.1.1
sudo ./install.sh
```

## Build locally

```bash
make test
make deb-amd64          # dist/universe_0.1.1_amd64.deb
make deb-arm64          # dist/universe_0.1.1_arm64.deb
make deb-all            # both .deb packages

# With nfpm installed (deb + rpm + tar.gz):
make nfpm ARCH=amd64
make pack-all
```

## Development

```bash
make run          # open GUI with PYTHONPATH=src
make test         # run tests
```

CLI:

```bash
PYTHONPATH=src python3 -m universe list
PYTHONPATH=src python3 -m universe integrate /path/to/AppImage
PYTHONPATH=src python3 -m universe integrate-and-run /path/to/AppImage
PYTHONPATH=src python3 -m universe run <app-id>
PYTHONPATH=src python3 -m universe remove <app-id>
PYTHONPATH=src python3 -m universe open /path/to/AppImage
PYTHONPATH=src python3 -m universe gui
```

Integrated AppImages are stored in `~/Applications`. Configuration lives in `~/.config/universe/apps.json`.

## Remove AppImageLauncher

If AppImageLauncher is still installed:

```bash
systemctl --user stop appimagelauncherd.service
sudo apt purge -y appimagelauncher
sudo apt autoremove -y
rm -f ~/.config/appimagelauncher.cfg
```

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).

See also [CHANGELOG.md](CHANGELOG.md), [SECURITY.md](SECURITY.md), and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
