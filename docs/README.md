# 📚 Documentation Index

This folder contains the maintenance documentation for the **NiceGui Windows Base** template.

The documentation is aligned with the current `0.9.0` project shape, which includes the reusable NiceGUI application shell, shared UI components, component catalog, diagnostics page, log viewer, status page, validated settings page, settings subsystem, shared application state, native window geometry persistence, multi-monitor visibility guards, expanded tests, template customization helpers, release automation, and direct PyInstaller packaging.

---

## 🧭 Recommended reading order

1. [Development environment](development_environment.md) — complete setup flow for Windows.
2. [Python 3.13 setup on Windows](python_windows_setup.md) — Python installation, validation, and virtual environment setup.
3. [VS Code setup on Windows](vscode_setup.md) — editor, interpreter, Ruff, pytest, coverage, and Markdown tooling.
4. [PowerShell execution policy](powershell_execution_policy.md) — safe fixes for blocked PowerShell scripts.
5. [Architecture overview](architecture.md) — startup flow, module boundaries, SPA routing, settings, logging, native window persistence, and packaging inputs.
6. [UI shell guide](ui_shell.md) — application shell, routes, components, theme helpers, and page extension rules.
7. [Runtime support services](runtime_support.md) — diagnostics snapshots, bounded log reading, validated preferences, and status history.
8. [Execution modes](execution_modes.md) — native, web development, module, script, and packaged execution.
9. [Settings subsystem](settings.md) — `settings.toml`, persistence rules, scoped updates, validation, and runtime paths.
10. [Application state](state.md) — shared `AppState`, runtime diagnostics, persisted settings, and UI-facing status.
11. [Native window state package guide](../src/desktop_app/infrastructure/native_window_state/README.md) — startup restore, move/resize capture, multi-monitor clamping, and persistence rules.
12. [Logger package guide](../src/desktop_app/infrastructure/logger/README.md) — package-local guide for startup buffering, rotating file logs, settings integration, and shutdown cleanup.
13. [Template customization](template_customization.md) — safe public identity updates for projects derived from this template.
14. [Release automation](release_automation.md) — repeated release metadata updates, changelog insertion, and validation workflow.
15. [Windows packaging](packaging_windows.md) — direct PyInstaller build, assets, settings template, version metadata, and splash screen.
16. [Code quality](code_quality.md) — Ruff, pytest, coverage, compile checks, cleanup script usage, and Markdown validation.
17. [First run checklist](first_run_checklist.md) — practical validation checklist for a fresh clone or machine.
18. [Troubleshooting](troubleshooting.md) — common issues and fixes.
19. [Changelog](../CHANGELOG.md) — release history, version changes, and migration notes.

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

| Area                        | Main location                                               | Detailed guide                                                                                       |
| --------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Application services        | `src/desktop_app/application/`                              | [Architecture overview](architecture.md), [UI shell guide](ui_shell.md)                              |
| Startup orchestration       | `src/desktop_app/app.py` and `src/desktop_app/application/` | [Architecture overview](architecture.md)                                                             |
| Application shell and pages | `src/desktop_app/ui/`                                       | [UI shell guide](ui_shell.md), [Architecture overview](architecture.md#-nicegui-spa-structure)       |
| Runtime state               | `src/desktop_app/core/state.py`                             | [Application state](state.md)                                                                        |
| Settings persistence        | `src/desktop_app/infrastructure/settings/`                  | [Settings subsystem](settings.md)                                                                    |
| Native window geometry      | `src/desktop_app/infrastructure/native_window_state/`       | [Native window state package guide](../src/desktop_app/infrastructure/native_window_state/README.md) |
| Logging                     | `src/desktop_app/infrastructure/logger/`                    | [Logger package guide](../src/desktop_app/infrastructure/logger/README.md)                           |
| Template customization      | `scripts/customize_template.py`                             | [Template customization](template_customization.md)                                                  |
| Release automation          | `scripts/prepare_release.py`                                | [Release automation](release_automation.md)                                                          |
| Windows packaging           | `scripts/package_windows.ps1`                               | [Windows packaging](packaging_windows.md)                                                            |
| Workspace cleanup           | `scripts/clean_project.ps1`                                 | [Code quality](code_quality.md#-workspace-cleanup)                                                   |

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

## 🧩 Template and release tooling

The project includes maintenance tools for common template lifecycle work:

```powershell
python scripts\customize_template.py --help
python scripts\prepare_release.py --help
```

Use [Template customization](template_customization.md) to update public project identity while keeping the internal `desktop_app` package stable. Use [Release automation](release_automation.md) to update repeated version metadata consistently before validation and packaging.

---

## 📦 Packaging decision

The project uses **PyInstaller directly** instead of `nicegui-pack`.

Reason: the measured size and build time were similar, while direct PyInstaller provides the required options for Windows version metadata, hidden splash imports, windowed execution, bundled settings data, bundled assets, and splash screen support.

See [Windows packaging](packaging_windows.md) for the full command and maintenance notes.

---

## 🔗 Back to project README

Return to the root [README](../README.md).
