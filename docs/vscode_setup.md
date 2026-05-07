# 🧰 VS Code Setup on Windows

This guide explains how to install and configure Visual Studio Code for the current **NiceGui Windows Base** project.

---

## 📌 When should you use this guide?

Use this guide when:

- VS Code is not installed;
- VS Code opened the wrong folder;
- VS Code does not detect `.venv`;
- imports appear unresolved;
- Ruff does not run on save;
- the integrated terminal uses a different Python version;
- recommended extensions were not installed.

---

## 📥 1. Download VS Code

Download the official installer:

```text
https://code.visualstudio.com/
```

Use the official installer for Windows. Avoid portable or unofficial builds unless you have a specific reason.

---

## ⚙️ 2. Install VS Code

During installation, the default options are usually enough.

Recommended Windows Explorer integration options:

- **Open with Code** action for files;
- **Open with Code** action for folders;
- register VS Code as an editor for supported file types;
- add VS Code to PATH.

These options are not mandatory, but they make daily use easier.

After installing, open VS Code once so it finishes initial setup.

---

## 📂 3. Open the repository root

In VS Code:

1. click **File > Open Folder**;
2. select the repository root folder;
3. confirm the folder opening.

The correct folder contains:

```text
pyproject.toml
```

The root should also contain files and folders such as:

```text
README.md
src
docs
scripts
dev_run.py
```

Do not open only `src`, `docs`, or `scripts`. Opening a subfolder can break or confuse:

- imports;
- editable package behavior;
- Ruff configuration;
- workspace settings;
- documentation links;
- integrated terminal commands.

---

## 🐍 4. Select the `.venv` interpreter

After creating `.venv`, select the project interpreter:

1. press `Ctrl + Shift + P`;
2. search for `Python: Select Interpreter`;
3. choose:

```text
.venv\Scripts\python.exe
```

If it does not appear:

1. select **Enter interpreter path**;
2. choose **Find**;
3. browse to:

```text
<repository-root>\.venv\Scripts\python.exe
```

Expected result:

- the VS Code status bar shows the `.venv` interpreter;
- Pylance resolves project imports;
- the integrated terminal can use the same environment.

---

## ▶️ 5. Use the integrated terminal

Open a new terminal:

```text
Terminal > New Terminal
```

Activate `.venv`, if it is not active:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Confirm the active interpreter:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

Expected result:

```text
Python 3.13.x
<repository-root>\.venv\Scripts\python.exe
```

---

## 📦 6. Install the project from the VS Code terminal

