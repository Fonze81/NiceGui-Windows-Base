# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test_mapper.py
# Purpose:
# Validate settings mapper behavior for AppState and LoggerConfig conversion.
# Behavior:
# Exercises supported settings properties, validation fallbacks, legacy aliases,
# logger configuration creation, and unsupported property errors.
# Notes:
# These tests avoid file I/O and NiceGUI dependencies. They target only the
# pure mapping behavior of desktop_app.infrastructure.settings.mapper.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from desktop_app.constants import (
    APPLICATION_TITLE,
    APPLICATION_VERSION,
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_ROTATE_BACKUP_COUNT,
)
from desktop_app.core.state import AppState, reset_app_state
from desktop_app.infrastructure.settings.mapper import (
    apply_setting_property_to_state,
    apply_settings_to_state,
    build_logger_config_from_state,
)
from desktop_app.infrastructure.settings.schema import SettingsScopeError

type StateGetter = Callable[[AppState], Any]


def nested_settings(property_path: str, value: Any) -> dict[str, Any]:
    """Build a nested settings mapping from a dotted property path.

    Args:
        property_path: Dotted settings path, such as ``app.window.width``.
        value: Value assigned to the final path segment.

    Returns:
        Nested mapping accepted by the settings mapper.
    """
    root: dict[str, Any] = {}
    cursor = root
    path_parts = property_path.split(".")

    for path_part in path_parts[:-1]:
        cursor = cursor.setdefault(path_part, {})

    cursor[path_parts[-1]] = value
    return root


@pytest.mark.parametrize(
    ("property_path", "raw_value", "state_getter", "expected_value"),
    [
        ("app.name", " Custom App ", lambda state: state.meta.name, "Custom App"),
        ("app.version", " 1.2.3 ", lambda state: state.meta.version, "1.2.3"),
        ("app.language", " pt-BR ", lambda state: state.meta.language, "pt-BR"),
        ("app.first_run", "false", lambda state: state.meta.first_run, False),
        ("app.window.x", "10", lambda state: state.window.x, 10),
        ("app.window.y", "20", lambda state: state.window.y, 20),
        ("app.window.width", "1200", lambda state: state.window.width, 1200),
        ("app.window.height", "800", lambda state: state.window.height, 800),
        (
            "app.window.maximized",
            "yes",
            lambda state: state.window.maximized,
            True,
        ),
        (
            "app.window.fullscreen",
            "true",
            lambda state: state.window.fullscreen,
            True,
        ),
        ("app.window.monitor", "2", lambda state: state.window.monitor, 2),
        (
            "app.window.storage_key",
            " custom_window_state ",
            lambda state: state.window.storage_key,
            "custom_window_state",
        ),
        ("app.ui.theme", " DARK ", lambda state: state.ui.theme, "dark"),
        ("app.ui.font_scale", "1.25", lambda state: state.ui.font_scale, 1.25),
        ("app.ui.dense_mode", "sim", lambda state: state.ui.dense_mode, True),
        (
            "app.ui.accent_color",
            " #111827 ",
            lambda state: state.ui.accent_color,
            "#111827",
        ),
        ("app.log.level", " debug ", lambda state: state.log.level, "DEBUG"),
        (
            "app.log.enable_console",
            "false",
            lambda state: state.log.enable_console,
            False,
        ),
        (
            "app.log.buffer_capacity",
            "1000",
            lambda state: state.log.buffer_capacity,
            1000,
        ),
        (
            "app.log.file_path",
            " logs/custom.log ",
            lambda state: state.log.file_path,
            Path("logs/custom.log"),
        ),
        (
            "app.log.rotate_max_bytes",
            "10 MB",
            lambda state: state.log.rotate_max_bytes,
            "10 MB",
        ),
        (
            "app.log.rotate_backup_count",
            "5",
            lambda state: state.log.rotate_backup_count,
            5,
        ),
        (
            "app.behavior.auto_save",
            "no",
            lambda state: state.behavior.auto_save,
            False,
        ),
    ],
)
def test_apply_setting_property_to_state_accepts_valid_values(
    property_path: str,
    raw_value: Any,
    state_getter: StateGetter,
    expected_value: Any,
) -> None:
    """Validate every supported property path with a valid external value."""
    state = AppState()

    apply_setting_property_to_state(
        state,
        nested_settings(property_path, raw_value),
        property_path,
    )

    assert state_getter(state) == expected_value
    assert state.settings_validation.warnings == []
    assert state.status.current_message is None


