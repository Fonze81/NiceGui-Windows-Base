# 🧯 Troubleshooting

This guide collects common issues for the current **NiceGui Windows Base** project.

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

---

## 🖼️ Packaged splash screen does not close

Confirm that `main(...)` in `src\desktop_app\app.py` calls:

```python
register_pyinstaller_splash_handler()
```

The handler registers `pyinstaller_splash.close_once` with `app.on_connect(...)` only when PyInstaller splash support is available. `app.py` imports the optional `pyi_splash` module dynamically during startup only when `sys.frozen` is true and stores the module reference for the later callback. This avoids importing the module too late, in a context where PyInstaller may no longer expose it. The controller calls `close()` only when the module exists and keeps an internal close-attempt flag to avoid repeated close attempts during reconnects.

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
pyinstaller --version
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

## 📦 Packaged executable prints startup messages twice

Likely cause: a frozen multiprocessing child process is re-entering the application startup flow.

For packaged execution, keep the standard entry point in `app.py`:

```python
if __name__ == "__main__":
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

## 🖨️ Startup message differs between terminal and page

The startup message should be built once in `main(...)` and reused for both terminal output and the NiceGUI page.

Expected pattern:

```python
startup_message = build_startup_message(...)
print(startup_message)

ui.run(
    partial(build_main_page, startup_message=startup_message),
    ...
)
```

Avoid rebuilding the message separately inside `build_main_page(...)`, because that can cause the terminal and page text to drift over time.

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

## 🏷️ Executable properties are missing

Confirm that the version info file exists:

```powershell
Test-Path .\scripts\version_info.txt
```

Confirm that PyInstaller is available in the active environment:

```powershell
pyinstaller --version
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
pyinstaller --version
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

## ⏱️ Cannot convert `System.Object[]` to `System.TimeSpan`

Error example:

```text
Cannot convert the "System.Object[]" value of type "System.Object[]" to type "System.TimeSpan".
```

Cause: a PowerShell function that should return only elapsed time also wrote native command output to the success output pipeline.

Fix: execute native commands through `Invoke-NativeCommand`, which writes command output to the host and keeps the function return clean:

```powershell
& $Command @Arguments 2>&1 | ForEach-Object {
    Write-Host $_
}
```

Then assign the elapsed time with an explicit type:

```powershell
[TimeSpan]$pyInstallerElapsed = Invoke-PyInstallerBuild
```

---

## 📦 NativeCommandError from PyInstaller log output

Error example:

```text
pyinstaller.exe : 204 INFO: PyInstaller: 6.20.0, contrib hooks: 2026.4
CategoryInfo          : NotSpecified: ... RemoteException
FullyQualifiedErrorId : NativeCommandError
```

Cause: PyInstaller can write normal progress logs to stderr. The packaging script also uses `$ErrorActionPreference = "Stop"` so real errors stop the build. If stderr is redirected with `2>&1` without temporarily relaxing error handling, PowerShell can treat normal stderr output as `NativeCommandError`.

Fix: `Invoke-NativeCommand` must temporarily set native command error handling to a non-terminating mode and then validate the native command exit code explicitly:

```powershell
$ErrorActionPreference = "Continue"
& $Command @Arguments 2>&1 | ForEach-Object {
    Write-Host $_
}
$exitCode = $LASTEXITCODE
```

The script should then throw only when `$exitCode` is different from zero.

This keeps PyInstaller logs visible while still failing correctly when the build command actually fails.

---

## 📦 nicegui-pack is no longer used

The project previously compared `nicegui-pack` and direct PyInstaller packaging.

Measured results were similar:

| Packager     |     Size |    Time |
| ------------ | -------: | ------: |
| nicegui-pack | 41.26 MB | 80.54 s |
| PyInstaller  | 40.37 MB | 78.36 s |

The project now uses direct PyInstaller only because it supports `--version-file` and keeps future splash screen configuration available without a second post-processing path.

If old documentation or terminal commands mention `nicegui-pack`, use this instead:

```powershell
.\scripts\package_windows.ps1
```

The script now creates:

```text
dist\nicegui-windows-base.exe
dist\packaging_report.md
```

---

## 🔗 Related documents

- [Python 3.13 setup on Windows](python_windows_setup.md)
- [VS Code setup](vscode_setup.md)
- [Execution modes](execution_modes.md)
- [Windows packaging](packaging_windows.md)
