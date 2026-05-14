# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/__init__.py
# Purpose:
# Expose the public native window state package API.
# Behavior:
# Re-exports only the startup, event, persistence, and geometry helpers used by
# application code while keeping implementation details in focused submodules.
# Notes:
# Import from this package in application code. Tests may import submodules when
# they need to validate implementation details directly.
# -----------------------------------------------------------------------------

from __future__ import annotations

from desktop_app.infrastructure.native_window_state.arguments import (
    apply_initial_native_window_options,
    apply_native_window_args_from_state,
)
from desktop_app.infrastructure.native_window_state.events import (
    refresh_native_window_state_from_proxy,
    update_native_window_position,
    update_native_window_size,
    update_native_window_state,
)
from desktop_app.infrastructure.native_window_state.persistence import (
    persist_native_window_state_on_exit,
)
from desktop_app.infrastructure.native_window_state.service import (
    normalize_persisted_window_geometry,
)

__all__ = [
    "apply_initial_native_window_options",
    "apply_native_window_args_from_state",
    "normalize_persisted_window_geometry",
    "persist_native_window_state_on_exit",
    "refresh_native_window_state_from_proxy",
    "update_native_window_position",
    "update_native_window_size",
    "update_native_window_state",
]
