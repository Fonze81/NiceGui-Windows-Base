# 🧰 Development Environment Setup

This guide explains how to prepare a basic development environment for the **NiceGUI Hello World** repository on Windows.

The goal is to help developers install the required tools, create a Python 3.13 virtual environment, activate it, install the project in editable mode, run the NiceGUI application in native mode, use web development mode while creating the interface, organize code with Ruff, package it as a Windows executable with nicegui-pack, and open the project in Visual Studio Code.

---

## 📌 When should you use this guide?

Use this guide when:

- Python is not installed yet;
- Visual Studio Code is not installed yet;
- the repository was just cloned or created;
- you need to create a local `.venv`;
- PowerShell blocks virtual environment activation;
- VS Code needs to be configured to use the project environment;
- the project needs to be installed from `pyproject.toml`;
- the local NiceGUI application needs to be executed;
- NiceGUI native mode needs to be tested;
- the interface needs to be developed faster in browser mode;
- code quality needs to be checked or formatted with Ruff;
- the application needs to be packaged as a Windows executable with `nicegui-pack`.

---

## 🧭 Recommended setup flow

Follow this order:

1. Install Python 3.13.
2. Install Visual Studio Code.
3. Open the repository folder in VS Code.
4. Create the `.venv` with Python 3.13.
5. Activate the `.venv`.
6. Apply a temporary PowerShell execution policy only if activation is blocked.
7. Select the `.venv` interpreter in VS Code.
8. Install the project in editable mode.
9. Run the NiceGUI application through the project command.
10. Use web development mode while creating the interface.
11. Check and format code with Ruff.
12. Package the application as a Windows executable.
13. Confirm that Python runs from the virtual environment.

---

## 🐍 1. Install Python 3.13

Download Python from the official website:

```text
https://www.python.org/downloads/windows/
```

Use **Python 3.13.x** for this project.

This project uses NiceGUI native mode, which depends on `pywebview`. On Windows, `pywebview` can depend on `pythonnet`. The current native-mode dependency chain has shown installation issues when the virtual environment is created with Python 3.14, so Python 3.13 should be used for this project until the dependency chain officially supports newer Python versions.

During Python installation:

1. use the official Windows installer;
2. install Python **3.13.x**;
3. enable **Add python.exe to PATH**, if the option appears;
4. keep the recommended installation options unless you have a specific reason to change them;
5. close and reopen PowerShell after installation.

On Windows, a newly installed Python version may not appear immediately in an already opened terminal. Start by closing and reopening PowerShell or VS Code.

If the old Python version is still being used after reopening the terminal, restart Windows and check again.

After installing Python, open a new PowerShell window and check if Python 3.13 is available:

```powershell
py -3.13 --version
```

Expected result:

```text
Python 3.13.x
```

You can also list the Python versions detected by the Python launcher:

```powershell
py -0p
```

If Python 3.13 does not appear, install Python 3.13, close and reopen PowerShell, and restart Windows if the new version is still not detected.

Avoid creating the `.venv` with Python 3.14 for this project.

### Check future pythonnet support

The Python 3.13 limit should be reviewed when `pythonnet` adds official support for newer Python versions.

Use these links to check future compatibility:

- PyPI project page: <https://pypi.org/project/pythonnet/>
- GitHub repository: <https://github.com/pythonnet/pythonnet>
- GitHub releases: <https://github.com/pythonnet/pythonnet/releases>
- GitHub issue for Python 3.14 support: <https://github.com/pythonnet/pythonnet/issues/2610>

Before changing the project to a newer Python version, confirm that:

- the PyPI `Requires-Python` field allows the new version;
- a compatible `pythonnet` release exists;
- `pywebview` installs successfully on Windows;
- `nicegui-hello-world` opens the NiceGUI native window correctly;
- `python dev_run.py` opens the browser-based development mode correctly;
- `ruff check .` works correctly;
- `scripts\package_windows.ps1` generates the Windows executable correctly.

---

## 🧰 2. Install Visual Studio Code

Download Visual Studio Code from the official website:

```text
https://code.visualstudio.com/
```

During installation, the default options are usually enough.

For easier daily usage on Windows, you may enable:

- **Open with Code** action for files;
- **Open with Code** action for folders;
- registering VS Code as an editor for supported file types;
- adding VS Code to the system PATH.

