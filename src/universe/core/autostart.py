"""Autostart desktop entry management."""

from __future__ import annotations

from universe.core.config import AppConfig
from universe.core.desktop_entry import build_exec, write_desktop_file_lines
from universe.core.paths import autostart_dir, autostart_entry_path


def sync_autostart(config: AppConfig, remove: bool = False) -> None:
    path = autostart_entry_path(config.id)
    if remove or not config.autostart:
        if path.exists():
            path.unlink()
        return

    autostart_dir().mkdir(parents=True, exist_ok=True)
    lines = write_desktop_file_lines(
        name=config.display_name(),
        exec_line=build_exec(config),
        icon=config.icon_key(),
        app_id=config.id,
        autostart=True,
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
