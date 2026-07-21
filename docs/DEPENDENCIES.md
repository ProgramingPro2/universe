# Dependency tree

Universe itself has **no PyPI runtime dependencies**. All third-party requirements are
system packages provided by the distro (or optional external tools).

Declared packaging `Depends` (Debian/Ubuntu names):

```
universe
├── python3                          (>= 3.10)
├── python3-gi                       # PyGObject bindings
├── gir1.2-gtk-4.0                   # GTK 4 GObject introspection
├── gir1.2-adw-1                     # libadwaita GI typelib
├── libadwaita-1-0                   # libadwaita shared library
├── desktop-file-utils               # update-desktop-database
└── libfuse2t64 | libfuse2           # FUSE for type-2 AppImages
```

## Runtime (required)

| Component | Debian / Ubuntu package | Typical license | Used for |
|---|---|---|---|
| Python 3.10+ | `python3` | PSF-2.0 | App runtime |
| PyGObject | `python3-gi` | LGPL-2.1+ | GTK / Adwaita bindings |
| GTK 4 | `gir1.2-gtk-4.0` (+ libs) | LGPL-2.1+ | GUI |
| libadwaita | `gir1.2-adw-1`, `libadwaita-1-0` | LGPL-2.1+ | Adwaita widgets |
| desktop-file-utils | `desktop-file-utils` | GPL-2.0+ | Refresh desktop database |
| FUSE 2 | `libfuse2t64` or `libfuse2` | GPL-2.0 / LGPL-2.1 | Run type-2 AppImages |

Fedora / RHEL equivalents are pulled in by the `.rpm` package metadata (same logical stack:
`python3`, `python3-gobject`, GTK4, libadwaita, `desktop-file-utils`, `fuse`).

## Build / packaging (developers & CI)

| Tool | Purpose | Typical license |
|---|---|---|
| `make`, `fakeroot`, `dpkg-deb` | Build `.deb` | GPL |
| `nfpm` | Build `.deb` / `.rpm` / tarball in CI | MIT |
| `unittest` (stdlib) | Tests | PSF-2.0 |
| `setuptools` (build-system) | Python packaging metadata | MIT |

No locked `requirements.txt` is needed for runtime: `pyproject.toml` has
`dependencies = []`.

## Optional (features, not hard Depends)

| Tool | Purpose |
|---|---|
| `appimageupdatetool` | In-app “Update with appimageupdatetool” |
| `gtk-update-icon-cache` | Refresh icon theme cache after integrate |
| `xdg-mime` | Set default AppImage MIME handler in `postinst` |

## Standard library

Universe uses only the Python standard library plus PyGObject (`gi`). There is no
vendored third-party Python source tree under `src/`.

## Source of truth

- Packaging Depends: [`packaging/debian/control.in`](../packaging/debian/control.in), [`packaging/nfpm.yaml`](../packaging/nfpm.yaml)
- Python package metadata: [`pyproject.toml`](../pyproject.toml)
- Human install notes: [`README.md`](../README.md)
