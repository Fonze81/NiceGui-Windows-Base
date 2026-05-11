# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/file_system.py
# Purpose:
# Provide small file-system helpers reused by infrastructure modules.
# Behavior:
# Centralizes parent-directory creation and atomic text writes so persistence
# code does not duplicate low-level file handling.
# Notes:
# This module must stay independent from logging, settings, and UI code so it
# can be reused safely during early startup.
# -----------------------------------------------------------------------------

from __future__ import annotations

from contextlib import suppress
from os import PathLike
from pathlib import Path

type _FilePath = str | PathLike[str]


def ensure_parent_dir(file_path: _FilePath) -> None:
    """Ensure that the parent directory for a file exists.

    Args:
        file_path: File path whose parent directory must exist.
    """
    target_path = Path(file_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(
    file_path: _FilePath,
    content: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Write text using an atomic file replacement.

    Args:
        file_path: Final destination file.
        content: Text content to write.
        encoding: Text encoding used by the temporary file.

    Raises:
        OSError: If the temporary file cannot be written, removed, or replaced.
        UnicodeError: If the content cannot be encoded with the selected encoding.
    """
    target_path = Path(file_path)
    ensure_parent_dir(target_path)

    temporary_path = target_path.with_name(f"{target_path.name}.tmp")

    try:
        temporary_path.write_text(content, encoding=encoding)
        temporary_path.replace(target_path)
    except (OSError, UnicodeError):
        with suppress(OSError):
            temporary_path.unlink(missing_ok=True)

        raise
