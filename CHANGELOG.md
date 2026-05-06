# 📝 Changelog

All notable changes to **NiceGui Windows Base** are documented in this file.

This changelog focuses on release-relevant changes for maintainers and users of the template.

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
