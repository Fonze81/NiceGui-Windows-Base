# -----------------------------------------------------------------------------
# File: src/desktop_app/app.py
# Purpose:
# Define the NiceGUI Windows Base application entry point.
# Behavior:
# Loads persisted settings, configures the official logging subsystem, builds the
# main NiceGUI page, registers lifecycle handlers, and starts NiceGUI in native
# mode by default or browser reload mode during development.
# Notes:
# Runtime detection, state, settings, asset path resolution, splash handling,
# lifecycle handlers, and logger internals are delegated to dedicated modules to
# keep this entry point focused on application startup orchestration.
# -----------------------------------------------------------------------------

import os
import sys
from datetime import datetime
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path

from nicegui import native, ui

from desktop_app.constants import (
    APPLICATION_TITLE,
    DEFAULT_WEB_PORT,
    PAGE_IMAGE_FILENAME,
    SPLASH_IMAGE_FILENAME,
)
from desktop_app.core.runtime import (
    build_startup_message,
    describe_runtime_mode,
    describe_startup_source,
    detect_startup_source,
    get_nicegui_modes,
    is_frozen_executable,
)
from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.asset_paths import (
    get_application_icon_path,
    resolve_asset_path,
)
from desktop_app.infrastructure.lifecycle import register_lifecycle_handlers
from desktop_app.infrastructure.logger import (
    logger_bootstrap,
    logger_enable_file_logging,
    logger_get_logger,
    resolve_log_file_path,
)
from desktop_app.infrastructure.settings import (
    build_logger_config_from_state,
    load_settings,
)
from desktop_app.infrastructure.settings.paths import get_pyinstaller_temp_dir

logger = logger_get_logger(__name__)


def configure_logging(*, state: AppState | None = None) -> Path:
    """Load settings and configure the official logging subsystem.

    Args:
        state: Optional application state. Uses the global state when omitted.

    Returns:
        The configured log file path.
    """
    current_state = state if state is not None else get_app_state()
    current_state.paths.working_directory = Path.cwd()
    current_state.paths.executable_path = Path(sys.executable).resolve()
    current_state.paths.pyinstaller_temp_dir = get_pyinstaller_temp_dir()

    load_settings(state=current_state)
    current_state.paths.settings_file_path = current_state.settings.file_path

    frozen_executable = is_frozen_executable()
    log_file_path = resolve_log_file_path(
        current_state.log.file_path,
        frozen_executable=frozen_executable,
    )

    current_state.log.effective_file_path = log_file_path
    current_state.paths.log_file_path = log_file_path

    logger_bootstrap(
        build_logger_config_from_state(
            current_state,
            file_path=log_file_path,
            enable_console=current_state.log.enable_console and not frozen_executable,
        )
    )

    current_state.log.file_logging_enabled = logger_enable_file_logging()
    current_state.log.early_buffering_enabled = (
        not current_state.log.file_logging_enabled
    )
    if not current_state.log.file_logging_enabled:
        logger.warning(
            "File logging could not be enabled. Continuing without log file."
        )

    logger.info("Logging initialized for %s.", current_state.meta.name)
    logger.debug("Settings file ready at: %s", current_state.settings.file_path)
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


def build_main_page(*, application_name: str, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        application_name: Application name shown in the page.
        startup_message: Startup diagnostic message shown in the page.
    """
    state = get_app_state()
    state.ui_session.active_view = "home"
    state.ui_session.last_page_built_at = datetime.now()
    state.ui_session.is_busy = False
    state.ui_session.busy_message = None

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
        state.assets.page_image_path = Path(page_image_path)
        logger.debug("Page image resolved for the main page: %s", page_image_path)

        ui.image(page_image_path).classes("h-40 w-40 rounded-2xl object-contain")

        ui.label(application_name).classes(
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
    state = get_app_state()
    configure_logging(state=state)
    logger.info("Starting %s startup sequence.", state.meta.name)

    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(development_mode=development_mode)
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=state.meta.name or APPLICATION_TITLE,
    )
    state.runtime.startup_message = startup_message

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

    register_lifecycle_handlers(native_mode=native_mode)

    icon_path = get_application_icon_path()
    splash_image_path = resolve_asset_path(SPLASH_IMAGE_FILENAME)
    state.assets.icon_path = Path(icon_path)
    state.assets.splash_image_path = Path(splash_image_path)
    logger.debug("Application icon prepared for NiceGUI: %s", icon_path)
    logger.debug("Splash image path prepared for diagnostics: %s", splash_image_path)

    runtime_port = get_runtime_port(native_mode=native_mode)
    state.runtime.startup_source = startup_source
    state.runtime.native_mode = native_mode
    state.runtime.reload_enabled = reload_enabled
    state.runtime.port = runtime_port

    logger.info(
        "Starting NiceGUI runtime in %s on port %s.",
        "native mode" if native_mode else "web mode",
        runtime_port,
    )

    ui_run_options = {
        "native": native_mode,
        "reload": reload_enabled,
        "title": state.meta.name or APPLICATION_TITLE,
        "favicon": icon_path,
        "port": runtime_port,
        "host": "127.0.0.1",
    }

    if reload_enabled:
        ui_run_options.update(
            {
                "uvicorn_reload_dirs": "src",
                "uvicorn_reload_includes": "*.py",
                "uvicorn_reload_excludes": (
                    "logs/*,logs/**/*,*.log,settings.toml,build/*,dist/*,"
                    ".venv/*,.venv/**/*"
                ),
            }
        )
        logger.debug("NiceGUI reload file watching configured for development mode.")

    # NiceGUI expects a callable that builds the UI when a client connects.
    # partial binds the startup message without calling build_main_page now.
    ui.run(
        partial(
            build_main_page,
            application_name=state.meta.name or APPLICATION_TITLE,
            startup_message=startup_message,
        ),
        **ui_run_options,
    )


if __name__ == "__main__":
    freeze_support()
    main()
