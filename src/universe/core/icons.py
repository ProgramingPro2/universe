"""Resolve icon files for integrated applications."""

from __future__ import annotations

import shutil
from pathlib import Path

from universe.core.config import AppConfig
from universe.core.paths import icon_path, icons_base_dir, scalable_icon_path


def bundled_fallback_icon_path() -> Path | None:
    candidates = [
        Path("/usr/share/icons/hicolor/scalable/apps/universe.svg"),
        Path(__file__).resolve().parents[2].parent / "data" / "icons" / "hicolor" / "scalable" / "apps" / "universe.svg",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def resolve_icon_file(config: AppConfig) -> Path | None:
    if config.custom_icon_path:
        custom = Path(config.custom_icon_path).expanduser()
        if custom.is_file():
            return custom

    for size in (256, 128, 64, 48, 32, 16):
        candidate = icon_path(config.id, size)
        if candidate.is_file():
            return candidate

    scalable = scalable_icon_path(config.id)
    if scalable.is_file():
        return scalable

    appimage = Path(config.appimage_path).expanduser()
    sidecar = appimage.parent / f".universe-icon-{config.id}.png"
    if sidecar.is_file():
        return sidecar

    return None


def install_fallback_icon(app_id: str) -> str:
    source = bundled_fallback_icon_path()
    icon_key = f"universe-{app_id}"
    if source is None:
        return icon_key

    dest = scalable_icon_path(app_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    ensure_icon_index()
    return icon_key


def ensure_icon_index() -> None:
    index = icons_base_dir() / "index.theme"
    if index.exists():
        return
    icons_base_dir().mkdir(parents=True, exist_ok=True)
    index.write_text(
        "[Icon Theme]\n"
        "Name=Universe\n"
        "Comment=Icons for Universe integrated apps\n"
        "Directories=scalable/apps,256x256/apps,128x128/apps,64x64/apps,48x48/apps,32x32/apps\n\n"
        "[scalable/apps]\n"
        "Size=256\n"
        "Type=Scalable\n"
        "MinSize=16\n"
        "MaxSize=512\n\n"
        "[256x256/apps]\n"
        "Size=256\n"
        "Type=Fixed\n\n"
        "[128x128/apps]\n"
        "Size=128\n"
        "Type=Fixed\n\n"
        "[64x64/apps]\n"
        "Size=64\n"
        "Type=Fixed\n\n"
        "[48x48/apps]\n"
        "Size=48\n"
        "Type=Fixed\n\n"
        "[32x32/apps]\n"
        "Size=32\n"
        "Type=Fixed\n",
        encoding="utf-8",
    )
