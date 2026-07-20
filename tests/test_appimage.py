"""Tests for AppImage helpers."""

import tempfile
import unittest
from pathlib import Path

from universe.core.appimage import is_appimage, sanitize_id


class AppImageTests(unittest.TestCase):
    def test_sanitize_id(self) -> None:
        self.assertEqual(sanitize_id("My Cool App!"), "my-cool-app")
        self.assertEqual(sanitize_id("---"), "appimage")

    def test_is_appimage_by_name(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".AppImage") as handle:
            path = Path(handle.name)
            self.assertTrue(is_appimage(path))
        self.assertFalse(is_appimage(Path("foo.bin")))

    def test_is_appimage_rejects_plain_app_without_elf(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".app") as handle:
            path = Path(handle.name)
            handle.write(b"not-elf")
            handle.flush()
            self.assertFalse(is_appimage(path))

    def test_is_appimage_accepts_app_with_elf_magic(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".app") as handle:
            path = Path(handle.name)
            handle.write(b"\x7fELF" + b"\x00" * 16)
            handle.flush()
            self.assertTrue(is_appimage(path))


if __name__ == "__main__":
    unittest.main()
