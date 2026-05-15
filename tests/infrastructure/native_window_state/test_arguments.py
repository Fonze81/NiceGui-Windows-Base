"""Tests for native window startup argument synchronization."""

from __future__ import annotations

from types import ModuleType
from typing import Any

import pytest

from desktop_app.core.state import AppState


def test_apply_initial_native_window_options_uses_persisted_geometry(
    native_window_state_module: ModuleType,
) -> None:
    """Native run options and window args receive persisted geometry."""
    state = AppState()
    state.window.x = 30
    state.window.y = 40
    state.window.width = 1440
    state.window.height = 900
    state.window.fullscreen = True
    options: dict[str, Any] = {}

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert options == {}
    assert native_window_state_module.bridge.app.native.window_args == {
        "width": 1440,
        "height": 900,
        "fullscreen": True,
        "x": 30,
        "y": 40,
    }


def test_apply_native_window_args_from_state_can_run_before_main(
    native_window_state_module: ModuleType,
) -> None:
    """Native window args can be prepared without building ui.run options."""
    state = AppState()
    state.window.x = 700
    state.window.y = 500
    state.window.width = 1366
    state.window.height = 768

    native_window_state_module.apply_native_window_args_from_state(state=state)

    assert native_window_state_module.bridge.app.native.window_args == {
        "width": 1366,
        "height": 768,
        "fullscreen": False,
        "x": 700,
        "y": 500,
    }


def test_apply_initial_native_window_options_omits_position_when_disabled(
    native_window_state_module: ModuleType,
) -> None:
    """Window position is not forced when persistence is disabled."""
    state = AppState()
    state.window.persist_state = False
    options: dict[str, Any] = {}

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert options == {}
    assert native_window_state_module.bridge.app.native.window_args == {
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }


def test_apply_initial_native_window_options_clears_stale_position_when_disabled(
    native_window_state_module: ModuleType,
) -> None:
    """Disabled persistence removes stale native position arguments."""
    state = AppState()
    state.window.persist_state = False
    options: dict[str, Any] = {}
    native_window_state_module.bridge.app.native.window_args.update(
        {"x": 500, "y": 600, "min_size": (400, 300)}
    )

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert native_window_state_module.bridge.app.native.window_args == {
        "min_size": (400, 300),
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }


def test_apply_native_window_args_resets_geometry_when_persistence_is_disabled(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disabled persistence clears stale saved geometry and uses defaults."""
    state = AppState()
    state.window.persist_state = False
    state.window.x = 1600
    state.window.y = 900
    state.window.width = 300
    state.window.height = 200
    state.window.maximized = True
    state.window.fullscreen = True
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    native_window_state_module.apply_native_window_args_from_state(state=state)

    assert state.window.x == 100
    assert state.window.y == 100
    assert state.window.width == 1024
    assert state.window.height == 720
    assert state.window.maximized is False
    assert state.window.fullscreen is False
    assert state.window.persist_state is False
    assert state.window.last_saved_at is not None
    assert native_window_state_module.bridge.app.native.window_args == {
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }
    assert save_calls == ["window"]


def test_get_native_window_args_creates_missing_dict(
    native_window_state_module: ModuleType,
) -> None:
    """Native window args are initialized when NiceGUI exposes no dictionary."""
    native_window_state_module.bridge.app.native.window_args = None

    window_args = native_window_state_module.bridge._get_native_window_args()

    assert window_args == {}
    assert native_window_state_module.bridge.app.native.window_args is window_args
