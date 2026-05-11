# 🧯 Troubleshooting

This guide collects common issues for the current **NiceGui Windows Base** project.

---

## 🐍 Python 3.13 is not found

Check installed versions:

```powershell
py -0p
```

If Python 3.13 is missing:

1. install Python 3.13 from the official website;
2. close and reopen PowerShell;
3. close and reopen VS Code;
4. restart Windows if needed.

See [Python 3.13 setup on Windows](python_windows_setup.md).

---

## ⚙️ `.venv` was created with the wrong Python version

Recreate it:

```powershell
Deactivate
Remove-Item -Recurse -Force .venv
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
pytest
```

---

## 🔐 PowerShell blocks `.venv` activation

Use a process-level policy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

See [PowerShell execution policy](powershell_execution_policy.md).

---

## 🚀 `nicegui-windows-base` is not recognized

Possible causes:

- `.venv` is not active;
- editable installation was not run;
- the terminal was opened before installation;
- VS Code selected a different interpreter.

Fix:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,packaging]"
nicegui-windows-base
```

Diagnostic alternative:

```powershell
python -m desktop_app
```

---

## 🧩 Imports appear unresolved in VS Code

Confirm:

- VS Code opened the repository root;
- the interpreter is `.venv\Scripts\python.exe`;
- editable installation completed.

Fix:

```powershell
python -m pip install -e ".[dev,packaging]"
```

Then reload VS Code:

```text
Ctrl + Shift + P > Developer: Reload Window
```

---

## 🧪 VS Code does not discover tests

Confirm that VS Code opened the repository root and that `.vscode\settings.json` enables pytest.

Expected settings include:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.cwd": "${workspaceFolder}",
  "python.testing.pytestArgs": ["tests"]
}
```

Then run:

```text
Ctrl + Shift + P > Python: Configure Tests
```

Choose `pytest` and the `tests` folder.

If discovery still fails, validate from the terminal:

```powershell
pytest --collect-only
```

---

## 🧪 Pytest import mismatch

Example symptom:

```text
import file mismatch
```

Possible causes:

- duplicate test module names were imported by path instead of importlib mode;
- stale `__pycache__` files exist;
- pytest was run from a subfolder instead of the repository root.

Fix:

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
pytest
```

The project config uses:

```toml
--import-mode=importlib
```

This reduces collisions when different folders contain files with the same base name.

---

## 📊 Coverage report is missing files

Run coverage from the repository root:

```powershell
pytest --cov=desktop_app --cov-report=term-missing
```

The coverage configuration in `pyproject.toml` points to:

```toml
source = ["desktop_app"]
```

If a new package or module is not shown, confirm that:

- it is below `src\desktop_app`;
- it is imported by tests;
- tests are not skipped;
- the command is running inside the correct `.venv`.

---

## 🔁 Startup logs appear duplicated in development mode

Likely cause:

```python
reload=True
```

On Windows, reload can create more than one process. Keep reload only in `dev_run.py`.

Normal execution should use:

```powershell
nicegui-windows-base
```

---

## 🔁 NiceGUI says `You must call ui.run()`

Confirm that `dev_run.py` uses the multiprocessing-safe guard:

```python
if __name__ in {"__main__", "__mp_main__"}:
    main(development_mode=True)
