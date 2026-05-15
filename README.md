# NiceGui Windows Base

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-3.11%2B-2ea44f)](https://nicegui.io/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/tests-pytest-blueviolet)](https://docs.pytest.org/)

A minimal **NiceGui Windows Base** template for Windows desktop applications built with Python 3.13, NiceGUI native mode, browser-based development mode, persistent settings, structured logging, automated tests, template customization, release automation, and direct PyInstaller packaging.

---

## ✨ What is included

- Python package using the `src` layout;
- project metadata, dependencies, CLI entry point, package data, pytest, coverage, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-windows-base`;
- module execution through `python -m desktop_app`;
- a Windows cleanup script for generated caches, coverage outputs, egg-info metadata, and build artifacts;
- template customization tooling for public project identity updates without renaming `desktop_app`;
- release automation tooling for repeated version metadata and changelog updates;
- browser development execution through `python dev_run.py`;
- centralized typed `AppState` for runtime, UI, settings, assets, logging, lifecycle, and status information;
- persistent `settings.toml` support with full-file, group, and single-property load/save operations;
- native window size and position persistence controlled by `app.window.persist_state`;
- multi-monitor guard rails that keep restored native windows visible after monitor changes;
- bundled default settings template at `src/desktop_app/settings.toml`;
- defensive settings conversion for manually edited TOML values;
- narrative startup diagnostics shown in console logs when available, UI, and rotating log file;
- reusable application shell with navigation, shared layout, component catalog, diagnostics, logs, status, and settings pages;
- application services for diagnostics snapshots, bounded log reading, preference updates, and status history;
- centralized UI theme helpers and generic component builders for cards, page headers, feedback, and navigation;
- slim application entry point with startup bootstrap, runtime option building, and page composition split into focused modules;
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
│   ├── launch.json
│   └── settings.json
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── code_quality.md
│   ├── development_environment.md
│   ├── execution_modes.md
│   ├── first_run_checklist.md
│   ├── release_automation.md
│   ├── packaging_windows.md
│   ├── powershell_execution_policy.md
│   ├── python_windows_setup.md
│   ├── runtime_support.md
│   ├── settings.md
│   ├── state.md
│   ├── template_customization.md
│   ├── troubleshooting.md
│   ├── ui_shell.md
│   └── vscode_setup.md
├── scripts/
│   ├── clean_project.ps1
│   ├── customize_template.py
│   ├── package_windows.ps1
│   ├── prepare_release.py
│   └── version_info.txt
├── src/
│   └── desktop_app/
│       ├── application/
│       │   ├── __init__.py
│       │   ├── bootstrap.py
│       │   ├── diagnostics.py
│       │   ├── log_reader.py
│       │   ├── preferences.py
│       │   ├── run_options.py
│       │   ├── runtime_context.py
│       │   └── status.py
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
│       ├── project_tools/
│       │   ├── __init__.py
│       │   ├── common.py
│       │   ├── release_automation.py
│       │   └── template_customization.py
│       ├── infrastructure/
│       │   ├── logger/
│       │   │   ├── __init__.py
│       │   │   ├── bootstrapper.py
│       │   │   ├── byte_size.py
│       │   │   ├── config.py
│       │   │   ├── defaults.py
│       │   │   ├── exceptions.py
│       │   │   ├── handlers.py
│       │   │   ├── paths.py
│       │   │   ├── README.md
│       │   │   ├── service.py
│       │   │   └── validators.py
│       │   ├── settings/
│       │   ├── __init__.py
│       │   ├── asset_paths.py
│       │   ├── byte_size.py
│       │   ├── file_system.py
│       │   ├── lifecycle.py
│       │   ├── native_window_state/
│       │   │   ├── __init__.py
│       │   │   ├── arguments.py
│       │   │   ├── assignment.py
│       │   │   ├── bridge.py
│       │   │   ├── defaults.py
│       │   │   ├── events.py
│       │   │   ├── geometry.py
│       │   │   ├── models.py
│       │   │   ├── persistence.py
│       │   │   ├── README.md
│       │   │   └── service.py
│       │   └── splash.py
│       ├── ui/
│       │   ├── components/
│       │   │   ├── __init__.py
│       │   │   ├── cards.py
│       │   │   ├── feedback.py
│       │   │   ├── navigation.py
│       │   │   └── page.py
│       │   ├── pages/
│       │   │   ├── __init__.py
│       │   │   ├── components.py
│       │   │   ├── diagnostics.py
│       │   │   ├── index.py
│       │   │   ├── logs.py
│       │   │   ├── not_found.py
│       │   │   ├── routes.py
│       │   │   ├── settings.py
│       │   │   └── status.py
│       │   ├── __init__.py
│       │   ├── layout.py
│       │   ├── router.py
│       │   └── theme.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── constants.py
│       └── settings.toml
├── tests/
│   ├── application/
│   ├── core/
│   ├── infrastructure/
│   ├── project_tools/
│   ├── ui/
│   │   └── test_pages_and_router.py
│   ├── test_app.py
│   ├── test_constants.py
│   └── test_desktop_app_main.py
├── CHANGELOG.md
├── dev_run.py
├── pyproject.toml
└── README.md
```

The root `settings.toml` is intentionally not listed as source structure. It is a
runtime-generated file ignored by Git; the tracked default template is
`src/desktop_app/settings.toml`.

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
- `APPLICATION_TITLE`, `APPLICATION_VERSION`, command names, and application-level constants in [`src/desktop_app/constants.py`](src/desktop_app/constants.py);
- logger package defaults in [`src/desktop_app/infrastructure/logger/defaults.py`](src/desktop_app/infrastructure/logger/defaults.py), if the logging package itself is reused or renamed;
- default settings in [`src/desktop_app/settings.toml`](src/desktop_app/settings.toml);
- executable name and version metadata in [`scripts/package_windows.ps1`](scripts/package_windows.ps1) and [`scripts/version_info.txt`](scripts/version_info.txt);
- README text, documentation titles, and visual assets.

For routine public-identity changes, use [Template customization](docs/template_customization.md). The helper keeps the internal `desktop_app` package stable and updates the repeated public metadata points.

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

Clean generated files when caches or build outputs need to be removed:

```powershell
.\scripts\clean_project.ps1
```

Preview cleanup without deleting files:

```powershell
.\scripts\clean_project.ps1 -DryRun
```

Preview public template identity customization:

```powershell
python scripts\customize_template.py --help
```

Prepare repeated release metadata for a future version:

```powershell
python scripts\prepare_release.py 0.10.0 --dry-run
```

Package the Windows executable:

```powershell
.\scripts\package_windows.ps1
```

---

## 🧭 Main commands

| Task                           | Command                                              |
| ------------------------------ | ---------------------------------------------------- |
| Install project                | `python -m pip install -e ".[dev,packaging]"`        |
| Run native app                 | `nicegui-windows-base`                               |
| Run as module                  | `python -m desktop_app`                              |
| Run app script directly        | `python src\desktop_app\app.py`                      |
| Run web development            | `python dev_run.py`                                  |
| Run all tests                  | `pytest`                                             |
| Run tests with coverage        | `pytest --cov=desktop_app --cov-report=term-missing` |
| Check code                     | `ruff check .`                                       |
| Check formatting               | `ruff format --check .`                              |
| Format code                    | `ruff format .`                                      |
| Clean generated files          | `.\scripts\clean_project.ps1`                        |
| Preview cleanup                | `.\scripts\clean_project.ps1 -DryRun`                |
| Preview template customization | `python scripts\customize_template.py --help`        |
| Prepare release metadata       | `python scripts\prepare_release.py 0.10.0 --dry-run` |
| Package for Windows            | `.\scripts\package_windows.ps1`                      |
| Run packaged executable        | `.\dist\nicegui-windows-base.exe`                    |

All runtime commands assume the virtual environment is active and the editable install has already been completed.

---

## 🖨️ Startup diagnostics

The application builds one startup message and reuses it in console logs when available, UI, and rotating logs.

Current confirmed message shapes:

```text
NiceGui Windows Base is starting from the pyproject command in native mode with reload disabled.
NiceGui Windows Base is starting from module execution in native mode with reload disabled.
NiceGui Windows Base is starting from direct script execution in native mode with reload disabled.
NiceGui Windows Base is starting from the development runner in web mode with reload enabled.
NiceGui Windows Base is starting from the packaged executable in native mode with reload disabled.
```

The public command `nicegui-windows-base` and `python -m desktop_app` route through `src\desktop_app\__main__.py`. That wrapper captures the original command or module source before `runpy` changes `sys.argv`, then executes `desktop_app.app` with `__main__` semantics and passes the preserved source through `init_globals`.

This keeps the Windows-safe native-window startup path required by `app.native.window_args` while still allowing the runtime detector to show distinct startup sources for the pyproject command, module execution, and direct script execution. See [Execution modes](docs/execution_modes.md) for details.

The runtime log records the operational story of the run: settings load, native window geometry preparation, logger configuration, startup source detection, runtime mode selection, lifecycle handler registration, NiceGUI startup, client connections, native window lifecycle, window settings persistence, exceptions, and shutdown. Repeated page rendering and geometry evidence stay at `DEBUG` so the `INFO` flow remains readable. See [Logger package guide](src/desktop_app/infrastructure/logger/README.md).

---

## 🖥️ Application shell

Version 0.9.0 keeps the reusable application shell stable and adds maintenance tooling for template customization and release metadata automation.

Current built-in SPA pages:

| Route          | Purpose                                                                  |
| -------------- | ------------------------------------------------------------------------ |
| `/`            | Landing page with startup status and template capabilities.              |
| `/components`  | Live catalog for reusable page headers, cards, badges, and empty states. |
| `/diagnostics` | Runtime diagnostics rendered from a reusable support snapshot service.   |
| `/logs`        | Bounded viewer backed by a reusable log snapshot service.                |
| `/status`      | Current status and recent in-memory status history for this run.         |
| `/settings`    | Validated preference page backed by application services and settings.   |

The UI remains domain-neutral. Add project-specific features as new pages and services instead of placing integration logic directly in NiceGUI callbacks. See [UI shell guide](docs/ui_shell.md) and [Architecture overview](docs/architecture.md#-nicegui-spa-structure).

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

### 🪟 Native window persistence

When `app.window.persist_state = true`, the application restores native window size and position from `settings.toml`, updates `AppState.window` from native move and resize events, and saves the `window` group when the application exits.

Before applying persisted coordinates, the Windows monitor work areas are enumerated through Win32 APIs. The saved position is clamped against the most relevant monitor so a monitor change cannot leave the window unreachable. This supports secondary monitors and negative virtual-screen coordinates.

When `app.window.persist_state = false`, saved geometry is reset to `WindowState` defaults and persisted back to TOML so stale coordinates are not reused later.

See [Settings persistence](docs/settings.md), [Application state](docs/state.md), and [Native window state package guide](src/desktop_app/infrastructure/native_window_state/README.md).

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
- [Architecture overview](docs/architecture.md)
- [Execution modes](docs/execution_modes.md)
- [UI shell guide](docs/ui_shell.md)
- [Runtime support services](docs/runtime_support.md)
- [Windows packaging](docs/packaging_windows.md)
- [Logger package guide](src/desktop_app/infrastructure/logger/README.md)
- [Settings persistence](docs/settings.md)
- [Application state](docs/state.md)
- [Native window state package guide](src/desktop_app/infrastructure/native_window_state/README.md)
- [Code quality and tests](docs/code_quality.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 📝 Release notes

See [CHANGELOG.md](CHANGELOG.md) for version history, release notes, and migration notes.
