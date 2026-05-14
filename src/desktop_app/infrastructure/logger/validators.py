# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/validators.py
# Purpose:
# Validate and normalize data used by the logging subsystem configuration.
# Behavior:
# Converts raw values such as logger level names, file paths, buffer limits, and
# size strings into safe values used by the rest of the logging subsystem.
# Notes:
# Exception messages are written in English because they are useful in logs,
# tracebacks, tests, and technical diagnostics.
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from desktop_app.infrastructure.logger.byte_size import parse_byte_size
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.defaults import (
    MAX_BUFFER_CAPACITY,
    MAX_ROTATE_BACKUP_COUNT,
    MAX_ROTATE_MAX_BYTES,
    MIN_BUFFER_CAPACITY,
    MIN_ROTATE_BACKUP_COUNT,
    MIN_ROTATE_MAX_BYTES,
)
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError

_STANDARD_LOG_LEVELS: Final[dict[str, int]] = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


def normalize_logger_name(name: object) -> str:
    """Validate and trim the logger name.

    Args:
        name: Raw logger name.

    Returns:
        Normalized logger name.

    Raises:
        TypeError: If the value is not a string.
        LoggerValidationError: If the value is empty.
    """
    if not isinstance(name, str):
        raise TypeError("Logger name must be a string.")

    normalized_name = name.strip()
    if not normalized_name:
        raise LoggerValidationError("Logger name must not be empty.")

    return normalized_name


def normalize_logger_level(level: object) -> int:
    """Convert a logger level into the integer value used by logging.

    Args:
        level: Raw logger level, such as logging.INFO or "INFO".

    Returns:
        Numeric logger level recognized by the logging module.

    Raises:
        TypeError: If the value type is not supported.
        LoggerValidationError: If the string does not represent a valid level.
    """
    if isinstance(level, bool):
        raise TypeError("Logger level must be an int or a string, not bool.")

    if isinstance(level, int):
        return level

    if isinstance(level, str):
        normalized_level = level.strip().upper()
        if not normalized_level:
            raise LoggerValidationError("Logger level string must not be empty.")

        resolved_level = _STANDARD_LOG_LEVELS.get(normalized_level)
        if resolved_level is not None:
            return resolved_level

        raise LoggerValidationError(
            "Logger level must be a valid logging name or integer value."
        )

    raise TypeError("Logger level must be an int or a string.")


def normalize_enable_console(enable_console: object) -> bool:
    """Validate the flag that enables or disables console logging.

    Args:
        enable_console: Raw console logging flag.

    Returns:
        Validated boolean flag.

    Raises:
        TypeError: If the value is not a boolean.
    """
    if not isinstance(enable_console, bool):
        raise TypeError("Enable console flag must be a bool.")

    return enable_console


def normalize_file_path(file_path: object) -> Path:
    """Validate and convert the log file path to Path.

    Args:
        file_path: Raw file path as a string or Path.

    Returns:
        Normalized path.

    Raises:
        TypeError: If the value type is not supported.
        LoggerValidationError: If a string path is empty.
    """
    if not isinstance(file_path, str | Path):
        raise TypeError("Log file path must be a string or pathlib.Path.")

    if isinstance(file_path, str) and not file_path.strip():
        raise LoggerValidationError("Log file path must not be empty.")

    return Path(file_path)


def normalize_size_to_bytes(size: object) -> int:
    """Validate and convert a size value to bytes.

    Args:
        size: Size in bytes or text format, such as "5 MB".

    Returns:
        Size converted to bytes.

    Raises:
        TypeError: If the value type is not supported.
        LoggerValidationError: If the value is empty, invalid, or lower than 1.
    """
    if isinstance(size, bool):
        raise TypeError("Size must be an int or a string, not bool.")

    if not isinstance(size, int | str):
        raise TypeError("Size must be an int or a string.")

    try:
        return parse_byte_size(size)
    except ValueError as exc:
        message = str(exc).replace("Byte size", "Size")
        raise LoggerValidationError(message) from exc


