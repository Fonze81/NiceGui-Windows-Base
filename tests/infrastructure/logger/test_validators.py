import logging
from pathlib import Path

import pytest

from desktop_app.constants import (
    MAX_BUFFER_CAPACITY,
    MAX_ROTATE_BACKUP_COUNT,
    MAX_ROTATE_MAX_BYTES,
    MIN_BUFFER_CAPACITY,
    MIN_ROTATE_BACKUP_COUNT,
    MIN_ROTATE_MAX_BYTES,
)
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError
from desktop_app.infrastructure.logger.validators import (
    normalize_buffer_capacity,
    normalize_enable_console,
    normalize_file_path,
    normalize_logger_config,
    normalize_logger_level,
    normalize_logger_name,
    normalize_rotate_backup_count,
    normalize_rotate_max_bytes,
    normalize_size_to_bytes,
    validate_logger_reconfiguration,
)


def test_normalize_logger_name_trims_valid_name() -> None:
    assert normalize_logger_name("  desktop_app  ") == "desktop_app"


@pytest.mark.parametrize("value", [None, 1, object()])
def test_normalize_logger_name_rejects_non_string_values(value: object) -> None:
    with pytest.raises(TypeError, match="Logger name must be a string"):
        normalize_logger_name(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_normalize_logger_name_rejects_empty_strings(value: str) -> None:
    with pytest.raises(LoggerValidationError, match="Logger name must not be empty"):
        normalize_logger_name(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (logging.INFO, logging.INFO),
        ("INFO", logging.INFO),
        (" debug ", logging.DEBUG),
    ],
)
def test_normalize_logger_level_accepts_valid_values(
    value: int | str,
    expected: int,
) -> None:
    assert normalize_logger_level(value) == expected


def test_normalize_logger_level_rejects_bool() -> None:
    with pytest.raises(TypeError, match="not bool"):
        normalize_logger_level(True)


@pytest.mark.parametrize("value", [None, 1.5, object()])
def test_normalize_logger_level_rejects_unsupported_types(value: object) -> None:
    with pytest.raises(TypeError, match="Logger level must be an int or a string"):
        normalize_logger_level(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_normalize_logger_level_rejects_empty_strings(value: str) -> None:
    with pytest.raises(
        LoggerValidationError,
        match="Logger level string must not be empty",
    ):
        normalize_logger_level(value)


def test_normalize_logger_level_rejects_unknown_level_name() -> None:
    with pytest.raises(LoggerValidationError, match="valid logging name"):
        normalize_logger_level("INVALID")


@pytest.mark.parametrize("value", [True, False])
def test_normalize_enable_console_accepts_boolean_values(value: bool) -> None:
    assert normalize_enable_console(value) is value


@pytest.mark.parametrize("value", [None, 1, "true"])
def test_normalize_enable_console_rejects_non_boolean_values(value: object) -> None:
    with pytest.raises(TypeError, match="Enable console flag must be a bool"):
        normalize_enable_console(value)


def test_normalize_file_path_accepts_string_path() -> None:
    assert normalize_file_path("logs/app.log") == Path("logs/app.log")


def test_normalize_file_path_accepts_path_instance() -> None:
    path = Path("logs/app.log")

    assert normalize_file_path(path) == path


@pytest.mark.parametrize("value", [None, 1, object()])
def test_normalize_file_path_rejects_unsupported_values(value: object) -> None:
    with pytest.raises(TypeError, match="Log file path must be a string"):
        normalize_file_path(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_normalize_file_path_rejects_empty_strings(value: str) -> None:
    with pytest.raises(LoggerValidationError, match="Log file path must not be empty"):
        normalize_file_path(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, 1),
        ("1 B", 1),
        ("512KB", 512 * 1024),
        ("5 MB", 5 * 1024 * 1024),
    ],
)
def test_normalize_size_to_bytes_accepts_valid_values(
    value: int | str,
    expected: int,
) -> None:
    assert normalize_size_to_bytes(value) == expected


def test_normalize_size_to_bytes_rejects_bool() -> None:
    with pytest.raises(TypeError, match="not bool"):
        normalize_size_to_bytes(False)


@pytest.mark.parametrize("value", [None, 1.5, object()])
def test_normalize_size_to_bytes_rejects_unsupported_types(value: object) -> None:
    with pytest.raises(TypeError, match="Size must be an int or a string"):
        normalize_size_to_bytes(value)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (0, "Size must be greater than zero"),
        ("", "Size string must not be empty"),
        ("10 XB", "Size string must use a valid format"),
    ],
)
def test_normalize_size_to_bytes_converts_value_errors_to_logger_validation_errors(
    value: int | str,
    message: str,
) -> None:
    with pytest.raises(LoggerValidationError, match=message):
        normalize_size_to_bytes(value)


