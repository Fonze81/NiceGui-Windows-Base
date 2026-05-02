# 🧰 Development Environment Setup

This guide explains how to prepare a basic development environment for the **NiceGUI Hello World** repository on Windows.

The goal is to help developers install the required tools, create a Python 3.13 virtual environment, activate it, install project dependencies, run the NiceGUI application in native mode, package it as a Windows executable with nicegui-pack, and open the project in Visual Studio Code.

---

## 📌 When should you use this guide?

Use this guide when:

- Python is not installed yet;
- Visual Studio Code is not installed yet;
- the repository was just cloned or created;
- you need to create a local `.venv`;
- PowerShell blocks virtual environment activation;
- VS Code needs to be configured to use the project environment;
- NiceGUI needs to be installed from `requirements.txt`;
- the local application script needs to be executed;
- NiceGUI native mode needs to be tested;
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
8. Install the project dependencies.
9. Run the NiceGUI application in native mode.
10. Package the application as a Windows executable.
11. Confirm that Python runs from the virtual environment.

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
- `python src\nicegui_hello_world\app.py` opens the NiceGUI native window correctly;
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
requirements.txt
docs
scripts
src
```

Avoid opening only the `src` folder. Keeping VS Code opened at the repository root makes configuration, paths, and terminal usage easier.

---

## 🧱 4. Understand the src layout

The project now uses a `src` layout.

```text
.
├── src/
│   └── nicegui_hello_world/
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── scripts/
├── docs/
├── README.md
└── requirements.txt
```

The application code lives inside:

```text
src\nicegui_hello_world
```

The main application entry point is:

```text
src\nicegui_hello_world\app.py
```

This keeps source code separated from documentation, scripts, generated files, and repository metadata.

At this step, the project still uses `requirements.txt` and direct script execution. A package installation file such as `pyproject.toml` can be introduced later when the project needs an editable install or a command-line entry point.

---

## ⚙️ 5. Create the virtual environment with Python 3.13

Open PowerShell in the repository root folder and run:

```powershell
py -3.13 -m venv .venv
```

This command explicitly creates the virtual environment with Python 3.13.

After creating the `.venv`, activate it and confirm the version before installing dependencies.

The `.venv` folder stores the local Python environment for this project.

This helps avoid conflicts with:

- other Python projects;
- globally installed packages;
- different dependency versions;
- old environment settings;
- accidental usage of Python 3.14 with native-mode dependencies.

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

## 📦 9. Install project dependencies

With the `.venv` activated, upgrade `pip`:

```powershell
python -m pip install --upgrade pip
```

Then install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

The dependency file should contain:

```text
nicegui
pywebview
pyinstaller
```

NiceGUI provides the application framework.

pywebview provides the native desktop window used by NiceGUI native mode.

PyInstaller provides the `pyinstaller` command used internally by `nicegui-pack` during packaging.

Because native mode depends on this dependency chain, the project should currently use Python 3.13 instead of Python 3.14.

---

## ▶️ 10. Run the NiceGUI application in native mode

After installing the dependencies, run the application from the repository root:

```powershell
python src\nicegui_hello_world\app.py
```

The main application file should contain:

```python
from nicegui import native, ui


def create_ui() -> None:
    """Build the main NiceGUI interface."""
    ui.label("Hello, NiceGUI!")


def main() -> None:
    """Run the NiceGUI application."""
    ui.run(create_ui, native=True, reload=False, port=native.find_open_port())


if __name__ == "__main__":
    main()
