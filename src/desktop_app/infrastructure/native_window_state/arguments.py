# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/arguments.py
# Purpose:
# Prepare and synchronize NiceGUI native window startup arguments.
# Behavior:
# Normalizes persisted geometry before ui.run starts and writes the final
# startup geometry into app.native.window_args, which is the single source of
# truth for pywebview window creation.
# Notes:
# Do not also pass window geometry through ui.run options. Keeping native
# geometry centralized avoids backend-dependent startup ordering issues.
# -----------------------------------------------------------------------------

from __future__ import annotations

from logging import Logger
from typing import Any, Final

from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state.bridge import (
    _get_native_window_args,
)
from desktop_app.infrastructure.native_window_state.defaults import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)

logger: Final[Logger] = logger_get_logger(__name__)


def apply_native_window_args_from_state(*, state: AppState | None = None) -> None:
    """Apply native pywebview arguments from AppState before ``main`` runs.

    NiceGUI native mode reads ``app.native.window_args`` while creating the
    pywebview window. Position values must be assigned as early as possible,
    before the application entry point starts ``ui.run``. Persisted values are
    normalized first so monitor changes do not leave the window off screen.

    Args:
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()
    from desktop_app.infrastructure.native_window_state.service import (
        normalize_persisted_window_geometry,
    )

    normalize_persisted_window_geometry(state=current_state)
    _sync_native_window_args_from_state(current_state)


def _sync_native_window_args_from_state(current_state: AppState) -> None:
    """Synchronize NiceGUI native window arguments with AppState.

    Args:
        current_state: Application state containing normalized window values.
    """
    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)

    window_args = _get_native_window_args()
    window_args["width"] = width
    window_args["height"] = height
    window_args["fullscreen"] = current_state.window.fullscreen
    window_args.pop("hidden", None)

    if current_state.window.persist_state:
        window_args["x"] = current_state.window.x
        window_args["y"] = current_state.window.y
    else:
        window_args.pop("x", None)
        window_args.pop("y", None)

    logger.debug(
        "Native window arguments synchronized from state: size=(%s, %s), "
        "position=(%s, %s), fullscreen=%s, persist_state=%s.",
        width,
        height,
        window_args.get("x"),
        window_args.get("y"),
        current_state.window.fullscreen,
        current_state.window.persist_state,
    )


def apply_initial_native_window_options(
    ui_run_options: dict[str, Any],
    *,
    state: AppState | None = None,
) -> None:
    """Prepare native window startup arguments before ``ui.run`` starts.

    Window geometry has a single startup source of truth: ``app.native.window_args``.
    This function intentionally does not add ``window_size``, ``fullscreen``,
    ``window_position``, or other window-related keys to ``ui_run_options``.
    Keeping those values out of ``ui.run`` avoids conflicts between NiceGUI run
    options and pywebview native creation arguments.

    Args:
        ui_run_options: Mutable options dictionary passed to ``ui.run``. It is
            accepted for compatibility with the app startup flow and is not
            modified with window geometry values.
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()

    apply_native_window_args_from_state(state=current_state)

    window_args = _get_native_window_args()
    logger.debug(
        "Native window startup prepared through app.native.window_args only: "
        "size=(%s, %s), position=(%s, %s), fullscreen=%s, persist_state=%s.",
        window_args.get("width"),
        window_args.get("height"),
        window_args.get("x"),
        window_args.get("y"),
        window_args.get("fullscreen"),
        current_state.window.persist_state,
    )


def _coerce_window_width(value: int) -> int:
    """Return a safe persisted window width.

    Args:
        value: Candidate width.

    Returns:
        Width clamped to the minimum accepted value.
    """
    return max(int(value), MIN_WINDOW_WIDTH)


def _coerce_window_height(value: int) -> int:
    """Return a safe persisted window height.

    Args:
        value: Candidate height.

    Returns:
        Height clamped to the minimum accepted value.
    """
    return max(int(value), MIN_WINDOW_HEIGHT)
