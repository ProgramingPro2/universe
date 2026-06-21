"""Shared Gtk.FileDialog helpers for AppImage file selection."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk

from universe.core.paths import applications_dir, home


def _appimage_filter() -> Gtk.FileFilter:
    filter_appimage = Gtk.FileFilter()
    filter_appimage.set_name("AppImage files")
    for pattern in ("*.AppImage", "*.appimage", "*.APP", "*.APPImage"):
        filter_appimage.add_pattern(pattern)
    for suffix in ("AppImage", "appimage", "APP"):
        filter_appimage.add_suffix(suffix)
    filter_appimage.add_mime_type("application/vnd.appimage")
    filter_appimage.add_mime_type("application/x-iso9660-appimage")
    return filter_appimage


def _all_files_filter() -> Gtk.FileFilter:
    filter_all = Gtk.FileFilter()
    filter_all.set_name("All files")
    filter_all.add_pattern("*")
    return filter_all


def build_file_filters() -> tuple[Gio.ListStore, Gtk.FileFilter]:
    app_filter = _appimage_filter()
    all_filter = _all_files_filter()
    store = Gio.ListStore.new(Gtk.FileFilter)
    store.append(app_filter)
    store.append(all_filter)
    return store, app_filter


def configure_appimage_dialog(dialog: Gtk.FileDialog) -> Gtk.FileFilter:
    store, app_filter = build_file_filters()
    dialog.set_filters(store)
    dialog.set_default_filter(app_filter)
    return app_filter


def default_appimage_folder() -> Gio.File:
    apps = applications_dir()
    if apps.is_dir():
        return Gio.File.new_for_path(str(apps))
    downloads = home() / "Downloads"
    if downloads.is_dir():
        return Gio.File.new_for_path(str(downloads))
    return Gio.File.new_for_path(str(home()))


def create_appimage_dialog(title: str) -> Gtk.FileDialog:
    dialog = Gtk.FileDialog(title=title)
    configure_appimage_dialog(dialog)
    dialog.set_initial_folder(default_appimage_folder())
    return dialog
