# 📝 Changelog

All notable changes to **NiceGui Windows Base** are documented in this file.

This changelog focuses on release-relevant changes for maintainers and users of the template.

---

## [0.6.0] - 2026-05-12

### ✨ Added

- Added a NiceGUI SPA shell using `ui.sub_pages`, with route registration in `desktop_app.ui.router`, shared layout in `desktop_app.ui.layout`, and page modules under `desktop_app.ui.pages`.
- Added the in-app fallback page for unknown SPA paths.
- Added focused UI tests for layout mounting, route registration, index page rendering, and fallback page rendering.
- Added additional native window tests for proxy geometry refresh, Win32 monitor enumeration edge cases, failed persistence paths, and geometry coercion helpers.
- Added `scripts/clean_project.ps1` documentation coverage for cache, coverage, egg-info, build artifact, dry-run, and optional log cleanup workflows.

### 🔄 Changed

- Changed the project version from `0.5.0` to `0.6.0`.
- Updated Windows version metadata in `scripts/version_info.txt` to `0.6.0.0`.
- Updated the bundled and root `settings.toml` version values to `0.6.0`.
- Renamed the default page builder from `build_main_page` to `build_index_page` to match the `ui/pages/index.py` SPA structure.
- Updated README and maintenance documentation to reflect the SPA package layout, the current `__main__.py` execution routing, and generated-file cleanup workflow.
- Simplified native window default reset logic by removing an unreachable dataclass-field guard.

### 🐞 Fixed

- Fixed documentation drift between `pyproject.toml`, `scripts/version_info.txt`, `settings.toml`, README, the SPA UI package layout, and cleanup tooling.
- Updated test coverage scope for UI modules and native window edge cases so maintainers can run the documented `--cov-fail-under=100` validation command.

### 🧭 Migration notes

- Reinstall the project after upgrading so package metadata and package data are refreshed:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- Rebuild the executable so Windows file properties show version `0.6.0.0` and the updated bundled settings template is included:

```powershell
.\scripts\package_windows.ps1
```

---

## [0.5.0] - 2026-05-11

### ✨ Added

- Added native window size and position persistence for NiceGUI native mode.
- Added `app.window.persist_state` to control whether native window geometry is restored and saved.
- Added `desktop_app.infrastructure.native_window_state` to isolate native geometry restore, event capture, multi-monitor validation, and scoped window settings persistence.
- Added Windows multi-monitor visibility guards using Win32 monitor work areas so persisted coordinates remain reachable after monitor changes without shrinking saved window dimensions.
- Added focused tests for native geometry extraction from NiceGUI event arguments, restore behavior, close/shutdown persistence behavior, disabled persistence resets, and multi-monitor position correction.
- Added orchestration tests for startup bootstrap, top-level `app.py`, and main page composition using fake NiceGUI objects.
- Added `docs/native_window_persistence.md` with startup flow, multi-monitor behavior, save rules, validation commands, and troubleshooting guidance.
- Added focused `desktop_app.application` startup modules for logging bootstrap, runtime context resolution, and NiceGUI run option construction.
- Added a dedicated UI page module to keep page composition outside the application entry point.

### 🔄 Changed

- Changed the project version from `0.4.0` to `0.5.0`.
- Updated Windows version metadata in `scripts/version_info.txt` to `0.5.0.0`.
- Updated application constants and the bundled default settings template to version `0.5.0`.
- Updated startup to load settings and apply `app.native.window_args` before `main()` starts, keeping persisted `x` and `y` available before the native window is created.
- Updated native lifecycle handlers so `moved` and `resized` events update `AppState.window` and the `window` settings group is saved on close or shutdown.
- Updated README, documentation index, execution modes, settings, state, first-run checklist, and troubleshooting documentation for native window persistence.
- Refactored `src/desktop_app/app.py` into a smaller entry point that delegates logging bootstrap, runtime setup, and UI composition to dedicated modules.
- Centralized native window startup geometry in `app.native.window_args` and kept window geometry options out of `ui.run(...)`.
- Changed startup diagnostics to use configured logging instead of raw `print(...)` in `app.py`.

