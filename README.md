# NiceGUI Hello World

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)

A Hello World template for NiceGUI projects.

## Development environment

This project currently targets Python 3.13.x for the native mode dependency chain used on Windows.

See the setup guide for installation, execution, and packaging details:

- [Development Environment Setup](docs/development_environment.md)

## Project structure

```text
.
├── docs/
│   └── development_environment.md
├── scripts/
│   └── package_windows.ps1
├── src/
│   └── nicegui_hello_world/
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── pyproject.toml
└── README.md
```

## Install

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[packaging]"
```

## Run locally

Use the project command:

```powershell
nicegui-hello-world
```

Alternative module execution:

```powershell
python -m nicegui_hello_world
```

Direct script execution remains useful for quick diagnostics:

```powershell
python src\nicegui_hello_world\app.py
```

## Package for Windows

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script, run it with a process-level policy bypass:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

The application uses an explicit NiceGUI root function in `ui.run(...)` so the packaged executable does not rely on NiceGUI script mode.
