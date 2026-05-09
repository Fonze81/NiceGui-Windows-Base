# 🧹 Code Quality

Ruff, pytest, coverage, compile checks, and Markdown validation are the current quality tools for this project.

Use this guide before committing changes to Python modules, tests, packaging scripts, or documentation.

---

## 🎯 Goals

The quality workflow is designed to:

- catch syntax errors early;
- keep imports organized;
- keep formatting stable across machines;
- validate behavior through pytest;
- measure test coverage through coverage.py and pytest-cov;
- keep Markdown documents readable and linked consistently;
- avoid accidental drift between code, tests, and documentation.

---

## 📦 Install development tools

Development and packaging tools are installed through optional dependency groups:

```powershell
python -m pip install -e ".[dev,packaging]"
```

The `dev` group currently includes:

- `pytest`;
- `pytest-cov`;
- `coverage[toml]`;
- `ruff`.

The `packaging` group includes:

- `pyinstaller`.

---

## ✅ Recommended validation before committing

Run these commands from the repository root with `.venv` active:

```powershell
python -m compileall -q src dev_run.py
pytest
ruff check .
ruff format --check .
```

Purpose:

| Command                                  | Purpose                                                                           |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| `python -m compileall -q src dev_run.py` | Detect syntax errors without starting NiceGUI.                                    |
| `pytest`                                 | Run the full test suite.                                                          |
| `ruff check .`                           | Validate linting, import order, modernization, bugbear, and simplification rules. |
| `ruff format --check .`                  | Confirm that Python formatting is already applied.                                |

Use modifying commands only when you intentionally want tools to edit files.

---

## 🧪 Test commands

Run all tests:

```powershell
pytest
```

Run one package area:

```powershell
pytest tests/core
pytest tests/infrastructure
pytest tests/infrastructure/logger
pytest tests/infrastructure/settings
```

Run one file:

```powershell
pytest tests/infrastructure/settings/test_service.py
```

Run one test:

```powershell
pytest tests/infrastructure/settings/test_service.py::test_load_settings_uses_bundled_defaults_when_persistent_file_is_missing
```

---

## 📊 Coverage commands

Run coverage for the whole package:

```powershell
pytest --cov=desktop_app --cov-report=term-missing
```

Generate HTML coverage:

```powershell
pytest --cov=desktop_app --cov-report=html
```

Open the report:

```powershell
start htmlcov\index.html
```

Run coverage for a specific package:

```powershell
pytest tests/infrastructure/settings `
    --cov=desktop_app.infrastructure.settings `
    --cov-report=term-missing
```

The coverage configuration lives in `pyproject.toml`.

---

## ⚙️ Current Ruff configuration

Ruff configuration lives in:

```text
pyproject.toml
```

Current configuration:

```toml
[tool.ruff]
line-length = 88
target-version = "py313"
src = ["src"]
extend-exclude = [".venv", "build", "dist"]

[tool.ruff.lint]
select = ["B", "E", "F", "I", "SIM", "UP"]

[tool.ruff.format]
docstring-code-format = true
line-ending = "auto"
quote-style = "double"
```

Rule groups currently cover:

- common Python errors;
- pycodestyle checks;
- import sorting;
- Python modernization suggestions;
- bugbear checks;
- simplification suggestions.

---

## 🛠️ Fix and format

Apply safe lint fixes:

```powershell
ruff check --fix .
```

Format Python code:

```powershell
ruff format .
```

Ruff does not replace tests. After applying fixes or formatting, run:

```powershell
pytest
```

---

## 🧪 Current test layout

The test suite follows the source package structure:

```text
tests
├── core
│   ├── test_core_init.py
│   ├── test_runtime.py
│   └── test_state.py
├── infrastructure
│   ├── logger
│   ├── settings
│   ├── test_asset_paths.py
│   ├── test_byte_size.py
│   ├── test_file_system.py
│   ├── test_lifecycle.py
│   └── test_splash.py
├── test_app.py
├── test_constants.py
└── test_desktop_app_main.py
```

Important testing notes:

- tests should be small and focused;
- tests should not depend on the developer machine's real `settings.toml`;
- settings tests should use temporary directories and monkeypatching;
- logger tests should release handlers to avoid locked files on Windows;
- NiceGUI callback-heavy behavior should be isolated behind small functions where possible;
- blocking integrations, such as SAP GUI or RPA, should be tested outside the UI thread.

---

## ⚙️ Pytest configuration

Pytest configuration lives in `pyproject.toml` and currently uses:

```toml
[tool.pytest.ini_options]
addopts = [
    "--import-mode=importlib",
    "--strict-config",
    "--strict-markers",
]
pythonpath = ["src"]
testpaths = ["tests"]
```

`--import-mode=importlib` reduces test module import collisions when different folders contain files with the same base name.

---

## 💾 Ruff on save in VS Code

VS Code runs Ruff on save through:

```text
.vscode\settings.json
```

See:

- [VS Code setup](vscode_setup.md)

---

## 📝 Markdown validation

Markdown documentation is validated in VS Code through:

```text
DavidAnson.vscode-markdownlint
```

Markdown formatting can be handled by Prettier through:

```text
esbenp.prettier-vscode
```

Markdown documentation in this project may use emojis in headings to improve readability. Python code, comments, and docstrings must not use emojis.

Recommended Markdown checks during review:

- headings are sequential and not duplicated;
- code blocks have language identifiers when useful;
- relative links point to existing files;
- repeated explanations are centralized in one document and linked from others;
- README, docs, changelog, packaging, settings, and state documentation do not contradict one another.

---

## 🔗 Related documents

- [VS Code setup](vscode_setup.md)
- [Settings subsystem](settings.md)
- [Application state](state.md)
- [Troubleshooting](troubleshooting.md)
