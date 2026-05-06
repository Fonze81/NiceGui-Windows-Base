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
APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"
PYINSTALLER_SPLASH_MODULE = "pyi_splash"
DEFAULT_WEB_PORT = 8080
PACKAGED_ASSETS_DIR = Path("desktop_app") / "assets"
LOCAL_ASSETS_DIR = "assets"
LOG_FILE_PATH = Path("logs") / "nicegui_windows_base.log"
PYPROJECT_COMMAND_NAMES = ("nicegui-windows-base", "nicegui-windows-base.exe")
