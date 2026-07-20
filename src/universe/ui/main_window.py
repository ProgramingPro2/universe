"""Main Universe manager window."""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from universe.core import appimage
from universe.core.config import take_config_warning
from universe.core.discover import discover_appimages
from universe.core.integrator import integrate, run_app
from universe.ui.app_card import AppCard, DiscoverCard
from universe.ui.file_dialog import create_appimage_dialog
from universe.ui.settings_dialog import AppSettingsWindow


class UniverseMainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.set_title("Universe")
        self.set_default_size(900, 600)

        header = Adw.HeaderBar()
        add_button = Gtk.Button(label="Add AppImage")
        add_button.connect("clicked", self._add_appimage)
        header.pack_start(add_button)

        self._integrated_flow = Gtk.FlowBox()
        self._integrated_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self._integrated_flow.set_homogeneous(True)
        self._integrated_flow.set_max_children_per_line(4)
        self._integrated_flow.set_min_children_per_line(2)

        self._discovered_flow = Gtk.FlowBox()
        self._discovered_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self._discovered_flow.set_homogeneous(True)
        self._discovered_flow.set_max_children_per_line(4)
        self._discovered_flow.set_min_children_per_line(2)

        integrated_scrolled = Gtk.ScrolledWindow()
        integrated_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        integrated_scrolled.set_min_content_height(220)
        integrated_scrolled.set_child(self._integrated_flow)

        discovered_scrolled = Gtk.ScrolledWindow()
        discovered_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        discovered_scrolled.set_min_content_height(220)
        discovered_scrolled.set_child(self._discovered_flow)

        self._integrated_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        integrated_label = Gtk.Label(label="Integrated")
        integrated_label.add_css_class("title-3")
        integrated_label.set_halign(Gtk.Align.START)
        self._integrated_section.append(integrated_label)
        self._integrated_section.append(integrated_scrolled)

        self._discovered_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        discovered_label = Gtk.Label(label="Discovered on disk")
        discovered_label.add_css_class("title-3")
        discovered_label.set_halign(Gtk.Align.START)
        self._discovered_section.append(discovered_label)
        self._discovered_section.append(discovered_scrolled)

        self._content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self._content_box.set_margin_top(12)
        self._content_box.set_margin_bottom(12)
        self._content_box.set_margin_start(12)
        self._content_box.set_margin_end(12)
        self._content_box.append(self._integrated_section)
        self._content_box.append(self._discovered_section)

        self._empty_label = Gtk.Label(
            label="No AppImages found yet.\nAdd one with the button above or place files in ~/Applications.",
            justify=Gtk.Justification.CENTER,
        )
        self._empty_label.add_css_class("dim-label")
        self._empty_label.set_margin_top(48)

        self._stack = Gtk.Stack()
        self._stack.add_named(self._content_box, "content")
        self._stack.add_named(self._empty_label, "empty")

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.append(header)
        root.append(self._stack)
        self.set_content(root)

        self._reload()

    def _clear_flow(self, flow: Gtk.FlowBox) -> None:
        while child := flow.get_first_child():
            flow.remove(child)

    def _reload(self) -> None:
        from universe.core.config import list_apps

        self._clear_flow(self._integrated_flow)
        self._clear_flow(self._discovered_flow)

        apps = list_apps()
        warning = take_config_warning()
        discovered = discover_appimages()

        for config in apps:
            card = AppCard(config, self._handle_run, self._handle_settings)
            self._integrated_flow.append(card)

        for path in discovered:
            card = DiscoverCard(path, self._handle_integrate)
            self._discovered_flow.append(card)

        has_content = bool(apps) or bool(discovered)
        self._stack.set_visible_child_name("content" if has_content else "empty")
        self._integrated_section.set_visible(bool(apps))
        self._discovered_section.set_visible(bool(discovered))

        if warning:
            self._show_error(warning, heading="Configuration recovery")

    def _handle_run(self, app_id: str) -> None:
        try:
            run_app(app_id)
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _handle_integrate(self, path: Path) -> None:
        try:
            integrate(path, move_into_apps=True, run_after=False)
            self._reload()
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _handle_settings(self, app_id: str) -> None:
        try:
            window = AppSettingsWindow(app_id, self, self._reload)
            window.present()
        except ValueError as exc:
            self._show_error(str(exc))

    def _add_appimage(self, *_args: object) -> None:
        try:
            dialog = create_appimage_dialog("Select AppImage")
            dialog.open(self, None, self._on_file_selected)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            self._show_error(f"Could not open file chooser: {exc}")

    def _on_file_selected(self, dialog: Gtk.FileDialog, result: object) -> None:
        try:
            file = dialog.open_finish(result)
        except Exception as exc:
            # GLib.Error on cancel — ignore cancellations, show other failures.
            message = str(exc)
            if "dismissed" in message.lower() or "cancelled" in message.lower() or "canceled" in message.lower():
                return
            self._show_error(f"Could not open file: {exc}")
            return
        path = Path(file.get_path() or "")
        if not appimage.is_appimage(path):
            self._show_error("Selected file is not an AppImage.")
            return
        self._handle_integrate(path)

    def _show_error(self, message: str, heading: str = "Error") -> None:
        dialog = Adw.MessageDialog(heading=heading, body=message, transient_for=self)
        dialog.add_response("ok", "OK")
        dialog.present()