@pytest.mark.parametrize("value", [MIN_BUFFER_CAPACITY, MAX_BUFFER_CAPACITY])
def test_normalize_buffer_capacity_accepts_boundary_values(value: int) -> None:
    assert normalize_buffer_capacity(value) == value


@pytest.mark.parametrize("value", [True, None, "1"])
def test_normalize_buffer_capacity_rejects_non_integer_values(value: object) -> None:
    with pytest.raises(TypeError, match="Buffer capacity must be an int"):
        normalize_buffer_capacity(value)


def test_normalize_buffer_capacity_rejects_value_below_minimum() -> None:
    with pytest.raises(LoggerValidationError, match="greater than or equal"):
        normalize_buffer_capacity(MIN_BUFFER_CAPACITY - 1)


def test_normalize_buffer_capacity_rejects_value_above_maximum() -> None:
    with pytest.raises(LoggerValidationError, match="less than or equal"):
        normalize_buffer_capacity(MAX_BUFFER_CAPACITY + 1)


@pytest.mark.parametrize("value", [MIN_ROTATE_MAX_BYTES, MAX_ROTATE_MAX_BYTES])
def test_normalize_rotate_max_bytes_accepts_boundary_values(value: int) -> None:
    assert normalize_rotate_max_bytes(value) == value


def test_normalize_rotate_max_bytes_accepts_string_size() -> None:
    assert normalize_rotate_max_bytes("1 MB") == MIN_ROTATE_MAX_BYTES


def test_normalize_rotate_max_bytes_rejects_value_below_minimum() -> None:
    with pytest.raises(LoggerValidationError, match="greater than or equal"):
        normalize_rotate_max_bytes(MIN_ROTATE_MAX_BYTES - 1)


def test_normalize_rotate_max_bytes_rejects_value_above_maximum() -> None:
    with pytest.raises(LoggerValidationError, match="less than or equal"):
        normalize_rotate_max_bytes(MAX_ROTATE_MAX_BYTES + 1)


@pytest.mark.parametrize("value", [MIN_ROTATE_BACKUP_COUNT, MAX_ROTATE_BACKUP_COUNT])
def test_normalize_rotate_backup_count_accepts_boundary_values(value: int) -> None:
    assert normalize_rotate_backup_count(value) == value


@pytest.mark.parametrize("value", [True, None, "1"])
def test_normalize_rotate_backup_count_rejects_non_integer_values(
    value: object,
) -> None:
    with pytest.raises(TypeError, match="Rotate backup count must be an int"):
        normalize_rotate_backup_count(value)


def test_normalize_rotate_backup_count_rejects_value_below_minimum() -> None:
    with pytest.raises(LoggerValidationError, match="greater than or equal"):
        normalize_rotate_backup_count(MIN_ROTATE_BACKUP_COUNT - 1)


def test_normalize_rotate_backup_count_rejects_value_above_maximum() -> None:
    with pytest.raises(LoggerValidationError, match="less than or equal"):
        normalize_rotate_backup_count(MAX_ROTATE_BACKUP_COUNT + 1)


def test_validate_logger_reconfiguration_accepts_same_logger_name() -> None:
    validate_logger_reconfiguration(
        current_config=LoggerConfig(name="desktop_app"),
        new_config=LoggerConfig(name="desktop_app", level="DEBUG"),
    )


def test_validate_logger_reconfiguration_rejects_logger_name_change() -> None:
    with pytest.raises(
        LoggerValidationError,
        match="Root logger name cannot be changed",
    ):
        validate_logger_reconfiguration(
            current_config=LoggerConfig(name="desktop_app"),
            new_config=LoggerConfig(name="other_app"),
        )


def test_normalize_logger_config_returns_normalized_copy() -> None:
    config = LoggerConfig(
        name=" desktop_app ",
        level=" debug ",
        enable_console=False,
        buffer_capacity=MIN_BUFFER_CAPACITY,
        file_path="logs/app.log",
        rotate_max_bytes="1 MB",
        rotate_backup_count=MIN_ROTATE_BACKUP_COUNT,
    )

    normalized_config = normalize_logger_config(config)

    assert normalized_config == LoggerConfig(
        name="desktop_app",
        level=logging.DEBUG,
        enable_console=False,
        buffer_capacity=MIN_BUFFER_CAPACITY,
        file_path=Path("logs/app.log"),
        rotate_max_bytes=MIN_ROTATE_MAX_BYTES,
        rotate_backup_count=MIN_ROTATE_BACKUP_COUNT,
    )
    assert normalized_config is not config


@pytest.mark.parametrize("value", [None, {}, object()])
def test_normalize_logger_config_rejects_non_logger_config_values(
    value: object,
) -> None:
    with pytest.raises(TypeError, match="Logger config must be a LoggerConfig"):
        normalize_logger_config(value)
