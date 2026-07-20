# Security Policy

## Reporting a vulnerability

Please open a private security advisory on GitHub if available, or open an issue marked security-sensitive at:

https://github.com/ProgramingPro2/universe/security

If that is not possible, open a public issue without exploit details and ask for a contact channel.

## Trust model

Universe manages AppImages on your system. Integrating or opening an AppImage can **execute** that file to extract metadata (for example `--appimage-extract` or `--appimage-updateinfo`). Treat AppImages like any other untrusted binary: only integrate software from sources you trust.

Desktop shortcuts are written under your user `~/.local/share/applications`. Display names, environment variables, and launch arguments are sanitized before writing `.desktop` files.
