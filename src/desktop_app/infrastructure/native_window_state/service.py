# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/service.py
# Purpose:
# Coordinate native window geometry normalization and startup preparation.
# Behavior:
# Applies persistence rules, delegates monitor math to geometry.py, delegates
# settings writes to persistence.py, and keeps NiceGUI native startup arguments
# synchronized with normalized AppState values.
# Notes:
# This module is the public orchestration layer for startup-time native window
# state handling.
# -----------------------------------------------------------------------------

from __future__ import annotations

from logging import Logger
from typing import Final

from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state.arguments import (
    _sync_native_window_args_from_state,
)
from desktop_app.infrastructure.native_window_state.assignment import (
    _assign_if_different,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _normalize_window_geometry,
)
from desktop_app.infrastructure.native_window_state.persistence import (
    _reset_window_geometry_to_defaults,
    _save_normalized_window_group,
)

logger: Final[Logger] = logger_get_logger(__name__)


def normalize_persisted_window_geometry(*, state: AppState | None = None) -> bool:
    """Normalize persisted native window geometry before restoration.

    The persisted window position can become invalid when the user removes,
    changes, or reorders monitors. This function keeps the window anchored to a
    visible part of the selected monitor work area without resizing the saved
    width or height.
    When persistence is disabled, persisted geometry is reset to defaults and
    saved so stale values are not reused later.

    Args:
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when the in-memory state was changed.
    """
    current_state = state if state is not None else get_app_state()

    if not current_state.window.persist_state:
        changed = _reset_window_geometry_to_defaults(current_state.window)
        if changed:
            _save_normalized_window_group(current_state)
        return changed

    safe_x, safe_y, safe_width, safe_height = _normalize_window_geometry(
        x=current_state.window.x,
        y=current_state.window.y,
        width=current_state.window.width,
        height=current_state.window.height,
    )

    changed = _assign_if_different(current_state.window, "width", safe_width)
    changed = (
        _assign_if_different(current_state.window, "height", safe_height) or changed
    )
    changed = _assign_if_different(current_state.window, "x", safe_x) or changed
    changed = _assign_if_different(current_state.window, "y", safe_y) or changed

    if changed:
        _save_normalized_window_group(current_state)
        _sync_native_window_args_from_state(current_state)

    return changed
