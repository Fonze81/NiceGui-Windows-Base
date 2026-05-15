# -----------------------------------------------------------------------------
# File: src/desktop_app/project_tools/release_automation.py
# Purpose:
# Automate the repeated metadata updates required before a project release.
# Behavior:
# Validates semantic versions, updates package metadata, application constants,
# bundled settings, Windows version resources, tests, and inserts a changelog
# section when the target version is not already documented.
# Notes:
# This module does not run Git, tests, packaging, or external commands. Release
# validation remains explicit so maintainers can inspect failures directly.
# -----------------------------------------------------------------------------

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Final

import tomlkit

from desktop_app.project_tools.common import (
    ChangedFile,
    ProjectToolError,
    read_project_text,
    replace_required_pattern,
    write_project_text,
)

SEMVER_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
VERSIONED_FILES: Final[tuple[str, ...]] = (
    "pyproject.toml",
    "src/desktop_app/constants.py",
    "src/desktop_app/settings.toml",
    "scripts/version_info.txt",
    "tests/test_constants.py",
    "CHANGELOG.md",
)


@dataclass(frozen=True, slots=True)
class ReleasePlan:
    """Describe a release metadata update.

    Attributes:
        version: Semantic version in MAJOR.MINOR.PATCH format.
        release_date: Release date in ISO format.
    """

    version: str
    release_date: str

    @property
    def windows_version(self) -> str:
        """Return the four-part Windows file version string."""
        return f"{self.version}.0"

    @property
    def version_tuple(self) -> tuple[int, int, int, int]:
        """Return the four-part Windows version tuple."""
        major, minor, patch = _parse_version(self.version)
        return major, minor, patch, 0


def build_release_plan(version: str, *, release_date: str | None = None) -> ReleasePlan:
    """Build and validate a release plan.

    Args:
        version: Semantic version in MAJOR.MINOR.PATCH format.
        release_date: Optional ISO release date. Uses today's date when omitted.

    Returns:
        Validated release plan.

    Raises:
        ProjectToolError: If the version or date is invalid.
    """
    normalized_version = version.strip()
    _parse_version(normalized_version)

    normalized_date = (
        release_date.strip() if release_date is not None else date.today().isoformat()
    )
    _parse_release_date(normalized_date)

    return ReleasePlan(version=normalized_version, release_date=normalized_date)


def prepare_release(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool = False,
) -> tuple[ChangedFile, ...]:
    """Apply release metadata updates to the project.

    Args:
        project_root: Repository root directory.
        plan: Release metadata plan.
        dry_run: When true, report changes without writing files.

    Returns:
        File update results for every release-managed file.
    """
    return (
        _update_pyproject(project_root, plan, dry_run=dry_run),
        _update_constants(project_root, plan, dry_run=dry_run),
        _update_settings_template(project_root, plan, dry_run=dry_run),
        _update_version_info(project_root, plan, dry_run=dry_run),
        _update_constants_test(project_root, plan, dry_run=dry_run),
        _update_changelog(project_root, plan, dry_run=dry_run),
    )


