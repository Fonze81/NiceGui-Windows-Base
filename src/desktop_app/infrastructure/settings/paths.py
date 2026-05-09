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

from desktop_app.constants import (
    APP_ROOT_ENV_VAR,
    SETTINGS_FILE_NAME,
)
from desktop_app.core.runtime import is_frozen_executable


def resolve_settings_root() -> Path:
    """Resolve the persistent settings root directory.

    Returns:
        Directory used for the editable settings.toml file.
    """
    settings_root_value = os.getenv(APP_ROOT_ENV_VAR)

    if settings_root_value:
        return Path(settings_root_value).expanduser().resolve()

    if is_frozen_executable():
        return Path(sys.executable).resolve().parent

    return Path.cwd().resolve()


def resolve_settings_file_path() -> Path:
    """Resolve the default persistent settings file path.

    Returns:
        Absolute path to the editable settings.toml file.
    """
    return resolve_settings_root() / SETTINGS_FILE_NAME


def resolve_default_settings_path() -> Path:
    """Resolve the default persistent settings file path.

    Returns:
        Absolute path to the editable settings.toml file.
    """
    return resolve_settings_file_path()


def resolve_pyinstaller_temp_dir() -> Path | None:
    """Resolve the PyInstaller extraction directory when available.

    Returns:
        Extraction directory, or None during normal Python execution.
    """
    pyinstaller_temp_dir: str | None = getattr(sys, "_MEIPASS", None)

    if pyinstaller_temp_dir is None:
        return None

    return Path(pyinstaller_temp_dir).resolve()


def get_pyinstaller_temp_dir() -> Path | None:
    """Resolve the PyInstaller extraction directory when available.

    Returns:
        Extraction directory, or None during normal Python execution.
    """
    return resolve_pyinstaller_temp_dir()


def resolve_bundled_settings_candidate_paths() -> list[Path]:
    """Resolve candidate paths for the bundled settings template.

    Returns:
        Ordered list of template candidate paths.
    """
    candidate_paths: list[Path] = []
    pyinstaller_temp_dir = resolve_pyinstaller_temp_dir()

    if pyinstaller_temp_dir is not None:
        candidate_paths.append(
            pyinstaller_temp_dir / "desktop_app" / SETTINGS_FILE_NAME
        )
        candidate_paths.append(pyinstaller_temp_dir / SETTINGS_FILE_NAME)

    package_root = Path(__file__).resolve().parents[2]
    candidate_paths.append(package_root / SETTINGS_FILE_NAME)
    candidate_paths.append(Path.cwd() / SETTINGS_FILE_NAME)

    return candidate_paths


def get_bundled_settings_candidate_paths() -> list[Path]:
    """Resolve candidate paths for the bundled settings template.

    Returns:
        Ordered list of template candidate paths.
    """
    return resolve_bundled_settings_candidate_paths()


def read_bundled_settings_template_text() -> str | None:
    """Read the bundled settings template text when available.

    Returns:
        Template text, or None when no candidate exists.
    """
    for candidate_path in resolve_bundled_settings_candidate_paths():
        if candidate_path.is_file():
            return candidate_path.read_text(encoding="utf-8")

    return None


def read_bundled_settings_text() -> str | None:
    """Read the bundled settings template text when available.

    Returns:
        Template text, or None when no candidate exists.
    """
    return read_bundled_settings_template_text()
