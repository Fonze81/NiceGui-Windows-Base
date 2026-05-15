# -----------------------------------------------------------------------------
# File: src/desktop_app/project_tools/common.py
# Purpose:
# Provide shared file helpers for project maintenance tools.
# Behavior:
# Reads and updates repository files using relative paths, reports changed files,
# and fails fast when expected release or template markers are missing.
# Notes:
# These helpers are intentionally small and have no NiceGUI dependency so release
# and customization scripts can run safely before the desktop application starts.
# -----------------------------------------------------------------------------

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

UTF8: Final[str] = "utf-8"


class ProjectToolError(RuntimeError):
    """Represent a recoverable project maintenance tool error."""


@dataclass(frozen=True, slots=True)
class ChangedFile:
    """Describe the result of a file update.

    Attributes:
        path: Project-relative file path.
        changed: Whether the file content changed or would change in dry-run mode.
    """

    path: Path
    changed: bool


def read_project_text(project_root: Path, relative_path: str | Path) -> str:
    """Read a UTF-8 project file.

    Args:
        project_root: Repository root directory.
        relative_path: Path relative to the repository root.

    Returns:
        File content.

    Raises:
        ProjectToolError: If the expected file does not exist.
    """
    file_path = project_root / relative_path
    if not file_path.is_file():
        raise ProjectToolError(f"Expected project file was not found: {relative_path}")

    return file_path.read_text(encoding=UTF8)


def write_project_text(
    project_root: Path,
    relative_path: str | Path,
    content: str,
    *,
    dry_run: bool = False,
) -> ChangedFile:
    """Write a UTF-8 project file only when content changes.

    Args:
        project_root: Repository root directory.
        relative_path: Path relative to the repository root.
        content: New file content.
        dry_run: When true, report changes without writing files.

    Returns:
        File update result.
    """
    current_content = read_project_text(project_root, relative_path)
    changed = current_content != content
    if changed and not dry_run:
        (project_root / relative_path).write_text(content, encoding=UTF8)

    return ChangedFile(Path(relative_path), changed)


def replace_required_pattern(
    text: str,
    pattern: str,
    replacement: str,
    *,
    marker: str,
    flags: int = 0,
) -> str:
    """Replace a required regular expression pattern once.

    Args:
        text: Source text.
        pattern: Regular expression pattern.
        replacement: Replacement text.
        marker: Human-readable marker used in error messages.
        flags: Regular expression flags.

    Returns:
        Updated text.

    Raises:
        ProjectToolError: If the required pattern is missing.
    """
    updated_text, replacement_count = re.subn(
        pattern, replacement, text, count=1, flags=flags
    )
    if replacement_count != 1:
        raise ProjectToolError(f"Required marker was not found: {marker}")

    return updated_text
