# -----------------------------------------------------------------------------
# File: src/desktop_app/app.py
# Purpose:
# Define the NiceGUI Windows Base application entry point.
# Behavior:
# Configures logging, resolves application assets, handles the optional
# PyInstaller splash screen, builds the main NiceGUI page, and starts NiceGUI in
# native mode by default or browser reload mode during development.
# Notes:
# Runtime detection is delegated to desktop_app.core.runtime. Application
# constants and splash handling still live in this module until dedicated
# modules are introduced.
# -----------------------------------------------------------------------------

import importlib
import logging
import os
import sys
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path
from types import ModuleType

from nicegui import app, native, ui

from desktop_app.core.runtime import (
    build_startup_message,
    detect_startup_source,
    get_nicegui_modes,
    get_runtime_root,
    is_frozen_executable,
)

APPLICATION_TITLE = "NiceGui Windows Base"
APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"
PYINSTALLER_SPLASH_MODULE = "pyi_splash"
DEFAULT_WEB_PORT = 8080
PACKAGED_ASSETS_DIR = Path("desktop_app") / "assets"
LOCAL_ASSETS_DIR = "assets"
LOG_FILE_PATH = Path("logs") / "nicegui_windows_base.log"

logger = logging.getLogger(__name__)

_pyinstaller_splash_module: ModuleType | None = None
_pyinstaller_splash_close_attempted = False


def get_log_file_path() -> Path:
    """Return the log file path for the current runtime.

    Returns:
        A writable log path near the executable in frozen mode or in the current
        working directory during normal Python execution.
    """
    if is_frozen_executable():
        return Path(sys.executable).resolve().parent / LOG_FILE_PATH

    return Path.cwd() / LOG_FILE_PATH


def configure_logging() -> Path:
    """Configure application logging for terminal and file diagnostics.

    Returns:
        The configured log file path.
    """
    log_file_path = get_log_file_path()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    logger.info("Application logging is ready.")
    logger.debug("Log file path: %s", log_file_path)
    logger.debug("Current working directory: %s", Path.cwd())
    logger.debug("sys.executable: %s", sys.executable)
    logger.debug("sys.argv: %s", sys.argv)
    logger.debug("sys.frozen: %s", getattr(sys, "frozen", None))
    logger.debug("sys._MEIPASS: %s", getattr(sys, "_MEIPASS", None))
    logger.debug("Process ID: %s", os.getpid())

    return log_file_path


def resolve_asset_path(filename: str) -> str:
    """Return an absolute path for an application asset.

    Args:
        filename: Asset filename stored in the application assets directory.

    Returns:
        Absolute path to the requested asset file as a string.
    """
    runtime_root = get_runtime_root()

    if is_frozen_executable():
        asset_path = runtime_root / PACKAGED_ASSETS_DIR / filename
    else:
        asset_path = runtime_root / LOCAL_ASSETS_DIR / filename

    logger.debug("Resolved asset path for %s: %s", filename, asset_path)
    logger.debug("Asset exists: %s", asset_path.exists())

    return str(asset_path)


