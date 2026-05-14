# -----------------------------------------------------------------------------
# File: src/desktop_app/app.py
# Purpose:
# Provide the NiceGUI Windows Base application entry point.
# Behavior:
# Coordinates startup bootstrap, runtime context resolution, lifecycle handler
# registration, and the final NiceGUI ui.run call.
# Notes:
# Detailed logging setup, runtime option construction, native window preparation,
# and UI composition are delegated to focused modules to keep this entry point
# small and maintainable.
# -----------------------------------------------------------------------------

from __future__ import annotations

from multiprocessing import freeze_support

from nicegui import ui

from desktop_app.application.bootstrap import (
    configure_logging,
    prepare_native_window_arguments_before_main,
)
from desktop_app.application.run_options import build_ui_run_options
from desktop_app.application.runtime_context import resolve_runtime_launch_context
from desktop_app.constants import APPLICATION_TITLE
from desktop_app.core.runtime import ENTRY_SOURCE_HINT_GLOBAL
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.lifecycle import register_lifecycle_handlers
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.router import register_spa_routes

logger = logger_get_logger(__name__)
entry_source_hint = globals().get(ENTRY_SOURCE_HINT_GLOBAL)

prepare_native_window_arguments_before_main()


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    state = get_app_state()
    configure_logging(state=state)
    logger.info("Starting %s startup sequence.", state.meta.name)

    runtime_context = resolve_runtime_launch_context(
        development_mode=development_mode,
        state=state,
        entry_source_hint=entry_source_hint,
    )

    logger.info("Startup status: %s", runtime_context.startup_message)

    register_lifecycle_handlers(native_mode=runtime_context.native_mode)

    logger.info(
        "Starting NiceGUI runtime in %s on port %s.",
        "native mode" if runtime_context.native_mode else "web mode",
        runtime_context.port,
    )

    register_spa_routes(
        application_name=state.meta.name or APPLICATION_TITLE,
        startup_message=runtime_context.startup_message,
    )

    ui.run(**build_ui_run_options(runtime_context, state=state))


if __name__ == "__main__":
    freeze_support()
    main()
