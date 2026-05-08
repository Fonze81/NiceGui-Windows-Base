# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/service.py
# Purpose:
# Expose simple functions for using the logging subsystem across the application.
# Behavior:
# Maintains a single controlled LoggerBootstrapper instance and provides
# functions for bootstrap, configuration updates, child logger access, file
# logging activation, and shutdown.
# Notes:
# The module-level instance is a controlled singleton. It prevents each part of
# the application from creating its own handlers, which could duplicate log
# messages and keep log files locked on Windows. logger_get_logger() is safe to
# call during module import because it performs an early memory-only bootstrap
# when the official logger configuration has not been applied yet.
# -----------------------------------------------------------------------------

import logging
from logging import Logger
from pathlib import Path

from desktop_app.infrastructure.logger.bootstrapper import LoggerBootstrapper
from desktop_app.infrastructure.logger.config import LoggerConfig

_logger_bootstrapper: LoggerBootstrapper | None = None


def logger_create_bootstrapper(
    config: LoggerConfig | None = None,
) -> LoggerBootstrapper:
    """Create an independent LoggerBootstrapper instance.

    Args:
        config: Optional logger configuration. When omitted, early bootstrap uses
            memory buffering without console output.

    Returns:
        Configured bootstrapper instance.
    """
    bootstrap_config = config or LoggerConfig(enable_console=False)
    return LoggerBootstrapper(config=bootstrap_config)


def logger_get_bootstrapper() -> LoggerBootstrapper:
    """Return the global bootstrapper, creating it when needed.

    Returns:
        Global LoggerBootstrapper instance.
    """
    global _logger_bootstrapper

    if _logger_bootstrapper is None:
        _logger_bootstrapper = logger_create_bootstrapper()

    return _logger_bootstrapper


def logger_bootstrap(config: LoggerConfig | None = None) -> Logger:
    """Initialize or update the global application logger.

    Args:
        config: Optional configuration used to create or update the logger.

    Returns:
        Initialized root logger.
    """
    global _logger_bootstrapper

    if _logger_bootstrapper is None:
        _logger_bootstrapper = logger_create_bootstrapper(config=config)
    elif config is not None:
        _logger_bootstrapper.update_config(config)

    return _logger_bootstrapper.bootstrap()


def logger_get_logger(name: str = "") -> Logger:
    """Return the application root logger or one of its child loggers.

    This function is safe to call during module import. If the global
    bootstrapper does not exist yet, it creates one and performs an early
    bootstrap with the memory handler so initial records can be preserved until
    file logging is enabled.

    Args:
        name: Requested logger name. It can be empty, relative, or absolute.

    Returns:
        Requested logger instance.
    """
    bootstrapper = logger_get_bootstrapper()

    if not bootstrapper.is_bootstrapped:
        bootstrapper.bootstrap()

    root_name = bootstrapper.root_logger.name
    if not name or name == root_name:
        return bootstrapper.root_logger

    if name.startswith(f"{root_name}."):
        return logging.getLogger(name)

    return bootstrapper.root_logger.getChild(name)


def logger_update_config(config: LoggerConfig) -> None:
    """Update the global logger configuration.

    Args:
        config: Requested logger configuration.
    """
    global _logger_bootstrapper

    if _logger_bootstrapper is None:
        _logger_bootstrapper = logger_create_bootstrapper(config=config)
        return

    _logger_bootstrapper.update_config(config)


def logger_enable_file_logging(file_path: Path | str | None = None) -> bool:
    """Enable file logging on the global logger.

    Args:
        file_path: Optional path used to override the configured log file path.

    Returns:
        True when file logging was enabled; False when activation failed.
    """
    return logger_get_bootstrapper().enable_file_logging(file_path)


def logger_shutdown() -> None:
    """Shut down the global logger and release active handlers."""
    global _logger_bootstrapper

    if _logger_bootstrapper is None:
        return

    _logger_bootstrapper.shutdown()
    _logger_bootstrapper = None
