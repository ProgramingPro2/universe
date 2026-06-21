"""Build desktop entry Exec lines and write desktop files."""

from __future__ import annotations

from pathlib import Path

from universe.core.config import AppConfig


def build_exec(config: AppConfig) -> str:
    parts: list[str] = []
    for key, value in sorted(config.env_vars.items()):
        parts.append(f"{key}={value}")
    exec_prefix = "env " + " ".join(parts) + " " if parts else ""
    args = config.launch_args.strip()
    command = f"{exec_prefix}{config.appimage_path}"
    if args:
        command = f"{command} {args}"
    return command


def write_desktop_entry(config: AppConfig, desktop_path: Path) -> None:
    categories = config.categories or ["Utility"]
    keywords = config.keywords or ["AppImage"]
    icon = config.icon_key()
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={config.display_name()}",
        f"Exec={build_exec(config)}",
        f"Icon={icon}",
        "Terminal=false",
        f"Categories={';'.join(categories)};",
        f"Keywords={';'.join(keywords)};",
        "StartupNotify=true",
        f"X-Universe-AppId={config.id}",
    ]
    if config.version:
        lines.append(f"X-AppImage-Version={config.version}")
    desktop_path.parent.mkdir(parents=True, exist_ok=True)
    desktop_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
