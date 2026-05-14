# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/persistence.py
# Purpose:
# Persist native window geometry to the settings window group.
# Behavior:
# Saves normalized or final native window state through the settings package and
# records save timestamps in AppState.
# Notes:
# This module intentionally owns settings writes for native window state. Event
# handlers only update in-memory geometry.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from desktop_app.core.state import AppState, WindowState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state.assignment import (
    _assign_if_different,
)
from desktop_app.infrastructure.native_window_state.events import (
    update_native_window_state,
)
from desktop_app.infrastructure.settings import save_settings_group

logger: Final[Logger] = logger_get_logger(__name__)


def persist_native_window_state_on_exit(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Persist native window geometry during application exit.

    Args:
        event_args: Native lifecycle event arguments received from NiceGUI.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when the settings file was saved successfully or persistence is
        disabled; False when saving was attempted and failed.
    """
    current_state = state if state is not None else get_app_state()

    if not current_state.window.persist_state:
        logger.info("Native window state persistence is disabled by settings.")
        return True

    update_native_window_state(*event_args, state=current_state)
    return _save_native_window_group(current_state)


def _save_native_window_group(state: AppState) -> bool:
    """Persist the current native window group to settings.toml.

    Args:
        state: Application state whose window group should be saved.

    Returns:
        True when the settings file was saved successfully.
    """
    state.window.last_saved_at = datetime.now()
    saved = save_settings_group("window", state=state)
    if saved:
        logger.info("Native window state persisted successfully.")
        return True

    logger.warning("Native window state could not be persisted.")
    return False


def _reset_window_geometry_to_defaults(window_state: WindowState) -> bool:
    """Reset persisted geometry fields to WindowState defaults.

    Args:
        window_state: Mutable window state to reset.

    Returns:
        True when at least one value was changed.
    """
    defaults = WindowState()
    changed = False
    reset_field_names = (
        "x",
        "y",
        "width",
        "height",
        "maximized",
        "fullscreen",
        "monitor",
    )

    for field_name in reset_field_names:
        changed = (
            _assign_if_different(
                window_state,
                field_name,
                getattr(defaults, field_name),
            )
            or changed
        )

    return changed


def _save_normalized_window_group(state: AppState) -> bool:
    """Save normalized window settings after startup validation.

    Args:
        state: Application state whose window group should be saved.

    Returns:
        True when the settings file was saved successfully.
    """
    state.window.last_saved_at = datetime.now()
    saved = save_settings_group("window", state=state)
    if saved:
        logger.info("Normalized native window settings saved successfully.")
        return True

    logger.warning("Normalized native window settings could not be saved.")
    return False
