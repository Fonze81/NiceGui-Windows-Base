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

APPLICATION_TITLE: Final[str] = "NiceGui Windows Base"
APPLICATION_VERSION: Final[str] = "0.4.1"
APP_ICON_FILENAME: Final[str] = "app_icon.ico"
PAGE_IMAGE_FILENAME: Final[str] = "page_image.png"
SPLASH_IMAGE_FILENAME: Final[str] = "splash_light.png"

DEFAULT_WEB_PORT: Final[int] = 8080

LOCAL_ASSETS_DIR: Final[Path] = Path("assets")
PACKAGED_ASSETS_DIR: Final[Path] = Path("desktop_app") / "assets"

LOGGER_NAME: Final[str] = "desktop_app"
LOG_LEVEL: Final[str] = "INFO"
LOG_FILE_PATH: Final[Path] = Path("logs") / "app.log"

DEFAULT_LOGGER_NAME: Final[str] = LOGGER_NAME
DEFAULT_LOG_LEVEL: Final[str] = LOG_LEVEL
DEFAULT_LOG_FILE_PATH: Final[Path] = LOG_FILE_PATH

DEFAULT_BUFFER_CAPACITY: Final[int] = 500
DEFAULT_ROTATE_MAX_BYTES: Final[int] = 5 * 1024 * 1024
DEFAULT_ROTATE_BACKUP_COUNT: Final[int] = 3

MIN_BUFFER_CAPACITY: Final[int] = 1
MAX_BUFFER_CAPACITY: Final[int] = 100_000

MIN_ROTATE_MAX_BYTES: Final[int] = 1 * 1024 * 1024
MAX_ROTATE_MAX_BYTES: Final[int] = 1 * 1024 * 1024 * 1024

MIN_ROTATE_BACKUP_COUNT: Final[int] = 0
MAX_ROTATE_BACKUP_COUNT: Final[int] = 100

CONSOLE_LOG_FORMAT: Final[str] = "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s"
FILE_LOG_FORMAT: Final[str] = (
    "%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)
CONSOLE_DATE_FORMAT: Final[str] = "%H:%M:%S"
FILE_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

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
