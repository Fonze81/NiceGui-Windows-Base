# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/paths.py
# Purpose:
# Resolve the runtime location of application log files.
# Behavior:
# Builds a writable log path in the current working directory during normal
# Python execution and next to the executable during PyInstaller execution.
# Notes:
# This module intentionally avoids importing runtime.py because runtime.py uses
# the logger package during import. Keeping the path resolver here prevents a
# circular dependency between runtime detection and logging initialization.
# -----------------------------------------------------------------------------

import sys
from os import PathLike
from pathlib import Path

from desktop_app.constants import DEFAULT_LOG_FILE_PATH

type _PathInput = str | PathLike[str]


def resolve_log_file_path(
    log_file_path: _PathInput = DEFAULT_LOG_FILE_PATH,
    *,
    frozen_executable: bool | None = None,
    executable_path: _PathInput | None = None,
    working_directory: _PathInput | None = None,
) -> Path:
    """Return the runtime log file path.

    Args:
        log_file_path: Relative or absolute log file path.
        frozen_executable: Optional explicit frozen state. When omitted, the
            value is read from sys.frozen.
        executable_path: Optional executable path. When omitted, sys.executable
            is used for frozen execution.
        working_directory: Optional working directory. When omitted, Path.cwd()
            is used for normal Python execution.

    Returns:
        Absolute log file path for the current runtime.
    """
    requested_path = Path(log_file_path)

    if requested_path.is_absolute():
        return requested_path

    if _is_frozen_executable(frozen_executable):
        runtime_executable = Path(executable_path or sys.executable).resolve()
        return runtime_executable.parent / requested_path

    runtime_working_directory = Path(working_directory or Path.cwd()).resolve()
    return runtime_working_directory / requested_path


def _is_frozen_executable(frozen_executable: bool | None) -> bool:
    """Return whether the current process is a frozen executable.

    Args:
        frozen_executable: Optional explicit frozen state.

    Returns:
        True when the process is frozen; otherwise False.
    """
    if frozen_executable is not None:
        return frozen_executable

    return bool(getattr(sys, "frozen", False))
