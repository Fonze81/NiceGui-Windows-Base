# NiceGUI Hello World

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)

A minimal **NiceGUI Hello World template** for Windows development, native desktop execution, browser-based UI development, code quality with Ruff, and Windows executable packaging with direct PyInstaller.

---

## ✨ What is included

- Python package using `src` layout;
- project metadata, dependencies, entry point, package assets, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-hello-world`;
- browser-based development execution through `python dev_run.py`;
- startup diagnostics shown in the terminal and in the UI;
- packaged and normal asset resolution for the application icon and page image;
- PyInstaller packaging with executable icon, bundled assets, and Windows version metadata;
- VS Code recommendations and Ruff-on-save workspace settings;
- maintenance documentation in [`docs`](docs/README.md).

---

## 📁 Project structure

```text
NiceGUI Hello World/
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
│   └── nicegui_hello_world/
│       ├── assets/
│       │   ├── app_icon.ico
│       │   └── page_image.png
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── dev_run.py
├── pyproject.toml
└── README.md
```

---

## 🚀 Quick start

Create and activate a virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
```

Run in native desktop mode:

```powershell
nicegui-hello-world
```

Run in browser development mode with reload:

```powershell
python dev_run.py
```

---

## 🖨️ Startup diagnostics

The application prints how it was started, which mode is active, and whether reload is enabled. The same message is shown in the page.

Examples:

```text
Initializing NiceGUI Hello World from dev_run.py in web mode with reload active.
Initializing NiceGUI Hello World from pyproject command in native mode with reload inactive.
Initializing NiceGUI Hello World from package in native mode with reload inactive.
```

---

## 🖼️ Assets

Runtime assets are stored in:

```text
src
icegui_hello_worldssets
```

Current assets:

- `app_icon.ico` — used by `ui.run(favicon=...)` and by PyInstaller `--icon`;
- `page_image.png` — shown in the NiceGUI page.

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
