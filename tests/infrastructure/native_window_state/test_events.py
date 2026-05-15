"""Tests for native window event payload readers."""

from __future__ import annotations

import asyncio
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import AppState


def test_update_native_window_size_uses_resize_payload(
    native_window_state_module: ModuleType,
) -> None:
    """Resize event width and height payloads update AppState."""
    state = AppState()

    updated = native_window_state_module.update_native_window_size(
        1366,
        768,
        state=state,
    )

    assert updated is True
    assert state.window.width == 1366
    assert state.window.height == 768


def test_update_native_window_position_uses_move_payload(
    native_window_state_module: ModuleType,
) -> None:
    """Move event x and y payloads update AppState."""
    state = AppState()

    updated = native_window_state_module.update_native_window_position(
        44,
        88,
        state=state,
    )

    assert updated is True
    assert state.window.x == 44
    assert state.window.y == 88


def test_update_native_window_state_uses_event_window(
    native_window_state_module: ModuleType,
    fake_window_cls: type,
) -> None:
    """Window lifecycle event arguments update AppState geometry."""
    state = AppState()
    window = fake_window_cls(x=55, y=66, width=1300, height=760)

    updated = native_window_state_module.update_native_window_state(window, state=state)

    assert updated is True
    assert state.window.x == 55
    assert state.window.y == 66
    assert state.window.width == 1300
    assert state.window.height == 760


def test_update_native_window_state_falls_back_to_main_window(
    native_window_state_module: ModuleType,
    fake_window_cls: type,
) -> None:
    """The current NiceGUI main window is used when event args are empty."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = fake_window_cls(
        x=70,
        y=80,
        width=1100,
        height=700,
    )

    updated = native_window_state_module.update_native_window_state(state=state)

    assert updated is True
    assert state.window.x == 70
    assert state.window.y == 80
    assert state.window.width == 1100
    assert state.window.height == 700


def test_update_native_window_state_ignores_invalid_or_small_values(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid geometry values do not overwrite safe defaults."""
    state = AppState()
    window = SimpleNamespace(x="bad", y=25, width=200, height=100)

    updated = native_window_state_module.update_native_window_state(window, state=state)

    assert updated is True
    assert state.window.x == 100
    assert state.window.y == 25
    assert state.window.width == 1024
    assert state.window.height == 720


