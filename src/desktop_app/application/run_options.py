# -----------------------------------------------------------------------------
# File: src/desktop_app/application/run_options.py
# Purpose:
# Build the final NiceGUI ui.run options dictionary.
# Behavior:
# Converts the resolved runtime context into ui.run keyword arguments and applies
# native window startup preparation when native mode is enabled.
# Notes:
# Window geometry must stay centralized in app.native.window_args. Do not add
# window_size, window_position, fullscreen, or similar geometry keys here.
# -----------------------------------------------------------------------------

from __future__ import annotations

from logging import Logger
from typing import Any, Final

from desktop_app.application.runtime_context import RuntimeLaunchContext
from desktop_app.constants import APPLICATION_TITLE
from desktop_app.core.state import AppState
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state import (
    apply_initial_native_window_options,
)

logger: Final[Logger] = logger_get_logger(__name__)


def build_ui_run_options(
    context: RuntimeLaunchContext,
    *,
    state: AppState,
) -> dict[str, Any]:
    """Build NiceGUI ``ui.run`` options for the resolved runtime context.

    Args:
        context: Resolved runtime launch context.
        state: Current application state.

    Returns:
        Mutable options dictionary passed to ``ui.run``.
    """
    ui_run_options: dict[str, Any] = {
        "native": context.native_mode,
        "reload": context.reload_enabled,
        "title": state.meta.name or APPLICATION_TITLE,
        "favicon": context.icon_path,
        "port": context.port,
        "host": "127.0.0.1",
    }

    if context.native_mode:
        apply_initial_native_window_options(ui_run_options, state=state)

    if context.reload_enabled:
        ui_run_options.update(_build_reload_options())
        logger.debug("NiceGUI reload file watching configured for development mode.")

    return ui_run_options


def _build_reload_options() -> dict[str, str]:
    """Return NiceGUI reload options for browser development mode."""
    return {
        "uvicorn_reload_dirs": "src",
        "uvicorn_reload_includes": "*.py",
        "uvicorn_reload_excludes": (
            "logs/*,logs/**/*,*.log,settings.toml,build/*,dist/*,.venv/*,.venv/**/*"
        ),
    }
