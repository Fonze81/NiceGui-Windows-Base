"""Tests for native window state persistence."""

from __future__ import annotations

from types import ModuleType

import pytest

from desktop_app.core.state import AppState


def test_persist_native_window_state_on_exit_skips_when_disabled(
    native_window_state_module: ModuleType,
    fake_window_cls: type,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disabled persistence does not write settings on exit."""
    state = AppState()
    state.window.persist_state = False
    save_calls = 0

    def fail_if_saved(*_args: object, **_kwargs: object) -> bool:
        """Fail the test when persistence unexpectedly writes settings."""
        nonlocal save_calls
        save_calls += 1
        return False

    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        fail_if_saved,
    )

    result = native_window_state_module.persist_native_window_state_on_exit(
        fake_window_cls(),
        state=state,
    )

    assert result is True
    assert save_calls == 0
    assert state.window.last_saved_at is None


def test_persist_native_window_state_on_exit_saves_window_group(
    native_window_state_module: ModuleType,
    fake_window_cls: type,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Enabled persistence captures geometry and saves only the window group."""
    state = AppState()
    calls: list[tuple[str, AppState]] = []

    def save_group(group: str, *, state: AppState) -> bool:
        """Capture the requested settings group."""
        calls.append((group, state))
        return True

    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        save_group,
    )

    result = native_window_state_module.persist_native_window_state_on_exit(
        fake_window_cls(x=15, y=25, width=1500, height=900),
        state=state,
    )

    assert result is True
    assert calls == [("window", state)]
    assert state.window.x == 15
    assert state.window.y == 25
    assert state.window.width == 1500
    assert state.window.height == 900
    assert state.window.last_saved_at is not None


def test_persist_native_window_state_on_exit_reports_save_failure(
    native_window_state_module: ModuleType,
    fake_window_cls: type,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failed native window persistence is reported as False."""
    state = AppState()
    monkeypatch.setattr(
        native_window_state_module.persistence,
        "save_settings_group",
        lambda _group, *, state: False,
    )

    saved = native_window_state_module.persist_native_window_state_on_exit(
        fake_window_cls(),
        state=state,
    )

    assert saved is False
    assert state.window.last_saved_at is not None
