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

from pathlib import Path


def ensure_parent_dir(file_path: Path) -> None:
    """Ensure that the parent directory for a file exists.

    Args:
        file_path: File path whose parent directory must exist.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(
    file_path: Path,
    content: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Write text using an atomic file replacement.

    Args:
        file_path: Final destination file.
        content: Text content to write.
        encoding: Text encoding used by the temporary file.
    """
    ensure_parent_dir(file_path)

    temporary_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    temporary_path.write_text(content, encoding=encoding)
    temporary_path.replace(file_path)
