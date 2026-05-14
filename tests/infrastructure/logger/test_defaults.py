"""Test logger package default constants."""

from pathlib import Path

from desktop_app.infrastructure.logger import defaults

EXPECTED_DEFAULTS_PUBLIC_API: tuple[str, ...] = (
    "DEFAULT_LOGGER_NAME",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_FILE_PATH",
    "DEFAULT_BUFFER_CAPACITY",
    "DEFAULT_ROTATE_MAX_BYTES",
    "DEFAULT_ROTATE_BACKUP_COUNT",
    "MIN_BUFFER_CAPACITY",
    "MAX_BUFFER_CAPACITY",
    "MIN_ROTATE_MAX_BYTES",
    "MAX_ROTATE_MAX_BYTES",
    "MIN_ROTATE_BACKUP_COUNT",
    "MAX_ROTATE_BACKUP_COUNT",
    "CONSOLE_LOG_FORMAT",
    "FILE_LOG_FORMAT",
    "CONSOLE_DATE_FORMAT",
    "FILE_DATE_FORMAT",
)


def test_logger_defaults_exports_expected_symbols() -> None:
    """Verify that logger defaults expose the expected constants."""
    assert defaults.__all__ == EXPECTED_DEFAULTS_PUBLIC_API


def test_logger_default_values_match_current_template_behavior() -> None:
    """Verify that defaults preserve the current logger behavior."""
    assert defaults.DEFAULT_LOGGER_NAME == "desktop_app"
    assert defaults.DEFAULT_LOG_LEVEL == "INFO"
    assert Path("logs") / "app.log" == defaults.DEFAULT_LOG_FILE_PATH
    assert defaults.DEFAULT_BUFFER_CAPACITY == 500
    assert defaults.DEFAULT_ROTATE_MAX_BYTES == 5 * 1024 * 1024
    assert defaults.DEFAULT_ROTATE_BACKUP_COUNT == 3


def test_logger_default_limits_are_consistent() -> None:
    """Verify that default values remain inside accepted validation limits."""
    assert defaults.MIN_BUFFER_CAPACITY <= defaults.DEFAULT_BUFFER_CAPACITY
    assert defaults.DEFAULT_BUFFER_CAPACITY <= defaults.MAX_BUFFER_CAPACITY
    assert defaults.MIN_ROTATE_MAX_BYTES <= defaults.DEFAULT_ROTATE_MAX_BYTES
    assert defaults.DEFAULT_ROTATE_MAX_BYTES <= defaults.MAX_ROTATE_MAX_BYTES
    assert defaults.MIN_ROTATE_BACKUP_COUNT <= defaults.DEFAULT_ROTATE_BACKUP_COUNT
    assert defaults.DEFAULT_ROTATE_BACKUP_COUNT <= defaults.MAX_ROTATE_BACKUP_COUNT


def test_logger_default_formats_include_expected_record_fields() -> None:
    """Verify that default formatter strings include useful diagnostics."""
    assert "%(asctime)s" in defaults.CONSOLE_LOG_FORMAT
    assert "%(levelname)s" in defaults.CONSOLE_LOG_FORMAT
    assert "%(message)s" in defaults.CONSOLE_LOG_FORMAT
    assert "%(filename)s" in defaults.FILE_LOG_FORMAT
    assert "%(lineno)d" in defaults.FILE_LOG_FORMAT
    assert defaults.CONSOLE_DATE_FORMAT == "%H:%M:%S"
    assert defaults.FILE_DATE_FORMAT == "%Y-%m-%d %H:%M:%S"