```

The first argument passed to `ui.run(...)` is the root function used to build the interface.

This is important for packaging. When UI elements are created directly at module level without a root function or decorated page, NiceGUI may use script mode. Script mode can fail after packaging because the executable is not a Python source file.

The `native=True` option opens the NiceGUI interface in a desktop-style window instead of relying only on the external browser.

The `reload=False` option is important for packaged execution because the reload server should not be used inside the executable.

The `native.find_open_port()` call lets NiceGUI choose an available local port, reducing the chance of port conflicts when the packaged application starts.

Keep the terminal open while testing the application. Stop the app with `Ctrl + C` when finished.

If the native window does not open, check the terminal output first. Native mode depends on `pywebview` and may also depend on Windows components already installed on the machine, such as the webview backend used by `pywebview`.

---

## 📦 11. Package the application as a Windows executable

This project can be packaged with `nicegui-pack`.

At this point, packaging is intentionally simple and does not use a `settings.toml` file. Runtime behavior is still configured directly in `app.py`.

Before packaging, confirm that the application works locally:

```powershell
python src\nicegui_hello_world\app.py
```

Then run the packaging script:

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script, run it with a process-level execution policy bypass:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

The script:

1. installs dependencies from `requirements.txt`;
2. checks whether `pyinstaller` is available in the active environment;
3. removes previous `build`, `dist`, and `.spec` outputs;
4. runs `nicegui-pack`;
5. checks whether `nicegui-pack` failed;
6. confirms that `dist\nicegui-hello-world.exe` was actually created.

The `nicegui-pack` command uses PyInstaller internally. The packaging command generated by `nicegui-pack` calls `pyinstaller`, so PyInstaller must be installed and available in the active `.venv`.

### Current packaging command

```powershell
nicegui-pack `
  --onefile `
  --windowed `
  --clean `
  --noconfirm `
  --name "nicegui-hello-world" `
  src\nicegui_hello_world\app.py
```

### Why use a root function?

Packaging a NiceGUI script that creates UI elements directly at module level can fail in a packaged executable.

The observed error was:

```text
SyntaxError: source code string cannot contain null bytes
```

The traceback showed NiceGUI trying to execute `sys.argv[0]` with `runpy.run_path(...)`. In a packaged executable, `sys.argv[0]` points to the `.exe`, not to a Python `.py` source file. The `.exe` contains binary bytes, so Python raises a null-byte syntax error.

Using an explicit root function in `ui.run(create_ui, ...)` avoids this script-mode packaging path and lets NiceGUI build the page from a normal callable.

### Why use `--onefile`?

`--onefile` creates a single executable file in the `dist` folder.

This is convenient for a first distribution test, but the executable may take longer to start because it needs to unpack support files at runtime.

### Why use `--windowed`?

`--windowed` hides the terminal console when opening the executable.

Use this option only because the application already runs with:

```python
ui.run(create_ui, native=True, reload=False, port=native.find_open_port())
```

When diagnosing packaging failures, temporarily remove `--windowed` from the script so the console can show errors.

### Expected output

After packaging, the executable should be available at:

```text
dist\nicegui-hello-world.exe
```

Run it from PowerShell:

```powershell
.\dist\nicegui-hello-world.exe
```

A native desktop-style window should open with the Hello NiceGUI interface.

### No `settings.toml` yet

This packaging step does not introduce `settings.toml`.

That keeps the project simple while packaging is being validated for the first time.

Configuration can move to a dedicated settings file later if the application needs persistent runtime options, environment-specific behavior, or more structured configuration.

---

## 🧩 12. Recommended VS Code extensions

VS Code extension recommendations should be treated as optional developer environment helpers.

They can improve editing, navigation, Git visualization, and visual comfort, but they are not required to run the project.

A common place to keep project extension recommendations is:

```text
.vscode/extensions.json
```

Keeping extension recommendations in this file helps VS Code suggest them when the repository folder is opened.

### Required vs optional behavior

The project should not depend on these extensions to work.

If a developer does not install them:

- the repository should still open normally;
- Python should still work from the `.venv`;
- source files should still be editable;
- Git should still work from the terminal or GitHub Desktop.

### Core development recommendations

These extensions are useful for Python and Markdown editing:

| Extension           | Identifier                   | Purpose                          |
| ------------------- | ---------------------------- | -------------------------------- |
| Python              | `ms-python.python`           | Python language support          |
| Pylance             | `ms-python.vscode-pylance`   | Python analysis and IntelliSense |
| Markdown All in One | `yzhang.markdown-all-in-one` | Markdown editing support         |
| EditorConfig        | `editorconfig.editorconfig`  | Consistent editor settings       |

### Optional visual and productivity recommendations

These extensions improve the developer experience, but they are only preferences:

| Extension           | Identifier                    | Purpose                                         |
| ------------------- | ----------------------------- | ----------------------------------------------- |
| Dracula Theme       | `dracula-theme.theme-dracula` | Optional dark color theme                       |
| FiraCode Font       | `seyyedkhandon.firacode`      | Optional Fira Code font helper                  |
| Material Icon Theme | `PKief.material-icon-theme`   | Optional file and folder icons                  |
| Bookmarks           | `alefragnani.Bookmarks`       | Optional code navigation bookmarks              |
| Git Graph           | `mhutchie.git-graph`          | Optional visual Git branch and commit history   |
| Git History         | `donjayamanne.githistory`     | Optional file and repository history inspection |
| Todo Tree           | `Gruntfuggly.todo-tree`       | Optional TODO and FIXME tracking                |
| Trailing Spaces     | `shardulm94.trailing-spaces`  | Optional trailing whitespace visualization      |


### Optional Fira Code font

Fira Code is a font used by the editor. It can be installed manually on Windows or assisted by the optional VS Code extension:

```text
seyyedkhandon.firacode
```

Even when using the extension, the font may still need to be installed on the operating system and VS Code may need to be restarted.

Example workspace or VS Code setting:

```json
{
    "editor.fontFamily": "'Fira Code', Consolas, 'Courier New', monospace",
    "editor.fontLigatures": true
}
```

If Fira Code is not installed or not available to VS Code, the editor will use one of the fallback fonts.

Install only what is useful for your workflow and repository needs.

---

## ✅ 13. Quick validation checklist

Before continuing development, confirm:

- [ ] Python 3.13 is installed.
- [ ] `py -3.13 --version` works.
- [ ] VS Code is installed.
- [ ] The repository root folder is open in VS Code.
- [ ] The `.venv` folder exists in the repository root.
- [ ] The `.venv` was created with Python 3.13.
- [ ] The `.venv` is activated in PowerShell.
- [ ] `python --version` returns `Python 3.13.x`.
- [ ] `python -c "import sys; print(sys.executable)"` points to `.venv`.
- [ ] VS Code is using `.venv\Scripts\python.exe`.
- [ ] PowerShell policy was changed only temporarily, if activation was blocked.
- [ ] `python -m pip install -r requirements.txt` completed successfully.
- [ ] `python src\nicegui_hello_world\app.py` starts the NiceGUI application.
- [ ] A native desktop-style window opens with the Hello NiceGUI interface.
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

If Python was recently installed or updated and the terminal still shows the previous version, close and reopen PowerShell or VS Code. If the version still does not change, restart Windows and check again.

If the `.venv` was created incorrectly or with Python 3.14, remove it and create it again with Python 3.13:

```powershell
Deactivate
Remove-Item -Recurse -Force .venv
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Expected result:

