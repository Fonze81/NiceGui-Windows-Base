# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/logging_helpers.py
# Purpose:
# Provide defensive logging helpers for the settings package.
# Behavior:
# Allows settings startup code to emit diagnostics only when a logger is
# available, without forcing callers to pass one.
# Notes:
# The helpers intentionally accept logging.Logger instead of the project logger
# service so settings code can remain easy to test.
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
from typing import Any


def log_debug(logger: logging.Logger | None, message: str, *args: Any) -> None:
    """Log a debug message when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message format.
        args: Message arguments.
    """
    if logger is not None:
        logger.debug(message, *args)


def log_info(logger: logging.Logger | None, message: str, *args: Any) -> None:
    """Log an info message when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message format.
        args: Message arguments.
    """
    if logger is not None:
        logger.info(message, *args)


def log_warning(logger: logging.Logger | None, message: str, *args: Any) -> None:
    """Log a warning message when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message format.
        args: Message arguments.
    """
    if logger is not None:
        logger.warning(message, *args)


def log_exception(logger: logging.Logger | None, message: str, *args: Any) -> None:
    """Log an exception message when a logger is available.

    Args:
        logger: Optional logger instance.
        message: Message format.
        args: Message arguments.
    """
    if logger is not None:
        logger.exception(message, *args)
