"""Test logger bootstrapper lifecycle, reconfiguration, and failure paths."""

import logging
from logging import Handler, Logger
from logging.handlers import MemoryHandler, RotatingFileHandler
from pathlib import Path
from uuid import uuid4

import pytest

from desktop_app.infrastructure.logger import bootstrapper as bootstrapper_module
from desktop_app.infrastructure.logger.bootstrapper import LoggerBootstrapper
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError


# Helper functions keep logger setup isolated per test.
def _build_logger_name() -> str:
    """Return a unique logger name for isolated tests."""
    return f"test.logger.{uuid4()}"


def _build_test_logger_config(
    log_file_path: Path,
    *,
    enable_console: bool = False,
    level: int | str = "INFO",
    name: str | None = None,
    rotate_max_bytes: int | str = "1 MB",
    rotate_backup_count: int = 1,
    buffer_capacity: int = 10,
) -> LoggerConfig:
    """Build a logger configuration with test-safe defaults."""
    return LoggerConfig(
        name=name or _build_logger_name(),
        level=level,
        enable_console=enable_console,
        buffer_capacity=buffer_capacity,
        file_path=log_file_path,
        rotate_max_bytes=rotate_max_bytes,
        rotate_backup_count=rotate_backup_count,
    )


def _get_handlers_by_type(
    logger: Logger,
    handler_type: type[Handler],
) -> list[Handler]:
    """Return all logger handlers that match the requested type."""
    return [handler for handler in logger.handlers if isinstance(handler, handler_type)]


def _has_handler(logger: Logger, handler_type: type[Handler]) -> bool:
    """Return whether the logger has a handler of the requested type."""
    return bool(_get_handlers_by_type(logger, handler_type))


# Initialization and bootstrap tests.
def test_initializes_with_normalized_config(tmp_path: Path) -> None:
    """Verify that the bootstrapper initializes with normalized config."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        level="debug",
        enable_console=False,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.config.level == logging.DEBUG
        assert bootstrapper.config.file_path == tmp_path / "app.log"
        assert bootstrapper.root_logger.name == config.name
        assert bootstrapper.root_logger.level == logging.DEBUG
        assert bootstrapper.root_logger.propagate is False
        assert bootstrapper.is_bootstrapped is False
        assert bootstrapper.is_shutdown is False
    finally:
        bootstrapper.shutdown()


def test_initializes_with_default_config() -> None:
    """Verify that the bootstrapper initializes with default config."""
    bootstrapper = LoggerBootstrapper()

    try:
        assert isinstance(bootstrapper.config, LoggerConfig)
        assert isinstance(bootstrapper.root_logger, Logger)
        assert bootstrapper.is_bootstrapped is False
        assert bootstrapper.is_shutdown is False
    finally:
        bootstrapper.shutdown()


def test_configure_memory_handler_is_idempotent(tmp_path: Path) -> None:
    """Verify that configure memory handler is idempotent."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)

    try:
        bootstrapper.bootstrap()
        first_handlers = list(bootstrapper.root_logger.handlers)

        bootstrapper._configure_memory_handler()

        assert bootstrapper.root_logger.handlers == first_handlers
    finally:
        bootstrapper.shutdown()


def test_bootstrap_adds_memory_handler_and_console_handler_when_enabled(
    tmp_path: Path,
) -> None:
    """Verify that bootstrap adds memory handler and console handler when enabled."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        logger = bootstrapper.bootstrap()

        assert logger is bootstrapper.root_logger
        assert bootstrapper.is_bootstrapped is True
        assert bootstrapper.is_shutdown is False
        assert _has_handler(logger, MemoryHandler)
        assert _has_handler(logger, logging.StreamHandler)
    finally:
        bootstrapper.shutdown()


def test_bootstrap_does_not_add_console_handler_when_disabled(
    tmp_path: Path,
) -> None:
    """Verify that bootstrap does not add console handler when disabled."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=False,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        logger = bootstrapper.bootstrap()

        assert _has_handler(logger, MemoryHandler)
        assert not _has_handler(logger, logging.StreamHandler)
    finally:
        bootstrapper.shutdown()


def test_bootstrap_is_idempotent(tmp_path: Path) -> None:
    """Verify that bootstrap is idempotent."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        first_logger = bootstrapper.bootstrap()
        first_handlers = list(first_logger.handlers)

        second_logger = bootstrapper.bootstrap()

        assert second_logger is first_logger
        assert second_logger.handlers == first_handlers
    finally:
        bootstrapper.shutdown()


# Configuration update tests.
def test_update_config_applies_level_to_logger_and_active_handlers(
    tmp_path: Path,
) -> None:
    """Verify that updating config applies level to logger and active handlers."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
        level="INFO",
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        bootstrapper.bootstrap()
        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "app.log",
                enable_console=True,
                level="DEBUG",
                name=config.name,
            )
        )

        assert bootstrapper.config.level == logging.DEBUG
        assert bootstrapper.root_logger.level == logging.DEBUG
        assert all(
            handler.level == logging.DEBUG
            for handler in bootstrapper.root_logger.handlers
        )
    finally:
        bootstrapper.shutdown()


