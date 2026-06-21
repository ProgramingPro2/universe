"""Autostart desktop entry management."""

from __future__ import annotations

from universe.core.config import AppConfig
from universe.core.desktop_entry import build_exec
from universe.core.paths import autostart_dir, autostart_entry_path


def sync_autostart(config: AppConfig, remove: bool = False) -> None:
    path = autostart_entry_path(config.id)
    if remove or not config.autostart:
        if path.exists():
            path.unlink()
        return

    autostart_dir().mkdir(parents=True, exist_ok=True)
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={config.display_name()}",
        f"Exec={build_exec(config)}",
        f"Icon={config.icon_key()}",
        "Terminal=false",
        "X-GNOME-Autostart-enabled=true",
        f"X-Universe-AppId={config.id}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
