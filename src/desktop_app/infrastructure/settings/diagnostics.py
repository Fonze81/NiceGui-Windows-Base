# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/diagnostics.py
# Purpose:
# Isolate optional logging helpers used by the settings package.
# Behavior:
# Writes diagnostic messages only when a logger instance is provided, allowing
# settings loading to run safely before final file logging is active.
# Notes:
# Log messages remain in English and use deferred formatting arguments.
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging


def log_debug(logger: logging.Logger | None, message: str, *args: object) -> None:
    """Log a debug message only when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message written to the logger.
        *args: Deferred logging format arguments.
    """
    if logger is not None:
        logger.debug(message, *args)


def log_info(logger: logging.Logger | None, message: str, *args: object) -> None:
    """Log an info message only when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message written to the logger.
        *args: Deferred logging format arguments.
    """
    if logger is not None:
        logger.info(message, *args)


def log_warning(logger: logging.Logger | None, message: str, *args: object) -> None:
    """Log a warning message only when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message written to the logger.
        *args: Deferred logging format arguments.
    """
    if logger is not None:
        logger.warning(message, *args)


def log_exception(logger: logging.Logger | None, message: str) -> None:
    """Log an exception only when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message written to the logger.
    """
    if logger is not None:
        logger.exception(message)
