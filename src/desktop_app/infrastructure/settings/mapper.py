# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/mapper.py
# Purpose:
# Map settings.toml data to AppState and LoggerConfig.
# Behavior:
# Reads already parsed TOML values, applies safe conversions and range checks,
# then updates either all application state, one settings group, or one
# individual settings property. It also builds a logger configuration from the
# validated state.
# Notes:
# Handler creation and file logging remain the responsibility of the logger
# package. This module only translates settings data.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from desktop_app.constants import (
    APPLICATION_TITLE,
    APPLICATION_VERSION,
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_ROTATE_BACKUP_COUNT,
    MAX_BUFFER_CAPACITY,
    MAX_ROTATE_BACKUP_COUNT,
    MAX_ROTATE_MAX_BYTES,
    MIN_BUFFER_CAPACITY,
    MIN_ROTATE_BACKUP_COUNT,
    MIN_ROTATE_MAX_BYTES,
)
from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.logger import LoggerConfig
from desktop_app.infrastructure.settings.constants import (
    ALLOWED_LOG_LEVELS,
    ALLOWED_THEMES,
)
from desktop_app.infrastructure.settings.conversion import (
    get_nested_value,
    to_bool,
    to_float,
    to_int,
    to_path,
    try_parse_byte_size,
)
from desktop_app.infrastructure.settings.schema import (
    SettingsGroup,
    get_settings_scope_paths,
)


