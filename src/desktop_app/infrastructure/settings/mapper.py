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
# package. This module only translates settings data and records validation
# warnings in AppState without touching the UI or the file system.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

from desktop_app.constants import (
    ALLOWED_LOG_LEVELS,
    ALLOWED_THEMES,
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
from desktop_app.core.state import AppState, ThemeName, get_app_state
from desktop_app.infrastructure.logger import LoggerConfig
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
    SettingsScopeError,
    get_settings_scope_paths,
)

type SettingsData = Mapping[str, Any]
type PropertyApplier = Callable[[AppState, SettingsData, str], None]

_MIN_WINDOW_WIDTH = 400
_MIN_WINDOW_HEIGHT = 300
_DEFAULT_WINDOW_WIDTH = 1024
_DEFAULT_WINDOW_HEIGHT = 720
_DEFAULT_WINDOW_MONITOR = 0
_DEFAULT_WINDOW_STORAGE_KEY = "nicegui_windows_base_window_state"
_DEFAULT_THEME = "light"
_DEFAULT_FONT_SCALE = 1.0
_DEFAULT_ACCENT_COLOR = "#2563EB"
_DEFAULT_ROTATE_MAX_BYTES_TEXT = "5 MB"


def apply_settings_to_state(
    state: AppState,
    settings_data: SettingsData,
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

    Raises:
        SettingsScopeError: If the requested group or property path is not
            supported by the settings schema.
    """
    for selected_path in get_settings_scope_paths(
        group=group,
        property_path=property_path,
    ):
        apply_setting_property_to_state(state, settings_data, selected_path)


def apply_setting_property_to_state(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    """Apply one parsed TOML property to the application state.

    Args:
        state: Application state that receives the converted value.
        settings_data: Parsed TOML mapping.
        property_path: Supported property path to load.

    Raises:
        SettingsScopeError: If the property path is not handled by this mapper.
    """
    try:
        property_applier = _PROPERTY_APPLIERS[property_path]
    except KeyError as exc:
        raise SettingsScopeError(
            f"Unsupported settings property path: {property_path!r}."
        ) from exc

    property_applier(state, settings_data, property_path)


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


def _apply_app_name(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.meta.name = _get_stripped_string(
        settings_data,
        property_path,
        state.meta.name,
    )

    if not state.meta.name:
        state.meta.name = APPLICATION_TITLE
        _record_settings_warning(state, "Invalid application name in settings.toml.")


def _apply_app_version(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.meta.version = _get_stripped_string(
        settings_data,
        property_path,
        state.meta.version,
    )

    if not state.meta.version:
        state.meta.version = APPLICATION_VERSION
        _record_settings_warning(state, "Invalid application version in settings.toml.")


def _apply_app_language(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.meta.language = _get_stripped_string(
        settings_data,
        property_path,
        state.meta.language,
    )


def _apply_app_first_run(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.meta.first_run = to_bool(
        _get_setting(settings_data, property_path, state.meta.first_run),
        state.meta.first_run,
    )


def _apply_window_x(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.x = to_int(
        _get_setting(settings_data, property_path, state.window.x),
        state.window.x,
    )


def _apply_window_y(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.y = to_int(
        _get_setting(settings_data, property_path, state.window.y),
        state.window.y,
    )


def _apply_window_width(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.width = to_int(
        _get_setting(settings_data, property_path, state.window.width),
        state.window.width,
    )

    if state.window.width < _MIN_WINDOW_WIDTH:
        state.window.width = _DEFAULT_WINDOW_WIDTH
        _record_settings_warning(state, "Invalid window width in settings.toml.")


def _apply_window_height(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.height = to_int(
        _get_setting(settings_data, property_path, state.window.height),
        state.window.height,
    )

    if state.window.height < _MIN_WINDOW_HEIGHT:
        state.window.height = _DEFAULT_WINDOW_HEIGHT
        _record_settings_warning(state, "Invalid window height in settings.toml.")


def _apply_window_maximized(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.maximized = to_bool(
        _get_setting(settings_data, property_path, state.window.maximized),
        state.window.maximized,
    )


def _apply_window_fullscreen(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.fullscreen = to_bool(
        _get_setting(settings_data, property_path, state.window.fullscreen),
        state.window.fullscreen,
    )


def _apply_window_monitor(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.monitor = to_int(
        _get_setting(settings_data, property_path, state.window.monitor),
        state.window.monitor,
    )

    if state.window.monitor < 0:
        state.window.monitor = _DEFAULT_WINDOW_MONITOR
        _record_settings_warning(state, "Invalid monitor index in settings.toml.")


def _apply_window_persist_state(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.persist_state = to_bool(
        _get_setting(settings_data, property_path, state.window.persist_state),
        state.window.persist_state,
    )


def _apply_window_storage_key(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.window.storage_key = _get_stripped_string(
        settings_data,
        property_path,
        state.window.storage_key,
    )

    if not state.window.storage_key:
        state.window.storage_key = _DEFAULT_WINDOW_STORAGE_KEY
        _record_settings_warning(state, "Invalid window storage key in settings.toml.")


def _apply_ui_theme(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    theme = _get_stripped_string(
        settings_data,
        property_path,
        state.ui.theme,
    ).lower()

    if theme not in ALLOWED_THEMES:
        state.ui.theme = "light"
        _record_settings_warning(state, "Invalid UI theme in settings.toml.")
        return

    state.ui.theme = cast(ThemeName, theme)


def _apply_ui_font_scale(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.ui.font_scale = to_float(
        _get_setting(settings_data, property_path, state.ui.font_scale),
        state.ui.font_scale,
    )

    if not 0.75 <= state.ui.font_scale <= 1.5:
        state.ui.font_scale = _DEFAULT_FONT_SCALE
        _record_settings_warning(state, "Invalid UI font scale in settings.toml.")


def _apply_ui_dense_mode(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.ui.dense_mode = to_bool(
        _get_setting(settings_data, property_path, state.ui.dense_mode),
        state.ui.dense_mode,
    )


def _apply_ui_accent_color(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.ui.accent_color = _get_stripped_string(
        settings_data,
        property_path,
        state.ui.accent_color,
    )

    if not state.ui.accent_color:
        state.ui.accent_color = _DEFAULT_ACCENT_COLOR
        _record_settings_warning(state, "Invalid UI accent color in settings.toml.")


def _apply_log_level(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.log.level = _get_stripped_string(
        settings_data,
        property_path,
        state.log.level,
    ).upper()

    if state.log.level not in ALLOWED_LOG_LEVELS:
        state.log.level = DEFAULT_LOG_LEVEL
        _record_settings_warning(state, "Invalid log level in settings.toml.")


def _apply_log_enable_console(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    legacy_console_value = _get_setting(
        settings_data,
        "app.log.console",
        state.log.enable_console,
    )
    state.log.enable_console = to_bool(
        _get_setting(settings_data, property_path, legacy_console_value),
        state.log.enable_console,
    )


def _apply_log_buffer_capacity(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.log.buffer_capacity = to_int(
        _get_setting(settings_data, property_path, state.log.buffer_capacity),
        state.log.buffer_capacity,
    )

    if not MIN_BUFFER_CAPACITY <= state.log.buffer_capacity <= MAX_BUFFER_CAPACITY:
        state.log.buffer_capacity = DEFAULT_BUFFER_CAPACITY
        _record_settings_warning(state, "Invalid log buffer capacity in settings.toml.")


def _apply_log_file_path(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    state.log.file_path = to_path(
        _get_setting(settings_data, property_path, state.log.file_path),
        DEFAULT_LOG_FILE_PATH,
    )


def _apply_log_rotate_max_bytes(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
    raw_value = _get_setting(settings_data, property_path, state.log.rotate_max_bytes)

    if not _is_valid_log_rotation(raw_value):
        state.log.rotate_max_bytes = _DEFAULT_ROTATE_MAX_BYTES_TEXT
        _record_settings_warning(state, "Invalid log rotation size in settings.toml.")
        return

    state.log.rotate_max_bytes = _format_rotate_max_bytes(raw_value)


def _apply_log_rotate_backup_count(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
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
        _record_settings_warning(state, "Invalid log backup count in settings.toml.")


def _apply_behavior_auto_save(
    state: AppState,
    settings_data: SettingsData,
    property_path: str,
) -> None:
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


def _get_setting(
    settings_data: SettingsData,
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


def _get_stripped_string(
    settings_data: SettingsData,
    property_path: str,
    default: str,
) -> str:
    """Return a setting converted to a stripped string.

    Args:
        settings_data: Parsed TOML mapping.
        property_path: Dotted settings path.
        default: Fallback value.

    Returns:
        Stripped string representation of the parsed value or fallback.
    """
    return str(_get_setting(settings_data, property_path, default)).strip()


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


def _format_rotate_max_bytes(value: int | str) -> str:
    """Return a logger rotation size that remains compatible with LogState.

    Args:
        value: Validated size as integer bytes or text format.

    Returns:
        Text value accepted by the logger byte-size parser.
    """
    if isinstance(value, int):
        return f"{value} B"

    return value.strip()


_PROPERTY_APPLIERS: dict[str, PropertyApplier] = {
    "app.name": _apply_app_name,
    "app.version": _apply_app_version,
    "app.language": _apply_app_language,
    "app.first_run": _apply_app_first_run,
    "app.window.x": _apply_window_x,
    "app.window.y": _apply_window_y,
    "app.window.width": _apply_window_width,
    "app.window.height": _apply_window_height,
    "app.window.maximized": _apply_window_maximized,
    "app.window.fullscreen": _apply_window_fullscreen,
    "app.window.monitor": _apply_window_monitor,
    "app.window.persist_state": _apply_window_persist_state,
    "app.window.storage_key": _apply_window_storage_key,
    "app.ui.theme": _apply_ui_theme,
    "app.ui.font_scale": _apply_ui_font_scale,
    "app.ui.dense_mode": _apply_ui_dense_mode,
    "app.ui.accent_color": _apply_ui_accent_color,
    "app.log.level": _apply_log_level,
    "app.log.enable_console": _apply_log_enable_console,
    "app.log.buffer_capacity": _apply_log_buffer_capacity,
    "app.log.file_path": _apply_log_file_path,
    "app.log.rotate_max_bytes": _apply_log_rotate_max_bytes,
    "app.log.rotate_backup_count": _apply_log_rotate_backup_count,
    "app.behavior.auto_save": _apply_behavior_auto_save,
}
