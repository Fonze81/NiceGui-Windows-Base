# 🚀 Release Automation

This guide explains how to prepare release metadata consistently across the **NiceGui Windows Base** template.

Use it when creating a new version after source, tests, UI, or documentation changes are complete.

---

## 🎯 What the release tool updates

The release preparation script updates the repeated version markers that must stay aligned:

- `pyproject.toml` project version;
- `src/desktop_app/constants.py` `APPLICATION_VERSION`;
- `src/desktop_app/settings.toml` bundled settings template version;
- `scripts/version_info.txt` Windows `filevers`, `prodvers`, `FileVersion`, and `ProductVersion`;
- `tests/test_constants.py` version expectation;
- `CHANGELOG.md`, when the target release section does not already exist.

The script does **not** run Git commands, tests, Ruff, PyInstaller, publishing, or tagging. Those steps remain explicit so maintainers can inspect errors directly.

---

## ▶️ Run a dry run first

From the repository root:

```powershell
python scripts\prepare_release.py 0.10.0 --date 2026-06-01 --dry-run
```

The dry run reports the files that would change without writing them.

---

## ✅ Apply release metadata

```powershell
python scripts\prepare_release.py 0.10.0 --date 2026-06-01
```

If `--date` is omitted, the script uses the current date from the machine running the command.

The version must use semantic `MAJOR.MINOR.PATCH` format, for example:

```text
0.10.0
1.0.0
1.2.3
```

---

## 🧪 Validate before publishing

Run the full quality gate:

```powershell
python -m compileall -q src dev_run.py scripts\customize_template.py scripts\prepare_release.py
ruff check .
ruff format --check .
pytest tests --cov=desktop_app --cov-report=term-missing --cov-fail-under=100
```

On Windows, also validate packaging and the generated executable:

```powershell
.\scripts\package_windows.ps1
.\dist\nicegui-windows-base.exe
```

If the template was customized, replace `nicegui-windows-base.exe` with the customized executable name.

---

## 🧭 Suggested release workflow

1. Finish source, UI, tests, and documentation changes.
2. Run the release preparation script in dry-run mode.
3. Apply the release metadata update.
4. Review `CHANGELOG.md` and refine user-facing release notes.
5. Run compile, Ruff, formatting, pytest, and coverage checks.
6. Validate Windows packaging on a real Windows machine.
7. Inspect the generated `dist\packaging_report.md`.
8. Commit the release preparation.
9. Create a Git tag only after the validation evidence is acceptable.

Before destructive Git operations, inspect the current state:

```powershell
git status
git branch --show-current
git log --oneline -5
```

---

## 🔗 Related documents

- [Documentation index](README.md)
- [Template customization](template_customization.md)
- [Windows packaging](packaging_windows.md)
- [Code quality](code_quality.md)
- [Changelog](../CHANGELOG.md)
