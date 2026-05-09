# -----------------------------------------------------------------------------
# File: tests/test_constants.py
# Purpose:
# Validate the public constants exposed by desktop_app.constants.
# Behavior:
# Imports the constants module and verifies the public API, default values, path
# composition, immutable allowed-value collections, and numeric boundaries.
# Notes:
# These tests intentionally treat constants as a stable contract used by startup,
# settings, logging, asset resolution, and packaging code.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

from desktop_app import constants

EXPECTED_PUBLIC_CONSTANTS: tuple[str, ...] = (
    "APPLICATION_TITLE",
    "APPLICATION_VERSION",
    "APP_ICON_FILENAME",
    "PAGE_IMAGE_FILENAME",
    "SPLASH_IMAGE_FILENAME",
    "DEFAULT_WEB_PORT",
    "LOCAL_ASSETS_DIR",
    "PACKAGED_ASSETS_DIR",
    "LOGGER_NAME",
    "LOG_LEVEL",
    "LOG_FILE_PATH",
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
    "PYINSTALLER_SPLASH_MODULE",
    "PYPROJECT_COMMAND_NAMES",
    "SETTINGS_FILE_NAME",
    "APP_ROOT_ENV_VAR",
    "ALLOWED_LOG_LEVELS",
    "ALLOWED_THEMES",
)


def test_public_api_exports_only_supported_constants() -> None:
    """Ensure wildcard imports expose the supported constants contract."""
    assert constants.__all__ == EXPECTED_PUBLIC_CONSTANTS


def test_application_identity_and_asset_constants() -> None:
    """Verify application metadata and asset file names."""
    assert constants.APPLICATION_TITLE == "NiceGui Windows Base"
    assert constants.APPLICATION_VERSION == "0.4.0"
    assert constants.APP_ICON_FILENAME == "app_icon.ico"
    assert constants.PAGE_IMAGE_FILENAME == "page_image.png"
    assert constants.SPLASH_IMAGE_FILENAME == "splash_light.png"


def test_runtime_and_asset_path_constants() -> None:
    """Verify runtime port and asset directory path constants."""
    assert constants.DEFAULT_WEB_PORT == 8080
    assert Path("assets") == constants.LOCAL_ASSETS_DIR
    assert Path("desktop_app") / "assets" == constants.PACKAGED_ASSETS_DIR


def test_logger_identity_default_aliases_and_file_path() -> None:
    """Verify logger defaults and compatibility aliases."""
    assert constants.LOGGER_NAME == "desktop_app"
    assert constants.LOG_LEVEL == "INFO"
    assert Path("logs") / "app.log" == constants.LOG_FILE_PATH
    assert constants.DEFAULT_LOGGER_NAME == constants.LOGGER_NAME
    assert constants.DEFAULT_LOG_LEVEL == constants.LOG_LEVEL
    assert constants.DEFAULT_LOG_FILE_PATH == constants.LOG_FILE_PATH


def test_logger_buffer_and_rotation_defaults_are_within_limits() -> None:
    """Verify logger numeric defaults and accepted boundaries."""
    assert constants.DEFAULT_BUFFER_CAPACITY == 500
    assert constants.MIN_BUFFER_CAPACITY == 1
    assert constants.MAX_BUFFER_CAPACITY == 100_000
    assert constants.MIN_BUFFER_CAPACITY <= constants.DEFAULT_BUFFER_CAPACITY
    assert constants.DEFAULT_BUFFER_CAPACITY <= constants.MAX_BUFFER_CAPACITY

    assert constants.DEFAULT_ROTATE_MAX_BYTES == 5 * 1024 * 1024
    assert constants.MIN_ROTATE_MAX_BYTES == 1 * 1024 * 1024
    assert constants.MAX_ROTATE_MAX_BYTES == 1 * 1024 * 1024 * 1024
    assert constants.MIN_ROTATE_MAX_BYTES <= constants.DEFAULT_ROTATE_MAX_BYTES
    assert constants.DEFAULT_ROTATE_MAX_BYTES <= constants.MAX_ROTATE_MAX_BYTES

    assert constants.DEFAULT_ROTATE_BACKUP_COUNT == 3
    assert constants.MIN_ROTATE_BACKUP_COUNT == 0
    assert constants.MAX_ROTATE_BACKUP_COUNT == 100
    assert constants.MIN_ROTATE_BACKUP_COUNT <= constants.DEFAULT_ROTATE_BACKUP_COUNT
    assert constants.DEFAULT_ROTATE_BACKUP_COUNT <= constants.MAX_ROTATE_BACKUP_COUNT


def test_logger_format_constants() -> None:
    """Verify console and file logger format strings."""
    assert constants.CONSOLE_LOG_FORMAT == (
        "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s"
    )
    assert constants.FILE_LOG_FORMAT == (
        "%(asctime)s.%(msecs)03d | %(levelname)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )
    assert constants.CONSOLE_DATE_FORMAT == "%H:%M:%S"
    assert constants.FILE_DATE_FORMAT == "%Y-%m-%d %H:%M:%S"


def test_packaging_and_settings_constants() -> None:
    """Verify packaging, command detection, and settings constants."""
    assert constants.PYINSTALLER_SPLASH_MODULE == "pyi_splash"
    assert constants.PYPROJECT_COMMAND_NAMES == (
        "nicegui-windows-base",
        "nicegui-windows-base.exe",
    )
    assert constants.SETTINGS_FILE_NAME == "settings.toml"
    assert constants.APP_ROOT_ENV_VAR == "DESKTOP_APP_ROOT"


def test_allowed_values_are_immutable_sets() -> None:
    """Verify allowed value collections are immutable and complete."""
    assert (
        frozenset(
            {
                "CRITICAL",
                "ERROR",
                "WARNING",
                "WARN",
                "INFO",
                "DEBUG",
                "NOTSET",
            }
        )
        == constants.ALLOWED_LOG_LEVELS
    )
    assert frozenset({"light", "dark", "system"}) == constants.ALLOWED_THEMES
