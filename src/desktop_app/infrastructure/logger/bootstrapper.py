# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/bootstrapper.py
# Purpose:
# Control the lifecycle of the application's main logger.
# Behavior:
# Configures the root application logger, keeps early records in memory, enables
# console output when requested, and later transfers preserved records to the
# main rotating log file.
# Notes:
# File operations can fail because of permissions, invalid paths, or operating
# system locks. For that reason, file logging activation returns True or False,
# logs the failure when possible, and does not stop the application.
# -----------------------------------------------------------------------------

import logging
from contextlib import suppress
from dataclasses import replace
from logging import Handler, Logger
from logging.handlers import MemoryHandler, RotatingFileHandler
from pathlib import Path

from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.handlers import (
    create_bounded_memory_handler,
    create_console_handler,
    create_rotating_file_handler,
    flush_memory_handler_to_target,
    remove_and_close_handler_safely,
)
from desktop_app.infrastructure.logger.validators import (
    normalize_file_path,
    normalize_logger_config,
    normalize_rotate_max_bytes,
    validate_logger_reconfiguration,
)


class LoggerBootstrapper:
    """Manage logger initialization, updates, and shutdown.

    Args:
        config: Initial logger configuration. When omitted, LoggerConfig
            defaults are used.
    """

    def __init__(self, config: LoggerConfig | None = None) -> None:
        """Initialize the bootstrapper with validated configuration.

        Args:
            config: Initial logger configuration. When omitted, LoggerConfig
                defaults are used.
        """
        self._config = normalize_logger_config(config or LoggerConfig())
        self._root_logger = logging.getLogger(self._config.name)

        self._console_handler: Handler | None = None
        self._memory_handler: MemoryHandler | None = None
        self._file_handler: RotatingFileHandler | None = None

        self._is_bootstrapped = False
        self._is_shutdown = False

        self._configure_root_logger()

    @property
    def config(self) -> LoggerConfig:
        """Return the currently applied normalized configuration."""
        return self._config

    @property
    def is_bootstrapped(self) -> bool:
        """Return whether the logger has completed the initial bootstrap."""
        return self._is_bootstrapped

    @property
    def is_shutdown(self) -> bool:
        """Return whether the logger was explicitly shut down."""
        return self._is_shutdown

    @property
    def root_logger(self) -> Logger:
        """Return the root logger controlled by this bootstrapper."""
        return self._root_logger

    @property
    def _current_level(self) -> int:
        """Return the normalized current log level."""
        return int(self._config.level)

    @property
    def _current_file_path(self) -> Path:
        """Return the normalized current log file path."""
        return Path(self._config.file_path)

    @property
    def _current_rotate_max_bytes(self) -> int:
        """Return the normalized current maximum rotation size."""
        return normalize_rotate_max_bytes(self._config.rotate_max_bytes)

    def bootstrap(self) -> Logger:
        """Configure the root logger, memory buffer, and optional console output.

        Returns:
            Configured root logger.
        """
        if self._is_bootstrapped:
            return self._root_logger

        self._configure_root_logger()
        self._configure_memory_handler()
        self._configure_console_handler()

        self._is_bootstrapped = True
        self._is_shutdown = False

        self._root_logger.debug("Logger bootstrap completed.")
        return self._root_logger

    def update_config(self, config: LoggerConfig) -> None:
        """Update applicable configuration without recreating the whole logger.

        Args:
            config: Requested new logger configuration.
        """
        normalized_config = normalize_logger_config(config)
        validate_logger_reconfiguration(self._config, normalized_config)

        previous_file_path = self._current_file_path
        previous_rotate_max_bytes = self._current_rotate_max_bytes
        previous_rotate_backup_count = self._config.rotate_backup_count
        file_logging_is_active = self._file_handler is not None

        self._config = normalized_config
        self._apply_current_level()
        self._synchronize_console_handler()

        file_handler_must_be_recreated = (
            previous_file_path != self._current_file_path
            or previous_rotate_max_bytes != self._current_rotate_max_bytes
            or previous_rotate_backup_count != self._config.rotate_backup_count
        )

        if file_logging_is_active and file_handler_must_be_recreated:
            self._recreate_active_file_handler()

    def enable_file_logging(self, file_path: Path | str | None = None) -> bool:
        """Enable file logging and transfer preserved memory records.

        Args:
            file_path: Optional path to override the configured log file path.

        Returns:
            True when file logging was enabled; False when activation failed.
        """
        if not self._is_bootstrapped:
            self.bootstrap()

        target_path = self._resolve_target_file_path(file_path)
        new_handler: RotatingFileHandler | None = None

        try:
            new_handler = create_rotating_file_handler(
                file_path=target_path,
                level=self._current_level,
                max_bytes=self._current_rotate_max_bytes,
                backup_count=self._config.rotate_backup_count,
            )

            remove_and_close_handler_safely(self._root_logger, self._file_handler)
            self._file_handler = new_handler
            self._root_logger.addHandler(self._file_handler)

            flush_memory_handler_to_target(
                self._memory_handler,
                self._file_handler,
            )

            remove_and_close_handler_safely(self._root_logger, self._memory_handler)
            self._memory_handler = None

            self._root_logger.debug("Main file logging enabled.")
            return True

        except Exception:
            if new_handler is not None:
                remove_and_close_handler_safely(self._root_logger, new_handler)
                if self._file_handler is new_handler:
                    self._file_handler = None

            self._root_logger.exception("File logging could not be enabled.")
            return False

    def shutdown(self) -> None:
        """Remove and close all handlers controlled by this bootstrapper."""
        if self._is_shutdown:
            return

        with suppress(Exception):
            self._root_logger.debug("Logger shutdown started.")
            self._root_logger.debug("Logger shutdown completed.")

        remove_and_close_handler_safely(self._root_logger, self._memory_handler)
        remove_and_close_handler_safely(self._root_logger, self._console_handler)
        remove_and_close_handler_safely(self._root_logger, self._file_handler)

        self._memory_handler = None
        self._console_handler = None
        self._file_handler = None

        self._is_shutdown = True
        self._is_bootstrapped = False

    def _configure_root_logger(self) -> None:
        """Apply level and propagation behavior to the root logger."""
        self._root_logger.setLevel(self._current_level)
        self._root_logger.propagate = False

    def _configure_memory_handler(self) -> None:
        """Attach the temporary memory handler when needed."""
        if self._memory_handler is not None:
            return

        self._memory_handler = create_bounded_memory_handler(
            capacity=self._config.buffer_capacity,
            level=self._current_level,
        )
        self._root_logger.addHandler(self._memory_handler)

    def _configure_console_handler(self) -> None:
        """Attach the console handler when configuration allows it."""
        if not self._config.enable_console or self._console_handler is not None:
            return

        self._console_handler = create_console_handler(self._current_level)
        self._root_logger.addHandler(self._console_handler)

    def _synchronize_console_handler(self) -> None:
        """Keep the console handler aligned with the current configuration."""
        if self._config.enable_console:
            if self._console_handler is None and self._is_bootstrapped:
                self._configure_console_handler()
            return

        if self._console_handler is not None:
            remove_and_close_handler_safely(self._root_logger, self._console_handler)
            self._console_handler = None

    def _apply_current_level(self) -> None:
        """Apply the current level to the root logger and active handlers."""
        self._root_logger.setLevel(self._current_level)

        for handler in (
            self._memory_handler,
            self._console_handler,
            self._file_handler,
        ):
            if handler is not None:
                handler.setLevel(self._current_level)

    def _recreate_active_file_handler(self) -> None:
        """Recreate the active file handler after file-related config changes."""
        if not self.enable_file_logging():
            self._root_logger.error("Active file logging reconfiguration failed.")

    def _resolve_target_file_path(self, file_path: Path | str | None) -> Path:
        """Resolve the final log file path.

        Args:
            file_path: Optional path received during file logging activation.

        Returns:
            Normalized path used by the file handler.
        """
        if file_path is None:
            return self._current_file_path

        normalized_path = normalize_file_path(file_path)
        self._config = replace(self._config, file_path=normalized_path)

        return normalized_path
