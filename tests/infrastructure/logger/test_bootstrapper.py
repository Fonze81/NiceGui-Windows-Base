# -----------------------------------------------------------------------------
# File: tests/infrastructure/logger/test_bootstrapper.py
# Purpose:
# Validate the logger bootstrapper lifecycle and configuration behavior.
# Behavior:
# Exercises bootstrap, console synchronization, file logging activation, handler
# recreation, cleanup, and recoverable file logging failures.
# Notes:
# Tests use unique logger names to avoid handler leakage between test cases.
# -----------------------------------------------------------------------------

import logging
from collections.abc import Iterator
from logging import Handler
from pathlib import Path
from uuid import uuid4

import pytest

from desktop_app.infrastructure.logger.bootstrapper import LoggerBootstrapper
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError

_ROTATE_MAX_BYTES = 1_048_576


def _unique_logger_name() -> str:
    return f"desktop_app.tests.bootstrapper.{uuid4().hex}"


def _cleanup_logger(logger_name: str) -> None:
    logger = logging.getLogger(logger_name)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.propagate = True
    logger.setLevel(logging.NOTSET)


def _make_config(
    tmp_path: Path,
    *,
    logger_name: str | None = None,
    level: int | str = "INFO",
    enable_console: bool = True,
    file_name: str = "app.log",
    buffer_capacity: int = 5,
    rotate_max_bytes: int | str = _ROTATE_MAX_BYTES,
    rotate_backup_count: int = 1,
) -> LoggerConfig:
    return LoggerConfig(
        name=logger_name or _unique_logger_name(),
        level=level,
        enable_console=enable_console,
        buffer_capacity=buffer_capacity,
        file_path=tmp_path / file_name,
        rotate_max_bytes=rotate_max_bytes,
        rotate_backup_count=rotate_backup_count,
    )


@pytest.fixture
def logger_name() -> Iterator[str]:
    name = _unique_logger_name()
    yield name
    _cleanup_logger(name)


def test_init_uses_default_config_and_exposes_properties() -> None:
    bootstrapper = LoggerBootstrapper()

    try:
        assert bootstrapper.config.name == "desktop_app"
        assert bootstrapper.root_logger.name == "desktop_app"
        assert bootstrapper.root_logger.propagate is False
        assert bootstrapper.is_bootstrapped is False
        assert bootstrapper.is_shutdown is False
        assert bootstrapper._current_level == logging.INFO
        assert bootstrapper._current_file_path == Path("logs") / "app.log"
        assert bootstrapper._current_rotate_max_bytes == 5 * 1024 * 1024
    finally:
        bootstrapper.shutdown()
        _cleanup_logger("desktop_app")


def test_bootstrap_adds_memory_and_console_handlers(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, level="DEBUG")
    )

    try:
        logger = bootstrapper.bootstrap()
        same_logger = bootstrapper.bootstrap()

        assert same_logger is logger
        assert bootstrapper.is_bootstrapped is True
        assert bootstrapper.is_shutdown is False
        assert bootstrapper._memory_handler in logger.handlers
        assert bootstrapper._console_handler in logger.handlers
        assert bootstrapper._memory_handler is not None
        assert bootstrapper._memory_handler.level == logging.DEBUG
        assert bootstrapper._console_handler is not None
        assert bootstrapper._console_handler.level == logging.DEBUG

        bootstrapper._configure_memory_handler()
        bootstrapper._configure_console_handler()

        assert logger.handlers.count(bootstrapper._memory_handler) == 1
        assert logger.handlers.count(bootstrapper._console_handler) == 1
    finally:
        bootstrapper.shutdown()

    assert bootstrapper.is_bootstrapped is False
    assert bootstrapper.is_shutdown is True
    assert bootstrapper._memory_handler is None
    assert bootstrapper._console_handler is None
    assert bootstrapper._file_handler is None

    bootstrapper.shutdown()
    assert bootstrapper.is_shutdown is True


def test_bootstrap_skips_console_when_disabled(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, enable_console=False)
    )

    try:
        bootstrapper.bootstrap()
        bootstrapper._configure_console_handler()

        assert bootstrapper._memory_handler is not None
        assert bootstrapper._console_handler is None
    finally:
        bootstrapper.shutdown()


def test_update_config_synchronizes_level_and_console_handler(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, level="INFO")
    )
    bootstrapper.bootstrap()

    try:
        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                level="DEBUG",
                enable_console=False,
            )
        )

        assert bootstrapper.root_logger.level == logging.DEBUG
        assert bootstrapper._memory_handler is not None
        assert bootstrapper._memory_handler.level == logging.DEBUG
        assert bootstrapper._console_handler is None

        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                level="WARNING",
                enable_console=False,
            )
        )

        assert bootstrapper.root_logger.level == logging.WARNING
        assert bootstrapper._console_handler is None

        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                level="ERROR",
                enable_console=True,
            )
        )

        assert bootstrapper._console_handler is not None
        assert bootstrapper._console_handler.level == logging.ERROR

        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                level="CRITICAL",
                enable_console=True,
            )
        )

        assert bootstrapper._console_handler is not None
        assert bootstrapper._console_handler.level == logging.CRITICAL
    finally:
        bootstrapper.shutdown()


