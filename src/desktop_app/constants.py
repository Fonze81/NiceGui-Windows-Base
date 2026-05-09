# -----------------------------------------------------------------------------
# File: src/desktop_app/constants.py
# Purpose:
# Store shared application constants.
# Behavior:
# Provides stable values used by application startup, UI configuration, asset
# resolution, logging, and packaged execution.
# Notes:
# Keep this module free of runtime logic and external side effects. Do not add
# values here unless they are reused across modules or represent application
# configuration.
# -----------------------------------------------------------------------------

from pathlib import Path

APPLICATION_TITLE = "NiceGui Windows Base"
APPLICATION_VERSION = "0.3.4"
APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"
SPLASH_IMAGE_FILENAME = "splash_light.png"

DEFAULT_WEB_PORT = 8080

LOCAL_ASSETS_DIR = Path("assets")
PACKAGED_ASSETS_DIR = Path("desktop_app") / "assets"

LOGGER_NAME = "desktop_app"
LOG_LEVEL = "INFO"
LOG_FILE_PATH = Path("logs") / "app.log"

DEFAULT_LOGGER_NAME = LOGGER_NAME
DEFAULT_LOG_LEVEL = LOG_LEVEL
DEFAULT_LOG_FILE_PATH = LOG_FILE_PATH

DEFAULT_BUFFER_CAPACITY = 500
DEFAULT_ROTATE_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_ROTATE_BACKUP_COUNT = 3

MIN_BUFFER_CAPACITY = 1
MAX_BUFFER_CAPACITY = 100_000

MIN_ROTATE_MAX_BYTES = 1 * 1024 * 1024
MAX_ROTATE_MAX_BYTES = 1 * 1024 * 1024 * 1024

MIN_ROTATE_BACKUP_COUNT = 0
MAX_ROTATE_BACKUP_COUNT = 100

CONSOLE_LOG_FORMAT = "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s"
FILE_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)
CONSOLE_DATE_FORMAT = "%H:%M:%S"
FILE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

PYINSTALLER_SPLASH_MODULE = "pyi_splash"

PYPROJECT_COMMAND_NAMES = (
    "nicegui-windows-base",
    "nicegui-windows-base.exe",
)

SETTINGS_FILE_NAME = "settings.toml"
APP_ROOT_ENV_VAR = "DESKTOP_APP_ROOT"

ALLOWED_LOG_LEVELS = {
    "CRITICAL",
    "ERROR",
    "WARNING",
    "WARN",
    "INFO",
    "DEBUG",
    "NOTSET",
}

ALLOWED_THEMES = {"light", "dark", "system"}
