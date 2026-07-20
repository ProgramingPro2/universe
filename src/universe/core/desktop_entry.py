"""Build desktop entry Exec lines and write desktop files."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

from universe.core.config import AppConfig

_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitize_desktop_value(value: str) -> str:
    """Remove control characters that would break .desktop key lines."""
    return _CONTROL_RE.sub("", value).strip()


def _quote_exec_token(token: str) -> str:
    """Quote a single Exec argument for desktop-entry Exec keys."""
    if not token:
        return '""'
    if re.search(r'[\s"\\$`]', token):
        escaped = token.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
        return f'"{escaped}"'
    return token


def build_exec(config: AppConfig) -> str:
    parts: list[str] = []
    for key, value in sorted(config.env_vars.items()):
        clean_key = sanitize_desktop_value(key)
        clean_value = sanitize_desktop_value(value)
        if not clean_key or "=" in clean_key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", clean_key):
            continue
        parts.append(f"{clean_key}={_quote_exec_token(clean_value)}")

    exec_prefix = "env " + " ".join(parts) + " " if parts else ""
    path = sanitize_desktop_value(config.appimage_path)
    command = f"{exec_prefix}{_quote_exec_token(path)}"
    args = sanitize_desktop_value(config.launch_args)
    if args:
        # Preserve user-provided argv splitting, then re-quote each token.
        try:
            arg_tokens = shlex.split(args, posix=True)
        except ValueError:
            arg_tokens = args.split()
        quoted_args = " ".join(_quote_exec_token(token) for token in arg_tokens if token)
        if quoted_args:
            command = f"{command} {quoted_args}"
    return command


def _sanitize_list(values: list[str], fallback: list[str]) -> list[str]:
    cleaned = [sanitize_desktop_value(item) for item in values]
    cleaned = [item for item in cleaned if item and ";" not in item]
    return cleaned or list(fallback)


def write_desktop_file_lines(
    *,
    name: str,
    exec_line: str,
    icon: str,
    app_id: str,
    categories: list[str] | None = None,
    keywords: list[str] | None = None,
    version: str = "",
    autostart: bool = False,
) -> list[str]:
    safe_name = sanitize_desktop_value(name) or app_id
    safe_icon = sanitize_desktop_value(icon) or f"universe-{app_id}"
    cats = _sanitize_list(categories or [], ["Utility"])
    keys = _sanitize_list(keywords or [], ["AppImage"])
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={safe_name}",
        f"Exec={exec_line}",
        f"Icon={safe_icon}",
        "Terminal=false",
    ]
    if not autostart:
        lines.append(f"Categories={';'.join(cats)};")
        lines.append(f"Keywords={';'.join(keys)};")
        lines.append("StartupNotify=true")
    else:
        lines.append("X-GNOME-Autostart-enabled=true")
    lines.append(f"X-Universe-AppId={sanitize_desktop_value(app_id)}")
    if version and not autostart:
        lines.append(f"X-AppImage-Version={sanitize_desktop_value(version)}")
    return lines


def write_desktop_entry(config: AppConfig, desktop_path: Path) -> None:
    lines = write_desktop_file_lines(
        name=config.display_name(),
        exec_line=build_exec(config),
        icon=config.icon_key(),
        app_id=config.id,
        categories=config.categories,
        keywords=config.keywords,
        version=config.version,
        autostart=False,
    )
    desktop_path.parent.mkdir(parents=True, exist_ok=True)
    desktop_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
