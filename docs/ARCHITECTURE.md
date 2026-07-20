# Universe

Architecture and packaging notes for Universe AppImage Manager.

## Layout

- `src/universe/core/` — integration logic, config, AppImage parsing, desktop entries
- `src/universe/ui/` — GTK4/libadwaita GUI
- `data/` — desktop entries, MIME XML, icons
- `packaging/` — launcher, debian scripts, nfpm config, install.sh
- `tests/` — unittest suite

## Data flow

1. User double-clicks `.AppImage` → `universe-open.desktop` → `universe open`
2. If not integrated, GTK dialog offers integrate-and-run or run-once
3. Integration copies/moves to `~/Applications`, writes desktop entry and icon
4. Universe GUI reads `~/.config/universe/apps.json` and displays cards

## Config

- Path: `~/.config/universe/apps.json`
- Corrupt JSON is backed up to `apps.json.bak` and the app starts with an empty list
- App IDs are unique; collisions get a `-2`, `-3`, … suffix

## Desktop entries

`desktop_entry.py` builds both menu and autostart `.desktop` files:

- Control characters stripped from string fields
- `Exec` paths and env values quoted for spaces/special characters
- Invalid env keys dropped

## Trust

Metadata extraction may execute the AppImage. See [SECURITY.md](../SECURITY.md).

## Packaging

`make stage` copies sources into `build/stage` (without `__pycache__`). `make deb` / `make nfpm` produce `.deb`, `.rpm`, and `.tar.gz` for the current `VERSION` in the Makefile.
