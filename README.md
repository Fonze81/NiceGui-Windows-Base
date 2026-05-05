# NiceGui Windows Base

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)

A minimal **NiceGui Windows Base template** for Windows development, native desktop execution, browser-based UI development, code quality with Ruff, and Windows executable packaging with direct PyInstaller.

---

## ✨ What is included

- Python package using `src` layout;
- project metadata, dependencies, entry point, package assets, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-windows-base`;
- browser-based development execution through `python dev_run.py`;
- startup diagnostics shown in the terminal and in the UI;
- packaged and normal asset resolution for the application icon and page image;
- PyInstaller packaging with executable icon, bundled assets, Windows version metadata, and splash screen;
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
│       │   ├── page_image.png
│       │   ├── splash.svg
│       │   ├── splash_dark.png
│       │   └── splash_light.png
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── dev_run.py
├── pyproject.toml
└── README.md
```

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
| Run native app           | `nicegui-windows-base`                         |
| Run as module            | `python -m desktop_app`               |
| Run app script directly  | `python src\desktop_app\app.py`       |
| Run web development mode | `python dev_run.py`                           |
| Check code               | `ruff check .`                                |
| Check formatting         | `ruff format --check .`                       |
| Format code              | `ruff format .`                               |
| Package for Windows      | `.\scripts\package_windows.ps1`               |

---

## 🖨️ Startup diagnostics

The application prints how it was started, which mode is active, and whether reload is enabled. The same message is shown in the page.

Examples:

```text
Initializing NiceGui Windows Base from pyproject command in native mode with reload inactive.
Initializing NiceGui Windows Base from module in native mode with reload inactive.
Initializing NiceGui Windows Base from script in native mode with reload inactive.
Initializing NiceGui Windows Base from dev_run.py in web mode with reload active.
Initializing NiceGui Windows Base from package in native mode with reload inactive.
```

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

`app.py` resolves asset paths for both normal Python execution and packaged execution.

---

## 📚 Documentation

Start with the [documentation index](docs/README.md).

Main guides:

- [Development environment](docs/development_environment.md)
- [Execution modes](docs/execution_modes.md)
- [Windows packaging](docs/packaging_windows.md)
- [Code quality with Ruff](docs/code_quality.md)
- [Troubleshooting](docs/troubleshooting.md)
