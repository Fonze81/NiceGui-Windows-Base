# -----------------------------------------------------------------------------
# File: src/desktop_app/project_tools/template_customization.py
# Purpose:
# Customize public template identity values for a derived project.
# Behavior:
# Updates project metadata, command names, application title, packaging metadata,
# settings defaults, and user-facing documentation text without renaming the
# internal desktop_app package.
# Notes:
# Package renaming is intentionally out of scope because it requires coordinated
# import, test, asset, documentation, and packaging changes.
# -----------------------------------------------------------------------------

from __future__ import annotations

import re
from dataclasses import dataclass
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

DEFAULT_PROJECT_NAME: Final[str] = "nicegui-windows-base"
DEFAULT_DISPLAY_NAMES: Final[tuple[str, ...]] = (
    "NiceGui Windows Base",
    "NiceGUI Windows Base",
)
DEFAULT_AUTHOR_NAME: Final[str] = "NiceGui Windows Base contributors"
DEFAULT_STORAGE_KEY: Final[str] = "nicegui_windows_base_window_state"
ENTRY_POINT: Final[str] = "desktop_app.__main__:run"
IDENTITY_TEXT_SUFFIXES: Final[frozenset[str]] = frozenset(
    {".json", ".md", ".ps1", ".py", ".txt"}
)
IGNORED_IDENTITY_PATHS: Final[frozenset[str]] = frozenset(
    {
        "CHANGELOG.md",
        "pyproject.toml",
        "scripts/package_windows.ps1",
        "scripts/version_info.txt",
        "src/desktop_app/constants.py",
        "src/desktop_app/settings.toml",
    }
)
IGNORED_IDENTITY_PARTS: Final[tuple[tuple[str, ...], ...]] = (
    ("src", "desktop_app", "project_tools"),
    ("tests", "project_tools"),
)


@dataclass(frozen=True, slots=True)
class TemplateIdentity:
    """Describe public template identity values for a derived project.

    Attributes:
        project_name: Slug used for package metadata, CLI command, and executable.
        display_name: Human-readable application name shown to users.
        description: Project metadata description.
        author_name: Maintainer or contributor display name.
    """

    project_name: str
    display_name: str
    description: str
    author_name: str

    @property
    def executable_name(self) -> str:
        """Return the Windows executable file name."""
        return f"{self.project_name}.exe"

    @property
    def snake_name(self) -> str:
        """Return the project slug converted to snake_case."""
        return self.project_name.replace("-", "_")

    @property
    def storage_key(self) -> str:
        """Return the default native window persistence key."""
        return f"{self.snake_name}_window_state"


def build_template_identity(
    *,
    project_name: str,
    display_name: str,
    description: str,
    author_name: str,
) -> TemplateIdentity:
    """Build and validate template identity values.

    Args:
        project_name: Slug used for public commands and metadata.
        display_name: Human-readable application name.
        description: Project metadata description.
        author_name: Maintainer or contributor display name.

    Returns:
        Validated template identity.

    Raises:
        ProjectToolError: If any required value is invalid.
    """
    normalized_project_name = project_name.strip()
    normalized_display_name = display_name.strip()
    normalized_description = description.strip()
    normalized_author_name = author_name.strip()

    _validate_project_name(normalized_project_name)
    _validate_required_text(normalized_display_name, "display name")
    _validate_required_text(normalized_description, "description")
    _validate_required_text(normalized_author_name, "author name")

    return TemplateIdentity(
        project_name=normalized_project_name,
        display_name=normalized_display_name,
        description=normalized_description,
        author_name=normalized_author_name,
    )


def customize_template(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool = False,
) -> tuple[ChangedFile, ...]:
    """Apply public identity customization to the project template.

    Args:
        project_root: Repository root directory.
        identity: Public identity values for the derived project.
        dry_run: When true, report changes without writing files.

    Returns:
        File update results for every inspected file.
    """
    changes = [
        _update_pyproject(project_root, identity, dry_run=dry_run),
        _update_constants(project_root, identity, dry_run=dry_run),
        _update_settings_template(project_root, identity, dry_run=dry_run),
        _update_packaging_script(project_root, identity, dry_run=dry_run),
        _update_version_info(project_root, identity, dry_run=dry_run),
    ]
    changes.extend(_update_identity_text_files(project_root, identity, dry_run=dry_run))
    return tuple(changes)


def _validate_project_name(project_name: str) -> None:
    """Validate a package and command slug."""
    if re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", project_name) is None:
        raise ProjectToolError(
            "Project name must use lowercase letters, numbers, and hyphens only."
        )

    if "--" in project_name:
        raise ProjectToolError("Project name must not contain repeated hyphens.")


def _validate_required_text(value: str, field_name: str) -> None:
    """Validate a required non-empty text value."""
    if not value:
        raise ProjectToolError(f"Template {field_name} cannot be empty.")


