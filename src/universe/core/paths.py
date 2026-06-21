"""Filesystem paths used by Universe."""

from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    return Path(os.path.expanduser("~"))


def applications_dir() -> Path:
    return home() / "Applications"


def config_dir() -> Path:
    return home() / ".config" / "universe"


def apps_config_path() -> Path:
    return config_dir() / "apps.json"


def desktop_entries_dir() -> Path:
    return home() / ".local" / "share" / "applications"


def icons_base_dir() -> Path:
    return home() / ".local" / "share" / "icons" / "hicolor"


def autostart_dir() -> Path:
    return home() / ".config" / "autostart"


def desktop_entry_path(app_id: str) -> Path:
    return desktop_entries_dir() / f"universe-{app_id}.desktop"


def autostart_entry_path(app_id: str) -> Path:
    return autostart_dir() / f"universe-{app_id}.desktop"


def icon_path(app_id: str, size: int) -> Path:
    return icons_base_dir() / f"{size}x{size}" / "apps" / f"universe-{app_id}.png"


def scalable_icon_path(app_id: str) -> Path:
    return icons_base_dir() / "scalable" / "apps" / f"universe-{app_id}.svg"


def ensure_dirs() -> None:
    applications_dir().mkdir(parents=True, exist_ok=True)
    config_dir().mkdir(parents=True, exist_ok=True)
    desktop_entries_dir().mkdir(parents=True, exist_ok=True)
    autostart_dir().mkdir(parents=True, exist_ok=True)
