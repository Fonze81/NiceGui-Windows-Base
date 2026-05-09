# NiceGui Windows Base

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-3.11%2B-2ea44f)](https://nicegui.io/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/tests-pytest-blueviolet)](https://docs.pytest.org/)

A minimal **NiceGui Windows Base** template for Windows desktop applications built with Python 3.13, NiceGUI native mode, browser-based development mode, persistent settings, structured logging, automated tests, and direct PyInstaller packaging.

---

## ✨ What is included

- Python package using the `src` layout;
- project metadata, dependencies, CLI entry point, package data, pytest, coverage, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-windows-base`;
- module execution through `python -m desktop_app`;
- browser development execution through `python dev_run.py`;
- centralized typed `AppState` for runtime, UI, settings, assets, logging, lifecycle, and status information;
- persistent `settings.toml` support with full-file, group, and single-property load/save operations;
- bundled default settings template at `src/desktop_app/settings.toml`;
- defensive settings conversion for manually edited TOML values;
- narrative startup diagnostics shown in terminal, UI, and rotating log file;
- structured logger package with early startup buffering, rotating file logs, and safe shutdown;
- packaged and normal asset resolution for icon, page image, and splash image;
- optional PyInstaller splash screen support that closes after the first client connects;
- direct PyInstaller packaging with windowed mode, executable icon, bundled assets, bundled settings template, Windows version metadata, hidden splash import, and packaging report;
- pytest test suite with coverage configuration;
- VS Code recommendations, Ruff-on-save, Prettier formatting for non-Python files, and pytest discovery settings;
- maintenance documentation in [`docs`](docs/README.md).

---

## 📂 Current project structure

```text
.
├── .vscode/
│   ├── extensions.json
│   └── settings.json
├── docs/
│   ├── README.md
│   ├── code_quality.md
│   ├── development_environment.md
│   ├── execution_modes.md
│   ├── first_run_checklist.md
│   ├── logging.md
│   ├── packaging_windows.md
│   ├── powershell_execution_policy.md
│   ├── python_windows_setup.md
│   ├── settings.md
│   ├── state.md
│   ├── troubleshooting.md
│   └── vscode_setup.md
├── scripts/
│   ├── package_windows.ps1
│   └── version_info.txt
├── src/
│   └── desktop_app/
│       ├── assets/
│       │   ├── app_icon.ico
│       │   ├── logo.png
│       │   ├── page_image.png
│       │   ├── splash.svg
│       │   ├── splash_dark.png
│       │   └── splash_light.png
│       ├── core/
│       │   ├── __init__.py
│       │   ├── runtime.py
│       │   └── state.py
│       ├── infrastructure/
│       │   ├── logger/
│       │   ├── settings/
│       │   ├── __init__.py
│       │   ├── asset_paths.py
│       │   ├── byte_size.py
│       │   ├── file_system.py
│       │   ├── lifecycle.py
│       │   └── splash.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── constants.py
│       └── settings.toml
├── tests/
│   ├── core/
│   └── infrastructure/
├── CHANGELOG.md
├── dev_run.py
├── pyproject.toml
└── README.md
```

---

## 🧭 Naming model

This repository is a template, so it intentionally separates public project names from the internal Python package name.

| Element                 | Current value              | Purpose                                                                                  |
| ----------------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| Repository              | `nicegui-windows-base`     | Git repository and template identity.                                                    |
| Python package          | `desktop_app`              | Stable internal package used by imports, module execution, assets, tests, and packaging. |
| CLI command             | `nicegui-windows-base`     | User-facing command configured in `pyproject.toml`.                                      |
| Windows executable      | `nicegui-windows-base.exe` | Packaged desktop application artifact.                                                   |
| Visual application name | `NiceGui Windows Base`     | Name shown in UI, settings, logs, and Windows metadata.                                  |

When this template is reused, prefer changing public metadata first:

- project name, description, authors, and script command in [`pyproject.toml`](pyproject.toml);
- `APPLICATION_TITLE`, `APPLICATION_VERSION`, command names, and shared constants in [`src/desktop_app/constants.py`](src/desktop_app/constants.py);
- default settings in [`src/desktop_app/settings.toml`](src/desktop_app/settings.toml);
- executable name and version metadata in [`scripts/package_windows.ps1`](scripts/package_windows.ps1) and [`scripts/version_info.txt`](scripts/version_info.txt);
- README text, documentation titles, and visual assets.

Keeping `desktop_app` stable avoids unnecessary changes to imports, module paths, tests, asset packaging, and documentation links. Rename the package only when the new project has a strong technical reason to expose a domain-specific Python package name.

---

## 🚀 Quick start

Create and activate the virtual environment with Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, see [PowerShell execution policy](docs/powershell_execution_policy.md).

Install the project with development and packaging tools:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
```

Run the application normally in native mode:

```powershell
nicegui-windows-base
```

Run the application as a Python module:

```powershell
python -m desktop_app
```

Run browser development mode with reload:

```powershell
python dev_run.py
```

Run tests and quality checks:

```powershell
pytest
ruff check .
ruff format --check .
```

Package the Windows executable:

```powershell
.\scripts\package_windows.ps1
```

---

## 🧭 Main commands

| Task                    | Command                                              |
| ----------------------- | ---------------------------------------------------- |
| Install project         | `python -m pip install -e ".[dev,packaging]"`        |
| Run native app          | `nicegui-windows-base`                               |
| Run as module           | `python -m desktop_app`                              |
| Run app script directly | `python src\desktop_app\app.py`                      |
| Run web development     | `python dev_run.py`                                  |
| Run all tests           | `pytest`                                             |
| Run tests with coverage | `pytest --cov=desktop_app --cov-report=term-missing` |
| Check code              | `ruff check .`                                       |
| Check formatting        | `ruff format --check .`                              |
| Format code             | `ruff format .`                                      |
| Package for Windows     | `.\scripts\package_windows.ps1`                      |
| Run packaged executable | `.\dist\nicegui-windows-base.exe`                    |

All runtime commands assume the virtual environment is active and the editable install has already been completed.

---

## 🖨️ Startup diagnostics

The application builds one startup message and reuses it in terminal output, UI, and logs.

Examples:

```text
NiceGui Windows Base is starting from the pyproject command in native mode with reload disabled.
NiceGui Windows Base is starting from module execution in native mode with reload disabled.
NiceGui Windows Base is starting from direct script execution in native mode with reload disabled.
NiceGui Windows Base is starting from the development runner in web mode with reload enabled.
NiceGui Windows Base is starting from the packaged executable in native mode with reload disabled.
```

The runtime log records the operational story of the run: settings load, logger configuration, startup source detection, runtime mode selection, lifecycle handler registration, asset resolution, NiceGUI startup, page build, client connections, native window events, exceptions, and shutdown. See [Logging subsystem](docs/logging.md).

---

## ⚙️ Settings and state

The application loads settings before final logger configuration so persisted logging preferences can control level, console output, buffer size, file path, rotation size, and backup count.

The default settings template is bundled at:

```text
src\desktop_app\settings.toml
```

Persistent settings are resolved to:

| Runtime                 | Persistent settings location                |
| ----------------------- | ------------------------------------------- |
| Normal Python execution | `<current-working-directory>\settings.toml` |
| Packaged executable     | `<executable-directory>\settings.toml`      |
| Custom root             | `%DESKTOP_APP_ROOT%\settings.toml`          |

Loading a missing settings file is intentionally read-only and keeps in-memory defaults. The file is created only when a save operation runs.

See [Settings persistence](docs/settings.md) and [Application state](docs/state.md).

---

## 🖼️ Assets

Runtime assets are stored in:

```text
src\desktop_app\assets
```

Current assets:

- `app_icon.ico` — used by `ui.run(favicon=...)` and PyInstaller `--icon`;
- `page_image.png` — shown in the NiceGUI page;
- `splash_light.png` — used by PyInstaller `--splash` and intended to have an opaque light background;
- `splash_dark.png` and `splash.svg` — optional source/reference assets for future splash design changes;
- `logo.png` — optional branding asset.

[`asset_paths.py`](src/desktop_app/infrastructure/asset_paths.py) resolves assets for normal Python execution and packaged execution. It rejects absolute, rooted, drive-based, or parent-directory paths to keep asset access constrained to the bundled assets directory.

---

## 📚 Documentation

Start with the [documentation index](docs/README.md).

Main guides:

- [Development environment](docs/development_environment.md)
- [Execution modes](docs/execution_modes.md)
- [Windows packaging](docs/packaging_windows.md)
- [Logging subsystem](docs/logging.md)
- [Settings persistence](docs/settings.md)
- [Application state](docs/state.md)
- [Code quality and tests](docs/code_quality.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 📝 Release notes

See [CHANGELOG.md](CHANGELOG.md) for version history, release notes, and migration notes.