def _update_pyproject(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update package metadata and the public console script."""
    relative_path = Path("pyproject.toml")
    document = tomlkit.parse(read_project_text(project_root, relative_path))
    project = document["project"]
    project["name"] = identity.project_name
    project["description"] = identity.description
    project["authors"] = [{"name": identity.author_name}]

    scripts = project["scripts"]
    for script_name in list(scripts):
        if scripts[script_name] == ENTRY_POINT:
            del scripts[script_name]
    scripts[identity.project_name] = ENTRY_POINT

    return write_project_text(
        project_root, relative_path, tomlkit.dumps(document), dry_run=dry_run
    )


def _update_constants(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update public application constants."""
    relative_path = Path("src/desktop_app/constants.py")
    text = read_project_text(project_root, relative_path)
    text = replace_required_pattern(
        text,
        r'APPLICATION_TITLE: Final\[str\] = "[^"]+"',
        f'APPLICATION_TITLE: Final[str] = "{identity.display_name}"',
        marker="APPLICATION_TITLE",
    )
    text = replace_required_pattern(
        text,
        (
            r"PYPROJECT_COMMAND_NAMES: Final\[tuple\[str, \.\.\.\]\] = "
            r'\(\n    "[^"]+",\n    "[^"]+",\n\)'
        ),
        (
            "PYPROJECT_COMMAND_NAMES: Final[tuple[str, ...]] = (\n"
            f'    "{identity.project_name}",\n'
            f'    "{identity.executable_name}",\n'
            ")"
        ),
        marker="PYPROJECT_COMMAND_NAMES",
    )
    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _update_settings_template(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update bundled default settings identity values."""
    relative_path = Path("src/desktop_app/settings.toml")
    document = tomlkit.parse(read_project_text(project_root, relative_path))
    document["app"]["name"] = identity.display_name
    document["app"]["window"]["storage_key"] = identity.storage_key
    return write_project_text(
        project_root, relative_path, tomlkit.dumps(document), dry_run=dry_run
    )


def _update_packaging_script(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update the executable name used by the packaging script."""
    relative_path = Path("scripts/package_windows.ps1")
    text = read_project_text(project_root, relative_path)
    text = replace_required_pattern(
        text,
        r'\$appName = "[^"]+"',
        f'$appName = "{identity.project_name}"',
        marker="$appName",
    )
    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _update_version_info(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> ChangedFile:
    """Update Windows version resource identity strings."""
    relative_path = Path("scripts/version_info.txt")
    text = read_project_text(project_root, relative_path)
    replacements = {
        "CompanyName": identity.author_name,
        "FileDescription": identity.display_name,
        "InternalName": identity.project_name,
        "LegalCopyright": f"Copyright (c) {identity.author_name}",
        "OriginalFilename": identity.executable_name,
        "ProductName": identity.display_name,
    }
    for key, value in replacements.items():
        text = _replace_version_string_struct(text, key, value)

    return write_project_text(project_root, relative_path, text, dry_run=dry_run)


def _replace_version_string_struct(text: str, key: str, value: str) -> str:
    """Replace a StringStruct value inside scripts/version_info.txt."""
    return replace_required_pattern(
        text,
        rf'(StringStruct\(\s*"{re.escape(key)}",\s*")[^"]*("\s*,?\s*\))',
        rf"\g<1>{value}\2",
        marker=f"StringStruct {key}",
        flags=re.DOTALL,
    )


def _update_identity_text_files(
    project_root: Path,
    identity: TemplateIdentity,
    *,
    dry_run: bool,
) -> tuple[ChangedFile, ...]:
    """Update user-facing identity references in project text files."""
    changes: list[ChangedFile] = []
    for relative_path in _iter_identity_text_paths(project_root):
        text = read_project_text(project_root, relative_path)
        updated_text = _replace_identity_tokens(text, identity)
        changes.append(
            write_project_text(
                project_root,
                relative_path,
                updated_text,
                dry_run=dry_run,
            )
        )
    return tuple(changes)


def _iter_identity_text_paths(project_root: Path) -> tuple[Path, ...]:
    """Return text files that may contain public identity references."""
    relative_paths: list[Path] = []
    for file_path in project_root.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(project_root)
        if _should_skip_identity_path(relative_path):
            continue

        relative_paths.append(relative_path)

    return tuple(sorted(relative_paths))


def _should_skip_identity_path(relative_path: Path) -> bool:
    """Return whether a file should be ignored by identity text replacement."""
    parts = relative_path.parts
    if relative_path.as_posix() in IGNORED_IDENTITY_PATHS:
        return True

    if any(parts[: len(ignored)] == ignored for ignored in IGNORED_IDENTITY_PARTS):
        return True

    if any(part in {".git", ".venv", "build", "dist"} for part in parts):
        return True

    return not (
        relative_path.suffix in IDENTITY_TEXT_SUFFIXES
        or relative_path.name.endswith(".code-workspace")
    )


def _replace_identity_tokens(text: str, identity: TemplateIdentity) -> str:
    """Replace default template identity tokens in text content."""
    updated_text = text
    for display_name in DEFAULT_DISPLAY_NAMES:
        updated_text = updated_text.replace(display_name, identity.display_name)

    return (
        updated_text.replace(DEFAULT_PROJECT_NAME, identity.project_name)
        .replace(DEFAULT_STORAGE_KEY, identity.storage_key)
        .replace(DEFAULT_AUTHOR_NAME, identity.author_name)
    )
