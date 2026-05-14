"""Test logger handler factories and cleanup helpers."""

from __future__ import annotations

import logging
from logging import Handler, LogRecord
from pathlib import Path

import pytest

from desktop_app.infrastructure.logger.defaults import (
    CONSOLE_LOG_FORMAT,
    FILE_LOG_FORMAT,
)
from desktop_app.infrastructure.logger.handlers import (
    BoundedMemoryHandler,
    close_handler_safely,
    create_bounded_memory_handler,
    create_console_handler,
    create_rotating_file_handler,
    flush_memory_handler_to_target,
    remove_and_close_handler_safely,
    remove_handler_safely,
)


# Test helpers and doubles make handler behavior observable.
def make_log_record(message: str, level: int = logging.INFO) -> LogRecord:
    """Create a log record for handler tests.

    Args:
        message: Message stored in the log record.
        level: Numeric logging level.

    Returns:
        A configured log record.
    """
    return logging.LogRecord(
        name="desktop_app.tests",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )


class CollectingHandler(Handler):
    """Collect handled records and count cleanup calls."""

    def __init__(self, *, fail_on_flush: bool = False) -> None:
        """Initialize the collecting handler.

        Args:
            fail_on_flush: Whether flush should raise an error.
        """
        super().__init__()
        self.records: list[LogRecord] = []
        self.flush_count = 0
        self.close_count = 0
        self.fail_on_flush = fail_on_flush

    def emit(self, record: LogRecord) -> None:
        """Store the received log record.

        Args:
            record: Log record received by the handler.
        """
        self.records.append(record)

    def flush(self) -> None:
        """Count flush calls and optionally simulate a flush failure."""
        self.flush_count += 1
        if self.fail_on_flush:
            raise RuntimeError("flush failed")

    def close(self) -> None:
        """Count close calls and delegate base handler cleanup."""
        self.close_count += 1
        super().close()


class FailingCleanupHandler(Handler):
    """Handler that fails during cleanup to validate defensive helpers."""

    def __init__(self) -> None:
        """Initialize cleanup counters."""
        super().__init__()
        self.flush_count = 0
        self.close_count = 0

    def emit(self, record: LogRecord) -> None:
        """Fail if a test unexpectedly emits through this handler.

        Args:
            record: Unused log record.
        """
        raise RuntimeError("emit should not be called")

    def flush(self) -> None:
        """Count flush calls and raise an error."""
        self.flush_count += 1
        raise RuntimeError("flush failed")

    def close(self) -> None:
        """Count close calls and raise an error."""
        self.close_count += 1
        raise RuntimeError("close failed")


@pytest.fixture
def isolated_logger() -> logging.Logger:
    """Return a logger without handlers for cleanup tests.

    Returns:
        Logger instance with handlers cleared.
    """
    logger = logging.getLogger("desktop_app.tests.handlers")
    logger.handlers.clear()
    logger.propagate = False
    return logger


# Handler factory, buffering, flushing, and cleanup tests.
def test_bounded_memory_handler_keeps_only_recent_records() -> None:
    """Verify that bounded memory handler keeps only recent records."""
    handler = BoundedMemoryHandler(
        capacity=2,
        flushLevel=logging.CRITICAL + 1,
        target=None,
    )

    handler.emit(make_log_record("first"))
    handler.emit(make_log_record("second"))
    handler.emit(make_log_record("third"))

    assert [record.getMessage() for record in handler.buffer] == ["second", "third"]


def test_create_console_handler_configures_level_and_formatter() -> None:
    """Verify that create console handler configures level and formatter."""
    handler = create_console_handler(logging.WARNING)

    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.WARNING
    assert handler.formatter is not None
    assert handler.formatter._style._fmt == CONSOLE_LOG_FORMAT


def test_create_bounded_memory_handler_configures_capacity_target_and_level() -> None:
    """Verify that create bounded memory handler configures capacity target and
    level.
    """
    handler = create_bounded_memory_handler(capacity=3, level=logging.DEBUG)

    assert isinstance(handler, BoundedMemoryHandler)
    assert handler.capacity == 3
    assert handler.level == logging.DEBUG
    assert handler.flushLevel == logging.CRITICAL + 1
    assert handler.target is None


