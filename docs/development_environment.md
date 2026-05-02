# 🧰 Development Environment Setup

This guide explains how to prepare a basic development environment for the **NiceGUI Hello World** repository on Windows.

The goal is to help developers install the basic tools, create a virtual environment, activate it, install project dependencies, run the NiceGUI application, and open the project in Visual Studio Code.

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
- the local `app.py` script needs to be executed.

---

## 🧭 Recommended setup flow

Follow this order:

1. Install Python.
2. Install Visual Studio Code.
3. Open the repository folder in VS Code.
4. Create the `.venv`.
5. Activate the `.venv`.
6. Apply a temporary PowerShell execution policy only if activation is blocked.
7. Select the `.venv` interpreter in VS Code.
8. Install the project dependencies.
9. Run the NiceGUI application.
10. Confirm that Python runs from the virtual environment.

---

## 🐍 1. Install Python

Download Python from the official website:

```text
https://www.python.org/downloads/windows/
```

During installation:

1. use the official Windows installer;
2. enable **Add python.exe to PATH**, if the option appears;
3. keep the recommended installation options unless you have a specific reason to change them;
4. close and reopen PowerShell after installation.

On Windows, a newly installed Python version may not appear immediately in an already opened terminal. Start by closing and reopening PowerShell or VS Code.

If the old Python version is still being used after reopening the terminal, restart Windows and check again.

After installing Python, open a new PowerShell window and check if Python is available:

```powershell
python --version
```

You can also check the Python launcher:

```powershell
py --version
```

If both commands fail, follow this order:

1. close and reopen PowerShell;
2. close and reopen VS Code, if you are using the integrated terminal;
3. restart Windows;
4. reinstall Python and confirm that the PATH option was enabled.

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

The root folder should contain files created with the repository, such as:

```text
README.md
LICENSE
.gitignore
```

Avoid opening only a subfolder. Keeping VS Code opened at the repository root makes configuration, paths, and terminal usage easier.

---

## ⚙️ 4. Create the virtual environment

Open PowerShell in the repository root folder and run:

```powershell
py -m venv .venv
```

If the `py` launcher is not available, use:

```powershell
python -m venv .venv
```

The `.venv` folder stores the local Python environment for this project.

This helps avoid conflicts with:

- other Python projects;
- globally installed packages;
- different dependency versions;
- old environment settings.

Do not commit the `.venv` folder to Git.

---

## ▶️ 5. Activate the virtual environment

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

You can also confirm the executable path:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected result: the path should point to the repository `.venv`, similar to:

```text
C:\path\to\NiceGUI-Hello-World\.venv\Scripts\python.exe
```

---

## 🔐 6. Resolve PowerShell activation blocking

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

## 🐍 7. Select the `.venv` interpreter in VS Code

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

This helps VS Code use the same Python environment that was created for the repository.

---

## 📦 8. Install project dependencies

With the `.venv` activated, upgrade `pip`:

```powershell
python -m pip install --upgrade pip
```

Then install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

For this project step, the dependency file should contain NiceGUI:

```text
nicegui
```

Using `requirements.txt` keeps dependency installation repeatable for anyone cloning the repository.

---

## ▶️ 9. Run the NiceGUI application

After installing the dependencies, run the application from the repository root:

```powershell
python app.py
```

The minimal application file should contain:

```python
from nicegui import ui

ui.label("Hello, NiceGUI!")

ui.run()
```

The `ui.run()` call starts the NiceGUI application.

If the browser does not open automatically, check the local address printed in the terminal. In a default local run, NiceGUI commonly serves the application at:

```text
http://localhost:8080
```

Keep the terminal open while testing the application. Stop the app with `Ctrl + C` when finished.

---

## 🧩 10. Recommended VS Code extensions

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

## ✅ 11. Quick validation checklist

Before continuing development, confirm:

- [ ] Python is installed.
- [ ] VS Code is installed.
- [ ] The repository root folder is open in VS Code.
- [ ] The `.venv` folder exists in the repository root.
- [ ] The `.venv` is activated in PowerShell.
- [ ] `python --version` works.
- [ ] `python -c "import sys; print(sys.executable)"` points to `.venv`.
- [ ] VS Code is using `.venv\Scripts\python.exe`.
- [ ] PowerShell policy was changed only temporarily, if activation was blocked.
- [ ] `python -m pip install -r requirements.txt` completed successfully.
- [ ] `python app.py` starts the NiceGUI application.
- [ ] The Hello NiceGUI page opens in the browser or is available at the local address shown in the terminal.

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

If the `.venv` was created incorrectly, remove it and create it again:

```powershell
Remove-Item -Recurse -Force .venv
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python was recently installed or updated and the terminal still shows the previous version, close and reopen PowerShell or VS Code. If the version still does not change, restart Windows and check again.

If NiceGUI is not found when running `python app.py`, reinstall the dependencies inside the active `.venv`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

---

## ⬅️ Back

- [README](../README.md)