def test_update_config_rejects_logger_name_change(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(_make_config(tmp_path, logger_name=logger_name))

    try:
        with pytest.raises(LoggerValidationError, match="Root logger name cannot"):
            bootstrapper.update_config(
                _make_config(tmp_path, logger_name=_unique_logger_name())
            )
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_flushes_memory_records(
    tmp_path: Path,
    logger_name: str,
) -> None:
    log_file_path = tmp_path / "runtime.log"
    bootstrapper = LoggerBootstrapper(
        _make_config(
            tmp_path,
            logger_name=logger_name,
            level="INFO",
            enable_console=False,
        )
    )

    try:
        bootstrapper.bootstrap()
        bootstrapper.root_logger.info("record before file logging")

        assert bootstrapper.enable_file_logging(log_file_path) is True

        bootstrapper.root_logger.info("record after file logging")
        assert bootstrapper.is_bootstrapped is True
        assert bootstrapper._memory_handler is None
        assert bootstrapper._file_handler is not None
        assert bootstrapper.config.file_path == log_file_path
    finally:
        bootstrapper.shutdown()

    log_content = log_file_path.read_text(encoding="utf-8")
    assert "record before file logging" in log_content
    assert "record after file logging" in log_content


def test_enable_file_logging_uses_configured_file_path_when_no_override(
    tmp_path: Path,
    logger_name: str,
) -> None:
    config = _make_config(
        tmp_path,
        logger_name=logger_name,
        enable_console=False,
        file_name="configured.log",
    )
    bootstrapper = LoggerBootstrapper(config)

    try:
        assert bootstrapper.enable_file_logging() is True
        assert bootstrapper._file_handler is not None
        assert Path(bootstrapper._file_handler.baseFilename) == config.file_path
    finally:
        bootstrapper.shutdown()

    assert Path(config.file_path).exists()


def test_update_config_keeps_active_file_handler_when_file_settings_do_not_change(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, enable_console=False)
    )

    try:
        assert bootstrapper.enable_file_logging() is True
        original_file_handler = bootstrapper._file_handler

        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                level="ERROR",
                enable_console=True,
            )
        )

        assert bootstrapper._file_handler is original_file_handler
        assert bootstrapper._file_handler is not None
        assert bootstrapper._file_handler.level == logging.ERROR
        assert bootstrapper._console_handler is not None
        assert bootstrapper._console_handler.level == logging.ERROR
    finally:
        bootstrapper.shutdown()


def test_update_config_recreates_active_file_handler_when_file_settings_change(
    tmp_path: Path,
    logger_name: str,
) -> None:
    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, enable_console=False)
    )

    try:
        assert bootstrapper.enable_file_logging() is True
        original_file_handler = bootstrapper._file_handler

        bootstrapper.update_config(
            _make_config(
                tmp_path,
                logger_name=logger_name,
                enable_console=False,
                file_name="new.log",
                rotate_backup_count=2,
            )
        )

        assert bootstrapper._file_handler is not None
        assert bootstrapper._file_handler is not original_file_handler
        assert Path(bootstrapper._file_handler.baseFilename) == tmp_path / "new.log"
        assert bootstrapper._file_handler.backupCount == 2
    finally:
        bootstrapper.shutdown()


def test_enable_file_logging_returns_false_and_cleans_new_handler_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    logger_name: str,
) -> None:
    import desktop_app.infrastructure.logger.bootstrapper as bootstrapper_module

    def raise_during_memory_flush(*_: object) -> None:
        raise OSError("flush failed")

    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, enable_console=False)
    )
    bootstrapper.bootstrap()

    monkeypatch.setattr(
        bootstrapper_module,
        "flush_memory_handler_to_target",
        raise_during_memory_flush,
    )

    try:
        assert bootstrapper.enable_file_logging(tmp_path / "broken.log") is False
        assert bootstrapper._file_handler is None
        assert bootstrapper._memory_handler is not None
        assert not any(
            getattr(handler, "baseFilename", None) == str(tmp_path / "broken.log")
            for handler in bootstrapper.root_logger.handlers
        )
    finally:
        bootstrapper.shutdown()


def test_recreate_active_file_handler_logs_error_when_reactivation_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    logger_name: str,
) -> None:
    class CapturingHandler(Handler):
        def __init__(self) -> None:
            super().__init__()
            self.messages: list[str] = []

        def emit(self, record: logging.LogRecord) -> None:
            self.messages.append(record.getMessage())

    bootstrapper = LoggerBootstrapper(
        _make_config(tmp_path, logger_name=logger_name, enable_console=False)
    )
    capturing_handler = CapturingHandler()
    bootstrapper.root_logger.addHandler(capturing_handler)

    monkeypatch.setattr(bootstrapper, "enable_file_logging", lambda: False)

    try:
        bootstrapper._recreate_active_file_handler()

        assert (
            "Active file logging reconfiguration failed." in capturing_handler.messages
        )
    finally:
        bootstrapper.root_logger.removeHandler(capturing_handler)
        bootstrapper.shutdown()
