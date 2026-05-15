# 🧩 Template Customization

This guide explains how to customize the public identity of a project created from **NiceGui Windows Base** without renaming the internal Python package.

Use this guide when you are turning the template into a real business application and need to update names, command metadata, settings defaults, Windows executable metadata, and documentation references.

---

## 🎯 Supported scope

The customization tool updates public identity values only.

It intentionally keeps the internal package name as:

```text
desktop_app
```

Keeping `desktop_app` stable avoids unnecessary changes to imports, module execution, package data, asset paths, tests, documentation links, and PyInstaller entry points.

The tool updates:

- `pyproject.toml` project name, description, authors, and console script;
- `src/desktop_app/constants.py` application title and command detection names;
- `src/desktop_app/settings.toml` default app name and window storage key;
- `scripts/package_windows.ps1` executable name;
- `scripts/version_info.txt` Windows resource identity strings;
- maintained README, documentation, source comments/docstrings, and tests that reference the default public name.

It does **not** rename source folders, Python imports, project-tool defaults, historical changelog entries, or the internal package.

---

## ▶️ Run a dry run first

From the repository root:

```powershell
python scripts\customize_template.py `
    --project-name inventory-dashboard `
    --display-name "Inventory Dashboard" `
    --description "Inventory tracking desktop application." `
    --author-name "Example Team" `
    --dry-run
```

The dry run reports which files would change without writing them. It may include tests because identity-sensitive tests should keep passing after customization.

---

## ✅ Apply customization

After reviewing the dry run:

```powershell
python scripts\customize_template.py `
    --project-name inventory-dashboard `
    --display-name "Inventory Dashboard" `
    --description "Inventory tracking desktop application." `
    --author-name "Example Team"
```

The `--project-name` value must use lowercase letters, numbers, and hyphens only. Examples:

```text
inventory-dashboard
sap-export-console
sharepoint-sync-tool
```

---

## 🧪 Validate after customization

Run the standard quality gates:

```powershell
python -m compileall -q src dev_run.py scripts\customize_template.py scripts\prepare_release.py
ruff check .
ruff format --check .
pytest tests --cov=desktop_app --cov-report=term-missing --cov-fail-under=100
```

Then validate the application commands that now use the customized name:

```powershell
python -m pip install -e ".[dev,packaging]"
<custom-project-name>
python -m desktop_app
python dev_run.py
```

For packaged validation, see [Windows packaging](packaging_windows.md).

---

## 🧭 When package renaming is needed

Only rename the internal package when the new project has a strong technical reason to expose a domain-specific import path.

If package renaming is required, update all of these areas together:

- source folder under `src`;
- all Python imports;
- `pyproject.toml` package discovery, package data, and script target;
- `scripts/package_windows.ps1` entry point and bundled data paths;
- documentation links;
- tests and coverage source configuration;
- any path-based assumptions in packaging and asset resolution.

This is intentionally not automated by `scripts/customize_template.py` because partial package renames are high-risk and can break source execution, module execution, tests, and packaged execution.

---

## 🔗 Related documents

- [Documentation index](README.md)
- [Architecture overview](architecture.md)
- [Execution modes](execution_modes.md)
- [Release automation](release_automation.md)
- [Windows packaging](packaging_windows.md)
- [Troubleshooting](troubleshooting.md)