With `.venv` active:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,packaging]"
```

Editable installation is important because this project uses a `src` layout.

It allows Python, VS Code, and tooling to resolve:

```text
src\desktop_app
```

---

## 🧩 7. Recommended extensions

The project recommends extensions through:

```text
.vscode\extensions.json
```

When VS Code opens the repository, it may show a prompt to install recommended extensions.

You can also install them manually:

1. open the **Extensions** panel with `Ctrl + Shift + X`;
2. search by extension name or identifier;
3. click **Install**.

### Core recommendations

| Extension           | Identifier                   | Purpose                                      |
| ------------------- | ---------------------------- | -------------------------------------------- |
| Python              | `ms-python.python`           | Python language support                      |
| Pylance             | `ms-python.vscode-pylance`   | Python analysis and IntelliSense             |
| Ruff                | `charliermarsh.ruff`         | Linting, formatting, and import organization |
| Markdown All in One | `yzhang.markdown-all-in-one` | Markdown editing support                     |
| markdownlint        | `DavidAnson.vscode-markdownlint` | Markdown linting and style validation     |
| EditorConfig        | `editorconfig.editorconfig`  | Consistent editor behavior                   |

### Optional visual and productivity recommendations

| Extension           | Identifier                    | Purpose                                    |
| ------------------- | ----------------------------- | ------------------------------------------ |
| Dracula Theme       | `dracula-theme.theme-dracula` | Optional dark theme                        |
| FiraCode Font       | `seyyedkhandon.firacode`      | Optional font helper                       |
| Material Icon Theme | `PKief.material-icon-theme`   | Optional file and folder icons             |
| Bookmarks           | `alefragnani.Bookmarks`       | Optional navigation bookmarks              |
| Git Graph           | `mhutchie.git-graph`          | Optional Git branch visualization          |
| Git History         | `donjayamanne.githistory`     | Optional Git history inspection            |
| Todo Tree           | `Gruntfuggly.todo-tree`       | Optional TODO and FIXME tracking           |
| Trailing Spaces     | `shardulm94.trailing-spaces`  | Optional trailing whitespace visualization |

The project should still work if optional visual extensions are not installed.

---

## 🔤 8. Optional Fira Code setup

The `seyyedkhandon.firacode` extension can help with Fira Code, but the font may still need to be installed in Windows.

Recommended editor settings if the font is available:

```json
{
    "editor.fontFamily": "'Fira Code', Consolas, 'Courier New', monospace",
    "editor.fontLigatures": true
}
```

If Fira Code is unavailable, VS Code will use the fallback fonts.

---

## 💾 9. Ruff on save

Workspace settings live in:

```text
.vscode\settings.json
```

Current Python save behavior:

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

This means that when a Python file is explicitly saved, VS Code should:

- format it with Ruff;
- apply safe Ruff fixes;
- organize imports with Ruff.

Ruff-specific code actions are used instead of generic `source.fixAll` and `source.organizeImports` to avoid accidentally running other providers.

---

## 🗂️ 10. Workspace file visibility

The project uses VS Code `files.exclude` to keep the Explorer focused on files that are more relevant during daily development.

Some generated files, cache folders, build artifacts, metadata files, and stable infrastructure files are hidden from the Explorer because they are not expected to change frequently.

This does not remove files from the project and does not affect Git tracking. It only changes the VS Code Explorer view.

If a hidden file needs to be opened, use one of these options:

- `Ctrl + P` and type the file path;
- temporarily disable the related entry in `.vscode\settings.json`;
- open the file directly from the terminal.

Search exclusions are more conservative and mainly hide generated artifacts such as virtual environments, cache folders, compiled Python files, and distribution outputs.

---

## ✅ 11. Validate VS Code setup

Run these commands in the VS Code integrated terminal:

```powershell
python --version
python -c "import sys; print(sys.executable)"
python -m pip show nicegui
ruff check .
ruff format --check .
```

Then run the app:

```powershell
nicegui-windows-base
```

For development mode:

```powershell
python dev_run.py
```

---

## ⚠️ Common VS Code problems

### VS Code does not find `.venv`

Check that:

- the repository root is open;
- `.venv` exists in the root;
- `.venv\Scripts\python.exe` exists;
- the interpreter was selected manually;
- a new terminal was opened after selecting the interpreter.

### Imports appear unresolved

Run:

```powershell
python -m pip install -e ".[dev,packaging]"
```

Then reload the VS Code window:

```text
Ctrl + Shift + P > Developer: Reload Window
```

### Ruff does not run on save

Confirm that:

- the Ruff extension is installed;
- `.vscode\settings.json` exists;
- the opened folder is the repository root;
- Ruff is installed in `.venv`;
- a Python file is being saved, not a Markdown file.

Manual check:

```powershell
ruff check .
ruff format --check .
```

### Markdown linting does not run in VS Code

Confirm that:

- the markdownlint extension is installed;
- VS Code opened the repository root;
- the active file is a Markdown file;
- the extension is enabled in the current workspace.

Recommended extension identifier:

```text
DavidAnson.vscode-markdownlint
```

### Terminal uses the wrong Python

Check:

```powershell
python -c "import sys; print(sys.executable)"
```

If the path does not point to `.venv`, select the interpreter again and open a new terminal.

---

## 🔗 Related documents

- [Development environment](development_environment.md)
- [Python 3.13 setup on Windows](python_windows_setup.md)
- [PowerShell execution policy](powershell_execution_policy.md)
- [Code quality with Ruff](code_quality.md)
- [Troubleshooting](troubleshooting.md)
