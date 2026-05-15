# -----------------------------------------------------------------------------
# File: tests/project_tools/test_release_automation.py
# Purpose:
# Validate release metadata automation helpers.
# Behavior:
# Builds a minimal project tree, prepares a release, and checks metadata,
# Windows resources, tests, changelog insertion, validation, and dry-run mode.
# Notes:
# Tests use temporary files only and do not run packaging or Git commands.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

import pytest

from desktop_app.project_tools.common import ProjectToolError
from desktop_app.project_tools.release_automation import (
    build_release_plan,
    prepare_release,
)


def test_prepare_release_updates_release_managed_files(tmp_path: Path) -> None:
    """Release preparation updates every managed metadata file."""
    _write_release_project(tmp_path)
    plan = build_release_plan("1.2.3", release_date="2026-06-01")

    changes = prepare_release(tmp_path, plan)

    assert {change.path.as_posix() for change in changes if change.changed} == {
        "pyproject.toml",
        "src/desktop_app/constants.py",
        "src/desktop_app/settings.toml",
        "scripts/version_info.txt",
        "tests/test_constants.py",
        "CHANGELOG.md",
    }
    assert plan.windows_version == "1.2.3.0"
    assert plan.version_tuple == (1, 2, 3, 0)
    assert 'version = "1.2.3"' in _read(tmp_path, "pyproject.toml")
    assert 'APPLICATION_VERSION: Final[str] = "1.2.3"' in _read(
        tmp_path, "src/desktop_app/constants.py"
    )
    assert 'version = "1.2.3"' in _read(tmp_path, "src/desktop_app/settings.toml")
    assert "filevers=(1, 2, 3, 0)" in _read(tmp_path, "scripts/version_info.txt")
    assert "prodvers=(1, 2, 3, 0)" in _read(tmp_path, "scripts/version_info.txt")
    assert 'StringStruct("FileVersion", "1.2.3.0")' in _read(
        tmp_path, "scripts/version_info.txt"
    )
    assert 'assert constants.APPLICATION_VERSION == "1.2.3"' in _read(
        tmp_path, "tests/test_constants.py"
    )
    assert "## [1.2.3] - 2026-06-01" in _read(tmp_path, "CHANGELOG.md")


def test_prepare_release_is_idempotent_for_existing_changelog_section(
    tmp_path: Path,
) -> None:
    """Existing changelog sections are not duplicated."""
    _write_release_project(tmp_path)
    plan = build_release_plan("1.2.3", release_date="2026-06-01")

    prepare_release(tmp_path, plan)
    second_changes = prepare_release(tmp_path, plan)

    assert not any(change.changed for change in second_changes)
    assert _read(tmp_path, "CHANGELOG.md").count("## [1.2.3]") == 1


def test_prepare_release_dry_run_reports_without_writing(tmp_path: Path) -> None:
    """Dry-run mode reports release changes but does not write files."""
    _write_release_project(tmp_path)
    plan = build_release_plan("2.0.0", release_date="2026-06-02")

    changes = prepare_release(tmp_path, plan, dry_run=True)

    assert any(change.changed for change in changes)
    assert 'version = "0.9.0"' in _read(tmp_path, "pyproject.toml")
    assert "## [2.0.0]" not in _read(tmp_path, "CHANGELOG.md")


@pytest.mark.parametrize("version", ["1", "1.2", "1.2.3.4", "v1.2.3"])
def test_build_release_plan_rejects_invalid_versions(version: str) -> None:
    """Release versions must use MAJOR.MINOR.PATCH."""
    with pytest.raises(ProjectToolError, match="MAJOR.MINOR.PATCH"):
        build_release_plan(version, release_date="2026-06-01")


def test_build_release_plan_rejects_invalid_dates() -> None:
    """Release dates must use ISO format."""
    with pytest.raises(ProjectToolError, match="YYYY-MM-DD"):
        build_release_plan("1.2.3", release_date="06/01/2026")


def test_prepare_release_inserts_changelog_without_divider(tmp_path: Path) -> None:
    """Release preparation can use the first release heading as fallback."""
    _write_release_project(
        tmp_path, changelog="# Changelog\n\n## [0.9.0] - 2026-05-15\n"
    )
    plan = build_release_plan("1.0.0", release_date="2026-06-03")

    prepare_release(tmp_path, plan)

    assert "# Changelog\n\n## [1.0.0] - 2026-06-03\n" in _read(tmp_path, "CHANGELOG.md")


def test_prepare_release_fails_when_changelog_has_no_insertion_point(
    tmp_path: Path,
) -> None:
    """Release preparation fails clearly for malformed changelogs."""
    _write_release_project(tmp_path, changelog="# Changelog\n")
    plan = build_release_plan("1.0.0", release_date="2026-06-03")

    with pytest.raises(ProjectToolError, match="CHANGELOG.md"):
        prepare_release(tmp_path, plan)


def test_prepare_release_fails_when_required_marker_is_missing(tmp_path: Path) -> None:
    """Release preparation fails when an expected version marker changes."""
    _write_release_project(tmp_path)
    _write(tmp_path, "scripts/version_info.txt", "filevers=(0, 9, 0, 0)\n")
    plan = build_release_plan("1.0.0", release_date="2026-06-03")

    with pytest.raises(ProjectToolError, match="prodvers"):
        prepare_release(tmp_path, plan)


def _write_release_project(project_root: Path, *, changelog: str | None = None) -> None:
    """Create a minimal release-managed project tree."""
    _write(project_root, "pyproject.toml", '[project]\nversion = "0.9.0"\n')
    _write(
        project_root,
        "src/desktop_app/constants.py",
        'from typing import Final\nAPPLICATION_VERSION: Final[str] = "0.9.0"\n',
    )
    _write(project_root, "src/desktop_app/settings.toml", '[app]\nversion = "0.9.0"\n')
    _write(
        project_root,
        "scripts/version_info.txt",
        """filevers=(0, 9, 0, 0)
prodvers=(0, 9, 0, 0)
StringStruct("FileVersion", "0.9.0.0")
StringStruct("ProductVersion", "0.9.0.0")
""",
    )
    _write(
        project_root,
        "tests/test_constants.py",
        'assert constants.APPLICATION_VERSION == "0.9.0"\n',
    )
    _write(
        project_root,
        "CHANGELOG.md",
        changelog or "# Changelog\n\n---\n\n## [0.9.0] - 2026-05-15\n",
    )


def _write(project_root: Path, relative_path: str, content: str) -> None:
    """Write a project-relative UTF-8 file."""
    file_path = project_root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def _read(project_root: Path, relative_path: str) -> str:
    """Read a project-relative UTF-8 file."""
    return (project_root / relative_path).read_text(encoding="utf-8")