def test_create_rotating_file_handler_configures_file_output(tmp_path: Path) -> None:
    """Verify that create rotating file handler configures file output."""
    file_path = tmp_path / "logs" / "app.log"
    handler = create_rotating_file_handler(
        file_path=file_path,
        level=logging.ERROR,
        max_bytes=1_024,
        backup_count=2,
    )

    try:
        assert handler.level == logging.ERROR
        assert handler.maxBytes == 1_024
        assert handler.backupCount == 2
        assert handler.baseFilename == str(file_path)
        assert handler.formatter is not None
        assert handler.formatter._style._fmt == FILE_LOG_FORMAT
        assert file_path.parent.exists()

        handler.handle(make_log_record("file message", logging.ERROR))
        handler.flush()

        assert "file message" in file_path.read_text(encoding="utf-8")
    finally:
        handler.close()


def test_flush_memory_handler_to_target_returns_when_memory_handler_is_none() -> None:
    """Verify that flush memory handler to target returns when memory handler is
    none.
    """
    target_handler = CollectingHandler()

    flush_memory_handler_to_target(None, target_handler)

    assert target_handler.records == []
    assert target_handler.flush_count == 0


def test_flush_memory_handler_to_target_moves_records_and_clears_buffer() -> None:
    """Verify that flush memory handler to target moves records and clears buffer."""
    memory_handler = create_bounded_memory_handler(capacity=5, level=logging.DEBUG)
    first_record = make_log_record("first", logging.DEBUG)
    second_record = make_log_record("second", logging.INFO)
    memory_handler.emit(first_record)
    memory_handler.emit(second_record)
    target_handler = CollectingHandler()

    flush_memory_handler_to_target(memory_handler, target_handler)

    assert target_handler.records == [first_record, second_record]
    assert target_handler.flush_count == 1
    assert memory_handler.buffer == []


def test_flush_memory_handler_to_target_suppresses_target_flush_errors() -> None:
    """Verify that flush memory handler to target suppresses target flush errors."""
    memory_handler = create_bounded_memory_handler(capacity=5, level=logging.INFO)
    record = make_log_record("preserved")
    memory_handler.emit(record)
    target_handler = CollectingHandler(fail_on_flush=True)

    flush_memory_handler_to_target(memory_handler, target_handler)

    assert target_handler.records == [record]
    assert target_handler.flush_count == 1
    assert memory_handler.buffer == []


def test_remove_handler_safely_returns_when_handler_is_none(
    isolated_logger: logging.Logger,
) -> None:
    """Verify that remove handler safely returns when handler is none."""
    remove_handler_safely(isolated_logger, None)

    assert isolated_logger.handlers == []


def test_remove_handler_safely_removes_existing_handler(
    isolated_logger: logging.Logger,
) -> None:
    """Verify that remove handler safely removes existing handler."""
    handler = CollectingHandler()
    isolated_logger.addHandler(handler)

    remove_handler_safely(isolated_logger, handler)

    assert handler not in isolated_logger.handlers


def test_remove_handler_safely_suppresses_logger_errors(
    isolated_logger: logging.Logger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that remove handler safely suppresses logger errors."""
    handler = CollectingHandler()

    def raise_remove_error(_handler: Handler) -> None:
        """Simulate a logger failure while removing a handler."""
        raise RuntimeError("remove failed")

    monkeypatch.setattr(isolated_logger, "removeHandler", raise_remove_error)

    remove_handler_safely(isolated_logger, handler)


def test_close_handler_safely_returns_when_handler_is_none() -> None:
    """Verify that close handler safely returns when handler is none."""
    close_handler_safely(None)


def test_close_handler_safely_flushes_and_closes_handler() -> None:
    """Verify that close handler safely flushes and closes handler."""
    handler = CollectingHandler()

    close_handler_safely(handler)

    assert handler.flush_count == 1
    assert handler.close_count == 1


def test_close_handler_safely_suppresses_flush_and_close_errors() -> None:
    """Verify that close handler safely suppresses flush and close errors."""
    handler = FailingCleanupHandler()

    close_handler_safely(handler)

    assert handler.flush_count == 1
    assert handler.close_count == 1


def test_remove_and_close_handler_safely_removes_and_closes_handler(
    isolated_logger: logging.Logger,
) -> None:
    """Verify that remove and close handler safely removes and closes handler."""
    handler = CollectingHandler()
    isolated_logger.addHandler(handler)

    remove_and_close_handler_safely(isolated_logger, handler)

    assert handler not in isolated_logger.handlers
    assert handler.flush_count == 1
    assert handler.close_count == 1