### 🐞 Fixed

- Fixed persisted native window size and position capture when NiceGUI move and resize events arrive as event-argument objects.
- Fixed persisted `x` and `y` being ignored by applying native window arguments earlier in module initialization.
- Fixed the risk of opening the application outside a recoverable visible desktop area after monitor removal, monitor reordering, or resolution changes while preserving saved width and height.
- Fixed stale persisted geometry being reused after `app.window.persist_state` is changed to `false` by resetting geometry to defaults and saving the `window` group.
- Preserved the working TOML save behavior by keeping move and resize events in-memory only and saving the `window` group on close or shutdown.
- Kept `ui.run(...)` free of window geometry arguments while capturing valid runtime window updates from native event payloads and the native window proxy.
- Fixed `test_splash.py` collection in environments where NiceGUI is not installed by using a minimal test fake.
- Fixed the Ruff `E402` warning in `test_splash.py` while preserving the fake NiceGUI import guard used during test collection.
- Removed an unnecessary `type: ignore[arg-type]` in native window pair coercion.
- Narrowed file-system atomic write cleanup handling to documented I/O and encoding exceptions.

### 🧭 Migration notes

- Reinstall the project after upgrading so the package metadata and bundled settings template are refreshed:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- If a persistent `settings.toml` already exists, add the new setting or let the application save the `window` group:

```toml
[app.window]
persist_state = true
```

- To clear stale geometry from an existing runtime settings file, set `persist_state = false` once and start the application. The application resets geometry fields to defaults and saves the `window` group.

- Rebuild the executable so Windows file properties show version `0.5.0.0` and the updated bundled settings template is included:

```powershell
.\scripts\package_windows.ps1
```

---

## [0.4.0] - 2026-05-09

### ✨ Added

- Added a typed central `AppState` model with runtime, path, window, UI, UI session, asset, log, behavior, settings, validation, lifecycle, and status sections.
- Added persistent `settings.toml` support with full-file, group, and individual property load/save operations.
- Added bundled default settings template at `src/desktop_app/settings.toml`.
- Added settings path resolution for normal Python execution, packaged execution, PyInstaller extraction, and `%DESKTOP_APP_ROOT%` overrides.
- Added defensive settings conversion helpers for booleans, integers, floats, paths, and byte-size values.
- Added TOML document update helpers that preserve comments and unknown keys during scoped saves.
- Added `byte_size.py` for reusable parsing of values such as `5 MB`, `512KB`, and `1 GB`.
- Added `file_system.py` with parent-directory creation and atomic text writes.
- Added pytest and coverage configuration to `pyproject.toml`.
- Added extensive tests for core runtime, application state, logger, settings, asset paths, byte-size parsing, file-system helpers, lifecycle handlers, splash handling, constants, and module execution.
- Added VS Code pytest discovery settings and Prettier defaults for non-Python file types.
- Added documentation for settings persistence and application state.

### 🔄 Changed

- Changed the project version from `0.3.0` to `0.4.0`.
- Updated Windows version metadata in `scripts/version_info.txt` to `0.4.0.0`.
- Updated application constants and default settings to version `0.4.0`.
- Updated packaging to bundle `src\desktop_app\settings.toml` with the executable.
- Updated application startup so settings are loaded before final logger configuration.
- Updated runtime diagnostics to store effective settings, log, executable, working directory, and PyInstaller extraction paths in `AppState`.
- Updated development mode reload settings to watch Python source files and ignore logs, generated settings, build outputs, distribution outputs, and `.venv`.
- Updated documentation to reflect the current settings package, state model, tests, coverage, packaging inputs, and project structure.

### 🐞 Fixed

- Removed stale documentation references to the deleted `desktop_app.infrastructure.settings.constants` module.
- Clarified that missing `settings.toml` during load is not an error and does not create a file.
- Clarified packaged settings behavior so editable settings are stored next to the executable, not inside the PyInstaller temporary extraction directory.
- Clarified package-data requirements for both assets and the bundled settings template.

### 🧭 Migration notes

