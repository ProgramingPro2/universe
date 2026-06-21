"""Tests for config storage."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universe.core.config import AppConfig, get_app, list_apps, remove_app, save_app
from universe.core.paths import apps_config_path


class ConfigTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "apps.json"
            with patch("universe.core.config.apps_config_path", return_value=config_path):
                with patch("universe.core.config.ensure_dirs"):
                    app = AppConfig(
                        id="test-app",
                        appimage_path="/tmp/test.AppImage",
                        name="Test App",
                        version="1.0",
                        launch_args="--flag",
                        env_vars={"FOO": "bar"},
                        autostart=True,
                        categories=["Utility"],
                        keywords=["test"],
                    )
                    save_app(app)
                    loaded = get_app("test-app")
                    self.assertIsNotNone(loaded)
                    self.assertEqual(loaded.display_name(), "Test App")
                    self.assertEqual(loaded.launch_args, "--flag")
                    self.assertEqual(loaded.env_vars["FOO"], "bar")
                    apps = list_apps()
                    self.assertEqual(len(apps), 1)
                    remove_app("test-app")
                    self.assertIsNone(get_app("test-app"))


if __name__ == "__main__":
    unittest.main()
