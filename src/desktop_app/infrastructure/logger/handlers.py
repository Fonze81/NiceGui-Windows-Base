# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/handlers.py
# Purpose:
# Create and manage handlers used by the logging subsystem.
# Behavior:
# Provides console, bounded memory, and rotating file handlers. It also exposes
# safe helper functions to flush buffered records and remove or close handlers
# without interrupting the application during logging cleanup.
# Notes:
# The bounded memory handler keeps only the most recent records to avoid
# unbounded growth before file logging is enabled.
# -----------------------------------------------------------------------------

import logging
from contextlib import suppress
from logging import Handler, Logger, LogRecord
from logging.handlers import MemoryHandler, RotatingFileHandler
from pathlib import Path

from desktop_app.constants import (
    CONSOLE_DATE_FORMAT,
    CONSOLE_LOG_FORMAT,
    FILE_DATE_FORMAT,
    FILE_LOG_FORMAT,
)
from desktop_app.infrastructure.file_system import ensure_parent_dir


class BoundedMemoryHandler(MemoryHandler):
    """Keep only the most recent log records in memory.

    This avoids the default MemoryHandler behavior of accumulating records
    indefinitely when no target handler is configured yet.
    """

    def emit(self, record: LogRecord) -> None:
        """Store a record while respecting the configured capacity.

        Args:
            record: Log record received by the handler.
        """
        self.buffer.append(record)

        overflow = len(self.buffer) - self.capacity
        if overflow > 0:
            del self.buffer[:overflow]


def create_console_handler(level: int) -> Handler:
    """Create the handler responsible for console log output.

    Args:
        level: Minimum accepted log level.

    Returns:
        Configured console handler.
    """
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt=CONSOLE_LOG_FORMAT,
            datefmt=CONSOLE_DATE_FORMAT,
        )
    )
    return handler


def create_bounded_memory_handler(capacity: int, level: int) -> MemoryHandler:
    """Create the temporary bounded handler used before file logging is available.

    Args:
        capacity: Maximum number of records kept in memory.
        level: Minimum accepted log level.

    Returns:
        Bounded memory handler.
    """
    handler = BoundedMemoryHandler(
        capacity=capacity,
        flushLevel=logging.CRITICAL + 1,
        target=None,
    )
    handler.setLevel(level)
    return handler


def create_rotating_file_handler(
    file_path: Path,
    level: int,
    max_bytes: int,
    backup_count: int,
) -> RotatingFileHandler:
    """Create the handler responsible for writing rotating file logs.

    Args:
        file_path: Main log file path.
        level: Minimum accepted log level.
        max_bytes: Maximum file size before rotation.
        backup_count: Number of rotated files to keep.

    Returns:
        Configured rotating file handler.
    """
    ensure_parent_dir(file_path)

    handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt=FILE_LOG_FORMAT,
            datefmt=FILE_DATE_FORMAT,
        )
    )
    return handler


def flush_memory_handler_to_target(
    memory_handler: MemoryHandler | None,
    target_handler: Handler,
) -> None:
    """Send buffered memory records to a target handler.

    Args:
        memory_handler: Temporary handler that stored early log records.
        target_handler: Handler that will receive preserved records.
    """
    if memory_handler is None:
        return

    for record in list(memory_handler.buffer):
        target_handler.handle(record)

    with suppress(Exception):
        target_handler.flush()

    memory_handler.buffer.clear()


def remove_handler_safely(logger: Logger, handler: Handler | None) -> None:
    """Remove a handler from a logger without propagating cleanup failures.

    Args:
        logger: Logger that may contain the handler.
        handler: Handler to remove.
    """
    if handler is None:
        return

    with suppress(Exception):
        logger.removeHandler(handler)


def close_handler_safely(handler: Handler | None) -> None:
    """Close a handler without propagating I/O failures.

    Args:
        handler: Handler to flush and close.
    """
    if handler is None:
        return

    with suppress(Exception):
        handler.flush()

    with suppress(Exception):
        handler.close()


def remove_and_close_handler_safely(
    logger: Logger,
    handler: Handler | None,
) -> None:
    """Remove and close a handler defensively.

    Args:
        logger: Logger that may contain the handler.
        handler: Handler to remove and close.
    """
    remove_handler_safely(logger, handler)
    close_handler_safely(handler)
