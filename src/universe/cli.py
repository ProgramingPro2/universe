"""Universe command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from universe.core import appimage
from universe.core.config import find_by_path, list_apps, take_config_warning
from universe.core.integrator import integrate, remove_integration, run_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="universe", description="Universe AppImage Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    integrate_parser = sub.add_parser("integrate", help="Integrate an AppImage into the system")
    integrate_parser.add_argument("path", type=Path)
    integrate_parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy into ~/Applications instead of moving",
    )

    integrate_run_parser = sub.add_parser(
        "integrate-and-run",
        help="Integrate an AppImage and launch it",
    )
    integrate_run_parser.add_argument("path", type=Path)
    integrate_run_parser.add_argument("--copy", action="store_true")

    sub.add_parser("list", help="List integrated AppImages")

    remove_parser = sub.add_parser("remove", help="Remove an integrated AppImage")
    remove_parser.add_argument("id")

    run_parser = sub.add_parser("run", help="Run an integrated AppImage")
    run_parser.add_argument("id")

    open_parser = sub.add_parser("open", help="Open an AppImage (integrate dialog if needed)")
    open_parser.add_argument("path", type=Path)

    sub.add_parser("gui", help="Open the Universe manager window")

    return parser


def cmd_list() -> None:
    apps = list_apps()
    warning = take_config_warning()
    if warning:
        print(f"Warning: {warning}", file=sys.stderr)
    if not apps:
        print("No integrated AppImages.")
        return
    for app in apps:
        version = f" ({app.version})" if app.version else ""
        print(f"{app.id}: {app.display_name()}{version} -> {app.appimage_path}")


def cmd_integrate(path: Path, copy: bool, run_after: bool) -> int:
    try:
        config = integrate(path, move_into_apps=not copy, run_after=run_after)
        print(f"Integrated: {config.display_name()} [{config.id}]")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_remove(app_id: str) -> int:
    try:
        remove_integration(app_id)
        print(f"Removed: {app_id}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_run(app_id: str) -> int:
    try:
        run_app(app_id)
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_open(path: Path) -> int:
    path = path.resolve()
    if not appimage.is_appimage(path):
        print(f"Error: Not an AppImage: {path}", file=sys.stderr)
        return 1

    existing = find_by_path(path)
    if existing:
        return cmd_run(existing.id)

    from universe.ui.open_dialog import run_open_dialog

    return run_open_dialog(path)


def cmd_gui() -> int:
    from universe.ui.app import run_gui

    return run_gui()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        cmd_list()
        return 0
    if args.command == "integrate":
        return cmd_integrate(args.path, args.copy, run_after=False)
    if args.command == "integrate-and-run":
        return cmd_integrate(args.path, args.copy, run_after=True)
    if args.command == "remove":
        return cmd_remove(args.id)
    if args.command == "run":
        return cmd_run(args.id)
    if args.command == "open":
        return cmd_open(args.path)
    if args.command == "gui":
        return cmd_gui()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