def test_native_window_event_helpers_do_not_persist_settings(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Move and resize helpers update state without writing settings."""
    state = AppState()
    save_calls = 0

    def fail_if_saved(*_args: object, **_kwargs: object) -> bool:
        """Fail the test when event helpers unexpectedly write settings."""
        nonlocal save_calls
        save_calls += 1
        return False

    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        fail_if_saved,
    )

    size_updated = native_window_state_module.update_native_window_size(
        1280, 720, state=state
    )
    position_updated = native_window_state_module.update_native_window_position(
        300, 250, state=state
    )

    assert size_updated is True
    assert position_updated is True
    assert state.window.width == 1280
    assert state.window.height == 720
    assert state.window.x == 300
    assert state.window.y == 250
    assert state.window.last_saved_at is None
    assert save_calls == 0


def test_update_native_window_size_uses_nicegui_native_event_arguments(
    native_window_state_module: ModuleType,
) -> None:
    """NiceGUI NativeEventArguments resize payload updates AppState."""
    state = AppState()
    event_args = SimpleNamespace(args={"width": 1555, "height": 944})

    updated = native_window_state_module.update_native_window_size(
        event_args,
        state=state,
    )

    assert updated is True
    assert state.window.width == 1555
    assert state.window.height == 944


def test_update_native_window_position_uses_nicegui_native_event_arguments(
    native_window_state_module: ModuleType,
) -> None:
    """NiceGUI NativeEventArguments move payload updates AppState."""
    state = AppState()
    event_args = SimpleNamespace(args={"x": 321, "y": 654})

    updated = native_window_state_module.update_native_window_position(
        event_args,
        state=state,
    )

    assert updated is True
    assert state.window.x == 321
    assert state.window.y == 654


def test_update_native_window_state_returns_false_without_window(
    native_window_state_module: ModuleType,
) -> None:
    """State refresh reports no update when no native window is available."""
    state = AppState()

    updated = native_window_state_module.update_native_window_state(
        object(),
        state=state,
    )

    assert updated is False


def test_extract_pair_by_keys_skips_invalid_payload_before_valid_payload(
    native_window_state_module: ModuleType,
) -> None:
    """NativeEventArguments extraction continues until it finds a valid pair."""
    first = SimpleNamespace(args={"width": "bad", "height": 500})
    second = SimpleNamespace(args={"width": "640", "height": 480.5})

    assert native_window_state_module.events._extract_pair_by_keys(
        (first, second),
        "width",
        "height",
    ) == (640, 480)


def test_extract_pair_uses_nested_args_pair(
    native_window_state_module: ModuleType,
) -> None:
    """Pair extraction supports event objects whose args value is a pair."""
    event_args = SimpleNamespace(args=(111, 222))

    assert native_window_state_module.events._extract_pair((event_args,)) == (111, 222)


@pytest.mark.parametrize("raw_value", [True, None, "", "abc"])
def test_coerce_optional_int_rejects_invalid_values(
    native_window_state_module: ModuleType,
    raw_value: object,
) -> None:
    """Invalid geometry scalars are rejected instead of coerced."""
    assert native_window_state_module.events._coerce_optional_int(raw_value) is None


def test_coerce_pair_rejects_wrong_lengths(
    native_window_state_module: ModuleType,
) -> None:
    """Geometry pair coercion rejects one-item and three-item iterables."""
    assert native_window_state_module.events._coerce_pair((1,)) is None
    assert native_window_state_module.events._coerce_pair((1, 2, 3)) is None


def test_read_int_attribute_logs_ignored_invalid_attribute(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid native window attributes are skipped until a valid one is found."""
    value = SimpleNamespace(x="bad", left="25")

    assert (
        native_window_state_module.events._read_int_attribute(value, ("x", "left"))
        == 25
    )


def test_refresh_native_window_state_from_proxy_returns_false_without_window(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh is skipped safely when no native main window exists."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = None

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is False


def test_refresh_native_window_state_from_proxy_updates_complete_geometry(
    native_window_state_module: ModuleType,
    async_native_window_proxy_cls: type,
) -> None:
    """Proxy refresh updates position and size returned by async methods."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = (
        async_native_window_proxy_cls(
            position=(333, 444),
            size=(1280, 720),
        )
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 333
    assert state.window.y == 444
    assert state.window.width == 1280
    assert state.window.height == 720


def test_refresh_native_window_state_from_proxy_ignores_small_size(
    native_window_state_module: ModuleType,
    async_native_window_proxy_cls: type,
) -> None:
    """Proxy refresh ignores width and height below supported minimums."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = (
        async_native_window_proxy_cls(
            position=(100, 100),
            size=(100, 100),
        )
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is False
    assert state.window.width == 1024
    assert state.window.height == 720


def test_request_native_window_pair_returns_none_when_method_is_missing(
    native_window_state_module: ModuleType,
) -> None:
    """Missing proxy methods are reported as unavailable geometry."""
    result = asyncio.run(
        native_window_state_module.events._request_native_window_pair(
            object(), "missing"
        )
    )

    assert result is None


def test_request_native_window_pair_returns_none_when_method_fails(
    native_window_state_module: ModuleType,
    broken_native_window_proxy_cls: type,
) -> None:
    """Failing native proxy methods do not raise into lifecycle handlers."""
    result = asyncio.run(
        native_window_state_module.events._request_native_window_pair(
            broken_native_window_proxy_cls(),
            "get_position",
        )
    )

    assert result is None


def test_refresh_native_window_state_from_proxy_updates_size_without_position(
    native_window_state_module: ModuleType,
    partial_async_native_window_proxy_cls: type,
) -> None:
    """Proxy refresh can update size when position is unavailable."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = (
        partial_async_native_window_proxy_cls(
            position=None,
            size=(1440, 900),
        )
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 100
    assert state.window.y == 100
    assert state.window.width == 1440
    assert state.window.height == 900


def test_refresh_native_window_state_from_proxy_updates_position_without_size(
    native_window_state_module: ModuleType,
    partial_async_native_window_proxy_cls: type,
) -> None:
    """Proxy refresh can update position when size is unavailable."""
    state = AppState()
    native_window_state_module.bridge.app.native.main_window = (
        partial_async_native_window_proxy_cls(
            position=(333, 444),
            size=None,
        )
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 333
    assert state.window.y == 444
    assert state.window.width == 1024
    assert state.window.height == 720


def test_request_native_window_pair_accepts_synchronous_method_result(
    native_window_state_module: ModuleType,
    sync_native_window_proxy_cls: type,
) -> None:
    """Native proxy geometry methods may return a pair without awaiting."""
    result = asyncio.run(
        native_window_state_module.events._request_native_window_pair(
            sync_native_window_proxy_cls(),
            "get_size",
        )
    )

    assert result == (1440, 900)
