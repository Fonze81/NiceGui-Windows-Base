# NiceGui Windows Base

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)

A minimal **NiceGui Windows Base template** for Windows development, native desktop execution, browser-based UI development, code quality with Ruff, and Windows executable packaging with direct PyInstaller.

---

## ✨ What is included

- Python package using `src` layout;
- project metadata, dependencies, entry point, package assets, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-windows-base`;
- module execution through `python -m desktop_app`;
- browser-based development execution through `python dev_run.py`;
- narrative startup diagnostics shown in the terminal, rotating log file, and UI;
- packaged and normal asset resolution for the application icon and page image;
- structured logger package with startup buffering, rotating file logs, lifecycle logging, and safe shutdown;
- typed runtime state model and persistent `settings.toml` support with scoped load/save operations;
- optional PyInstaller splash screen support that closes after the first client connects;
- PyInstaller packaging with windowed mode, executable icon, bundled assets, Windows version metadata, hidden splash import, and splash screen;
- VS Code recommendations and Ruff-on-save workspace settings;
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
│   ├── settings.md
│   ├── packaging_windows.md
│   ├── powershell_execution_policy.md
│   ├── python_windows_setup.md
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
│       │   ├── byte_size.py
│       │   ├── file_system.py
│       │   ├── logger/
│       │   │   ├── __init__.py
│       │   │   ├── bootstrapper.py
│       │   │   ├── config.py
│       │   │   ├── exceptions.py
│       │   │   ├── handlers.py
│       │   │   ├── paths.py
│       │   │   ├── service.py
│       │   │   └── validators.py
│       │   ├── settings/
│       │   │   ├── __init__.py
│       │   │   ├── constants.py
│       │   │   ├── conversion.py
│       │   │   ├── mapper.py
│       │   │   ├── paths.py
│       │   │   ├── schema.py
│       │   │   ├── service.py
│       │   │   └── toml_document.py
│       │   ├── __init__.py
│       │   ├── asset_paths.py
│       │   ├── lifecycle.py
│       │   └── splash.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── constants.py
│       └── settings.toml
├── CHANGELOG.md
├── dev_run.py
├── pyproject.toml
└── README.md
```

---

## 🧭 Naming model

This repository is a template, so it intentionally separates the public project names from the internal Python package name.

| Element                 | Current value              | Purpose                                                                                 |
| ----------------------- | -------------------------- | --------------------------------------------------------------------------------------- |
| Repository              | `nicegui-windows-base`     | Git repository and template identity.                                                   |
| Python package          | `desktop_app`              | Stable internal package used by imports, module execution, assets, and packaging paths. |
| CLI command             | `nicegui-windows-base`     | User-facing command configured in `pyproject.toml`.                                     |
| Windows executable      | `nicegui-windows-base.exe` | Packaged desktop application artifact.                                                  |
| Visual application name | `NiceGui Windows Base`     | Name shown in the UI, logs, and application metadata.                                   |

The internal package is intentionally named `desktop_app`.

When this template is reused for a new project, the package usually does **not** need to be renamed. Prefer changing public project metadata instead, such as:

- project name, description, authors, and script command in `pyproject.toml`;
- `APPLICATION_TITLE`, log file name, and command detection constants in `src/desktop_app/constants.py`;
- executable name and version metadata in `scripts/package_windows.ps1` and `scripts/version_info.txt`;
- README text, documentation titles, and visual assets.

Keeping `desktop_app` stable avoids unnecessary changes to imports, module paths, entry points, asset packaging, tests, and documentation links.

Rename the package only when the new project has a strong technical reason to expose a domain-specific Python package name. If that happens, update all imports, `pyproject.toml`, PyInstaller paths, documentation, and tests together.

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

Run the application in browser development mode:

```powershell
python dev_run.py
```

Package the Windows executable:

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the packaging script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

---

## 🧭 Main commands

| Task                     | Command                                       |
| ------------------------ | --------------------------------------------- |
| Install project          | `python -m pip install -e ".[dev,packaging]"` |
| Run native app           | `nicegui-windows-base`                        |
| Run as module            | `python -m desktop_app`                       |
| Run app script directly  | `python src\desktop_app\app.py`               |
| Run web development mode | `python dev_run.py`                           |
| Check code               | `ruff check .`                                |
| Check formatting         | `ruff format --check .`                       |
| Format code              | `ruff format .`                               |
| Package for Windows      | `.\scripts\package_windows.ps1`               |

All runtime commands assume the virtual environment is active and the editable install has already been completed.

---

## 🖨️ Startup diagnostics

The application prints a narrative startup message that explains how it was started, which mode is active, and whether reload is enabled. The same message is shown in the page.

Examples:

```text
NiceGui Windows Base is starting from the pyproject command in native mode with reload disabled.
NiceGui Windows Base is starting from module execution in native mode with reload disabled.
NiceGui Windows Base is starting from direct script execution in native mode with reload disabled.
NiceGui Windows Base is starting from the development runner in web mode with reload enabled.
NiceGui Windows Base is starting from the packaged executable in native mode with reload disabled.
```

The log file also tells the operational story of the run: logging initialization, startup source detection, runtime mode selection, lifecycle handler registration, asset resolution, NiceGUI startup, page build, native window events, client disconnects, exceptions, and shutdown. See [Logging subsystem](docs/logging.md) for the logger architecture, buffering model, and rotation behavior.

---

## 🖼️ Assets

Runtime assets are stored in:

```text
src\desktop_app\assets
```

Current assets:

- `app_icon.ico` — used by `ui.run(favicon=...)` and by PyInstaller `--icon`;
- `page_image.png` — shown in the NiceGUI page;
- `splash_light.png` — used by PyInstaller `--splash` and intended to have an opaque light background;
- `splash_dark.png` and `splash.svg` — optional source/reference assets for future splash design changes.

`asset_paths.py` resolves asset paths for both normal Python execution and packaged execution.

---

## 📚 Documentation

Start with the [documentation index](docs/README.md).

Main guides:

- [Development environment](docs/development_environment.md)
- [Execution modes](docs/execution_modes.md)
- [Windows packaging](docs/packaging_windows.md)
- [Logging subsystem](docs/logging.md)
- [Settings and application state](docs/settings.md)
- [Code quality with Ruff](docs/code_quality.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 📝 Release notes

See [CHANGELOG.md](CHANGELOG.md) for version history, release notes, and migration notes.