- Reinstall the project after upgrading:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- Run the test suite and quality checks:

```powershell
pytest
ruff check .
ruff format --check .
```

- Rebuild the executable so Windows file properties show version `0.4.0.0` and the bundled settings template is included:

```powershell
.\scripts\package_windows.ps1
```

---

## [0.3.0] - 2026-05-07

### ✨ Added

- Added a dedicated logger package with configuration, validation, bounded startup buffering, rotating file handlers, safe shutdown, and a public logger API.
- Added `docs/logging.md` to explain logger architecture, startup buffering, file rotation, placeholder formatting, and maintenance checks.
- Added explicit runtime log path resolution inside the logger package so `app.py` only orchestrates logging startup.
- Added VS Code markdownlint as a recommended documentation-quality extension.

### 🔄 Changed

- Changed the project version from `0.2.0` to `0.3.0`.
- Updated Windows version metadata in `scripts/version_info.txt` to `0.3.0.0`.
- Updated documentation indexes and project structure references to include the logger package and logging guide.
- Updated packaging documentation examples to use the current `0.3.0` release metadata.
- Made the runtime log directory explicit in `.gitignore` so generated logs are not included in release artifacts.

### 🐞 Fixed

- Removed the generated runtime log file from the release source tree.
- Reduced application entry-point responsibility by moving log path resolution out of `app.py`.

### 🧭 Migration notes

- Reinstall the project after upgrading:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- Rebuild the executable so Windows file properties show version `0.3.0.0`:

```powershell
.\scripts\package_windows.ps1
```

---

## [0.2.0] - 2026-05-06

### ✨ Added

- Added the stable internal package name `desktop_app` to make the template easier to reuse without renaming the package for every new project.
- Added focused modules for runtime detection, asset path resolution, lifecycle logging, and PyInstaller splash handling.
- Added more narrative application logs for startup, shutdown, client connections, exceptions, native window events, and file-drop events.
- Added clearer `ui.run(...)` configuration through centralized run options.
- Added PyInstaller `--windowed` packaging and explicit `pyi_splash` hidden import support.
- Added documentation updates for the new package model, execution modes, packaging behavior, troubleshooting, and project setup.

### 🔄 Changed

- Changed the project version from `0.1.0` to `0.2.0`.
- Changed the internal source package from `nicegui_windows_base` to `desktop_app`.
- Updated the console script, module execution command, package data configuration, development runner, packaging script, and documentation to use `desktop_app`.
- Refactored `app.py` into a smaller startup orchestration module, delegating runtime, assets, lifecycle, and splash responsibilities to dedicated modules.
- Improved the startup status message so the terminal output and visible UI tell the same execution story.

### 🐞 Fixed

- Fixed packaged desktop execution so the native app opens without an additional console window.
- Improved PyInstaller splash reliability by keeping `pyi_splash` available in packaged builds.
- Reduced the risk of duplicated startup text and duplicated runtime responsibilities in `app.py`.

### 🧭 Migration notes

- Update imports from `nicegui_windows_base` to `desktop_app`.
- Reinstall the project after upgrading:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- Use this command for module execution:

```powershell
python -m desktop_app
```

- The public CLI command remains unchanged:

```powershell
nicegui-windows-base
```

---

## [0.1.0] - 2026-05-05

### ✨ Added

- Added the initial **NiceGui Windows Base** template.
- Added Python 3.13 project configuration with a `src` layout and the original `nicegui_windows_base` package.
- Added NiceGUI native desktop execution, browser development mode, module execution, and direct script diagnostic execution.
- Added the initial UI with application title, page image, description, and startup status message.
- Added runtime asset handling for normal Python execution and PyInstaller packaged execution.
- Added Windows packaging with PyInstaller, executable icon, bundled assets, splash screen, version metadata, and packaging report generation.
- Added Ruff configuration, VS Code workspace recommendations, and setup documentation for development, packaging, quality checks, and troubleshooting.

### 🧭 Notes

- This release established the first working baseline for the template.
- The original internal package was `nicegui_windows_base`; it was replaced by `desktop_app` in version `0.2.0`.
