# -----------------------------------------------------------------------------
# File: tests/project_tools/test_template_customization.py
# Purpose:
# Validate template identity customization helpers.
# Behavior:
# Builds a minimal project tree, applies customization, and checks metadata,
# settings, packaging resources, documentation text, validation, and dry-run mode.
# Notes:
# Tests use temporary files only and do not modify the real repository.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

import pytest

from desktop_app.project_tools.common import ProjectToolError
from desktop_app.project_tools.template_customization import (
    build_template_identity,
    customize_template,
)


def test_customize_template_updates_public_identity(tmp_path: Path) -> None:
    """Template customization updates the public identity contract."""
    _write_template_project(tmp_path)
    identity = build_template_identity(
        project_name="inventory-dashboard",
        display_name="Inventory Dashboard",
        description="Inventory tracking desktop application.",
        author_name="Example Team",
    )

    changes = customize_template(tmp_path, identity)

    changed_paths = {change.path.as_posix() for change in changes if change.changed}
    assert "pyproject.toml" in changed_paths
    assert "src/desktop_app/constants.py" in changed_paths
    assert "src/desktop_app/settings.toml" in changed_paths
    assert "scripts/package_windows.ps1" in changed_paths
    assert "scripts/version_info.txt" in changed_paths
    assert "README.md" in changed_paths

    assert 'name = "inventory-dashboard"' in _read(tmp_path, "pyproject.toml")
    assert 'description = "Inventory tracking desktop application."' in _read(
        tmp_path, "pyproject.toml"
    )
    assert 'inventory-dashboard = "desktop_app.__main__:run"' in _read(
        tmp_path, "pyproject.toml"
    )
    assert 'APPLICATION_TITLE: Final[str] = "Inventory Dashboard"' in _read(
        tmp_path, "src/desktop_app/constants.py"
    )
    assert '"inventory-dashboard.exe"' in _read(
        tmp_path, "src/desktop_app/constants.py"
    )
    assert 'name = "Inventory Dashboard"' in _read(
        tmp_path, "src/desktop_app/settings.toml"
    )
    assert 'storage_key = "inventory_dashboard_window_state"' in _read(
        tmp_path, "src/desktop_app/settings.toml"
    )
    assert '$appName = "inventory-dashboard"' in _read(
        tmp_path, "scripts/package_windows.ps1"
    )
    assert 'StringStruct("ProductName", "Inventory Dashboard")' in _read(
        tmp_path, "scripts/version_info.txt"
    )
    assert 'StringStruct("OriginalFilename", "inventory-dashboard.exe")' in _read(
        tmp_path, "scripts/version_info.txt"
    )
    assert "Inventory Dashboard" in _read(tmp_path, "README.md")
    assert "inventory-dashboard" in _read(tmp_path, "README.md")
    assert "nicegui-windows-base" not in _read(tmp_path, "README.md")
    assert "inventory_dashboard_window_state" in _read(
        tmp_path, "src/desktop_app/core/state.py"
    )
    assert "Inventory Dashboard" in _read(
        tmp_path, "NiceGui Windows Base.code-workspace"
    )
    assert "NiceGui Windows Base" in _read(tmp_path, ".venv/ignored.py")
    assert "NiceGui Windows Base" in _read(tmp_path, "CHANGELOG.md")
    assert "NiceGui Windows Base" in _read(
        tmp_path, "src/desktop_app/project_tools/template_customization.py"
    )
    assert "NiceGui Windows Base" in _read(
        tmp_path, "tests/project_tools/test_template_customization.py"
    )


def test_customize_template_dry_run_reports_without_writing(tmp_path: Path) -> None:
    """Dry-run mode reports changes but leaves files untouched."""
    _write_template_project(tmp_path)
    identity = build_template_identity(
        project_name="sales-console",
        display_name="Sales Console",
        description="Sales workflow application.",
        author_name="Sales Team",
    )

    changes = customize_template(tmp_path, identity, dry_run=True)

    assert any(change.changed for change in changes)
    assert 'name = "nicegui-windows-base"' in _read(tmp_path, "pyproject.toml")
    assert 'APPLICATION_TITLE: Final[str] = "NiceGui Windows Base"' in _read(
        tmp_path, "src/desktop_app/constants.py"
    )


@pytest.mark.parametrize(
    ("project_name", "message"),
    [
        ("Invalid", "lowercase"),
        ("bad_name", "lowercase"),
        ("bad--name", "repeated hyphens"),
        ("-bad", "lowercase"),
    ],
)
def test_build_template_identity_rejects_invalid_project_names(
    project_name: str,
    message: str,
) -> None:
    """Project slugs must be safe for package metadata and commands."""
    with pytest.raises(ProjectToolError, match=message):
        build_template_identity(
            project_name=project_name,
            display_name="Valid Name",
            description="Valid description.",
            author_name="Valid Author",
        )


