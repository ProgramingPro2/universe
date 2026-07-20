"""Tests for desktop entry generation."""

import tempfile
import unittest
from pathlib import Path

from universe.core.config import AppConfig
from universe.core.desktop_entry import build_exec, write_desktop_entry


class DesktopEntryTests(unittest.TestCase):
    def test_build_exec_with_env_and_args(self) -> None:
        config = AppConfig(
            id="demo",
            appimage_path="/home/user/Applications/demo.AppImage",
            env_vars={"FOO": "bar", "BAZ": "qux"},
            launch_args="--verbose",
        )
        exec_line = build_exec(config)
        self.assertIn("env", exec_line)
        self.assertIn("FOO=bar", exec_line)
        self.assertIn("BAZ=qux", exec_line)
        self.assertIn("--verbose", exec_line)
        self.assertIn("demo.AppImage", exec_line)

    def test_build_exec_quotes_spaces_in_path_and_env(self) -> None:
        config = AppConfig(
            id="demo",
            appimage_path="/home/user/My Apps/demo.AppImage",
            env_vars={"A": "1 2"},
            launch_args='--flag "hello world"',
        )
        exec_line = build_exec(config)
        self.assertIn('"/home/user/My Apps/demo.AppImage"', exec_line)
        self.assertIn('A="1 2"', exec_line)
        self.assertIn('"hello world"', exec_line)

    def test_name_newline_injection_stripped(self) -> None:
        config = AppConfig(
            id="evil",
            appimage_path="/tmp/demo.AppImage",
            custom_name="Evil\nExec=/bin/true",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evil.desktop"
            write_desktop_entry(config, path)
            text = path.read_text(encoding="utf-8")
            exec_keys = [line for line in text.splitlines() if line.startswith("Exec=")]
            self.assertEqual(len(exec_keys), 1)
            name_line = next(line for line in text.splitlines() if line.startswith("Name="))
            self.assertEqual(name_line, "Name=EvilExec=/bin/true")
            self.assertFalse(any(line.startswith("Exec=/bin/true") for line in text.splitlines()))

    def test_invalid_env_keys_dropped(self) -> None:
        config = AppConfig(
            id="demo",
            appimage_path="/tmp/demo.AppImage",
            env_vars={"BAD=KEY": "x", "GOOD": "y"},
        )
        exec_line = build_exec(config)
        self.assertIn("GOOD=y", exec_line)
        self.assertNotIn("BAD=KEY", exec_line)


if __name__ == "__main__":
    unittest.main()
