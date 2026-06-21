"""Discover AppImage files on disk."""

from __future__ import annotations

from pathlib import Path

from universe.core import appimage
from universe.core.config import list_apps
from universe.core.paths import applications_dir, home


def _integrated_paths() -> set[str]:
    return {app.appimage_path for app in list_apps()}


def discover_appimages() -> list[Path]:
    integrated = _integrated_paths()
    found: list[Path] = []

    search_dirs = [applications_dir(), home() / "Downloads", home() / "Desktop"]
    patterns = ("*.AppImage", "*.appimage", "*.APP", "*.APPImage")

    seen: set[str] = set()
    for directory in search_dirs:
        if not directory.is_dir():
            continue
        for pattern in patterns:
            for path in directory.glob(pattern):
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                if resolved in integrated:
                    continue
                if appimage.is_appimage(path):
                    found.append(path)

    return sorted(found, key=lambda p: p.name.lower())