def test_update_config_adds_console_handler_after_bootstrap(
    tmp_path: Path,
) -> None:
    """Verify that updating config adds console handler after bootstrap."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=False,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        bootstrapper.bootstrap()
        assert not _has_handler(bootstrapper.root_logger, logging.StreamHandler)

        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "app.log",
                enable_console=True,
                name=config.name,
            )
        )

        assert _has_handler(bootstrapper.root_logger, logging.StreamHandler)
    finally:
        bootstrapper.shutdown()


def test_update_config_does_not_add_console_before_bootstrap(
    tmp_path: Path,
) -> None:
    """Verify that updating config does not add console before bootstrap."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=False,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "app.log",
                enable_console=True,
                name=config.name,
            )
        )

        assert not _has_handler(bootstrapper.root_logger, logging.StreamHandler)
        assert bootstrapper.is_bootstrapped is False
    finally:
        bootstrapper.shutdown()


def test_update_config_removes_console_handler_when_disabled(
    tmp_path: Path,
) -> None:
    """Verify that updating config removes console handler when disabled."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        bootstrapper.bootstrap()
        assert _has_handler(bootstrapper.root_logger, logging.StreamHandler)

        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "app.log",
                enable_console=False,
                name=config.name,
            )
        )

        assert not _has_handler(bootstrapper.root_logger, logging.StreamHandler)
    finally:
        bootstrapper.shutdown()


def test_update_config_rejects_logger_name_change(tmp_path: Path) -> None:
    """Verify that updating config rejects logger name change."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)

    try:
        with pytest.raises(LoggerValidationError, match="Root logger name"):
            bootstrapper.update_config(
                _build_test_logger_config(
                    tmp_path / "app.log",
                    name=_build_logger_name(),
                )
            )
    finally:
        bootstrapper.shutdown()


def test_update_config_recreates_active_file_handler_when_file_path_changes(
    tmp_path: Path,
) -> None:
    """Verify that updating config recreates active file handler when file path
    changes.
    """
    first_log_file_path = tmp_path / "first.log"
    second_log_file_path = tmp_path / "second.log"
    config = _build_test_logger_config(first_log_file_path)
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.enable_file_logging() is True
        first_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        bootstrapper.update_config(
            _build_test_logger_config(
                second_log_file_path,
                name=config.name,
            )
        )
        second_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        assert second_file_handler is not first_file_handler
        assert Path(second_file_handler.baseFilename) == second_log_file_path
    finally:
        bootstrapper.shutdown()


def test_update_config_recreates_active_file_handler_when_rotation_changes(
    tmp_path: Path,
) -> None:
    """Verify that updating config recreates active file handler when rotation
    changes.
    """
    config = _build_test_logger_config(
        tmp_path / "app.log",
        rotate_max_bytes="1 MB",
        rotate_backup_count=1,
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.enable_file_logging() is True
        first_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "app.log",
                name=config.name,
                rotate_max_bytes="2 MB",
                rotate_backup_count=2,
            )
        )
        second_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        assert second_file_handler is not first_file_handler
        assert second_file_handler.maxBytes == 2 * 1024 * 1024
        assert second_file_handler.backupCount == 2
    finally:
        bootstrapper.shutdown()


def test_update_config_keeps_new_config_when_file_recreation_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that updating config keeps new config when file recreation fails."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.enable_file_logging() is True

        monkeypatch.setattr(
            bootstrapper,
            "enable_file_logging",
            lambda: False,
        )

        bootstrapper.update_config(
            _build_test_logger_config(
                tmp_path / "changed.log",
                name=config.name,
            )
        )

        assert bootstrapper.config.file_path == tmp_path / "changed.log"
    finally:
        bootstrapper.shutdown()


