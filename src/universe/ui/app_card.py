"""App card widgets for the main grid."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk

from universe.core.config import AppConfig
from universe.core.icons import bundled_fallback_icon_path, resolve_icon_file


def _make_icon_image(config: AppConfig | None, path: Path | None, pixel_size: int = 64) -> Gtk.Image:
    icon_file = None
    if config is not None:
        icon_file = resolve_icon_file(config)
    if icon_file is None and path is not None:
        sidecar = path.parent / f".universe-icon-{path.stem}.png"
        if sidecar.is_file():
            icon_file = sidecar

    if icon_file is not None:
        image = Gtk.Image.new_from_file(str(icon_file))
    else:
        fallback = bundled_fallback_icon_path()
        if fallback is not None:
            image = Gtk.Image.new_from_file(str(fallback))
        else:
            image = Gtk.Image.new_from_icon_name("application-x-executable")
    image.set_pixel_size(pixel_size)
    return image


class AppCard(Gtk.Box):
    def __init__(
        self,
        config: AppConfig,
        on_run: Callable[[str], None],
        on_settings: Callable[[str], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add_css_class("card")
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_size_request(180, 200)

        self._config = config
        self._on_run = on_run
        self._on_settings = on_settings

        icon = _make_icon_image(config, None)

        title = Gtk.Label(label=config.display_name())
        title.add_css_class("title-4")
        title.set_wrap(True)

        version_text = config.version or ""
        version = Gtk.Label(label=version_text)
        version.add_css_class("dim-label")

        run_button = Gtk.Button(label="Run")
        run_button.connect("clicked", self._handle_run)

        settings_button = Gtk.Button(icon_name="preferences-system-symbolic")
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self._handle_settings)

        button_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_row.set_halign(Gtk.Align.CENTER)
        button_row.append(run_button)
        button_row.append(settings_button)

        self.append(icon)
        self.append(title)
        if version_text:
            self.append(version)
        self.append(button_row)

    def _handle_run(self, _button: Gtk.Button) -> None:
        self._on_run(self._config.id)

    def _handle_settings(self, _button: Gtk.Button) -> None:
        self._on_settings(self._config.id)


class DiscoverCard(Gtk.Box):
    def __init__(self, path: Path, on_integrate: Callable[[Path], None]) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add_css_class("card")
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_size_request(180, 200)

        self._path = path
        self._on_integrate = on_integrate

        icon = _make_icon_image(None, path)

        title = Gtk.Label(label=path.stem)
        title.add_css_class("title-4")
        title.set_wrap(True)

        status = Gtk.Label(label="Not integrated")
        status.add_css_class("dim-label")

        integrate_button = Gtk.Button(label="Integrate")
        integrate_button.add_css_class("suggested-action")
        integrate_button.connect("clicked", self._handle_integrate)

        self.append(icon)
        self.append(title)
        self.append(status)
        self.append(integrate_button)

    def _handle_integrate(self, _button: Gtk.Button) -> None:
        self._on_integrate(self._path)
