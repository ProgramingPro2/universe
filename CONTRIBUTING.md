# Contributing to Universe

Thanks for helping improve Universe. This project is free software under the
GNU GPL v3 or later.

## Development setup

```bash
git clone https://github.com/ProgramingPro2/universe.git
cd universe
make test
make run
```

Runtime needs Python 3.10+, GTK 4, and libadwaita (see [README.md](README.md)).

## How to contribute

1. Open an issue for bugs or proposed features when practical.
2. Fork the repo and create a branch from `main`.
3. Make focused changes with clear commits.
4. Run `make test` before opening a pull request.
5. Open a PR describing what changed and why.

## Coding notes

- Package code lives under `src/universe/`.
- Prefer small, readable functions and explicit error handling.
- Add or update tests in `tests/` for behavior changes.
- Do not commit secrets, local `dist/` packages, or `.venv/`.

## License of contributions

By contributing, you agree that your contributions are licensed under the
same terms as the project: **GPL-3.0-or-later**. See [LICENSE](LICENSE) and
[COPYRIGHT](COPYRIGHT).

## Security

Do not file public issues for security vulnerabilities that include exploit
details. Prefer the process in [SECURITY.md](SECURITY.md).
