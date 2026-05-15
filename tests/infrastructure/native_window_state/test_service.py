"""Tests for native window geometry normalization service."""

from __future__ import annotations

from types import ModuleType

import pytest

from desktop_app.core.state import AppState


def test_normalize_persisted_window_geometry_clamps_position_after_monitor_change(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted coordinates beyond the current screen are clamped."""
    state = AppState()
    state.window.x = 1400
    state.window.y = 900
    state.window.width = 500
    state.window.height = 400
    save_calls: list[tuple[str, AppState]] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append((group, state)) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.y == 720
    assert state.window.width == 500
    assert state.window.height == 400
    assert state.window.last_saved_at is not None
    assert save_calls == [("window", state)]


def test_normalize_persisted_window_geometry_recovers_window_hidden_left_or_top(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted coordinates that hide the window before the screen are fixed."""
    state = AppState()
    state.window.x = -800
    state.window.y = -600
    state.window.width = 500
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 0
    assert state.window.y == 0
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_keeps_valid_secondary_monitor_position(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valid coordinates on a secondary monitor are not clamped to primary."""
    state = AppState()
    state.window.x = 2100
    state.window.y = 120
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.models.MonitorWorkArea(0, 0, 1920, 1040),
            native_window_state_module.models.MonitorWorkArea(1920, 0, 3840, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is False
    assert state.window.x == 2100
    assert state.window.y == 120
    assert save_calls == []


def test_normalize_persisted_window_geometry_clamps_against_selected_monitor(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Out-of-range coordinates are clamped inside the nearest monitor."""
    state = AppState()
    state.window.x = 3900
    state.window.y = 1200
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.models.MonitorWorkArea(0, 0, 1920, 1040),
            native_window_state_module.models.MonitorWorkArea(1920, 0, 3840, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 3648
    assert state.window.y == 936
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_supports_negative_monitor_coordinates(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordinates on a left-side monitor remain valid when visible there."""
    state = AppState()
    state.window.x = -1700
    state.window.y = 100
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.models.MonitorWorkArea(-1920, 0, 0, 1040),
            native_window_state_module.models.MonitorWorkArea(0, 0, 1920, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is False
    assert state.window.x == -1700
    assert state.window.y == 100
    assert save_calls == []


def test_normalize_persisted_window_geometry_limits_start_position_after_90_percent(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordinates after 90 percent of a work area are limited without resizing."""
    state = AppState()
    state.window.x = 800
    state.window.y = 767
    state.window.width = 400
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 800
    assert state.window.y == 720
    assert state.window.width == 400
    assert state.window.height == 400
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_synchronizes_native_args(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrected geometry is applied to current native args immediately."""
    state = AppState()
    state.window.x = 800
    state.window.y = 767
    state.window.width = 400
    state.window.height = 400

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda _group, *, state: True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert native_window_state_module.bridge.app.native.window_args == {
        "width": 400,
        "height": 400,
        "fullscreen": False,
        "x": 800,
        "y": 720,
    }


def test_normalize_persisted_window_geometry_preserves_oversized_window_dimensions(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Monitor visibility correction does not reduce saved width or height."""
    state = AppState()
    state.window.x = 1400
    state.window.y = 900
    state.window.width = 2500
    state.window.height = 1400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.y == 720
    assert state.window.width == 2500
    assert state.window.height == 1400
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_reports_save_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Normalization still reports changed in memory when save fails."""
    state = AppState()
    state.window.x = 1200
    monkeypatch.setattr(
        native_window_state_module.geometry,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda _group, *, state: False,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.last_saved_at is not None
