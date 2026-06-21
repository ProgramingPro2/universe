"""Per-app configuration persisted in ~/.config/universe/apps.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from universe.core.paths import apps_config_path, ensure_dirs


@dataclass
class AppConfig:
    id: str
    appimage_path: str
    name: str = ""
    version: str = ""
    icon_name: str = ""
    custom_name: str = ""
    custom_icon_path: str = ""
    launch_args: str = ""
    env_vars: dict[str, str] = field(default_factory=dict)
    autostart: bool = False
    categories: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    update_info: str = ""
    integrated_at: str = ""

    def display_name(self) -> str:
        return self.custom_name or self.name or self.id

    def icon_key(self) -> str:
        if self.custom_icon_path:
            return self.custom_icon_path
        if self.icon_name:
            return self.icon_name
        return f"universe-{self.id}"


def _load_raw() -> dict[str, Any]:
    path = apps_config_path()
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _save_raw(data: dict[str, Any]) -> None:
    ensure_dirs()
    path = apps_config_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def list_apps() -> list[AppConfig]:
    raw = _load_raw()
    apps: list[AppConfig] = []
    for app_id, payload in sorted(raw.items()):
        apps.append(_from_dict(app_id, payload))
    return apps


def get_app(app_id: str) -> AppConfig | None:
    raw = _load_raw()
    if app_id not in raw:
        return None
    return _from_dict(app_id, raw[app_id])


def save_app(config: AppConfig) -> None:
    raw = _load_raw()
    raw[config.id] = _to_dict(config)
    _save_raw(raw)


def remove_app(app_id: str) -> None:
    raw = _load_raw()
    if app_id in raw:
        del raw[app_id]
        _save_raw(raw)


def find_by_path(path: Path) -> AppConfig | None:
    resolved = str(path.resolve())
    for app in list_apps():
        if app.appimage_path == resolved:
            return app
    return None


def _from_dict(app_id: str, payload: dict[str, Any]) -> AppConfig:
    return AppConfig(
        id=app_id,
        appimage_path=payload.get("appimage_path", ""),
        name=payload.get("name", ""),
        version=payload.get("version", ""),
        icon_name=payload.get("icon_name", ""),
        custom_name=payload.get("custom_name", ""),
        custom_icon_path=payload.get("custom_icon_path", ""),
        launch_args=payload.get("launch_args", ""),
        env_vars=dict(payload.get("env_vars", {})),
        autostart=bool(payload.get("autostart", False)),
        categories=list(payload.get("categories", [])),
        keywords=list(payload.get("keywords", [])),
        update_info=payload.get("update_info", ""),
        integrated_at=payload.get("integrated_at", ""),
    )


def _to_dict(config: AppConfig) -> dict[str, Any]:
    data = asdict(config)
    del data["id"]
    return data