def get_application_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file as a string.
    """
    icon_path = resolve_asset_path(APP_ICON_FILENAME)
    logger.debug("Application icon path resolved: %s", icon_path)
    return icon_path


def get_runtime_port(*, native_mode: bool) -> int:
    """Return the port used by NiceGUI for the selected runtime mode.

    Args:
        native_mode: Whether the application runs in NiceGUI native mode.

    Returns:
        A free dynamic port for native mode or the stable development web port.
    """
    if native_mode:
        port = native.find_open_port()
        logger.debug("Native runtime port resolved: %s", port)
        return port

    logger.debug("Web development runtime port resolved: %s", DEFAULT_WEB_PORT)
    return DEFAULT_WEB_PORT


def load_pyinstaller_splash_module() -> ModuleType | None:
    """Load the optional PyInstaller splash module when available.

    Returns:
        The imported PyInstaller splash module, or None when unavailable.
    """
    if not is_frozen_executable():
        logger.debug("Skipping splash import because runtime is not frozen.")
        return None

    try:
        splash_module = importlib.import_module(PYINSTALLER_SPLASH_MODULE)
    except ImportError:
        logger.debug("PyInstaller splash module is not available.")
        return None

    logger.debug("PyInstaller splash module loaded.")
    return splash_module


def close_pyinstaller_splash_once() -> None:
    """Close the PyInstaller splash screen at most once."""
    global _pyinstaller_splash_close_attempted

    if _pyinstaller_splash_close_attempted:
        logger.debug("Skipping splash close because it was already attempted.")
        return

    _pyinstaller_splash_close_attempted = True

    if _pyinstaller_splash_module is None:
        logger.debug("Skipping splash close because no splash module was loaded.")
        return

    try:
        _pyinstaller_splash_module.close()
    except Exception:
        logger.exception("Failed to close PyInstaller splash screen.")
        return

    logger.debug("PyInstaller splash screen closed.")


def register_pyinstaller_splash_handler() -> None:
    """Register a handler to close the PyInstaller splash on first client connect."""
    global _pyinstaller_splash_module

    _pyinstaller_splash_module = load_pyinstaller_splash_module()

    if _pyinstaller_splash_module is None:
        logger.debug("PyInstaller splash handler was not registered.")
        return

    app.on_connect(close_pyinstaller_splash_once)
    logger.debug("PyInstaller splash handler registered.")


def build_main_page(*, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        startup_message: Startup diagnostic message shown in the page.
    """
    logger.info("Building the main page.")

    ui.query("body").classes("bg-slate-100")

    with (
        ui.column().classes(
            "fixed inset-0 items-center justify-center "
            "bg-gradient-to-br from-slate-50 via-white to-blue-50 p-6"
        ),
        ui.card().classes(
            "w-full max-w-2xl items-center gap-5 rounded-2xl p-8 text-center shadow-xl"
        ),
    ):
        page_image_path = resolve_asset_path(PAGE_IMAGE_FILENAME)
        logger.debug("Adding page image to UI: %s", page_image_path)

        ui.image(page_image_path).classes("h-40 w-40 rounded-2xl object-contain")

        ui.label(APPLICATION_TITLE).classes(
            "text-4xl font-bold tracking-tight text-slate-800"
        )
        ui.label("A minimal native and web Windows base template.").classes(
            "text-base text-slate-500"
        )

        with ui.card().classes(
            "w-full rounded-xl bg-slate-50 p-4 text-left shadow-none"
        ):
            ui.label("Startup status").classes(
                "text-sm font-semibold uppercase tracking-wide text-slate-500"
            )
            ui.label(startup_message).classes(
                "mt-1 text-sm leading-relaxed text-slate-700"
            )

    logger.info("Main page is ready.")


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    configure_logging()
    logger.info("Application startup begins.")

    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(development_mode=development_mode)
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=APPLICATION_TITLE,
    )

    if startup_source == "package":
        logger.info("Running as packaged executable.")
    elif development_mode:
        logger.info("Running in browser development mode.")
    else:
        logger.info("Running from %s.", startup_source)

    print(startup_message, flush=True)
    logger.debug("Startup message printed to terminal: %s", startup_message)

    register_pyinstaller_splash_handler()

    icon_path = get_application_icon_path()
    runtime_port = get_runtime_port(native_mode=native_mode)

    logger.info(
        "Starting NiceGUI in %s mode on port %s.",
        "native" if native_mode else "web",
        runtime_port,
    )

    # NiceGUI receives a callable that builds the UI later. partial keeps the
    # startup message bound without calling build_main_page before ui.run starts.
    ui.run(
        partial(build_main_page, startup_message=startup_message),
        native=native_mode,
        reload=reload_enabled,
        title=APPLICATION_TITLE,
        favicon=icon_path,
        port=runtime_port,
    )


if __name__ == "__main__":
    freeze_support()
    main()
