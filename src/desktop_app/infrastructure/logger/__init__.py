# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/__init__.py
# Purpose:
# Define the public API for the application logging package.
# Behavior:
# Re-exports the classes and functions that application modules can use without
# depending on the internal organization of the logging package.
# Notes:
# Add symbols to __all__ only when they are part of the official logger API.
# Internal bootstrapper lifecycle helpers remain available from service.py for
# focused tests and package maintenance.
# -----------------------------------------------------------------------------

from desktop_app.infrastructure.logger.bootstrapper import LoggerBootstrapper
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError
from desktop_app.infrastructure.logger.paths import resolve_log_file_path
from desktop_app.infrastructure.logger.service import (
    logger_bootstrap,
    logger_enable_file_logging,
    logger_get_logger,
    logger_shutdown,
)

__all__: tuple[str, ...] = (
    "LoggerBootstrapper",
    "LoggerConfig",
    "LoggerValidationError",
    "logger_bootstrap",
    "logger_enable_file_logging",
    "logger_get_logger",
    "resolve_log_file_path",
    "logger_shutdown",
)
