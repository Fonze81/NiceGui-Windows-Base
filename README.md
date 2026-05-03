# NiceGUI Hello World

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/lint%20%26%20format-ruff-46aef7)](https://docs.astral.sh/ruff/)

A minimal **NiceGUI Hello World template** for Windows development, native desktop execution, browser-based UI development, code quality with Ruff, and Windows executable packaging.

---

## ✨ What is included

- Python package using `src` layout;
- project metadata, dependencies, entry point, and Ruff configuration in `pyproject.toml`;
- normal native execution through `nicegui-hello-world`;
- browser-based development execution through `python dev_run.py`;
- startup diagnostics showing execution source, mode, and reload status;
- Ruff linting and formatting;
- VS Code extension recommendations and Ruff-on-save workspace settings;
- Windows packaging script using `nicegui-pack`.

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
│   └── package_windows.ps1
├── src/
│   └── nicegui_hello_world/
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
nicegui-hello-world
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
| Run native app           | `nicegui-hello-world`                         |
| Run as module            | `python -m nicegui_hello_world`               |
| Run app script directly  | `python src\nicegui_hello_world\app.py`       |
| Run web development mode | `python dev_run.py`                           |
| Check code               | `ruff check .`                                |
| Check formatting         | `ruff format --check .`                       |
| Format code              | `ruff format .`                               |
| Package for Windows      | `.\scripts\package_windows.ps1`               |

---

## 🖨️ Startup diagnostics

The application prints how it was started, which mode is active, and whether reload is enabled.

Examples:

```text
Initializing NiceGUI Hello World from pyproject command in native mode with reload inactive.
Initializing NiceGUI Hello World from module in native mode with reload inactive.
Initializing NiceGUI Hello World from script in native mode with reload inactive.
Initializing NiceGUI Hello World from dev_run.py in web mode with reload active.
Initializing NiceGUI Hello World from package in native mode with reload inactive.
```

Details are documented in [Execution modes](docs/execution_modes.md).

---

## 📚 Documentation

- [Documentation index](docs/README.md)
- [Development environment](docs/development_environment.md)
- [Python 3.13 setup on Windows](docs/python_windows_setup.md)
- [VS Code setup](docs/vscode_setup.md)
- [PowerShell execution policy](docs/powershell_execution_policy.md)
- [Execution modes](docs/execution_modes.md)
- [Code quality with Ruff](docs/code_quality.md)
- [Windows packaging](docs/packaging_windows.md)
- [First run checklist](docs/first_run_checklist.md)
- [Troubleshooting](docs/troubleshooting.md)
