# -----------------------------------------------------------------------------
# File: src/desktop_app/app.py
# Purpose:
# Define the NiceGUI Windows Base application entry point.
# Behavior:
# Configures logging, builds the main NiceGUI page, registers lifecycle handlers,
# and starts NiceGUI in native mode by default or browser reload mode during
# development.
# Notes:
# Runtime detection, asset path resolution, splash handling, and lifecycle
# handlers are delegated to dedicated modules to keep this entry point focused
# on application startup orchestration.
# -----------------------------------------------------------------------------

import logging
import os
import sys
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path

from nicegui import native, ui

from desktop_app.constants import (
    APPLICATION_TITLE,
    DEFAULT_WEB_PORT,
    LOG_FILE_PATH,
    PAGE_IMAGE_FILENAME,
)
from desktop_app.core.runtime import (
    build_startup_message,
    describe_runtime_mode,
    describe_startup_source,
    detect_startup_source,
    get_nicegui_modes,
    is_frozen_executable,
)
from desktop_app.infrastructure.asset_paths import (
    get_application_icon_path,
    resolve_asset_path,
)
from desktop_app.infrastructure.lifecycle import register_lifecycle_handlers

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

logger = logging.getLogger("desktop_app.app")


def resolve_log_file_path() -> Path:
    """Return the log file path for the current runtime.

    Returns:
        A writable log path near the executable in frozen mode or in the current
        working directory during normal Python execution.
    """
    if is_frozen_executable():
        return Path(sys.executable).resolve().parent / LOG_FILE_PATH

    return Path.cwd() / LOG_FILE_PATH


def create_log_handlers(log_file_path: Path) -> list[logging.Handler]:
    """Create application log handlers.

    Args:
        log_file_path: File path where logs should be written.

    Returns:
        Configured logging handlers for file and terminal output.
    """
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    return [file_handler, stream_handler]


def configure_logging() -> Path:
    """Configure application logging for terminal and file diagnostics.

    Returns:
        The configured log file path.
    """
    log_file_path = resolve_log_file_path()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=create_log_handlers(log_file_path),
        force=True,
    )

    logger.info("Logging initialized for %s.", APPLICATION_TITLE)
    logger.debug("Log file ready at: %s", log_file_path)
    logger.debug("Application working directory: %s", Path.cwd())
    logger.debug("Python executable in use: %s", sys.executable)
    logger.debug("Command-line arguments received: %s", sys.argv)
    logger.debug("Frozen executable marker: %s", getattr(sys, "frozen", None))
    logger.debug(
        "PyInstaller extraction directory marker: %s",
        getattr(sys, "_MEIPASS", None),
    )
    logger.debug("Operating system process ID: %s", os.getpid())

    return log_file_path


def get_runtime_port(*, native_mode: bool) -> int:
    """Return the port used by NiceGUI for the selected runtime mode.

    Args:
        native_mode: Whether the application runs in NiceGUI native mode.

    Returns:
        A free dynamic port for native mode or the stable development web port.
    """
    if native_mode:
        port = native.find_open_port()
        logger.debug("Runtime port selected for native mode: %s", port)
        return port

    logger.debug("Runtime port selected for web development mode: %s", DEFAULT_WEB_PORT)
    return DEFAULT_WEB_PORT


def build_main_page(*, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        startup_message: Startup diagnostic message shown in the page.
    """
    logger.info("Building the main page for the connected client.")

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
        logger.debug("Page image resolved for the main page: %s", page_image_path)

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

    logger.info("Main page built successfully.")


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    configure_logging()
    logger.info("Starting %s startup sequence.", APPLICATION_TITLE)

    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(development_mode=development_mode)
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=APPLICATION_TITLE,
    )

    logger.info(
        "Startup source resolved: %s.",
        describe_startup_source(startup_source),
    )
    logger.info(
        "Runtime mode resolved: %s.",
        describe_runtime_mode(
            native_mode=native_mode,
            reload_enabled=reload_enabled,
        ),
    )

    print(startup_message, flush=True)
    logger.debug("Startup status message sent to the terminal: %s", startup_message)

    register_lifecycle_handlers()

    icon_path = get_application_icon_path()
    logger.debug("Application icon prepared for NiceGUI: %s", icon_path)

    runtime_port = get_runtime_port(native_mode=native_mode)
    logger.info(
        "Starting NiceGUI runtime in %s on port %s.",
        "native mode" if native_mode else "web mode",
        runtime_port,
    )

    ui_run_options = {
        "native": native_mode,
        "reload": reload_enabled,
        "title": APPLICATION_TITLE,
        "favicon": icon_path,
        "port": runtime_port,
    }

    if reload_enabled:
        ui_run_options.update(
            {
                "uvicorn_reload_dirs": "src",
                "uvicorn_reload_includes": "*.py",
                "uvicorn_reload_excludes": (
                    "logs/*,logs/**/*,*.log,build/*,dist/*,.venv/*,.venv/**/*"
                ),
            }
        )
        logger.debug("NiceGUI reload file watching configured for development mode.")

    # NiceGUI expects a callable that builds the UI when a client connects.
    # partial binds the startup message without calling build_main_page now.
    ui.run(
        partial(build_main_page, startup_message=startup_message),
        **ui_run_options,
    )


if __name__ == "__main__":
    freeze_support()
    main()
