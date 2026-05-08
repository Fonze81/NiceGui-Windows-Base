# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/paths.py
# Purpose:
# Resolve paths used by the settings subsystem.
# Behavior:
# Locates the persistent settings.toml file and searches for a bundled template
# during normal Python execution and PyInstaller one-file execution.
# Notes:
# In PyInstaller one-file mode, editable settings must be stored next to the
# executable, not inside the temporary extraction directory.
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import sys
from pathlib import Path

from desktop_app.infrastructure.settings.constants import (
    APP_ROOT_ENV_VAR,
    SETTINGS_FILE_NAME,
)


def is_frozen_app() -> bool:
    """Return whether the process is running as a packaged executable.

    Returns:
        True when PyInstaller marks the process as frozen.
    """
    return bool(getattr(sys, "frozen", False))


def resolve_app_root() -> Path:
    """Resolve the persistent application root.

    Returns:
        Directory used for the editable settings.toml file.
    """
    app_root = os.getenv(APP_ROOT_ENV_VAR)

    if app_root:
        return Path(app_root).expanduser().resolve()

    if is_frozen_app():
        return Path(sys.executable).resolve().parent

    return Path.cwd().resolve()


def default_settings_path() -> Path:
    """Return the default persistent settings path.

    Returns:
        Absolute path to settings.toml.
    """
    return resolve_app_root() / SETTINGS_FILE_NAME


def pyinstaller_temp_dir() -> Path | None:
    """Return the PyInstaller extraction directory when available.

    Returns:
        Extraction directory, or None during normal Python execution.
    """
    temp_dir = getattr(sys, "_MEIPASS", None)

    if temp_dir is None:
        return None

    return Path(temp_dir).resolve()


def bundled_settings_candidates() -> list[Path]:
    """Return candidate paths for the bundled settings template.

    Returns:
        Ordered list of template candidate paths.
    """
    candidates: list[Path] = []
    temp_dir = pyinstaller_temp_dir()

    if temp_dir is not None:
        candidates.append(temp_dir / "desktop_app" / SETTINGS_FILE_NAME)
        candidates.append(temp_dir / SETTINGS_FILE_NAME)

    package_root = Path(__file__).resolve().parents[2]
    candidates.append(package_root / SETTINGS_FILE_NAME)
    candidates.append(Path.cwd() / SETTINGS_FILE_NAME)

    return candidates


def read_bundled_settings_text() -> str | None:
    """Read the bundled settings template text when available.

    Returns:
        Template text, or None when no candidate exists.
    """
    for candidate in bundled_settings_candidates():
        if candidate.exists() and candidate.is_file():
            return candidate.read_text(encoding="utf-8")

    return None
