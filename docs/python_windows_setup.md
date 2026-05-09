# 🐍 Python 3.13 Setup on Windows

This guide explains how to install, validate, and prepare Python 3.13 for the current **NiceGui Windows Base** project.

---

## 📌 When should you use this guide?

Use this guide when:

- Python is not installed;
- `py -3.13` does not work;
- Windows still shows an older Python version;
- the `.venv` needs to be created or recreated;
- VS Code uses the wrong Python interpreter;
- dependencies fail after changing Python versions.

---

## 🧭 Recommended Python version

Use Python 3.13.x.

The project defines this rule in `pyproject.toml`:

```toml
requires-python = ">=3.13,<3.14"
```

| Python version       | Project usage                                           |
| -------------------- | ------------------------------------------------------- |
| Python 3.12 or older | Not supported by this project configuration             |
| Python 3.13.x        | Recommended                                             |
| Python 3.14 or newer | Not recommended for the current native dependency chain |

---

## ❓ Why Python 3.13?

This project uses NiceGUI in native mode and packages a Windows executable. The native dependency chain includes `pywebview`, and on Windows that can involve `pythonnet`.

A previous installation attempt showed `pythonnet` wheel build failure when the environment involved Python 3.14. To keep the project reproducible now, use Python 3.13.x.

Review compatibility later through the official projects:

- `pythonnet`;
- `pywebview`;
- `NiceGUI`;
- `PyInstaller`.

Before changing the Python rule, confirm that:

- `pythonnet` supports the new Python version;
- `pywebview` installs successfully;
- native execution opens correctly;
- browser development mode opens correctly;
- the full pytest suite passes;
- PyInstaller generates a working executable through `scripts\package_windows.ps1`.

---

## 📥 1. Download Python

Download the official Windows installer:

```text
https://www.python.org/downloads/windows/
```

Prefer the official installer because it integrates well with the Windows Python launcher `py`.

---

## ⚙️ 2. Install Python

During installation:

1. install Python 3.13.x;
2. enable **Add python.exe to PATH**, if the option appears;
3. keep the recommended installer options;
4. close and reopen PowerShell after installation.

On Windows, a newly installed Python version may not appear in a terminal that was already open. Close and reopen PowerShell or VS Code first. Restart Windows if the old version is still shown.

---

## 🔎 3. List installed Python versions

```powershell
py -0p
```

Expected example:

```text
 -V:3.13 *        C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe
```

The exact path can be different. The important part is that Python 3.13 is listed.

---

## ✅ 4. Confirm Python 3.13

```powershell
py -3.13 --version
```

Expected result:

```text
Python 3.13.x
```

Confirm `pip`:

```powershell
py -3.13 -m pip --version
```

If `pip` is missing:

```powershell
py -3.13 -m ensurepip --upgrade
py -3.13 -m pip install --upgrade pip
```

---

## 📂 5. Enter the repository root

Use the folder that contains:

```text
pyproject.toml
```

Example:

```powershell
cd C:\path\to\NiceGui-Windows-Base
```

Do not create `.venv` inside `src`, `docs`, `scripts`, `tests`, or another subfolder.

---

## ⚙️ 6. Create `.venv`

```powershell
py -3.13 -m venv .venv
```

The `.venv` folder stores the project-local Python interpreter and dependencies.

Do not commit `.venv` to Git.

---

## ▶️ 7. Activate `.venv`

```powershell
.\.venv\Scripts\Activate.ps1
```

Expected terminal prefix:

```text
(.venv) PS C:\path\to\NiceGui-Windows-Base>
```

Confirm active Python:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

Expected executable path:

```text
<repository-root>\.venv\Scripts\python.exe
```

If activation is blocked, see [PowerShell execution policy](powershell_execution_policy.md).

---

## 📦 8. Upgrade pip and install the project

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
```

---

## ✅ 9. Validate the environment

Compile Python files:

```powershell
python -m compileall -q src dev_run.py
```

Run tests:

```powershell
pytest
```

Run the app:

```powershell
nicegui-windows-base
```

Run browser development mode:

```powershell
python dev_run.py
```

---

## 🧯 Recovery after using the wrong Python version

If `.venv` was created with the wrong Python version:

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

## 🔗 Related documents

- [Development environment](development_environment.md)
- [PowerShell execution policy](powershell_execution_policy.md)
- [VS Code setup](vscode_setup.md)
- [Code quality](code_quality.md)
- [Troubleshooting](troubleshooting.md)
