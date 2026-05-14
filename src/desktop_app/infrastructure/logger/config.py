# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/config.py
# Purpose:
# Define the configuration object used by the logging subsystem.
# Behavior:
# Provides a small dataclass with the options required to initialize console
# logging, bounded memory buffering, and rotating file logging.
# Notes:
# Validation is intentionally handled by validators.py so this object remains a
# simple data container.
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path

from desktop_app.infrastructure.logger.defaults import (
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGGER_NAME,
    DEFAULT_ROTATE_BACKUP_COUNT,
    DEFAULT_ROTATE_MAX_BYTES,
)

type LoggerLevel = int | str
type LogFilePath = str | Path
type LogRotationSize = int | str


@dataclass(slots=True)
class LoggerConfig:
    """Store logger configuration options.

    Attributes:
        name: Application root logger name.
        level: Minimum accepted log level as an integer or string.
        enable_console: Whether logs should also be written to the console.
        buffer_capacity: Maximum number of records kept before file logging.
        file_path: Main log file path.
        rotate_max_bytes: Maximum log file size before rotation.
        rotate_backup_count: Number of rotated log files to keep.
    """

    name: str = DEFAULT_LOGGER_NAME
    level: LoggerLevel = DEFAULT_LOG_LEVEL
    enable_console: bool = True
    buffer_capacity: int = DEFAULT_BUFFER_CAPACITY
    file_path: LogFilePath = DEFAULT_LOG_FILE_PATH
    rotate_max_bytes: LogRotationSize = DEFAULT_ROTATE_MAX_BYTES
    rotate_backup_count: int = DEFAULT_ROTATE_BACKUP_COUNT
