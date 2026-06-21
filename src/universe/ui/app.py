"""GTK application entry point."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from universe.ui.main_window import UniverseMainWindow


class UniverseApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id="io.universe.Universe")

    def do_activate(self) -> None:
        window = self.props.active_window
        if window is None:
            window = UniverseMainWindow(application=self)
        window.present()


def run_gui() -> int:
    app = UniverseApplication()
    return app.run(None)
