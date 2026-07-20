"""Per-app settings window."""

from __future__ import annotations

import shutil
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from universe.core.config import get_app, save_app
from universe.core.integrator import refresh_integration, remove_integration
from universe.core.updater import check_update_info, replace_appimage, update_with_tool
from universe.ui.file_dialog import create_appimage_dialog


class AppSettingsWindow(Gtk.Window):
    def __init__(self, app_id: str, parent: Gtk.Window, on_changed: callable) -> None:
        super().__init__(transient_for=parent, modal=True)
        self._app_id = app_id
        self._on_changed = on_changed
        self._config = get_app(app_id)
        if self._config is None:
            raise ValueError(f"Unknown app: {app_id}")

        self.set_title(f"Settings - {self._config.display_name()}")
        self.set_default_size(480, 560)

        toolbar = Adw.HeaderBar()
        close_button = Gtk.Button(icon_name="window-close-symbolic")
        close_button.connect("clicked", lambda *_: self.close())
        toolbar.pack_end(close_button)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        self._name_entry = Adw.EntryRow(title="Display name")
        self._name_entry.set_text(self._config.custom_name)

        self._args_entry = Adw.EntryRow(title="Launch arguments")
        self._args_entry.set_text(self._config.launch_args)

        self._env_entry = Adw.EntryRow(title="Environment (KEY=VALUE, comma-separated)")
        env_text = ",".join(f"{k}={v}" for k, v in self._config.env_vars.items())
        self._env_entry.set_text(env_text)

        self._categories_entry = Adw.EntryRow(title="Categories (semicolon-separated)")
        self._categories_entry.set_text(";".join(self._config.categories))

        self._keywords_entry = Adw.EntryRow(title="Keywords (semicolon-separated)")
        self._keywords_entry.set_text(";".join(self._config.keywords))

        self._autostart_switch = Adw.SwitchRow(title="Autostart on login")
        self._autostart_switch.set_active(self._config.autostart)

        update_info = Gtk.Label(
            label=self._config.update_info or "No embedded update information",
            wrap=True,
        )
        update_info.add_css_class("dim-label")

        save_button = Gtk.Button(label="Save changes")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self._save)

        check_update_button = Gtk.Button(label="Refresh update info")
        check_update_button.connect("clicked", self._refresh_update_info)

        replace_button = Gtk.Button(label="Replace AppImage file...")
        replace_button.connect("clicked", self._replace_appimage)

        update_tool_button = Gtk.Button(label="Update with appimageupdatetool")
        update_tool_button.connect("clicked", self._update_with_tool)

        remove_button = Gtk.Button(label="Remove integration")
        remove_button.add_css_class("destructive-action")
        remove_button.connect("clicked", self._remove)

        content.append(self._name_entry)
        content.append(self._args_entry)
        content.append(self._env_entry)
        content.append(self._categories_entry)
        content.append(self._keywords_entry)
        content.append(self._autostart_switch)
        content.append(update_info)
        content.append(save_button)
        content.append(check_update_button)
        content.append(replace_button)
        content.append(update_tool_button)
        content.append(remove_button)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.append(toolbar)
        root.append(content)
        self.set_child(root)

    def _show_error(self, message: str, heading: str = "Error") -> None:
        dialog = Adw.MessageDialog(heading=heading, body=message, transient_for=self)
        dialog.add_response("ok", "OK")
        dialog.present()

    def _parse_env(self, raw: str) -> dict[str, str]:
        result: dict[str, str] = {}
        if not raw.strip():
            return result
        for part in raw.split(","):
            part = part.strip()
            if not part or "=" not in part:
                continue
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
        return result

    def _save(self, *_args: object) -> None:
        config = get_app(self._app_id)
        if config is None:
            self._show_error("App is no longer integrated.")
            return
        try:
            config.custom_name = self._name_entry.get_text().strip()
            config.launch_args = self._args_entry.get_text().strip()
            config.env_vars = self._parse_env(self._env_entry.get_text())
            config.categories = [
                c.strip() for c in self._categories_entry.get_text().split(";") if c.strip()
            ]
            config.keywords = [
                k.strip() for k in self._keywords_entry.get_text().split(";") if k.strip()
            ]
            config.autostart = self._autostart_switch.get_active()
            save_app(config)
            refresh_integration(self._app_id)
            self._on_changed()
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _refresh_update_info(self, *_args: object) -> None:
        try:
            info = check_update_info(self._app_id)
            config = get_app(self._app_id)
            if config is None:
                self._show_error("App is no longer integrated.")
                return
            config.update_info = info
            save_app(config)
            self._show_error(
                info or "No embedded update information found.",
                heading="Update info",
            )
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _replace_appimage(self, *_args: object) -> None:
        try:
            dialog = create_appimage_dialog("Select replacement AppImage")
            dialog.open(self, None, self._on_replace_selected)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            self._show_error(f"Could not open file chooser: {exc}")

    def _on_replace_selected(self, dialog: Gtk.FileDialog, result: object) -> None:
        try:
            file = dialog.open_finish(result)
        except Exception as exc:
            message = str(exc)
            if "dismissed" in message.lower() or "cancelled" in message.lower() or "canceled" in message.lower():
                return
            self._show_error(f"Could not open file: {exc}")
            return
        path = Path(file.get_path() or "")
        if not path.is_file():
            self._show_error("Selected file does not exist.")
            return
        try:
            replace_appimage(self._app_id, path)
            self._on_changed()
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _update_with_tool(self, *_args: object) -> None:
        if not shutil.which("appimageupdatetool"):
            self._show_error(
                "Install appimageupdatetool to use automatic updates.",
                heading="Updater not found",
            )
            return
        try:
            if update_with_tool(self._app_id):
                self._on_changed()
            else:
                self._show_error("appimageupdatetool did not report a successful update.")
        except (OSError, ValueError) as exc:
            self._show_error(str(exc))

    def _remove(self, *_args: object) -> None:
        dialog = Adw.MessageDialog(
            heading="Remove integration?",
            body="This removes shortcuts but keeps the AppImage file.",
            transient_for=self,
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("remove", "Remove")
        dialog.set_default_response("remove")
        dialog.set_close_response("cancel")

        def on_response(_dlg: Adw.MessageDialog, response: str) -> None:
            if response != "remove":
                return
            try:
                remove_integration(self._app_id)
                self._on_changed()
                self.close()
            except (OSError, ValueError) as exc:
                self._show_error(str(exc))

        dialog.connect("response", on_response)
        dialog.present()