def _parse_version(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string."""
    match = SEMVER_PATTERN.fullmatch(version)
    if match is None:
        raise ProjectToolError("Version must use MAJOR.MINOR.PATCH format.")

    return tuple(int(part) for part in match.groups())


def _parse_release_date(release_date: str) -> date:
    """Parse an ISO release date string."""
    try:
        return date.fromisoformat(release_date)
    except ValueError as exc:
        raise ProjectToolError("Release date must use YYYY-MM-DD format.") from exc


def _update_pyproject(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update the project metadata version."""
    relative_path = Path("pyproject.toml")
    document = tomlkit.parse(read_project_text(project_root, relative_path))
    document["project"]["version"] = plan.version
    return write_project_text(
        project_root, relative_path, tomlkit.dumps(document), dry_run=dry_run
    )


def _update_constants(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update the application version constant."""
    relative_path = Path("src/desktop_app/constants.py")
    text = read_project_text(project_root, relative_path)
    text = replace_required_pattern(
        text,
        r'APPLICATION_VERSION: Final\[str\] = "[^"]+"',
        f'APPLICATION_VERSION: Final[str] = "{plan.version}"',
        marker="APPLICATION_VERSION",
    )
    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _update_settings_template(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update the bundled settings template version."""
    relative_path = Path("src/desktop_app/settings.toml")
    document = tomlkit.parse(read_project_text(project_root, relative_path))
    document["app"]["version"] = plan.version
    return write_project_text(
        project_root, relative_path, tomlkit.dumps(document), dry_run=dry_run
    )


def _update_version_info(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update Windows executable version metadata."""
    relative_path = Path("scripts/version_info.txt")
    text = read_project_text(project_root, relative_path)
    windows_tuple = plan.version_tuple
    text = replace_required_pattern(
        text,
        r"filevers=\(\d+, \d+, \d+, \d+\)",
        f"filevers={windows_tuple}",
        marker="filevers",
    )
    text = replace_required_pattern(
        text,
        r"prodvers=\(\d+, \d+, \d+, \d+\)",
        f"prodvers={windows_tuple}",
        marker="prodvers",
    )
    text = _replace_version_string_struct(text, "FileVersion", plan.windows_version)
    text = _replace_version_string_struct(text, "ProductVersion", plan.windows_version)
    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _replace_version_string_struct(text: str, key: str, value: str) -> str:
    """Replace a version StringStruct value inside scripts/version_info.txt."""
    return replace_required_pattern(
        text,
        rf'(StringStruct\(\s*"{re.escape(key)}",\s*")[^"]*("\s*,?\s*\))',
        rf"\g<1>{value}\2",
        marker=f"StringStruct {key}",
        flags=re.DOTALL,
    )


def _update_constants_test(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update the constants test version expectation."""
    relative_path = Path("tests/test_constants.py")
    text = read_project_text(project_root, relative_path)
    text = replace_required_pattern(
        text,
        r'assert constants\.APPLICATION_VERSION == "[^"]+"',
        f'assert constants.APPLICATION_VERSION == "{plan.version}"',
        marker="APPLICATION_VERSION test expectation",
    )
    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _update_changelog(
    project_root: Path,
    plan: ReleasePlan,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Insert a release changelog section when missing."""
    relative_path = Path("CHANGELOG.md")
    text = read_project_text(project_root, relative_path)
    if f"## [{plan.version}]" in text:
        return write_project_text(project_root, relative_path, text, dry_run=dry_run)

    updated_text = _insert_changelog_section(text, _build_changelog_section(plan))
    return write_project_text(
        project_root, relative_path, updated_text, dry_run=dry_run
    )


def _insert_changelog_section(text: str, section: str) -> str:
    """Insert a new changelog section after the introductory divider."""
    marker = "---\n\n"
    if marker in text:
        return text.replace(marker, f"{marker}{section}\n", 1)

    first_release_heading = text.find("\n## [")
    if first_release_heading == -1:
        raise ProjectToolError(
            "CHANGELOG.md does not contain a release insertion point."
        )

    prefix = text[: first_release_heading + 1]
    suffix = text[first_release_heading + 1 :]
    return f"{prefix}{section}\n{suffix}"


def _build_changelog_section(plan: ReleasePlan) -> str:
    """Build the default release automation changelog section."""
    return f"""## [{plan.version}] - {plan.release_date}

### 🔄 Changed

- Updated project release metadata to `{plan.version}` across package metadata,
  application constants, bundled settings, Windows version resources, and tests.

### 🧪 Tests and quality

- Run compile, Ruff, formatting, pytest, coverage, and Windows packaging
  validation before publishing the release.

### 🧭 Migration notes

- Reinstall the project after upgrading so editable metadata and package data are
  refreshed:

```powershell
python -m pip install -e \".[dev,packaging]\"
```

- Rebuild the executable so Windows file properties show `{plan.windows_version}`
  and bundled assets/settings are refreshed:

```powershell
.\\scripts\\package_windows.ps1
```
"""
