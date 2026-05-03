# 🧯 Troubleshooting

This guide collects common issues for the current **NiceGUI Hello World** project.

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

## 🚀 `nicegui-hello-world` is not recognized

Possible causes:

- `.venv` is not active;
- editable installation was not run;
- the terminal was opened before installation;
- VS Code selected a different interpreter.

Fix:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,packaging]"
nicegui-hello-world
```

Diagnostic alternative:

```powershell
python -m nicegui_hello_world
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
nicegui-hello-world
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

Do not solve this by adding `__mp_main__` to `app.py`.

For packaged execution, keep the app guard as:

```python
if __name__ == "__main__":
    freeze_support()
    main()
```

Use `__mp_main__` only in `dev_run.py`, where `reload=True` needs it during development on Windows:

```python
if __name__ in {"__main__", "__mp_main__"}:
    main(development_mode=True)
```

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
    partial(create_ui, startup_message=startup_message),
    ...
)
```

Avoid rebuilding the message separately inside `create_ui(...)`, because that can cause the terminal and page text to drift over time.

---

## 🔗 Related documents

- [Python 3.13 setup on Windows](python_windows_setup.md)
- [VS Code setup](vscode_setup.md)
- [Execution modes](execution_modes.md)
- [Windows packaging](packaging_windows.md)
