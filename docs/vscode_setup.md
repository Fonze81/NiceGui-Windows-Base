# 🧰 VS Code Setup on Windows

This guide explains how to install and configure Visual Studio Code for the current **NiceGui Windows Base** project.

---

## 📌 When should you use this guide?

Use this guide when:

- VS Code is not installed;
- VS Code opened the wrong folder;
- VS Code does not detect `.venv`;
- imports appear unresolved;
- tests are not discovered;
- coverage is not easy to run;
- Ruff does not run on save;
- Markdown linting does not run;
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
tests
scripts
dev_run.py
```

Do not open only `src`, `docs`, `scripts`, or `tests`. Opening a subfolder can break or confuse:

- imports;
- editable package behavior;
- pytest discovery;
- coverage paths;
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
- pytest uses the correct environment;
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

It allows Python, VS Code, pytest, coverage, and tooling to resolve:

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

| Extension           | Identifier                       | Purpose                                                            |
| ------------------- | -------------------------------- | ------------------------------------------------------------------ |
| Python              | `ms-python.python`               | Python language support, test discovery, and environment selection |
| Pylance             | `ms-python.vscode-pylance`       | Python analysis and IntelliSense                                   |
| Ruff                | `charliermarsh.ruff`             | Linting, formatting, and import organization                       |
| Markdown All in One | `yzhang.markdown-all-in-one`     | Markdown editing support                                           |
| markdownlint        | `DavidAnson.vscode-markdownlint` | Markdown linting and style validation                              |
| Prettier            | `esbenp.prettier-vscode`         | JSON, YAML, HTML, and Markdown formatting                          |
| EditorConfig        | `editorconfig.editorconfig`      | Consistent editor behavior                                         |

### Optional recommendations

| Extension           | Identifier                  | Purpose                                                       |
| ------------------- | --------------------------- | ------------------------------------------------------------- |
| Even Better TOML    | `tamasfe.even-better-toml`  | TOML editing support for `pyproject.toml` and `settings.toml` |
| Git Graph           | `mhutchie.git-graph`        | Git branch visualization                                      |
| Git History         | `donjayamanne.githistory`   | Git history inspection                                        |
| Todo Tree           | `Gruntfuggly.todo-tree`     | TODO and FIXME tracking                                       |
| Material Icon Theme | `PKief.material-icon-theme` | Optional file and folder icons                                |

The project should still work if optional visual extensions are not installed.

---

## 💾 8. Ruff on save

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

## 🧪 9. Pytest in VS Code

Workspace settings should enable pytest:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.cwd": "${workspaceFolder}",
  "python.testing.pytestArgs": ["tests"]
}
```

After changing settings:

```text
Ctrl + Shift + P > Python: Refresh Tests
```

Terminal validation:

```powershell
pytest --collect-only
pytest
```

---

## 📊 10. Coverage from VS Code terminal

Run:

```powershell
pytest --cov=desktop_app --cov-report=term-missing
```

HTML report:

```powershell
pytest --cov=desktop_app --cov-report=html
start htmlcov\index.html
```

The generated `htmlcov` directory should not be committed.

---

## 📝 11. Markdown and non-Python formatting

Recommended formatters:

| File type | Formatter                        |
| --------- | -------------------------------- |
| Python    | Ruff                             |
| JSON      | Prettier                         |
| JSONC     | VS Code JSON language features   |
| Markdown  | Prettier and markdownlint        |
| YAML      | Prettier                         |
| HTML      | Prettier                         |
| TOML      | Even Better TOML, when installed |

Markdown documentation may use emojis in headings. Python code, comments, and docstrings must not use emojis.

---

## ✅ 12. Validate VS Code setup

Run these commands in the VS Code integrated terminal:

```powershell
python --version
python -c "import sys; print(sys.executable)"
python -m pip show nicegui
pytest --collect-only
pytest
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

### Tests are not discovered

Confirm that:

- the Python extension is installed;
- pytest is enabled in `.vscode\settings.json`;
- VS Code opened the repository root;
- `.venv` is selected;
- the project was installed in editable mode.

Run:

```powershell
pytest --collect-only
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
- [Settings subsystem](settings.md)
- [Troubleshooting](troubleshooting.md)
