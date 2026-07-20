"""AppImage parsing and metadata extraction."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass
class AppImageMetadata:
    path: Path
    app_id: str
    name: str
    version: str
    icon_source: Path | None
    icon_size: int
    exec_line: str
    categories: list[str]
    keywords: list[str]
    update_info: str


def sanitize_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    slug = slug.strip("-")
    return slug or "appimage"


def _has_elf_magic(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(4) == b"\x7fELF"
    except OSError:
        return False


def is_appimage(path: Path) -> bool:
    if not path.is_file():
        return False
    name = path.name.lower()
    if name.endswith(".appimage"):
        return True
    # Bare ".app" is too broad (unrelated formats); require ELF magic.
    if name.endswith(".app"):
        return _has_elf_magic(path)
    return False


def make_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | 0o111)


def read_update_info(path: Path) -> str:
    try:
        result = subprocess.run(
            [str(path), "--appimage-updateinfo"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _parse_desktop_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def _find_desktop_file(root: Path) -> Path | None:
    candidates = list(root.glob("*.desktop"))
    if candidates:
        return candidates[0]
    app_dir = root / "usr" / "share" / "applications"
    if app_dir.is_dir():
        app_candidates = list(app_dir.glob("*.desktop"))
        if app_candidates:
            return app_candidates[0]
    for desktop in root.rglob("*.desktop"):
        return desktop
    return None


def _find_best_icon(root: Path, icon_hint: str) -> tuple[Path | None, int]:
    if icon_hint:
        for candidate in root.rglob(icon_hint):
            if candidate.is_file():
                return candidate, _icon_dimension(candidate)
        for ext in (".png", ".svg", ".xpm"):
            candidate = root / icon_hint
            if candidate.with_suffix(ext).exists():
                path = candidate.with_suffix(ext)
                return path, _icon_dimension(path)
            for found in root.rglob(f"{icon_hint}{ext}"):
                return found, _icon_dimension(found)

    pngs = [p for p in root.rglob("*.png") if "icon" in p.name.lower() or "apps" in str(p)]
    if not pngs:
        pngs = list(root.rglob("*.png"))
    if not pngs:
        return None, 0

    best = max(pngs, key=_icon_dimension)
    return best, _icon_dimension(best)


def _icon_dimension(path: Path) -> int:
    if path.suffix.lower() != ".png":
        return 256
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
        if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            return max(width, height)
    except OSError:
        pass
    return 256


def extract_metadata(path: Path) -> AppImageMetadata:
    path = path.resolve()
    if not is_appimage(path):
        raise ValueError(f"Not an AppImage: {path}")

    make_executable(path)
    update_info = read_update_info(path)

    with tempfile.TemporaryDirectory(prefix="universe-extract-") as tmp:
        work_dir = Path(tmp)
        result = subprocess.run(
            [str(path), "--appimage-extract"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if result.returncode != 0:
            stem = path.stem
            app_id = sanitize_id(stem)
            return AppImageMetadata(
                path=path,
                app_id=app_id,
                name=stem,
                version="",
                icon_source=None,
                icon_size=0,
                exec_line=str(path),
                categories=["Utility"],
                keywords=["AppImage"],
                update_info=update_info,
            )

        root = work_dir / "squashfs-root"
        desktop_path = _find_desktop_file(root)
        if desktop_path is None:
            stem = path.stem
            return AppImageMetadata(
                path=path,
                app_id=sanitize_id(stem),
                name=stem,
                version="",
                icon_source=None,
                icon_size=0,
                exec_line=str(path),
                categories=["Utility"],
                keywords=["AppImage"],
                update_info=update_info,
            )

        desktop = _parse_desktop_file(desktop_path)
        name = desktop.get("Name", path.stem)
        version = desktop.get("X-AppImage-Version", desktop.get("Version", ""))
        exec_line = desktop.get("Exec", str(path)).replace("%u", "%U").replace("%U", "")
        icon_hint = desktop.get("Icon", "")
        categories = [
            c.strip()
            for c in desktop.get("Categories", "Utility").split(";")
            if c.strip()
        ]
        keywords = [
            k.strip()
            for k in desktop.get("Keywords", "AppImage").split(";")
            if k.strip()
        ]

        icon_source, icon_size = _find_best_icon(root, icon_hint)
        app_id = sanitize_id(desktop.get("X-AppImage-Name", name))

        if icon_source and icon_source.is_file() and icon_source.suffix.lower() == ".png":
            persistent_icon = path.parent / f".universe-icon-{app_id}.png"
            shutil.copy2(icon_source, persistent_icon)
            icon_source = persistent_icon
            icon_size = _icon_dimension(persistent_icon)
        else:
            icon_source = None
            icon_size = 0

        return AppImageMetadata(
            path=path,
            app_id=app_id,
            name=name,
            version=version,
            icon_source=icon_source,
            icon_size=icon_size,
            exec_line=exec_line,
            categories=categories,
            keywords=keywords,
            update_info=update_info,
        )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