@pytest.mark.parametrize(
    ("display_name", "description", "author_name", "message"),
    [
        ("", "Description", "Author", "display name"),
        ("Display", "", "Author", "description"),
        ("Display", "Description", "", "author name"),
    ],
)
def test_build_template_identity_rejects_empty_required_text(
    display_name: str,
    description: str,
    author_name: str,
    message: str,
) -> None:
    """Required text identity fields cannot be empty."""
    with pytest.raises(ProjectToolError, match=message):
        build_template_identity(
            project_name="valid-project",
            display_name=display_name,
            description=description,
            author_name=author_name,
        )


def test_customize_template_fails_when_expected_file_is_missing(tmp_path: Path) -> None:
    """Customization fails clearly when the project tree is incomplete."""
    identity = build_template_identity(
        project_name="valid-project",
        display_name="Valid Project",
        description="Valid description.",
        author_name="Valid Author",
    )

    with pytest.raises(ProjectToolError, match="pyproject.toml"):
        customize_template(tmp_path, identity)


def test_customize_template_fails_when_required_marker_is_missing(
    tmp_path: Path,
) -> None:
    """Customization fails clearly when an expected marker changes."""
    _write_template_project(tmp_path)
    _write(tmp_path, "src/desktop_app/constants.py", "APPLICATION_VERSION = '0.9.0'\n")
    identity = build_template_identity(
        project_name="valid-project",
        display_name="Valid Project",
        description="Valid description.",
        author_name="Valid Author",
    )

    with pytest.raises(ProjectToolError, match="APPLICATION_TITLE"):
        customize_template(tmp_path, identity)


def _write_template_project(project_root: Path) -> None:
    """Create a minimal template-like project tree."""
    _write(
        project_root,
        "pyproject.toml",
        """[project]
name = "nicegui-windows-base"
version = "0.9.0"
description = "A Windows base template for NiceGUI applications."
authors = [{ name = "NiceGui Windows Base contributors" }]

[project.scripts]
nicegui-windows-base = "desktop_app.__main__:run"
other-command = "other.module:run"
""",
    )
    _write(
        project_root,
        "src/desktop_app/constants.py",
        """from typing import Final

APPLICATION_TITLE: Final[str] = "NiceGui Windows Base"
APPLICATION_VERSION: Final[str] = "0.9.0"
PYPROJECT_COMMAND_NAMES: Final[tuple[str, ...]] = (
    "nicegui-windows-base",
    "nicegui-windows-base.exe",
)
""",
    )
    _write(
        project_root,
        "src/desktop_app/settings.toml",
        """[app]
name = "NiceGui Windows Base"
version = "0.9.0"

[app.window]
storage_key = "nicegui_windows_base_window_state"
""",
    )
    _write(
        project_root,
        "scripts/package_windows.ps1",
        '$appName = "nicegui-windows-base"\n',
    )
    _write(
        project_root,
        "scripts/version_info.txt",
        """StringStruct("CompanyName", "NiceGui Windows Base contributors")
StringStruct("FileDescription", "NiceGUI Windows Base")
StringStruct("InternalName", "nicegui-windows-base")
StringStruct("LegalCopyright", "Copyright (c) NiceGui Windows Base contributors")
StringStruct("OriginalFilename", "nicegui-windows-base.exe")
StringStruct("ProductName", "NiceGUI Windows Base")
""",
    )
    for relative_path in (
        "README.md",
        "docs/README.md",
        "docs/template_customization.md",
        "src/desktop_app/core/state.py",
        "tests/test_constants.py",
        "NiceGui Windows Base.code-workspace",
    ):
        _write(
            project_root,
            relative_path,
            "NiceGui Windows Base uses nicegui-windows-base and "
            "nicegui_windows_base_window_state.\n",
        )
    _write(
        project_root,
        "CHANGELOG.md",
        "NiceGui Windows Base keeps historical nicegui-windows-base notes.\n",
    )
    _write(
        project_root,
        ".venv/ignored.py",
        "NiceGui Windows Base should be ignored in virtual environments.\n",
    )
    _write(
        project_root,
        "src/desktop_app/project_tools/template_customization.py",
        "NiceGui Windows Base and nicegui-windows-base defaults stay stable.\n",
    )
    _write(
        project_root,
        "tests/project_tools/test_template_customization.py",
        "NiceGui Windows Base and nicegui-windows-base tests stay stable.\n",
    )


def _write(project_root: Path, relative_path: str, content: str) -> None:
    """Write a project-relative UTF-8 file."""
    file_path = project_root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def _read(project_root: Path, relative_path: str) -> str:
    """Read a project-relative UTF-8 file."""
    return (project_root / relative_path).read_text(encoding="utf-8")