def normalize_buffer_capacity(buffer_capacity: object) -> int:
    """Validate the initial log buffer capacity.

    Args:
        buffer_capacity: Maximum number of records kept in memory.

    Returns:
        Validated buffer capacity.

    Raises:
        TypeError: If the value is not an integer.
        LoggerValidationError: If the value is outside the allowed range.
    """
    if isinstance(buffer_capacity, bool) or not isinstance(buffer_capacity, int):
        raise TypeError("Buffer capacity must be an int.")

    if buffer_capacity < MIN_BUFFER_CAPACITY:
        raise LoggerValidationError(
            f"Buffer capacity must be greater than or equal to {MIN_BUFFER_CAPACITY}."
        )

    if buffer_capacity > MAX_BUFFER_CAPACITY:
        raise LoggerValidationError(
            f"Buffer capacity must be less than or equal to {MAX_BUFFER_CAPACITY}."
        )

    return buffer_capacity


def normalize_rotate_max_bytes(rotate_max_bytes: object) -> int:
    """Validate the maximum log file size before rotation.

    Args:
        rotate_max_bytes: Size in bytes or text format with unit.

    Returns:
        Validated size in bytes.

    Raises:
        TypeError: If the value type is not supported.
        LoggerValidationError: If the value is outside the allowed range.
    """
    normalized_rotate_max_bytes = normalize_size_to_bytes(rotate_max_bytes)

    if normalized_rotate_max_bytes < MIN_ROTATE_MAX_BYTES:
        raise LoggerValidationError(
            f"Rotate max bytes must be greater than or equal to {MIN_ROTATE_MAX_BYTES}."
        )

    if normalized_rotate_max_bytes > MAX_ROTATE_MAX_BYTES:
        raise LoggerValidationError(
            f"Rotate max bytes must be less than or equal to {MAX_ROTATE_MAX_BYTES}."
        )

    return normalized_rotate_max_bytes


def normalize_rotate_backup_count(rotate_backup_count: object) -> int:
    """Validate the number of backup files kept during log rotation.

    Args:
        rotate_backup_count: Number of old files preserved by rotation.

    Returns:
        Validated backup count.

    Raises:
        TypeError: If the value is not an integer.
        LoggerValidationError: If the value is outside the allowed range.
    """
    if isinstance(rotate_backup_count, bool) or not isinstance(
        rotate_backup_count, int
    ):
        raise TypeError("Rotate backup count must be an int.")

    if rotate_backup_count < MIN_ROTATE_BACKUP_COUNT:
        raise LoggerValidationError(
            "Rotate backup count must be greater than or equal to "
            f"{MIN_ROTATE_BACKUP_COUNT}."
        )

    if rotate_backup_count > MAX_ROTATE_BACKUP_COUNT:
        raise LoggerValidationError(
            "Rotate backup count must be less than or equal to "
            f"{MAX_ROTATE_BACKUP_COUNT}."
        )

    return rotate_backup_count


def validate_logger_reconfiguration(
    current_config: LoggerConfig,
    new_config: LoggerConfig,
) -> None:
    """Prevent changing the root logger name during runtime.

    Args:
        current_config: Currently active logger configuration.
        new_config: Requested new logger configuration.

    Raises:
        LoggerValidationError: If the root logger name changes.
    """
    if current_config.name != new_config.name:
        raise LoggerValidationError(
            "Root logger name cannot be changed after bootstrapper creation."
        )


def normalize_logger_config(config: object) -> LoggerConfig:
    """Validate all logger configuration fields and return a normalized copy.

    Args:
        config: Raw logger configuration.

    Returns:
        Logger configuration with normalized fields.

    Raises:
        TypeError: If config is not a LoggerConfig instance.
        LoggerValidationError: If any configuration value is invalid.
    """
    if not isinstance(config, LoggerConfig):
        raise TypeError("Logger config must be a LoggerConfig instance.")

    return LoggerConfig(
        name=normalize_logger_name(config.name),
        level=normalize_logger_level(config.level),
        enable_console=normalize_enable_console(config.enable_console),
        buffer_capacity=normalize_buffer_capacity(config.buffer_capacity),
        file_path=normalize_file_path(config.file_path),
        rotate_max_bytes=normalize_rotate_max_bytes(config.rotate_max_bytes),
        rotate_backup_count=normalize_rotate_backup_count(config.rotate_backup_count),
    )
