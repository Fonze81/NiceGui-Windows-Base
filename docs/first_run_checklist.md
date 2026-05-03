# ✅ First Run Checklist

Use this checklist to validate a new clone or a new Windows machine.

---

## 📁 Project folder

- [ ] I opened the repository root folder.
- [ ] The folder contains `pyproject.toml`.
- [ ] The folder contains `src`.
- [ ] The folder contains `docs`.
- [ ] The folder contains `dev_run.py`.
- [ ] The folder contains `scripts\package_windows.ps1`.
- [ ] The folder contains `src\nicegui_hello_world\assets\app_icon.ico`.
- [ ] The folder contains `src\nicegui_hello_world\assets\page_image.png`.
- [ ] The folder contains `src\nicegui_hello_world\assets\splash_light.png`.

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
- [ ] VS Code opened the repository root, not only `src` or `docs`.
- [ ] The selected interpreter is `.venv\Scripts\python.exe`.
- [ ] Recommended extensions were reviewed.
- [ ] Ruff runs on save for Python files.

---

## ▶️ Execution

- [ ] Normal command works:

```powershell
nicegui-hello-world
```

- [ ] Module execution works:

```powershell
python -m nicegui_hello_world
```

- [ ] Direct script execution works:

```powershell
python src\nicegui_hello_world\app.py
```

- [ ] Development mode works:

```powershell
python dev_run.py
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

---

## 📦 Packaging

- [ ] PyInstaller is available:

```powershell
pyinstaller --version
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
dist\nicegui-hello-world.exe
```

- [ ] The executable opens the native app.

---

## 🔗 Related documents

- [Development environment](development_environment.md)
- [VS Code setup](vscode_setup.md)
- [Execution modes](execution_modes.md)
- [Troubleshooting](troubleshooting.md)

---

## 📦 Packaging validation

- [ ] `python -m pip install -e ".[dev,packaging]"` completed successfully.
- [ ] `.\scripts\package_windows.ps1` creates `dist\nicegui-hello-world.exe`.
- [ ] The executable has the project icon.
- [ ] The executable shows a splash screen during startup.
- [ ] The executable opens the NiceGUI native window.
- [ ] The page displays the PNG image and startup status message.
- [ ] `dist\packaging_report.md` is created.