# File logging activation and failure path tests.
def test_enable_file_logging_bootstraps_logger_when_needed(
    tmp_path: Path,
) -> None:
    """Verify that file logging bootstraps logger when needed."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)

    try:
        result = bootstrapper.enable_file_logging()

        assert result is True
        assert bootstrapper.is_bootstrapped is True
        assert _has_handler(bootstrapper.root_logger, RotatingFileHandler)
        assert not _has_handler(bootstrapper.root_logger, MemoryHandler)
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_uses_explicit_file_path(tmp_path: Path) -> None:
    """Verify that file logging uses explicit file path."""
    configured_path = tmp_path / "configured.log"
    explicit_path = tmp_path / "explicit.log"
    config = _build_test_logger_config(configured_path)
    bootstrapper = LoggerBootstrapper(config)

    try:
        result = bootstrapper.enable_file_logging(explicit_path)
        file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        assert result is True
        assert bootstrapper.config.file_path == explicit_path
        assert Path(file_handler.baseFilename) == explicit_path
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_replaces_existing_file_handler(
    tmp_path: Path,
) -> None:
    """Verify that file logging replaces existing file handler."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.enable_file_logging() is True
        first_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        assert bootstrapper.enable_file_logging(tmp_path / "new.log") is True
        second_file_handler = next(
            handler
            for handler in bootstrapper.root_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        assert second_file_handler is not first_file_handler
        assert first_file_handler not in bootstrapper.root_logger.handlers
        assert Path(second_file_handler.baseFilename) == tmp_path / "new.log"
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_returns_false_when_handler_creation_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that file logging returns false when handler creation fails."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)
    bootstrapper.bootstrap()

    def fail_create_rotating_file_handler(
        file_path: Path,
        level: int,
        max_bytes: int,
        backup_count: int,
    ) -> RotatingFileHandler:
        """Simulate a rotating file handler creation failure."""
        raise OSError("Forced file handler creation failure.")

    monkeypatch.setattr(
        bootstrapper_module,
        "create_rotating_file_handler",
        fail_create_rotating_file_handler,
    )

    try:
        result = bootstrapper.enable_file_logging()

        assert result is False
        assert not _has_handler(bootstrapper.root_logger, RotatingFileHandler)
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_returns_false_when_handler_setup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that file logging returns false when handler setup fails."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)
    bootstrapper.bootstrap()

    original_remove_and_close_handler_safely = (
        bootstrapper_module.remove_and_close_handler_safely
    )

    def fail_when_removing_previous_file_handler(
        logger: Logger,
        handler: Handler | None,
    ) -> None:
        """Simulate a failure before the new file handler is assigned."""
        if handler is None:
            raise RuntimeError("Forced failure before file handler assignment.")

        original_remove_and_close_handler_safely(logger, handler)

    try:
        with monkeypatch.context() as patch_context:
            patch_context.setattr(
                bootstrapper_module,
                "remove_and_close_handler_safely",
                fail_when_removing_previous_file_handler,
            )

            result = bootstrapper.enable_file_logging()

        assert result is False
        assert not _has_handler(bootstrapper.root_logger, RotatingFileHandler)
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_returns_false_and_clears_handler_when_flush_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that file logging returns false and clears handler when flush fails."""
    config = _build_test_logger_config(tmp_path / "app.log")
    bootstrapper = LoggerBootstrapper(config)
    bootstrapper.bootstrap()

    def fail_memory_flush(
        memory_handler: MemoryHandler | None,
        target_handler: Handler,
    ) -> None:
        """Simulate a failure while flushing buffered records."""
        raise RuntimeError("Forced memory flush failure.")

    monkeypatch.setattr(
        bootstrapper_module,
        "flush_memory_handler_to_target",
        fail_memory_flush,
    )

    try:
        result = bootstrapper.enable_file_logging()

        assert result is False
        assert not _has_handler(bootstrapper.root_logger, RotatingFileHandler)
    finally:
        bootstrapper.shutdown()


# Shutdown lifecycle tests.
def test_shutdown_is_idempotent(tmp_path: Path) -> None:
    """Verify that shutdown is idempotent."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
    )
    bootstrapper = LoggerBootstrapper(config)

    bootstrapper.bootstrap()
    bootstrapper.shutdown()
    bootstrapper.shutdown()

    assert bootstrapper.is_shutdown is True
    assert bootstrapper.is_bootstrapped is False
    assert bootstrapper.root_logger.handlers == []


def test_shutdown_removes_all_handlers_after_file_logging_enabled(
    tmp_path: Path,
) -> None:
    """Verify that shutdown removes all handlers after file logging enabled."""
    config = _build_test_logger_config(
        tmp_path / "app.log",
        enable_console=True,
    )
    bootstrapper = LoggerBootstrapper(config)

    bootstrapper.bootstrap()
    assert bootstrapper.enable_file_logging() is True
    assert bootstrapper.root_logger.handlers

    bootstrapper.shutdown()

    assert bootstrapper.root_logger.handlers == []
    assert bootstrapper.is_shutdown is True
    assert bootstrapper.is_bootstrapped is False