These options are helpful, but not mandatory.

---

## 📂 3. Open the repository folder

Open VS Code and choose:

```text
File > Open Folder
```

Select the root folder of the repository.

The root folder should contain files and folders such as:

```text
README.md
pyproject.toml
dev_run.py
docs
scripts
src
```

Avoid opening only the `src` folder. Keeping VS Code opened at the repository root makes configuration, paths, editable installation, and terminal usage easier.

---

## 🧱 4. Understand the src layout and pyproject.toml

The project uses a `src` layout and `pyproject.toml`.

```text
.
├── .vscode/
│   └── extensions.json
├── src/
│   └── nicegui_hello_world/
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── scripts/
├── docs/
├── dev_run.py
├── pyproject.toml
└── README.md
```

The application code lives inside:

```text
src\nicegui_hello_world
```

The project metadata, Python version rule, dependencies, optional development dependencies, optional packaging dependencies, command-line entry point, and Ruff configuration are defined in:

```text
pyproject.toml
```

The main generated command is:

```powershell
nicegui-hello-world
```

This command is available after editable installation.

---

## ⚙️ 5. Create the virtual environment with Python 3.13

Open PowerShell in the repository root folder and run:

```powershell
py -3.13 -m venv .venv
```

This command explicitly creates the virtual environment with Python 3.13.

After creating the `.venv`, activate it and confirm the version before installing dependencies.

Do not commit the `.venv` folder to Git.

---

## ▶️ 6. Activate the virtual environment

From the repository root folder, run:

```powershell
.\.venv\Scripts\Activate.ps1
```

When activation works, PowerShell usually shows something like:

```text
(.venv) PS C:\path\to\NiceGUI-Hello-World>
```

Then confirm which Python is active:

```powershell
python --version
```

Expected result:

```text
Python 3.13.x
```

You can also confirm the executable path:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected result: the path should point to the repository `.venv`, similar to:

```text
C:\path\to\NiceGUI-Hello-World\.venv\Scripts\python.exe
```

If the active version is Python 3.14, remove the `.venv` and recreate it with Python 3.13.

---

## 🔐 7. Resolve PowerShell activation blocking

PowerShell may block virtual environment activation with an error similar to:

```text
running scripts is disabled on this system
```

When this happens, apply a temporary process-level policy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the `.venv` again:

```powershell
.\.venv\Scripts\Activate.ps1
```

This policy applies only to the current PowerShell window.

After closing the terminal, the temporary bypass no longer applies.

Avoid changing machine-wide or permanent execution policies unless you understand the impact or your company allows it.

---

## 🐍 8. Select the `.venv` interpreter in VS Code

In VS Code:

1. press `Ctrl + Shift + P`;
2. search for `Python: Select Interpreter`;
3. select:

```text
.venv\Scripts\python.exe
```

If the interpreter does not appear automatically, choose **Enter interpreter path** and select:

```text
<repository-root>\.venv\Scripts\python.exe
```

This helps VS Code use the same Python 3.13 environment that was created for the repository.

After selecting the interpreter, open a new VS Code terminal and run:

```powershell
python --version
```

Expected result:

```text
Python 3.13.x
```

---

## 📦 9. Install the project in editable mode

With the `.venv` activated, upgrade `pip`:

```powershell
python -m pip install --upgrade pip
```

Then install the project in editable mode with development and packaging dependencies:

```powershell
python -m pip install -e ".[dev,packaging]"
```

This reads dependency information from `pyproject.toml`.

Editable installation is useful because:

- Python can import the package from the `src` layout;
- the `nicegui-hello-world` command becomes available;
- `python -m nicegui_hello_world` works;
- `python dev_run.py` can import the installed package;
- Ruff is installed for linting and formatting;
- packaging dependencies such as PyInstaller are installed;
- future package metadata can evolve in one central file.

---

---

## 🖨️ Startup message

The application prints startup information from `main(...)` in `src\nicegui_hello_world\app.py`.

The message shows:

- who started the application;
- whether it is running in native or web mode;
- whether reload is active or inactive.

Expected examples:

```text
Initializing NiceGUI Hello World from pyproject command in native mode with reload inactive.
Initializing NiceGUI Hello World from script in native mode with reload inactive.
Initializing NiceGUI Hello World from module in native mode with reload inactive.
Initializing NiceGUI Hello World from dev_run.py in web mode with reload active.
Initializing NiceGUI Hello World from package in native mode with reload inactive.
```

