# NiceGUI Hello World

[![Python](https://img.shields.io/badge/python-3.13.X-blue)](https://www.python.org/downloads/)

A Hello World template for NiceGUI projects.

## Development environment

This project currently targets Python 3.13.x or lower for the native mode dependency chain used on Windows.

See the setup guide for installation, execution, and packaging details:

- [Development Environment Setup](docs/development_environment.md)

## Run locally

```powershell
python app.py
```

## Package for Windows

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script, run it with a process-level policy bypass:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

The script installs the dependencies from `requirements.txt`, checks that `pyinstaller` is available, cleans previous build outputs, runs `nicegui-pack`, and validates that the expected executable was created.
