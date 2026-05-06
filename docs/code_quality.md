# 🧹 Code Quality with Ruff

Ruff is the current linting, import organization, and formatting tool for this project.

---

## 📦 Install Ruff

Ruff is installed through the `dev` optional dependency group:

```powershell
python -m pip install -e ".[dev,packaging]"
```

---

## ✅ Check code

```powershell
ruff check .
```

Check formatting without changing files:

```powershell
ruff format --check .
```

Recommended validation before committing:

```powershell
ruff check .
ruff format --check .
```

---

## 🛠️ Fix and format

Apply safe lint fixes:

```powershell
ruff check --fix .
```

Format code:

```powershell
ruff format .
```

Use modifying commands only when you intentionally want Ruff to edit files.

---

## ⚙️ Current configuration

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

## 💾 Ruff on save in VS Code

VS Code runs Ruff on save through:

```text
.vscode\settings.json
```

See:

- [VS Code setup](vscode_setup.md)

---

## 🔗 Related documents

- [VS Code setup](vscode_setup.md)
- [Troubleshooting](troubleshooting.md)