@pytest.mark.parametrize(
    ("property_path", "raw_value", "state_getter", "expected_value", "warning"),
    [
        (
            "app.name",
            " ",
            lambda state: state.meta.name,
            APPLICATION_TITLE,
            "Invalid application name in settings.toml.",
        ),
        (
            "app.version",
            " ",
            lambda state: state.meta.version,
            APPLICATION_VERSION,
            "Invalid application version in settings.toml.",
        ),
        (
            "app.window.width",
            399,
            lambda state: state.window.width,
            1024,
            "Invalid window width in settings.toml.",
        ),
        (
            "app.window.height",
            299,
            lambda state: state.window.height,
            720,
            "Invalid window height in settings.toml.",
        ),
        (
            "app.window.monitor",
            -1,
            lambda state: state.window.monitor,
            0,
            "Invalid monitor index in settings.toml.",
        ),
        (
            "app.window.storage_key",
            " ",
            lambda state: state.window.storage_key,
            "nicegui_windows_base_window_state",
            "Invalid window storage key in settings.toml.",
        ),
        (
            "app.ui.theme",
            "invalid",
            lambda state: state.ui.theme,
            "light",
            "Invalid UI theme in settings.toml.",
        ),
        (
            "app.ui.font_scale",
            2.0,
            lambda state: state.ui.font_scale,
            1.0,
            "Invalid UI font scale in settings.toml.",
        ),
        (
            "app.ui.accent_color",
            " ",
            lambda state: state.ui.accent_color,
            "#2563EB",
            "Invalid UI accent color in settings.toml.",
        ),
        (
            "app.log.level",
            "verbose",
            lambda state: state.log.level,
            DEFAULT_LOG_LEVEL,
            "Invalid log level in settings.toml.",
        ),
        (
            "app.log.buffer_capacity",
            0,
            lambda state: state.log.buffer_capacity,
            DEFAULT_BUFFER_CAPACITY,
            "Invalid log buffer capacity in settings.toml.",
        ),
        (
            "app.log.rotate_max_bytes",
            "10 KB",
            lambda state: state.log.rotate_max_bytes,
            "5 MB",
            "Invalid log rotation size in settings.toml.",
        ),
        (
            "app.log.rotate_max_bytes",
            "invalid",
            lambda state: state.log.rotate_max_bytes,
            "5 MB",
            "Invalid log rotation size in settings.toml.",
        ),
        (
            "app.log.rotate_backup_count",
            -1,
            lambda state: state.log.rotate_backup_count,
            DEFAULT_ROTATE_BACKUP_COUNT,
            "Invalid log backup count in settings.toml.",
        ),
    ],
)
def test_apply_setting_property_to_state_uses_fallback_for_invalid_values(
    property_path: str,
    raw_value: Any,
    state_getter: StateGetter,
    expected_value: Any,
    warning: str,
) -> None:
    """Validate fallback values and warning recording for invalid settings."""
    state = AppState()

    apply_setting_property_to_state(
        state,
        nested_settings(property_path, raw_value),
        property_path,
    )

    assert state_getter(state) == expected_value
    assert state.settings_validation.warnings == [warning]
    assert state.status.current_message is not None
    assert state.status.current_message.text == warning
    assert state.status.current_message.level == "warning"
    assert [message.text for message in state.status.history] == [warning]


def test_apply_settings_to_state_applies_selected_group_only() -> None:
    """Validate grouped loading without changing unrelated state groups."""
    state = AppState()
    settings_data = {
        "app": {
            "name": "Ignored App",
            "ui": {
                "theme": "system",
                "font_scale": 1.2,
                "dense_mode": True,
                "accent_color": "#0F172A",
            },
            "window": {"width": 1600},
        }
    }

    apply_settings_to_state(state, settings_data, group="ui")

    assert state.meta.name == APPLICATION_TITLE
    assert state.window.width == 1024
    assert state.ui.theme == "system"
    assert state.ui.font_scale == 1.2
    assert state.ui.dense_mode is True
    assert state.ui.accent_color == "#0F172A"


def test_apply_settings_to_state_applies_selected_property_only() -> None:
    """Validate individual property loading through the public scope function."""
    state = AppState()
    settings_data = {"app": {"name": "Mapped App", "version": "9.9.9"}}

    apply_settings_to_state(state, settings_data, property_path="app.name")

    assert state.meta.name == "Mapped App"
    assert state.meta.version == APPLICATION_VERSION


def test_apply_setting_property_to_state_uses_missing_default() -> None:
    """Validate that missing TOML paths preserve the current state value."""
    state = AppState()
    state.meta.language = "pt-BR"

    apply_setting_property_to_state(state, {}, "app.language")

    assert state.meta.language == "pt-BR"


def test_apply_setting_property_to_state_supports_legacy_console_alias() -> None:
    """Validate backward compatibility with the legacy log console setting."""
    state = AppState()
    settings_data = {"app": {"log": {"console": False}}}

    apply_setting_property_to_state(state, settings_data, "app.log.enable_console")

    assert state.log.enable_console is False


def test_apply_setting_property_to_state_accepts_integer_rotation_size() -> None:
    """Validate integer byte sizes while keeping LogState text-compatible."""
    state = AppState()

    apply_setting_property_to_state(
        state,
        nested_settings("app.log.rotate_max_bytes", 1_048_576),
        "app.log.rotate_max_bytes",
    )

    assert state.log.rotate_max_bytes == "1048576 B"


def test_apply_setting_property_to_state_rejects_unknown_property_path() -> None:
    """Validate direct mapper calls do not silently ignore unknown properties."""
    state = AppState()

    with pytest.raises(SettingsScopeError, match="Unsupported settings property path"):
        apply_setting_property_to_state(state, {}, "app.unknown")


def test_build_logger_config_from_explicit_state() -> None:
    """Validate logger configuration is copied from an explicit state."""
    state = AppState()
    state.log.level = "DEBUG"
    state.log.enable_console = False
    state.log.buffer_capacity = 10
    state.log.file_path = Path("logs/debug.log")
    state.log.rotate_max_bytes = "20 MB"
    state.log.rotate_backup_count = 7

    config = build_logger_config_from_state(state)

    assert config.level == "DEBUG"
    assert config.enable_console is False
    assert config.buffer_capacity == 10
    assert config.file_path == Path("logs/debug.log")
    assert config.rotate_max_bytes == "20 MB"
    assert config.rotate_backup_count == 7


def test_build_logger_config_from_global_state_with_overrides() -> None:
    """Validate global state loading and targeted logger config overrides."""
    state = reset_app_state()
    state.log.file_path = DEFAULT_LOG_FILE_PATH
    state.log.enable_console = True

    config = build_logger_config_from_state(
        file_path=Path("runtime/app.log"),
        enable_console=False,
    )

    assert config.file_path == Path("runtime/app.log")
    assert config.enable_console is False
    assert config.level == state.log.level
