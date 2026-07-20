# Changelog

## 0.1.1 — 2026-07-20

First public release candidate after hardening.

### Security and robustness

- Sanitize desktop-entry and autostart fields; quote `Exec` paths and env values (blocks newline injection and broken paths with spaces)
- Recover from corrupt `~/.config/universe/apps.json` (backup to `.bak`, empty list, user-visible warning)
- Disambiguate colliding app IDs instead of silently overwriting
- Treat `*.app` as AppImage only when the file has ELF magic; `*.AppImage` still accepted by extension

### Packaging and docs

- Version bump to 0.1.1
- Maintainer/homepage set to ProgramingPro2
- FUSE dependency: `libfuse2t64 | libfuse2`
- Strip `__pycache__` from staged packages
- README install paths match real artifact names
- Add SECURITY.md and architecture trust notes

### UI

- Surface replace/update/integrate failures in dialogs instead of silent catches

## 0.1.0

Internal packaging and CI scaffolding (not published as a GitHub Release).