```

---

## ⚙️ Persistent `settings.toml` is missing

This is normal during first run. The application can load bundled defaults from:

```text
src\desktop_app\settings.toml
```

A persistent runtime file is needed only when settings are saved.

See [Settings subsystem](settings.md).

---

## ⚙️ Settings are written to the wrong folder

Check whether `DESKTOP_APP_ROOT` is set:

```powershell
Get-ChildItem Env:\DESKTOP_APP_ROOT
```

When set, it intentionally changes the runtime root.

Clear it:

```powershell
Remove-Item Env:\DESKTOP_APP_ROOT
```

---

## ⚙️ Packaged executable cannot find default settings

Confirm that the packaging script includes:

```powershell
--add-data $settingsData
```

Also confirm:

```powershell
Test-Path .\src\desktop_app\settings.toml
```

Then clean old outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## ⚙️ Invalid setting value is ignored or replaced

The settings mapper validates values before applying them to state.

Examples:

- `app.ui.theme` must be `light`, `dark`, or `system`;
- `app.log.rotate_max_bytes` must be a supported byte-size value;
- numeric window values must be valid integers;
- boolean fields must be valid booleans.

Fix the value in the persistent `settings.toml` or delete the persistent file to use bundled defaults again.

---

## 🧹 Ruff is not recognized

Install project development dependencies:

```powershell
python -m pip install -e ".[dev,packaging]"
```

Check:

```powershell
ruff check .
ruff format --check .
```

---

## 💾 Ruff does not run on save in VS Code

Confirm:

- Ruff extension is installed;
- `.vscode\settings.json` exists;
- VS Code opened the repository root;
- the active file is a Python file;
- Ruff is installed in `.venv`.

Manual check:

```powershell
ruff check .
```

---

## 📦 PyInstaller is missing during packaging

Check:

```powershell
python -m PyInstaller --version
```

If missing:

```powershell
python -m pip install -e ".[dev,packaging]"
```

Then run packaging again:

```powershell
.\scripts\package_windows.ps1
```

---

## 📦 Packaging script is blocked by PowerShell

Use:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

---

## 🧊 Old executable is still being tested

Clean old outputs:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## 📦 Packaged executable logs startup messages twice

Likely cause: a frozen multiprocessing child process is re-entering the application startup flow.

For packaged execution, keep the Windows-safe entry point in `app.py`:

```python
if __name__ == "__main__":
    freeze_support()
    main()
```

`dev_run.py` keeps the `__mp_main__` guard because `reload=True` can use multiprocessing during development on Windows.

After changing `app.py`, clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## 🖨️ Startup message differs between logs and page

The startup message should be built once in `main(...)` and reused for state, logs, and the NiceGUI page.

Expected pattern:

```python
startup_message = build_startup_message(...)
logger.info("Startup status: %s", startup_message)

