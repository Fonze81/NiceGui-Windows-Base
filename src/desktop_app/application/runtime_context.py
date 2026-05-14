# -----------------------------------------------------------------------------
# File: src/desktop_app/application/runtime_context.py
# Purpose:
# Resolve the NiceGUI runtime context for the current application execution.
# Behavior:
# Detects startup source, native/reload mode, runtime port, startup message, and
# runtime assets, then mirrors those values into AppState for diagnostics.
# Notes:
# Keep this module focused on runtime decisions. Construction of ui.run options
# belongs in desktop_app.application.run_options.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Final

from nicegui import native

from desktop_app.constants import (
    APPLICATION_TITLE,
    DEFAULT_WEB_PORT,
    SPLASH_IMAGE_FILENAME,
)
from desktop_app.core.runtime import (
    build_startup_message,
    describe_runtime_mode,
    describe_startup_source,
    detect_startup_source,
    get_nicegui_modes,
)
from desktop_app.core.state import AppState
from desktop_app.infrastructure.asset_paths import (
    get_application_icon_path,
    resolve_asset_path,
)
from desktop_app.infrastructure.logger import logger_get_logger

logger: Final[Logger] = logger_get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RuntimeLaunchContext:
    """Store values needed to start NiceGUI.

    Attributes:
        startup_source: Resolved startup source, such as package or module.
        startup_message: Startup message shared by terminal and UI.
        native_mode: Whether NiceGUI should run in native mode.
        reload_enabled: Whether NiceGUI reload mode should be enabled.
        port: HTTP port selected for NiceGUI.
        icon_path: Application icon path used as NiceGUI favicon.
        splash_image_path: Splash image path stored for diagnostics.
    """

    startup_source: str
    startup_message: str
    native_mode: bool
    reload_enabled: bool
    port: int
    icon_path: str
    splash_image_path: str


def resolve_runtime_launch_context(
    *,
    development_mode: bool,
    state: AppState,
    entry_source_hint: object = None,
) -> RuntimeLaunchContext:
    """Resolve and store all runtime values needed before ``ui.run``.

    Args:
        development_mode: Whether to run in web development mode with reload.
        state: Application state to update.
        entry_source_hint: Optional startup source captured before runpy changed
            sys.argv.

    Returns:
        Resolved runtime launch context.
    """
    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(
        development_mode=development_mode,
        entry_source_hint=entry_source_hint,
    )
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=state.meta.name or APPLICATION_TITLE,
    )
    runtime_port = get_runtime_port(native_mode=native_mode)
    icon_path = get_application_icon_path()
    splash_image_path = resolve_asset_path(SPLASH_IMAGE_FILENAME)

    _store_runtime_context(
        state,
        startup_source=startup_source,
        startup_message=startup_message,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        runtime_port=runtime_port,
        icon_path=icon_path,
        splash_image_path=splash_image_path,
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

    return RuntimeLaunchContext(
        startup_source=startup_source,
        startup_message=startup_message,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        port=runtime_port,
        icon_path=icon_path,
        splash_image_path=splash_image_path,
    )


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


def _store_runtime_context(
    state: AppState,
    *,
    startup_source: str,
    startup_message: str,
    native_mode: bool,
    reload_enabled: bool,
    runtime_port: int,
    icon_path: str,
    splash_image_path: str,
) -> None:
    """Mirror resolved runtime values into AppState.

    Args:
        state: Application state to update.
        startup_source: Resolved startup source.
        startup_message: Startup message shared by terminal and UI.
        native_mode: Whether NiceGUI should run in native mode.
        reload_enabled: Whether NiceGUI reload mode should be enabled.
        runtime_port: HTTP port selected for NiceGUI.
        icon_path: Resolved icon path.
        splash_image_path: Resolved splash image path.
    """
    state.runtime.startup_source = startup_source
    state.runtime.startup_message = startup_message
    state.runtime.native_mode = native_mode
    state.runtime.reload_enabled = reload_enabled
    state.runtime.port = runtime_port
    state.assets.icon_path = Path(icon_path)
    state.assets.splash_image_path = Path(splash_image_path)

    logger.debug("Application icon prepared for NiceGUI: %s", icon_path)
    logger.debug("Splash image path prepared for diagnostics: %s", splash_image_path)
