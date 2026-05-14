# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/__init__.py
# Purpose:
# Expose the public native window state package API.
# Behavior:
# Re-exports startup, event, persistence, and geometry helpers used by the
# application while keeping implementation details in focused submodules.
# Notes:
# Import from this package in application code. Submodules are organized by
# responsibility for maintainability and targeted tests.
# -----------------------------------------------------------------------------

from __future__ import annotations

from desktop_app.infrastructure.native_window_state.arguments import (
    _coerce_window_height,
    _coerce_window_width,
    _sync_native_window_args_from_state,
    apply_initial_native_window_options,
    apply_native_window_args_from_state,
)
from desktop_app.infrastructure.native_window_state.bridge import (
    _get_native_window_args,
    app,
)
from desktop_app.infrastructure.native_window_state.events import (
    _coerce_optional_int,
    _coerce_pair,
    _extract_pair,
    _extract_pair_by_keys,
    _looks_like_window,
    _read_int_attribute,
    _request_native_window_pair,
    _select_native_window,
    refresh_native_window_state_from_proxy,
    update_native_window_position,
    update_native_window_size,
    update_native_window_state,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _clamp_axis_position,
    _get_windows_monitor_work_areas,
    _intersection_area,
    _normalize_window_geometry,
    _select_relevant_work_area,
    _squared_distance_between_centers,
)
from desktop_app.infrastructure.native_window_state.models import MonitorWorkArea
from desktop_app.infrastructure.native_window_state.persistence import (
    _reset_window_geometry_to_defaults,
    _save_native_window_group,
    _save_normalized_window_group,
    persist_native_window_state_on_exit,
)
from desktop_app.infrastructure.native_window_state.service import (
    normalize_persisted_window_geometry,
)

__all__ = [
    "MonitorWorkArea",
    "apply_initial_native_window_options",
    "apply_native_window_args_from_state",
    "normalize_persisted_window_geometry",
    "persist_native_window_state_on_exit",
    "refresh_native_window_state_from_proxy",
    "update_native_window_position",
    "update_native_window_size",
    "update_native_window_state",
]
