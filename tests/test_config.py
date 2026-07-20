"""Tests for config storage."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universe.core.config import (
    AppConfig,
    allocate_unique_id,
    get_app,
    list_apps,
    remove_app,
    save_app,
    take_config_warning,
)


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

    def test_corrupt_json_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "apps.json"
            config_path.write_text("{not-json", encoding="utf-8")
            with patch("universe.core.config.apps_config_path", return_value=config_path):
                with patch("universe.core.config.ensure_dirs"):
                    take_config_warning()
                    apps = list_apps()
                    self.assertEqual(apps, [])
                    warning = take_config_warning()
                    self.assertIsNotNone(warning)
                    self.assertTrue(config_path.with_suffix(".json.bak").exists())

    def test_allocate_unique_id_on_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "apps.json"
            with patch("universe.core.config.apps_config_path", return_value=config_path):
                with patch("universe.core.config.ensure_dirs"):
                    save_app(
                        AppConfig(
                            id="demo",
                            appimage_path="/tmp/one.AppImage",
                            name="One",
                        )
                    )
                    self.assertEqual(
                        allocate_unique_id("demo", "/tmp/two.AppImage"),
                        "demo-2",
                    )
                    self.assertEqual(
                        allocate_unique_id("demo", "/tmp/one.AppImage"),
                        "demo",
                    )


if __name__ == "__main__":
    unittest.main()