def apply_settings_to_state(
    state: AppState,
    settings_data: Mapping[str, Any],
    *,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> None:
    """Apply parsed TOML settings to the application state.

    Args:
        state: Application state that receives converted values.
        settings_data: Parsed TOML mapping.
        group: Optional settings group to load.
        property_path: Optional individual property path to load.
    """
    for selected_path in get_settings_scope_paths(
        group=group,
        property_path=property_path,
    ):
        apply_setting_property_to_state(state, settings_data, selected_path)


def apply_setting_property_to_state(
    state: AppState,
    settings_data: Mapping[str, Any],
    property_path: str,
) -> None:
    """Apply one parsed TOML property to the application state.

    Args:
        state: Application state that receives the converted value.
        settings_data: Parsed TOML mapping.
        property_path: Supported property path to load.
    """
    if property_path == "app.name":
        state.meta.name = str(
            _get_setting(settings_data, property_path, state.meta.name)
        ).strip()
        if not state.meta.name:
            state.meta.name = APPLICATION_TITLE
            _record_settings_warning(
                state,
                "Invalid application name in settings.toml.",
            )
        return

    if property_path == "app.version":
        state.meta.version = str(
            _get_setting(settings_data, property_path, state.meta.version)
        ).strip()
        if not state.meta.version:
            state.meta.version = APPLICATION_VERSION
            _record_settings_warning(
                state,
                "Invalid application version in settings.toml.",
            )
        return

    if property_path == "app.language":
        state.meta.language = str(
            _get_setting(settings_data, property_path, state.meta.language)
        ).strip()
        return

    if property_path == "app.first_run":
        state.meta.first_run = to_bool(
            _get_setting(settings_data, property_path, state.meta.first_run),
            state.meta.first_run,
        )
        return

    if property_path == "app.window.x":
        state.window.x = to_int(
            _get_setting(settings_data, property_path, state.window.x),
            state.window.x,
        )
        return

    if property_path == "app.window.y":
        state.window.y = to_int(
            _get_setting(settings_data, property_path, state.window.y),
            state.window.y,
        )
        return

    if property_path == "app.window.width":
        state.window.width = to_int(
            _get_setting(settings_data, property_path, state.window.width),
            state.window.width,
        )
        if state.window.width < 400:
            state.window.width = 1024
            _record_settings_warning(state, "Invalid window width in settings.toml.")
        return

    if property_path == "app.window.height":
        state.window.height = to_int(
            _get_setting(settings_data, property_path, state.window.height),
            state.window.height,
        )
        if state.window.height < 300:
            state.window.height = 720
            _record_settings_warning(state, "Invalid window height in settings.toml.")
        return

    if property_path == "app.window.maximized":
        state.window.maximized = to_bool(
            _get_setting(settings_data, property_path, state.window.maximized),
            state.window.maximized,
        )
        return

    if property_path == "app.window.fullscreen":
        state.window.fullscreen = to_bool(
            _get_setting(settings_data, property_path, state.window.fullscreen),
            state.window.fullscreen,
        )
        return

    if property_path == "app.window.monitor":
        state.window.monitor = to_int(
            _get_setting(settings_data, property_path, state.window.monitor),
            state.window.monitor,
        )
        if state.window.monitor < 0:
            state.window.monitor = 0
            _record_settings_warning(state, "Invalid monitor index in settings.toml.")
        return

    if property_path == "app.window.storage_key":
        state.window.storage_key = str(
            _get_setting(settings_data, property_path, state.window.storage_key)
        ).strip()
        if not state.window.storage_key:
            state.window.storage_key = "nicegui_windows_base_window_state"
            _record_settings_warning(
                state,
                "Invalid window storage key in settings.toml.",
            )
        return

    if property_path == "app.ui.theme":
        state.ui.theme = (
            str(_get_setting(settings_data, property_path, state.ui.theme))
            .strip()
            .lower()
        )
        if state.ui.theme not in ALLOWED_THEMES:
            state.ui.theme = "light"
            _record_settings_warning(state, "Invalid UI theme in settings.toml.")
        return

    if property_path == "app.ui.font_scale":
        state.ui.font_scale = to_float(
            _get_setting(settings_data, property_path, state.ui.font_scale),
            state.ui.font_scale,
        )
        if not 0.75 <= state.ui.font_scale <= 1.5:
            state.ui.font_scale = 1.0
            _record_settings_warning(state, "Invalid UI font scale in settings.toml.")
        return

    if property_path == "app.ui.dense_mode":
        state.ui.dense_mode = to_bool(
            _get_setting(settings_data, property_path, state.ui.dense_mode),
            state.ui.dense_mode,
        )
        return

    if property_path == "app.ui.accent_color":
        state.ui.accent_color = str(
            _get_setting(settings_data, property_path, state.ui.accent_color)
        ).strip()
        if not state.ui.accent_color:
            state.ui.accent_color = "#2563EB"
            _record_settings_warning(state, "Invalid UI accent color in settings.toml.")
        return

    if property_path == "app.log.level":
        state.log.level = (
            str(_get_setting(settings_data, property_path, state.log.level))
            .upper()
            .strip()
        )
        if state.log.level not in ALLOWED_LOG_LEVELS:
            state.log.level = DEFAULT_LOG_LEVEL
            _record_settings_warning(state, "Invalid log level in settings.toml.")
        return

    if property_path == "app.log.enable_console":
        state.log.enable_console = to_bool(
            _get_setting(
                settings_data,
                property_path,
                _get_setting(
                    settings_data,
                    "app.log.console",
                    state.log.enable_console,
                ),
            ),
            state.log.enable_console,
        )
        return

    if property_path == "app.log.buffer_capacity":
        state.log.buffer_capacity = to_int(
            _get_setting(settings_data, property_path, state.log.buffer_capacity),
            state.log.buffer_capacity,
        )
        if not MIN_BUFFER_CAPACITY <= state.log.buffer_capacity <= MAX_BUFFER_CAPACITY:
            state.log.buffer_capacity = DEFAULT_BUFFER_CAPACITY
            _record_settings_warning(
                state,
                "Invalid log buffer capacity in settings.toml.",
            )
        return

    if property_path == "app.log.file_path":
        state.log.file_path = to_path(
            _get_setting(settings_data, property_path, state.log.file_path),
            DEFAULT_LOG_FILE_PATH,
        )
        return

    if property_path == "app.log.rotate_max_bytes":
        state.log.rotate_max_bytes = str(
            _get_setting(settings_data, property_path, state.log.rotate_max_bytes)
        ).strip()
        if not _is_valid_log_rotation(state.log.rotate_max_bytes):
            state.log.rotate_max_bytes = "5 MB"
            _record_settings_warning(
                state,
                "Invalid log rotation size in settings.toml.",
            )
        return

    if property_path == "app.log.rotate_backup_count":
        state.log.rotate_backup_count = to_int(
            _get_setting(settings_data, property_path, state.log.rotate_backup_count),
            state.log.rotate_backup_count,
        )
        if not (
            MIN_ROTATE_BACKUP_COUNT
            <= state.log.rotate_backup_count
            <= MAX_ROTATE_BACKUP_COUNT
        ):
            state.log.rotate_backup_count = DEFAULT_ROTATE_BACKUP_COUNT
            _record_settings_warning(
                state,
                "Invalid log backup count in settings.toml.",
            )
        return

    if property_path == "app.behavior.auto_save":
        state.behavior.auto_save = to_bool(
            _get_setting(settings_data, property_path, state.behavior.auto_save),
            state.behavior.auto_save,
        )


def _record_settings_warning(state: AppState, message: str) -> None:
    """Record a settings validation warning in status and validation state.

    Args:
        state: Application state that receives warning metadata.
        message: Warning message to store.
    """
    state.settings_validation.warnings.append(message)
    state.status.push(message, "warning")


def build_logger_config_from_state(
    state: AppState | None = None,
    *,
    file_path: str | Path | None = None,
    enable_console: bool | None = None,
) -> LoggerConfig:
    """Build LoggerConfig from the application state.

    Args:
        state: Application state used as source. Uses the global state when omitted.
        file_path: Optional resolved log file path override.
        enable_console: Optional console logging override.

    Returns:
        LoggerConfig compatible with the logging package.
    """
    current_state = state if state is not None else get_app_state()

    config = LoggerConfig(
        level=current_state.log.level,
        enable_console=current_state.log.enable_console,
        buffer_capacity=current_state.log.buffer_capacity,
        file_path=current_state.log.file_path,
        rotate_max_bytes=current_state.log.rotate_max_bytes,
        rotate_backup_count=current_state.log.rotate_backup_count,
    )

    if file_path is not None:
        config = replace(config, file_path=file_path)

    if enable_console is not None:
        config = replace(config, enable_console=enable_console)

    return config


def _get_setting(
    settings_data: Mapping[str, Any],
    property_path: str,
    default: Any,
) -> Any:
    """Return one parsed TOML setting value.

    Args:
        settings_data: Parsed TOML mapping.
        property_path: Dotted settings path.
        default: Fallback value.

    Returns:
        Parsed value or fallback.
    """
    return get_nested_value(settings_data, property_path, default)


def _is_valid_log_rotation(value: int | str) -> bool:
    """Return whether a log rotation size is accepted.

    Args:
        value: Size in bytes or text format.

    Returns:
        True when the value is inside the allowed logger rotation range.
    """
    size_in_bytes = try_parse_byte_size(value)

    if size_in_bytes is None:
        return False

    return MIN_ROTATE_MAX_BYTES <= size_in_bytes <= MAX_ROTATE_MAX_BYTES
