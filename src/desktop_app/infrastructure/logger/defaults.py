# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/defaults.py
# Purpose:
# Store default values used by the logging package.
# Behavior:
# Provides logger names, file paths, handler formats, buffer limits, and rotation
# limits without depending on application-level constants.
# Notes:
# Keep this module free of runtime logic and imports from outside the logger
# package so the logging subsystem can be reused in other projects more easily.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
from typing import Final

DEFAULT_LOGGER_NAME: Final[str] = "desktop_app"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_LOG_FILE_PATH: Final[Path] = Path("logs") / "app.log"

DEFAULT_BUFFER_CAPACITY: Final[int] = 500
DEFAULT_ROTATE_MAX_BYTES: Final[int] = 5 * 1024 * 1024
DEFAULT_ROTATE_BACKUP_COUNT: Final[int] = 3

MIN_BUFFER_CAPACITY: Final[int] = 1
MAX_BUFFER_CAPACITY: Final[int] = 100_000

MIN_ROTATE_MAX_BYTES: Final[int] = 1 * 1024 * 1024
MAX_ROTATE_MAX_BYTES: Final[int] = 1 * 1024 * 1024 * 1024

MIN_ROTATE_BACKUP_COUNT: Final[int] = 0
MAX_ROTATE_BACKUP_COUNT: Final[int] = 100

CONSOLE_LOG_FORMAT: Final[str] = "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s"
FILE_LOG_FORMAT: Final[str] = (
    "%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)
CONSOLE_DATE_FORMAT: Final[str] = "%H:%M:%S"
FILE_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

__all__: Final[tuple[str, ...]] = (
    "DEFAULT_LOGGER_NAME",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_FILE_PATH",
    "DEFAULT_BUFFER_CAPACITY",
    "DEFAULT_ROTATE_MAX_BYTES",
    "DEFAULT_ROTATE_BACKUP_COUNT",
    "MIN_BUFFER_CAPACITY",
    "MAX_BUFFER_CAPACITY",
    "MIN_ROTATE_MAX_BYTES",
    "MAX_ROTATE_MAX_BYTES",
    "MIN_ROTATE_BACKUP_COUNT",
    "MAX_ROTATE_BACKUP_COUNT",
    "CONSOLE_LOG_FORMAT",
    "FILE_LOG_FORMAT",
    "CONSOLE_DATE_FORMAT",
    "FILE_DATE_FORMAT",
)
