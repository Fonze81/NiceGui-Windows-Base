# 📚 Documentation Index

This folder contains the maintenance documentation for the **NiceGui Windows Base** template.

The documentation is aligned with the current `0.6.1` project shape, which includes the NiceGUI SPA shell with `ui.sub_pages`, separated UI pages, the settings subsystem, shared application state, native window geometry persistence, multi-monitor visibility guards, expanded tests, and direct PyInstaller packaging.

---

## 🧭 Recommended reading order

1. [Development environment](development_environment.md) — complete setup flow for Windows.
2. [Python 3.13 setup on Windows](python_windows_setup.md) — Python installation, validation, and virtual environment setup.
3. [VS Code setup on Windows](vscode_setup.md) — editor, interpreter, Ruff, pytest, coverage, and Markdown tooling.
4. [PowerShell execution policy](powershell_execution_policy.md) — safe fixes for blocked PowerShell scripts.
5. [Architecture overview](architecture.md) — startup flow, module boundaries, SPA routing, settings, logging, native window persistence, and packaging inputs.
6. [Execution modes](execution_modes.md) — native, web development, module, script, and packaged execution.
7. [Settings subsystem](settings.md) — `settings.toml`, persistence rules, scoped updates, validation, and runtime paths.
8. [Application state](state.md) — shared `AppState`, runtime diagnostics, persisted settings, and UI-facing status.
9. [Native window persistence](native_window_persistence.md) — startup restore, move/resize capture, multi-monitor clamping, and persistence rules.
10. [Logger package guide](../src/desktop_app/infrastructure/logger/README.md) — package-local guide for startup buffering, rotating file logs, settings integration, and shutdown cleanup.
11. [Windows packaging](packaging_windows.md) — direct PyInstaller build, assets, settings template, version metadata, and splash screen.
12. [Code quality](code_quality.md) — Ruff, pytest, coverage, compile checks, cleanup script usage, and Markdown validation.
13. [First run checklist](first_run_checklist.md) — practical validation checklist for a fresh clone or machine.
14. [Troubleshooting](troubleshooting.md) — common issues and fixes.
15. [Changelog](../CHANGELOG.md) — release history, version changes, and migration notes.

---

## 🧭 Naming model

The source package is intentionally named `desktop_app`.

This is a stable, generic internal package name for the template. Public names such as the repository name, CLI command, executable name, and visible application title can be changed for each project without renaming the Python package.

Use these names consistently:

| Context                                                                   | Name                   |
| ------------------------------------------------------------------------- | ---------------------- |
| Python imports, module execution, package data, and internal source paths | `desktop_app`          |
| Default console script and Windows executable                             | `nicegui-windows-base` |
| Default visible application title                                         | `NiceGui Windows Base` |

See the root [README](../README.md#-naming-model) for the complete naming model and the list of public metadata that should be changed when the template is reused.

---

## 🏗️ Architecture summary

The project keeps the application entry point thin and moves focused responsibilities into dedicated packages:

| Area                   | Main location                                               | Detailed guide                                                             |
| ---------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------- |
| Startup orchestration  | `src/desktop_app/app.py` and `src/desktop_app/application/` | [Architecture overview](architecture.md)                                   |
| SPA layout and pages   | `src/desktop_app/ui/`                                       | [Architecture overview](architecture.md#-nicegui-spa-structure)            |
| Runtime state          | `src/desktop_app/core/state.py`                             | [Application state](state.md)                                              |
| Settings persistence   | `src/desktop_app/infrastructure/settings/`                  | [Settings subsystem](settings.md)                                          |
| Native window geometry | `src/desktop_app/infrastructure/native_window_state.py`     | [Native window persistence](native_window_persistence.md)                  |
| Logging                | `src/desktop_app/infrastructure/logger/`                    | [Logger package guide](../src/desktop_app/infrastructure/logger/README.md) |
| Windows packaging      | `scripts/package_windows.ps1`                               | [Windows packaging](packaging_windows.md)                                  |
| Workspace cleanup      | `scripts/clean_project.ps1`                                 | [Code quality](code_quality.md#-workspace-cleanup)                         |

The full architecture explanation was moved to [Architecture overview](architecture.md) to keep this index focused on navigation and avoid duplicated maintenance details.

---

## 💾 Settings persistence summary

The application ships with a bundled default settings template:

```text
src\desktop_app\settings.toml
```

At runtime, the persistent settings file is resolved as:

| Runtime                 | Persistent file                             |
| ----------------------- | ------------------------------------------- |
| Normal Python execution | `<current-working-directory>\settings.toml` |
| Environment override    | `%DESKTOP_APP_ROOT%\settings.toml`          |
| PyInstaller executable  | `<executable-directory>\settings.toml`      |

Missing persistent settings are not an error. The application can start from bundled defaults and later save a persistent file when settings are changed.

See [Settings subsystem](settings.md) for the complete behavior.

---

## 📦 Packaging decision

The project uses **PyInstaller directly** instead of `nicegui-pack`.

Reason: the measured size and build time were similar, while direct PyInstaller provides the required options for Windows version metadata, hidden splash imports, windowed execution, bundled settings data, bundled assets, and splash screen support.

See [Windows packaging](packaging_windows.md) for the full command and maintenance notes.

---

## 🔗 Back to project README

Return to the root [README](../README.md).
