"""Dialog shown when opening an unintegrated AppImage."""

from __future__ import annotations

import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from universe.core import appimage
from universe.core.integrator import integrate


def run_open_dialog(path: Path) -> int:
    path = path.resolve()
    app = Adw.Application(application_id="io.universe.OpenDialog")

    exit_code = 0

    def on_activate(application: Adw.Application) -> None:
        nonlocal exit_code
        metadata = appimage.extract_metadata(path)

        dialog = Adw.MessageDialog(
            heading="Integrate AppImage?",
            body=f"Do you want to integrate {metadata.name} into your system?",
            transient_for=None,
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("run-once", "Run Once")
        dialog.add_response("integrate", "Integrate and Run")
        dialog.set_default_response("integrate")
        dialog.set_close_response("cancel")

        def on_response(_dialog: Adw.MessageDialog, response: str) -> None:
            nonlocal exit_code
            if response == "integrate":
                try:
                    config = integrate(path, move_into_apps=True, run_after=True)
                    print(f"Integrated: {config.display_name()}")
                except (OSError, ValueError) as exc:
                    exit_code = 1
                    print(f"Error: {exc}")
            elif response == "run-once":
                appimage.make_executable(path)
                subprocess.Popen([str(path)])
            application.quit()

        dialog.connect("response", on_response)
        dialog.present()

    app.connect("activate", on_activate)
    app.run(None)
    return exit_code
