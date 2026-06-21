# Universe

Architecture and packaging notes for Universe AppImage Manager.

## Layout

- `src/universe/core/` - integration logic, config, AppImage parsing
- `src/universe/ui/` - GTK4/libadwaita GUI
- `data/` - desktop entries, MIME XML, icons
- `packaging/debian/` - `.deb` metadata

## Data flow

1. User double-clicks `.AppImage` -> `universe-open.desktop` -> `universe open`
2. If not integrated, GTK dialog offers integrate-and-run or run-once
3. Integration copies/moves to `~/Applications`, writes desktop entry and icon
4. Universe GUI reads `~/.config/universe/apps.json` and displays cards
