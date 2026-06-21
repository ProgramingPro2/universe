"""Tests for desktop entry generation."""

import unittest

from universe.core.config import AppConfig
from universe.core.desktop_entry import build_exec


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


if __name__ == "__main__":
    unittest.main()
