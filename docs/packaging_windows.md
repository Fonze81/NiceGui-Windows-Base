# 📦 Windows Packaging

This guide explains the current Windows executable packaging flow.

The project uses:

```text
scripts\package_windows.ps1
```

The script packages the application with `nicegui-pack`.

---

## ✅ Prerequisites

Activate `.venv` and install the project with packaging tools:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,packaging]"
```

Confirm PyInstaller is available:

```powershell
pyinstaller --version
```

---

## ▶️ Validate before packaging

Run the normal app first:

```powershell
nicegui-hello-world
```

Expected message:

```text
Initializing NiceGUI Hello World from pyproject command in native mode with reload inactive.
```

Also validate module execution:

```powershell
python -m nicegui_hello_world
```

---

## 🧹 Optional clean before packaging

The packaging script already removes previous `build`, `dist`, and `.spec` outputs.

Manual cleanup, if needed:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
```

---

## 🛠️ Run the packaging script

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

---

## 📄 Current packaging behavior

The script currently:

1. installs the project in editable mode with packaging dependencies;
2. checks if `pyinstaller` is available;
3. removes previous build outputs;
4. runs `nicegui-pack`;
5. checks whether `nicegui-pack` failed;
6. confirms that the expected executable exists.

The package entry file is:

```text
src\nicegui_hello_world\app.py
```

The expected executable is:

```text
dist\nicegui-hello-world.exe
```

---

## 📄 Current nicegui-pack command shape

The script uses a command equivalent to:

```powershell
nicegui-pack `
    --onefile `
    --windowed `
    --clean `
    --noconfirm `
    --name "nicegui-hello-world" `
    src\nicegui_hello_world\app.py
```

---

## 🧠 Why `ui.run(create_ui, ...)` matters

The application uses an explicit root function:

```python
ui.run(create_ui, native=native_mode, reload=reload_enabled, ...)
```

This avoids NiceGUI script-mode issues during packaging. Without an explicit root function, a packaged executable can make NiceGUI try to execute the executable path as Python source, which can fail because the executable is binary.

---

## 🧪 Test the executable

After packaging:

```powershell
.\dist\nicegui-hello-world.exe
```

Expected startup message:

```text
Initializing NiceGUI Hello World from package in native mode with reload inactive.
```

Confirm that:

- the native window opens;
- the Hello NiceGUI interface appears;
- no error appears during startup;
- the app closes correctly.

---

## ⚠️ Important current limitations

The current packaging flow does not configure:

- custom executable icon;
- splash screen;
- Windows version metadata;
- custom `.spec` file;
- external runtime assets.

Those should be documented only when they are actually introduced into the project.

---

## 🔗 Related documents

- [Execution modes](execution_modes.md)
- [PowerShell execution policy](powershell_execution_policy.md)
- [Troubleshooting](troubleshooting.md)
