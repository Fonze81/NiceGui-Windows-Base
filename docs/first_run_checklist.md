# ✅ First Run Checklist

Use this checklist to validate a new clone or a new Windows machine.

---

## 📁 Project folder

- [ ] I opened the repository root folder.
- [ ] The folder contains `pyproject.toml`.
- [ ] The folder contains `README.md`.
- [ ] The folder contains `CHANGELOG.md`.
- [ ] The folder contains `src`.
- [ ] The folder contains `docs`.
- [ ] The folder contains `tests`.
- [ ] The folder contains `dev_run.py`.
- [ ] The folder contains `scripts\clean_project.ps1`.
- [ ] The folder contains `scripts\package_windows.ps1`.
- [ ] The folder contains `scripts\version_info.txt`.
- [ ] The folder contains `src\desktop_app\settings.toml`.
- [ ] The folder contains `src\desktop_app\assets\app_icon.ico`.
- [ ] The folder contains `src\desktop_app\assets\logo.png`.
- [ ] The folder contains `src\desktop_app\assets\page_image.png`.
- [ ] The folder contains `src\desktop_app\assets\splash_light.png`.

---

## 🐍 Python

- [ ] Python 3.13 is installed.
- [ ] This command works:

```powershell
py -3.13 --version
```

- [ ] The displayed version is:

```text
Python 3.13.x
```

- [ ] The Python launcher lists Python 3.13:

```powershell
py -0p
```

---

## ⚙️ Virtual environment

- [ ] I created `.venv` in the repository root:

```powershell
py -3.13 -m venv .venv
```

- [ ] I activated `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
```

- [ ] The terminal shows `(.venv)`.
- [ ] `python --version` returns `Python 3.13.x`.
- [ ] `python -c "import sys; print(sys.executable)"` points to `.venv`.

---

## 🔐 PowerShell

- [ ] If activation was blocked, I used:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

- [ ] I activated `.venv` again after applying the temporary policy.

---

## 📦 Installation

- [ ] I upgraded `pip`:

```powershell
python -m pip install --upgrade pip
```

- [ ] I installed the project:

```powershell
python -m pip install -e ".[dev,packaging]"
```

---

## 🧰 VS Code

- [ ] VS Code is installed.
- [ ] VS Code opened the repository root, not only `src`, `docs`, `scripts`, or `tests`.
- [ ] The selected interpreter is `.venv\Scripts\python.exe`.
- [ ] Recommended extensions were reviewed.
- [ ] Ruff runs on save for Python files.
- [ ] pytest test discovery finds tests from the `tests` folder.
- [ ] Markdown linting is available for documentation files.

---

## ▶️ Execution

- [ ] Normal command works:

```powershell
nicegui-windows-base
```

- [ ] Module execution works:

```powershell
python -m desktop_app
```

- [ ] Direct script execution works:

```powershell
python src\desktop_app\app.py
```

- [ ] Development mode works:

```powershell
python dev_run.py
```

---

## ⚙️ Settings

- [ ] The bundled template exists:

```powershell
Test-Path .\src\desktop_app\settings.toml
```

- [ ] The template version is aligned with `pyproject.toml`:

```text
0.6.0
```

- [ ] Normal execution can start even when `<repository-root>\settings.toml` does not exist.
- [ ] When settings are saved later, they are written to the runtime root.
- [ ] `app.window.persist_state` exists in the `[app.window]` section.
- [ ] For isolated diagnostics, `DESKTOP_APP_ROOT` can point to a temporary folder.

Example:

```powershell
$env:DESKTOP_APP_ROOT = "C:\Temp\nicegui-windows-base-test"
nicegui-windows-base
```

After the diagnostic, clear it:

```powershell
Remove-Item Env:\DESKTOP_APP_ROOT
```

---

## 🪟 Native window persistence

- [ ] Normal native execution restores size from `[app.window]`.
- [ ] Normal native execution restores position from `[app.window]`.
- [ ] Moving and resizing the native window updates `settings.toml` after close.
- [ ] Setting `app.window.persist_state = false` resets geometry to defaults after one run.
- [ ] A manually invalid off-screen position is clamped back to a visible monitor area.
- [ ] Multi-monitor setups with a monitor to the left or above the primary display keep the window reachable.

Useful focused tests:

```powershell
pytest tests/application
pytest tests/infrastructure/test_native_window_state.py
pytest tests/infrastructure/test_lifecycle.py
pytest tests/ui
```

---

## 🧪 Tests

- [ ] Syntax compilation passes:

```powershell
python -m compileall -q src dev_run.py
```

- [ ] Full pytest suite passes:

```powershell
pytest
```

- [ ] Coverage report works:

```powershell
pytest --cov=desktop_app --cov-report=term-missing
```

---

## 🧹 Quality

- [ ] Ruff check passes:

```powershell
ruff check .
```

- [ ] Formatting check passes:

```powershell
ruff format --check .
```

- [ ] Cleanup preview works without deleting files:

```powershell
.\scripts\clean_project.ps1 -DryRun
```

- [ ] Default cleanup behavior is understood: `IncludeBuildArtifacts` is `true`, so `build`, `dist`, and generated `*.spec` files are removed unless `-IncludeBuildArtifacts:$false` is used.

---

## 📦 Packaging

- [ ] PyInstaller is available:

```powershell
python -m PyInstaller --version
```

- [ ] Packaging script runs:

```powershell
.\scripts\package_windows.ps1
```

- [ ] If blocked, this command works:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

- [ ] The executable exists:

```text
dist\nicegui-windows-base.exe
```

- [ ] The executable opens the native app.
- [ ] The executable has the project icon.
- [ ] The executable shows a splash screen during startup.
- [ ] The executable opens without an extra console window.
- [ ] The page displays the PNG image and startup status message.
- [ ] `dist\packaging_report.md` is created.
- [ ] `dist\logs\app.log` is created after the packaged executable starts.
- [ ] Packaged settings resolve next to the executable.
- [ ] The bundled default `settings.toml` is included in the packaged build.
- [ ] The log contains startup source, runtime mode, settings path, native window geometry, NiceGUI startup, page build, window persistence, and shutdown narrative.

---

## 🔗 Related documents

- [Development environment](development_environment.md)
- [VS Code setup](vscode_setup.md)
- [Execution modes](execution_modes.md)
- [Settings subsystem](settings.md)
- [Application state](state.md)
- [Native window persistence](native_window_persistence.md)
- [Logging subsystem](logging.md)
- [Code quality](code_quality.md)
- [Troubleshooting](troubleshooting.md)