ui.run(
    partial(build_main_page, startup_message=startup_message),
    ...
)
```

Avoid rebuilding the message separately inside `build_main_page(...)`, because that can cause the log and page text to drift over time.

---

## 🖼️ Icon does not appear

Confirm that the icon exists:

```powershell
Test-Path .\src\desktop_app\assets\app_icon.ico
```

If the executable icon did not update, clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

Windows Explorer may cache executable icons. If the file was rebuilt correctly but Explorer still shows the old icon, rename the executable or refresh/restart Explorer before retesting.

If the NiceGUI favicon does not appear in packaged mode, confirm that the packaging script still includes:

```powershell
--add-data $assetsData
```

---

## 🖼️ Page image does not appear

Confirm that the PNG exists:

```powershell
Test-Path .\src\desktop_app\assets\page_image.png
```

If the image does not appear only in packaged mode, confirm that the packaging script includes the full assets directory:

```powershell
--add-data $assetsData
```

Then clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## 🖼️ Packaged splash screen does not appear

Confirm that the packaging script includes `--splash` and that the image exists:

```powershell
Test-Path src\desktop_app\assets\splash_light.png
```

Then clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

During normal Python execution, no splash screen appears. The splash is a packaged-executable behavior.

If the splash still does not appear after packaging, confirm that the PyInstaller command includes both `--splash` and `--hidden-import pyi_splash`.

---

## 🖼️ Packaged splash screen does not close

Confirm that `register_lifecycle_handlers(native_mode=native_mode)` in `src\desktop_app\app.py` is called before `ui.run(...)`. It delegates splash setup through `register_splash_handler()` in `src\desktop_app\infrastructure\splash.py`:

```python
register_lifecycle_handlers(native_mode=native_mode)
```

The splash handler imports the optional `pyi_splash` module only when `sys.frozen` is true, stores the module reference, and registers `close_splash_once()` with `app.on_connect(...)`.

Also confirm that the packaging script keeps the hidden import:

```powershell
--hidden-import pyi_splash
```

---

## 🪟 Packaged executable opens a console window

Confirm that the PyInstaller arguments include:

```powershell
--windowed
```

Then clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

`--windowed` is required for the expected desktop behavior because the native NiceGUI window should open without an additional console window.

---

## 🏷️ Executable properties are missing

Confirm that the version info file exists:

```powershell
Test-Path .\scripts\version_info.txt
```

Confirm that PyInstaller is available in the active environment:

```powershell
python -m PyInstaller --version
```

If the command is not recognized, reinstall packaging dependencies:

```powershell
python -m pip install -e ".[packaging]"
```

Then package again:

```powershell
.\scripts\package_windows.ps1
```

If Windows Explorer still shows old properties, clean old outputs and rebuild:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## ⚖️ Packaging report was not created

Expected output:

```text
dist\packaging_report.md
```

If the report is missing, the PyInstaller packaging flow probably failed before the reporting step.

Check that PyInstaller is available in the active `.venv`:

```powershell
python -m PyInstaller --version
```

Then run the packaging script again:

```powershell
.\scripts\package_windows.ps1
```

The script should create:

```text
dist\nicegui-windows-base.exe
dist\packaging_report.md
```

---

## 📦 nicegui-pack is no longer used

The project previously compared `nicegui-pack` and direct PyInstaller packaging.

The project now uses direct PyInstaller only because it supports `--version-file`, `--windowed`, `--splash`, `--hidden-import pyi_splash`, bundled assets, and bundled settings without a second post-processing path.

Use this instead:

```powershell
.\scripts\package_windows.ps1
```

The script creates:

```text
dist\nicegui-windows-base.exe
dist\packaging_report.md
```

---

## 🪟 Native window opens outside the visible area

The application adjusts persisted coordinates against the current Windows monitor
work areas before positioning the native window. This safety check changes only
`x` and `y`; it does not reduce saved width or height. If the window is still not
reachable, disable persistence once in the persistent runtime file:

```toml
[app.window]
persist_state = false
```

Start the application again. It resets geometry to `WindowState` defaults and
saves the `window` settings group, while keeping `persist_state = false`.

Edit the correct file for the runtime:

| Runtime                 | File to edit                           |
| ----------------------- | -------------------------------------- |
| Normal Python execution | `<repository-root>\settings.toml`      |
| Packaged executable     | `<executable-directory>\settings.toml` |
| Custom root             | `%DESKTOP_APP_ROOT%\settings.toml`     |

Do not edit `src\desktop_app\settings.toml` expecting it to change an already
created persistent settings file. That source file is the bundled default
template.

---

## 🪟 Manual `x` and `y` changes are not reflected

Confirm that native mode is being used. Browser development mode does not create
a native desktop window, so native geometry is not applied there.

Also confirm the log contains a line similar to:

```text
Native window options prepared: size=(1024, 720), position=(100, 100), fullscreen=False, persist_state=True.
```

If the line shows the old values, the edited file is not the runtime settings
file that the application loaded.

---

## 🪟 Native window size is not saved

Resize events update `AppState.window` during runtime, but the TOML file is only
written when the native window closes or the application shuts down. Close the
application normally and then inspect the `[app.window]` section.

If `persist_state = false`, the application intentionally resets geometry and
does not save the live window size.

---

## 🔗 Related documents

- [Python 3.13 setup on Windows](python_windows_setup.md)
- [VS Code setup](vscode_setup.md)
- [Execution modes](execution_modes.md)
- [Settings subsystem](settings.md)
- [Application state](state.md)
- [Native window persistence](native_window_persistence.md)
- [Logging subsystem](logging.md)
- [Windows packaging](packaging_windows.md)
