# Universe AppImage Manager

[![Build](https://github.com/jpearce/universe/actions/workflows/build.yml/badge.svg)](https://github.com/jpearce/universe/actions/workflows/build.yml)

Universe integrates AppImages into your Linux desktop and provides a GUI to run and configure them.

## Features

- Double-click an AppImage to integrate it (desktop shortcut, icon, menu entry)
- **Universe** manager window to browse integrated AppImages
- Per-app settings: display name, launch args, environment variables, autostart, categories, keywords
- Update checking and manual AppImage replacement
- Works across major Linux desktops (XFCE, GNOME, KDE, Cinnamon, etc.)
- Packages for **amd64** and **arm64**: `.deb`, `.rpm`, and portable `.tar.gz`

## Requirements

- Python 3.10+
- GTK 4 and libadwaita (`python3-gi`, `gir1.2-gtk-4.0`, `gir1.2-adw-1`, `libadwaita-1-0`)
- `libfuse2` for type-2 AppImages
- `desktop-file-utils`

## Install

Download the latest build from [GitHub Actions artifacts](https://github.com/jpearce/universe/actions) or [Releases](https://github.com/jpearce/universe/releases).

### Debian / Ubuntu (.deb)

```bash
sudo dpkg -i dist/universe_0.1.0_amd64.deb   # or arm64
sudo apt-get install -f
```

### Fedora / RHEL (.rpm)

```bash
sudo rpm -i dist/universe_0.1.0_amd64.rpm   # or arm64
```

### Portable tarball (.tar.gz)

```bash
tar -xzf universe_0.1.0_amd64.tar.gz
cd universe_0.1.0_amd64
sudo ./install.sh
```

## Build locally

```bash
make test
make deb-amd64          # dist/universe_0.1.0_amd64.deb
make deb-arm64          # dist/universe_0.1.0_arm64.deb
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
