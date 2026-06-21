VERSION := 0.1.0
ARCH ?= amd64
PKG_NAME := universe
DEB_FILE := dist/$(PKG_NAME)_$(VERSION)_$(ARCH).deb
BUILD_ROOT := build/debian/$(PKG_NAME)_$(VERSION)_$(ARCH)
STAGE_ROOT := build/stage
PYTHON := /usr/bin/python3
NFPM_ARCH := $(ARCH)

.PHONY: all stage deb deb-amd64 deb-arm64 deb-all nfpm pack-all clean test install-dev run

all: deb-amd64

stage:
	rm -rf "$(STAGE_ROOT)"
	mkdir -p "$(STAGE_ROOT)/usr/lib/universe"
	mkdir -p "$(STAGE_ROOT)/usr/bin"
	mkdir -p "$(STAGE_ROOT)/usr/share/applications"
	mkdir -p "$(STAGE_ROOT)/usr/share/mime/packages"
	mkdir -p "$(STAGE_ROOT)/usr/share/icons/hicolor/scalable/apps"
	cp -r src/universe "$(STAGE_ROOT)/usr/lib/universe/"
	cp packaging/universe-launcher.py "$(STAGE_ROOT)/usr/bin/universe"
	chmod 755 "$(STAGE_ROOT)/usr/bin/universe"
	cp data/applications/io.universe.Universe.desktop "$(STAGE_ROOT)/usr/share/applications/"
	cp data/applications/universe-open.desktop "$(STAGE_ROOT)/usr/share/applications/"
	cp data/mime/universe.xml "$(STAGE_ROOT)/usr/share/mime/packages/"
	cp data/icons/hicolor/scalable/apps/universe.svg "$(STAGE_ROOT)/usr/share/icons/hicolor/scalable/apps/"

deb: stage
	rm -rf "$(BUILD_ROOT)"
	mkdir -p "$(BUILD_ROOT)/DEBIAN"
	cp -r "$(STAGE_ROOT)/usr" "$(BUILD_ROOT)/"
	sed 's/@ARCH@/$(ARCH)/' packaging/debian/control.in > "$(BUILD_ROOT)/DEBIAN/control"
	cp packaging/debian/postinst "$(BUILD_ROOT)/DEBIAN/postinst"
	cp packaging/debian/postrm "$(BUILD_ROOT)/DEBIAN/postrm"
	chmod 755 "$(BUILD_ROOT)/DEBIAN/postinst" "$(BUILD_ROOT)/DEBIAN/postrm"
	mkdir -p dist
	fakeroot dpkg-deb --build "$(BUILD_ROOT)" "$(DEB_FILE)"
	@echo "Built $(DEB_FILE)"

deb-amd64:
	$(MAKE) deb ARCH=amd64

deb-arm64:
	$(MAKE) deb ARCH=arm64

deb-all: deb-amd64 deb-arm64

nfpm: stage
	mkdir -p dist build
	sed 's/^arch:.*/arch: $(ARCH)/' packaging/nfpm.yaml > build/nfpm.yaml
	nfpm package -f build/nfpm.yaml -p deb -t dist/
	nfpm package -f build/nfpm.yaml -p rpm -t dist/
	$(MAKE) tarball ARCH=$(ARCH)

tarball: stage
	rm -rf build/tarball
	mkdir -p build/tarball/universe-$(VERSION)
	cp packaging/install.sh build/tarball/universe-$(VERSION)/
	chmod 755 build/tarball/universe-$(VERSION)/install.sh
	cp -r build/stage/usr build/tarball/universe-$(VERSION)/
	tar -czf dist/universe_$(VERSION)_$(ARCH).tar.gz -C build/tarball universe-$(VERSION)

pack-all: deb-all
	$(MAKE) nfpm ARCH=amd64
	$(MAKE) nfpm ARCH=arm64

clean:
	rm -rf build dist

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -q

install-dev:
	PYTHONPATH=src $(PYTHON) -m pip install -e .

run:
	PYTHONPATH=src $(PYTHON) -m universe gui
