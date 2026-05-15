# -----------------------------------------------------------------------------
# File: src/desktop_app/constants.py
# Purpose:
# Store shared application constants.
# Behavior:
# Provides stable values used by application startup, UI configuration, asset
# resolution, logging, settings persistence, and packaged execution.
# Notes:
# Keep this module free of runtime logic and external side effects. Do not add
# values here unless they are reused across modules or represent application
# configuration.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
from typing import Final

from desktop_app.infrastructure.logger.defaults import (
    CONSOLE_DATE_FORMAT,
    CONSOLE_LOG_FORMAT,
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGGER_NAME,
    DEFAULT_ROTATE_BACKUP_COUNT,
    DEFAULT_ROTATE_MAX_BYTES,
    FILE_DATE_FORMAT,
    FILE_LOG_FORMAT,
    MAX_BUFFER_CAPACITY,
    MAX_ROTATE_BACKUP_COUNT,
    MAX_ROTATE_MAX_BYTES,
    MIN_BUFFER_CAPACITY,
    MIN_ROTATE_BACKUP_COUNT,
    MIN_ROTATE_MAX_BYTES,
)

APPLICATION_TITLE: Final[str] = "NiceGui Windows Base"
APPLICATION_VERSION: Final[str] = "0.8.0"
APP_ICON_FILENAME: Final[str] = "app_icon.ico"
PAGE_IMAGE_FILENAME: Final[str] = "page_image.png"
SPLASH_IMAGE_FILENAME: Final[str] = "splash_light.png"

DEFAULT_WEB_PORT: Final[int] = 8080

LOCAL_ASSETS_DIR: Final[Path] = Path("assets")
PACKAGED_ASSETS_DIR: Final[Path] = Path("desktop_app") / "assets"

LOGGER_NAME: Final[str] = DEFAULT_LOGGER_NAME
LOG_LEVEL: Final[str] = DEFAULT_LOG_LEVEL
LOG_FILE_PATH: Final[Path] = DEFAULT_LOG_FILE_PATH

PYINSTALLER_SPLASH_MODULE: Final[str] = "pyi_splash"

PYPROJECT_COMMAND_NAMES: Final[tuple[str, ...]] = (
    "nicegui-windows-base",
    "nicegui-windows-base.exe",
)

SETTINGS_FILE_NAME: Final[str] = "settings.toml"
APP_ROOT_ENV_VAR: Final[str] = "DESKTOP_APP_ROOT"

ALLOWED_LOG_LEVELS: Final[frozenset[str]] = frozenset(
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

ALLOWED_THEMES: Final[frozenset[str]] = frozenset({"light", "dark", "system"})

__all__: Final[tuple[str, ...]] = (
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
