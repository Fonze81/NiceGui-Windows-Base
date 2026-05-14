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
    _coerce_window_height as _coerce_window_height,
)
from desktop_app.infrastructure.native_window_state.arguments import (
    _coerce_window_width as _coerce_window_width,
)
from desktop_app.infrastructure.native_window_state.arguments import (
    _sync_native_window_args_from_state as _sync_native_window_args_from_state,
)
from desktop_app.infrastructure.native_window_state.arguments import (
    apply_initial_native_window_options,
    apply_native_window_args_from_state,
)
from desktop_app.infrastructure.native_window_state.bridge import (
    _get_native_window_args as _get_native_window_args,
)
from desktop_app.infrastructure.native_window_state.bridge import (
    app as app,
)
from desktop_app.infrastructure.native_window_state.events import (
    _coerce_optional_int as _coerce_optional_int,
)
from desktop_app.infrastructure.native_window_state.events import (
    _coerce_pair as _coerce_pair,
)
from desktop_app.infrastructure.native_window_state.events import (
    _extract_pair as _extract_pair,
)
from desktop_app.infrastructure.native_window_state.events import (
    _extract_pair_by_keys as _extract_pair_by_keys,
)
from desktop_app.infrastructure.native_window_state.events import (
    _looks_like_window as _looks_like_window,
)
from desktop_app.infrastructure.native_window_state.events import (
    _read_int_attribute as _read_int_attribute,
)
from desktop_app.infrastructure.native_window_state.events import (
    _request_native_window_pair as _request_native_window_pair,
)
from desktop_app.infrastructure.native_window_state.events import (
    _select_native_window as _select_native_window,
)
from desktop_app.infrastructure.native_window_state.events import (
    refresh_native_window_state_from_proxy,
    update_native_window_position,
    update_native_window_size,
    update_native_window_state,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _clamp_axis_position as _clamp_axis_position,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _get_windows_monitor_work_areas as _get_windows_monitor_work_areas,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _intersection_area as _intersection_area,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _normalize_window_geometry as _normalize_window_geometry,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _select_relevant_work_area as _select_relevant_work_area,
)
from desktop_app.infrastructure.native_window_state.geometry import (
    _squared_distance_between_centers as _squared_distance_between_centers,
)
from desktop_app.infrastructure.native_window_state.models import MonitorWorkArea
from desktop_app.infrastructure.native_window_state.persistence import (
    _reset_window_geometry_to_defaults as _reset_window_geometry_to_defaults,
)
from desktop_app.infrastructure.native_window_state.persistence import (
    _save_native_window_group as _save_native_window_group,
)
from desktop_app.infrastructure.native_window_state.persistence import (
    _save_normalized_window_group as _save_normalized_window_group,
)
from desktop_app.infrastructure.native_window_state.persistence import (
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
