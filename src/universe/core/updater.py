"""AppImage update helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from universe.core import appimage
from universe.core.config import AppConfig, get_app, save_app
from universe.core.integrator import refresh_integration


def check_update_info(app_id: str) -> str:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")
    path = Path(config.appimage_path)
    return appimage.read_update_info(path)


def replace_appimage(app_id: str, new_path: Path) -> AppConfig:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")

    new_path = new_path.resolve()
    if not appimage.is_appimage(new_path):
        raise ValueError(f"Not an AppImage: {new_path}")

    old_path = Path(config.appimage_path)
    backup = old_path.with_suffix(old_path.suffix + ".bak")
    if old_path.exists():
        shutil.move(str(old_path), str(backup))

    shutil.copy2(new_path, old_path)
    appimage.make_executable(old_path)

    metadata = appimage.extract_metadata(old_path)
    config.name = metadata.name
    config.version = metadata.version
    config.update_info = metadata.update_info
    if metadata.categories:
        config.categories = metadata.categories
    if metadata.keywords:
        config.keywords = metadata.keywords
    save_app(config)
    refresh_integration(app_id)

    if backup.exists():
        backup.unlink()

    return config


def update_with_tool(app_id: str) -> bool:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")

    updater = shutil.which("appimageupdatetool")
    if updater is None:
        return False

    path = Path(config.appimage_path)
    result = subprocess.run([updater, str(path)], check=False)
    if result.returncode != 0:
        return False

    metadata = appimage.extract_metadata(path)
    config.version = metadata.version
    config.update_info = metadata.update_info
    save_app(config)
    refresh_integration(app_id)
    return True