```text
Python 3.13.x
```

If NiceGUI, pywebview, or PyInstaller is not found when running the application or packaging script, reinstall the dependencies inside the active Python 3.13 `.venv`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src\nicegui_hello_world\app.py
```

If `nicegui-pack` fails with `FileNotFoundError: [WinError 2] O sistema não pode encontrar o arquivo especificado` after printing a `pyinstaller` command, PyInstaller is missing or unavailable in the active environment.

Check it with:

```powershell
pyinstaller --version
```

If the command is not recognized, reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
```

Then package again:

```powershell
.\scripts\package_windows.ps1
```

If the packaged executable starts but shows `SyntaxError: source code string cannot contain null bytes`, check whether `app.py` is using a root function in `ui.run(...)`.

The correct pattern is:

```python
from nicegui import native, ui


def create_ui() -> None:
    """Build the main NiceGUI interface."""
    ui.label("Hello, NiceGUI!")


def main() -> None:
    """Run the NiceGUI application."""
    ui.run(create_ui, native=True, reload=False, port=native.find_open_port())


if __name__ == "__main__":
    main()
```

After changing `app.py`, clean old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

If the packaging script fails while using `--windowed`, remove `--windowed` temporarily from `scripts\package_windows.ps1` and run the script again to keep the console visible for diagnostics.

If an old executable keeps being tested by mistake, remove old build outputs and package again:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
.\scripts\package_windows.ps1
```

---

## ⬅️ Back

- [README](../README.md)