The source is detected as follows:

| Source | How it is identified |
|---|---|
| `dev_run.py` | `dev_run.py` calls `main(development_mode=True)` |
| `package` | `is_packaged()` detects a packaged executable |
| `pyproject command` | the command created by `[project.scripts]` starts the app |
| `module` | `python -m nicegui_hello_world` starts the app |
| `script` | `src\nicegui_hello_world\app.py` starts the app directly |

When `development_mode=True`, `main(...)` uses an explicit `if` to select the execution behavior:

```python
if development_mode:
    native_mode = False
    reload_enabled = True
else:
    native_mode = True
    reload_enabled = False
```

For normal execution, `development_mode` stays disabled, so the app uses native mode with reload disabled.

The packaged check is isolated in `is_packaged()`, while startup source detection is kept in `identify_startup_source(...)` to keep `main(...)` readable without adding heavy structure.

---

## ▶️ 10. Run the NiceGUI application normally

After installing the project, run the application from the repository root:

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

The normal application runs in native mode and is closer to the packaged executable behavior.

---

## 🌐 11. Run in web development mode

Use `dev_run.py` while creating or adjusting the interface:

```powershell
python dev_run.py
```

This command calls:

```python
main(development_mode=True)
```

Then `main(...)` starts the same UI in the browser with native mode disabled and reload enabled.

This mode is useful while building the web interface because:

- the browser is faster for visual iteration;
- `reload=True` reloads the app when code changes;
- the native desktop window does not need to be restarted manually after every small UI change;
- development stays separate from the native and packaged execution path.

Use this mode only for development.

### Windows multiprocessing guard

On Windows, reload mode uses multiprocessing and can re-run the script using the `__mp_main__` module name.

For this reason, `dev_run.py` must use:

```python
if __name__ in {"__main__", "__mp_main__"}:
    main()
```

If the guard only checks `__main__`, NiceGUI reload mode can fail with:

```text
You must call ui.run() to start the server.
```

---

## 🧹 12. Organize code with Ruff

Ruff is used as the project linting and formatting tool.

The configuration lives in:

```text
pyproject.toml
```

This keeps style rules close to the package metadata and avoids adding another configuration file while the project is still small.

### Ruff on save in VS Code

The project includes this workspace file:

```text
.vscode/settings.json
```

It enables Ruff automatically when a Python file is saved in VS Code.

Current settings:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

This configuration means:

- `editor.defaultFormatter` makes Ruff the Python formatter;
- `editor.formatOnSave` formats Python files when they are saved;
- `source.fixAll.ruff` applies safe Ruff fixes on save;
- `source.organizeImports.ruff` organizes imports with Ruff on save.

The Ruff-specific actions are used instead of generic `source.fixAll` and `source.organizeImports` so VS Code does not accidentally run other extensions for those actions.

The value `"explicit"` means the action runs when the file is explicitly saved. This is usually safer than running formatting and fixes continuously during automatic background saves.



Run lint checks:

```powershell
ruff check .
```

Check formatting without changing files:

```powershell
ruff format --check .
```

Apply safe lint fixes:

```powershell
ruff check --fix .
```

Format code:

```powershell
ruff format .
```

Recommended validation before committing changes:

```powershell
ruff check .
ruff format --check .
```

Use `ruff check --fix .` and `ruff format .` when you intentionally want Ruff to modify files.

### Current Ruff configuration

The project uses:

```toml
[tool.ruff]
line-length = 88
target-version = "py313"
src = ["src"]
extend-exclude = [
    ".venv",
    "build",
    "dist"
]

[tool.ruff.lint]
select = [
    "B",
    "E",
    "F",
    "I",
    "SIM",
    "UP"
]

[tool.ruff.format]
docstring-code-format = true
line-ending = "auto"
quote-style = "double"
```

The selected rules cover common Python errors, pycodestyle checks, import sorting, pyupgrade suggestions, bugbear checks, and simplification suggestions.

---

## 📦 13. Package the application as a Windows executable

Before packaging, confirm that the application works locally:

```powershell
nicegui-hello-world
```

Then run the packaging script:

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script, run it with a process-level execution policy bypass:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

