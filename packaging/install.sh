#!/bin/sh
set -e

PREFIX="${PREFIX:-/usr}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STAGE_ROOT="$SCRIPT_DIR"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo $0"
  exit 1
fi

install -d "$PREFIX/lib/universe"
install -d "$PREFIX/bin"
install -d "$PREFIX/share/applications"
install -d "$PREFIX/share/mime/packages"
install -d "$PREFIX/share/icons/hicolor/scalable/apps"
install -d "$PREFIX/share/doc/universe"

cp -r "$STAGE_ROOT/usr/lib/universe/universe" "$PREFIX/lib/universe/"
install -m 755 "$STAGE_ROOT/usr/bin/universe" "$PREFIX/bin/universe"
install -m 644 "$STAGE_ROOT/usr/share/applications/io.universe.Universe.desktop" \
  "$PREFIX/share/applications/"
install -m 644 "$STAGE_ROOT/usr/share/applications/universe-open.desktop" \
  "$PREFIX/share/applications/"
install -m 644 "$STAGE_ROOT/usr/share/mime/packages/universe.xml" \
  "$PREFIX/share/mime/packages/"
install -m 644 "$STAGE_ROOT/usr/share/icons/hicolor/scalable/apps/universe.svg" \
  "$PREFIX/share/icons/hicolor/scalable/apps/"
if [ -d "$STAGE_ROOT/usr/share/doc/universe" ]; then
  cp -r "$STAGE_ROOT/usr/share/doc/universe/." "$PREFIX/share/doc/universe/"
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$PREFIX/share/icons/hicolor" 2>/dev/null || true
fi
if command -v update-mime-database >/dev/null 2>&1; then
  update-mime-database "$PREFIX/share/mime" 2>/dev/null || true
fi

echo "Universe installed to $PREFIX"
