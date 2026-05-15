# -----------------------------------------------------------------------------
# File: tests/application/test_preferences.py
# Purpose:
# Validate preference update application services.
# Behavior:
# Exercises validation, AppState mutation, settings persistence calls, and status
# messages without importing NiceGUI.
# Notes:
# UI pages should only pass plain values into these services.
# -----------------------------------------------------------------------------

from __future__ import annotations

import desktop_app.application.preferences as preferences
from desktop_app.core.state import AppState


def test_update_theme_preference_validates_and_persists(
    monkeypatch,
) -> None:
    """Theme updates validate allowed values before saving."""
    state = AppState()
    save_calls: list[str] = []
    monkeypatch.setattr(
        preferences,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    result = preferences.update_theme_preference("dark", state=state)

    assert result.accepted is True
    assert result.saved is True
    assert result.level == "success"
    assert state.ui.theme == "dark"
    assert save_calls == ["ui"]

    invalid_result = preferences.update_theme_preference("invalid", state=state)

    assert invalid_result.accepted is False
    assert save_calls == ["ui"]


def test_update_font_scale_preference_rejects_out_of_range_values(
    monkeypatch,
) -> None:
    """Font scale updates reject unsafe values."""
    state = AppState()
    save_calls: list[str] = []
    monkeypatch.setattr(
        preferences,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    assert preferences.update_font_scale_preference("1.2", state=state).saved is True
    assert state.ui.font_scale == 1.2
    assert (
        preferences.update_font_scale_preference("2.0", state=state).accepted is False
    )
    assert preferences.update_font_scale_preference(True, state=state).accepted is False
    assert save_calls == ["ui"]


def test_update_accent_color_preference_validates_hex_values(
    monkeypatch,
) -> None:
    """Accent color updates accept only #RRGGBB values."""
    state = AppState()
    monkeypatch.setattr(
        preferences,
        "save_settings_group",
        lambda group, *, state: True,
    )

    result = preferences.update_accent_color_preference("#abcdef", state=state)

    assert result.saved is True
    assert state.ui.accent_color == "#ABCDEF"
    assert (
        preferences.update_accent_color_preference("blue", state=state).accepted
        is False
    )


def test_update_behavior_preference_persists_behavior_group(
    monkeypatch,
) -> None:
    """Behavior updates save the behavior settings group."""
    state = AppState()
    save_calls: list[str] = []
    monkeypatch.setattr(
        preferences,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or False,
    )

    result = preferences.update_auto_save_preference(False, state=state)

    assert state.behavior.auto_save is False
    assert result.accepted is True
    assert result.saved is False
    assert result.level == "error"
    assert save_calls == ["behavior"]