The script installs the project in editable mode with packaging dependencies, checks whether `pyinstaller` is available, cleans previous outputs, runs `nicegui-pack`, and confirms that `dist\nicegui-hello-world.exe` was created.

---

## 🧩 14. Recommended VS Code extensions

VS Code extension recommendations should be treated as optional developer environment helpers.

A common place to keep project extension recommendations is:

```text
.vscode/extensions.json
```

### Core development recommendations

| Extension | Identifier | Purpose |
|---|---|---|
| Python | `ms-python.python` | Python language support |
| Pylance | `ms-python.vscode-pylance` | Python analysis and IntelliSense |
| Ruff | `charliermarsh.ruff` | Ruff linting and formatting integration |
| Markdown All in One | `yzhang.markdown-all-in-one` | Markdown editing support |
| EditorConfig | `editorconfig.editorconfig` | Consistent editor settings |

### Optional visual and productivity recommendations

| Extension | Identifier | Purpose |
|---|---|---|
| Dracula Theme | `dracula-theme.theme-dracula` | Optional dark color theme |
| FiraCode Font | `seyyedkhandon.firacode` | Optional Fira Code font helper |
| Material Icon Theme | `PKief.material-icon-theme` | Optional file and folder icons |
| Bookmarks | `alefragnani.Bookmarks` | Optional code navigation bookmarks |
| Git Graph | `mhutchie.git-graph` | Optional visual Git branch and commit history |
| Git History | `donjayamanne.githistory` | Optional file and repository history inspection |
| Todo Tree | `Gruntfuggly.todo-tree` | Optional TODO and FIXME tracking |
| Trailing Spaces | `shardulm94.trailing-spaces` | Optional trailing whitespace visualization |

---

## ✅ 15. Quick validation checklist

Before continuing development, confirm:

- [ ] Python 3.13 is installed.
- [ ] `py -3.13 --version` works.
- [ ] VS Code is installed.
- [ ] The repository root folder is open in VS Code.
- [ ] The `.venv` folder exists in the repository root.
- [ ] The `.venv` was created with Python 3.13.
- [ ] The `.venv` is activated in PowerShell.
- [ ] `python --version` returns `Python 3.13.x`.
- [ ] `python -m pip install -e ".[dev,packaging]"` completed successfully.
- [ ] `nicegui-hello-world` starts the NiceGUI application.
- [ ] `python -m nicegui_hello_world` starts the NiceGUI application.
- [ ] `python dev_run.py` starts the browser-based development mode.
- [ ] `ruff check .` passes.
- [ ] `ruff format --check .` passes.
- [ ] Saving a Python file in VS Code runs Ruff formatting, fixes, and import organization.
- [ ] A native desktop-style window opens with the Hello NiceGUI interface in normal mode.
- [ ] `pyinstaller --version` works inside the active `.venv`.
- [ ] `scripts\package_windows.ps1` generates `dist\nicegui-hello-world.exe`.
- [ ] `dist\nicegui-hello-world.exe` opens the native Hello NiceGUI window.

---

## 🧯 Quick recovery

If the terminal is not using the expected Python environment, run this sequence from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python --version
python -c "import sys; print(sys.executable)"
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If the `.venv` was created incorrectly or with Python 3.14, remove it and create it again with Python 3.13:

```powershell
Deactivate
Remove-Item -Recurse -Force .venv
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

If imports fail, Ruff is not recognized, or the `nicegui-hello-world` command is not recognized, reinstall the project in editable mode:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
```

If Ruff does not run when saving files in VS Code, confirm that:

- the Ruff extension is installed;
- VS Code opened the repository root folder;
- `.vscode/settings.json` exists;
- the selected interpreter is `.venv\Scripts\python.exe`;
- the project was installed with `python -m pip install -e ".[dev,packaging]"`.

If Ruff reports issues, review them first:

```powershell
ruff check .
```

Then apply safe fixes only when intended:

```powershell
ruff check --fix .
ruff format .
```

If `python dev_run.py` fails with an import error for `nicegui_hello_world`, confirm that editable installation completed successfully:

```powershell
python -m pip install -e ".[dev,packaging]"
python dev_run.py
```

If an old executable keeps being tested by mistake, remove old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## ⬅️ Back

- [README](../README.md)
