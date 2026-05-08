# 📝 Changelog

All notable changes to **NiceGui Windows Base** are documented in this file.

This changelog focuses on release-relevant changes for maintainers and users of the template.

---

## [0.3.4] - 2026-05-07

### ✨ Added

- Added typed application state in `src/desktop_app/core/state.py`.
- Added persistent settings support through `src/desktop_app/infrastructure/settings`.
- Added bundled `src/desktop_app/settings.toml` first-run template.
- Added settings documentation in `docs/settings.md`.
- Added shared `file_system.py` and `byte_size.py` infrastructure helpers.
- Added scoped settings load and save helpers for full-file, group, and individual property operations.
- Added runtime path, asset, UI session, settings validation, and lifecycle state sections to `AppState`.
- Added `docs/state.md` with full state-model and NiceGUI binding guidance.

### 🔄 Changed

- Changed the project version from `0.3.0` to `0.3.4`.
- Updated Windows version metadata in `scripts/version_info.txt` to `0.3.4.0`.
- Updated application startup to load settings before final logger file activation.
- Updated packaging to include the bundled settings template.
- Renamed ambiguous settings helpers to explicit names such as `resolve_default_settings_path()` and `get_nested_value()`.
- Renamed the TOML document helper module to `toml_document.py` and removed the temporary settings logging helper wrapper.
- Reused byte-size parsing and parent-directory creation instead of duplicating helper logic.
- Updated settings service to use the official application logger during early startup instead of optional logger wrappers.
- Updated the logger service so early import-time bootstrap uses memory buffering without console output.
- Added `tomlkit` as a runtime dependency so settings comments and unknown keys can be preserved.
- Updated settings persistence to preserve unrelated settings when saving a single group or property.
- Changed settings loading to keep in-memory defaults when `settings.toml` is missing and create the file only on save.

### 🧭 Migration notes

- Reinstall the project after upgrading so `tomlkit` is available:

```powershell
python -m pip install -e ".[dev,packaging]"
```

- Rebuild the executable so Windows file properties show version `0.3.4.0`:

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
