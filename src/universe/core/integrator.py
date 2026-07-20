"""Desktop integration: shortcuts, icons, and system database updates."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from universe.core import appimage
from universe.core.autostart import sync_autostart
from universe.core.config import (
    AppConfig,
    allocate_unique_id,
    find_by_path,
    get_app,
    remove_app,
    save_app,
)
from universe.core.desktop_entry import write_desktop_entry
from universe.core.icons import ensure_icon_index, install_fallback_icon, resolve_icon_file
from universe.core.paths import (
    applications_dir,
    desktop_entry_path,
    ensure_dirs,
    icon_path,
    icons_base_dir,
    scalable_icon_path,
)


def _run_system_update() -> None:
    desktop_db = shutil.which("update-desktop-database")
    if desktop_db:
        subprocess.run(
            [desktop_db, str(Path.home() / ".local" / "share" / "applications")],
            check=False,
        )
    icon_cache = shutil.which("gtk-update-icon-cache")
    if icon_cache and icons_base_dir().exists():
        subprocess.run([icon_cache, "-f", "-t", str(icons_base_dir())], check=False)


def _install_icon(app_id: str, source: Path | None, size: int) -> str:
    if source is None or not source.is_file():
        return install_fallback_icon(app_id)

    target_size = size if size in (16, 24, 32, 48, 64, 128, 256, 512) else 256
    dest = icon_path(app_id, target_size)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    ensure_icon_index()
    return f"universe-{app_id}"


def refresh_integration(app_id: str) -> None:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")
    if resolve_icon_file(config) is None:
        install_fallback_icon(app_id)
    write_desktop_entry(config, desktop_entry_path(app_id))
    sync_autostart(config)
    _run_system_update()


def integrate(
    source_path: Path,
    move_into_apps: bool = True,
    run_after: bool = False,
) -> AppConfig:
    ensure_dirs()
    source_path = source_path.resolve()
    if not appimage.is_appimage(source_path):
        raise ValueError(f"Not an AppImage: {source_path}")

    existing = find_by_path(source_path)
    if existing:
        refresh_integration(existing.id)
        if run_after:
            run_app(existing.id)
        return existing

    metadata = appimage.extract_metadata(source_path)
    apps_dir = applications_dir()
    target_path = apps_dir / source_path.name

    if move_into_apps and source_path.parent != apps_dir:
        if target_path.exists():
            target_path = apps_dir / f"{metadata.app_id}-{source_path.name}"
        shutil.move(str(source_path), str(target_path))
        source_path = target_path
    elif source_path.parent != apps_dir:
        if not target_path.exists():
            shutil.copy2(source_path, target_path)
        source_path = target_path

    appimage.make_executable(source_path)
    app_id = allocate_unique_id(metadata.app_id, str(source_path))
    icon_name = _install_icon(app_id, metadata.icon_source, metadata.icon_size)

    config = AppConfig(
        id=app_id,
        appimage_path=str(source_path),
        name=metadata.name,
        version=metadata.version,
        icon_name=icon_name,
        categories=metadata.categories,
        keywords=metadata.keywords,
        update_info=metadata.update_info,
        integrated_at=appimage.utc_now_iso(),
    )
    save_app(config)
    write_desktop_entry(config, desktop_entry_path(config.id))
    sync_autostart(config)
    _run_system_update()

    if run_after:
        run_app(config.id)

    return config


def remove_integration(app_id: str) -> None:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")

    desktop = desktop_entry_path(app_id)
    if desktop.exists():
        desktop.unlink()

    for size in (16, 24, 32, 48, 64, 128, 256, 512):
        icon = icon_path(app_id, size)
        if icon.exists():
            icon.unlink()

    scalable = scalable_icon_path(app_id)
    if scalable.exists():
        scalable.unlink()

    sync_autostart(config, remove=True)
    remove_app(app_id)
    _run_system_update()


def run_app(app_id: str) -> subprocess.Popen[bytes]:
    config = get_app(app_id)
    if config is None:
        raise ValueError(f"Unknown app id: {app_id}")

    app_path = Path(config.appimage_path)
    if not app_path.is_file():
        raise FileNotFoundError(f"AppImage not found: {app_path}")

    env = os.environ.copy()
    for key, value in config.env_vars.items():
        env[key] = value

    args = [str(app_path)]
    if config.launch_args.strip():
        args.extend(config.launch_args.strip().split())

    return subprocess.Popen(args, env=env)
