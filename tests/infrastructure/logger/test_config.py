from dataclasses import fields, is_dataclass
from pathlib import Path

from desktop_app.constants import (
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGGER_NAME,
    DEFAULT_ROTATE_BACKUP_COUNT,
    DEFAULT_ROTATE_MAX_BYTES,
)
from desktop_app.infrastructure.logger.config import LoggerConfig


def test_logger_config_uses_expected_default_values() -> None:
    config = LoggerConfig()

    assert config.name == DEFAULT_LOGGER_NAME
    assert config.level == DEFAULT_LOG_LEVEL
    assert config.enable_console is True
    assert config.buffer_capacity == DEFAULT_BUFFER_CAPACITY
    assert config.file_path == DEFAULT_LOG_FILE_PATH
    assert config.rotate_max_bytes == DEFAULT_ROTATE_MAX_BYTES
    assert config.rotate_backup_count == DEFAULT_ROTATE_BACKUP_COUNT


def test_logger_config_accepts_custom_values() -> None:
    log_file_path = Path("logs/custom.log")

    config = LoggerConfig(
        name="custom_app",
        level=10,
        enable_console=False,
        buffer_capacity=25,
        file_path=log_file_path,
        rotate_max_bytes="10 MB",
        rotate_backup_count=7,
    )

    assert config.name == "custom_app"
    assert config.level == 10
    assert config.enable_console is False
    assert config.buffer_capacity == 25
    assert config.file_path == log_file_path
    assert config.rotate_max_bytes == "10 MB"
    assert config.rotate_backup_count == 7


def test_logger_config_accepts_string_paths_and_level_names() -> None:
    config = LoggerConfig(level="DEBUG", file_path="logs/debug.log")

    assert config.level == "DEBUG"
    assert config.file_path == "logs/debug.log"


def test_logger_config_is_a_slotted_dataclass() -> None:
    config = LoggerConfig()

    assert is_dataclass(config)
    assert [field.name for field in fields(config)] == [
        "name",
        "level",
        "enable_console",
        "buffer_capacity",
        "file_path",
        "rotate_max_bytes",
        "rotate_backup_count",
    ]
    assert not hasattr(config, "__dict__")
