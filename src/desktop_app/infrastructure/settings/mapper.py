# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/mapper.py
# Purpose:
# Map settings.toml data to AppState and LoggerConfig.
# Behavior:
# Reads already parsed TOML values, applies safe conversions and range checks,
# then updates the application state. It also builds a logger configuration from
# the validated state.
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


def apply_settings_to_state(
    state: AppState,
    settings_data: Mapping[str, Any],
) -> None:
    """Apply parsed TOML settings to the application state.

    Args:
        state: Application state that receives converted values.
        settings_data: Parsed TOML mapping.
    """

    def get_setting(path: str, default: Any) -> Any:
        return get_nested_value(settings_data, path, default)

    state.meta.name = str(get_setting("app.name", state.meta.name)).strip()
    state.meta.version = str(get_setting("app.version", state.meta.version)).strip()
    state.meta.language = str(get_setting("app.language", state.meta.language)).strip()
    state.meta.first_run = to_bool(
        get_setting("app.first_run", state.meta.first_run),
        state.meta.first_run,
    )

    if not state.meta.name:
        state.meta.name = APPLICATION_TITLE
        state.status.push("Invalid application name in settings.toml.", "warning")

    if not state.meta.version:
        state.meta.version = APPLICATION_VERSION
        state.status.push("Invalid application version in settings.toml.", "warning")

    state.window.x = to_int(get_setting("app.window.x", state.window.x), state.window.x)
    state.window.y = to_int(get_setting("app.window.y", state.window.y), state.window.y)
    state.window.width = to_int(
        get_setting("app.window.width", state.window.width),
        state.window.width,
    )
    state.window.height = to_int(
        get_setting("app.window.height", state.window.height),
        state.window.height,
    )
    state.window.maximized = to_bool(
        get_setting("app.window.maximized", state.window.maximized),
        state.window.maximized,
    )
    state.window.fullscreen = to_bool(
        get_setting("app.window.fullscreen", state.window.fullscreen),
        state.window.fullscreen,
    )
    state.window.monitor = to_int(
        get_setting("app.window.monitor", state.window.monitor),
        state.window.monitor,
    )
    state.window.storage_key = str(
        get_setting("app.window.storage_key", state.window.storage_key)
    ).strip()

    if state.window.width < 400:
        state.window.width = 1024
        state.status.push("Invalid window width in settings.toml.", "warning")

    if state.window.height < 300:
        state.window.height = 720
        state.status.push("Invalid window height in settings.toml.", "warning")

    if state.window.monitor < 0:
        state.window.monitor = 0
        state.status.push("Invalid monitor index in settings.toml.", "warning")

    if not state.window.storage_key:
        state.window.storage_key = "nicegui_windows_base_window_state"
        state.status.push("Invalid window storage key in settings.toml.", "warning")

    state.ui.theme = str(get_setting("app.ui.theme", state.ui.theme)).strip().lower()
    state.ui.font_scale = to_float(
        get_setting("app.ui.font_scale", state.ui.font_scale),
        state.ui.font_scale,
    )
    state.ui.dense_mode = to_bool(
        get_setting("app.ui.dense_mode", state.ui.dense_mode),
        state.ui.dense_mode,
    )
    state.ui.accent_color = str(
        get_setting("app.ui.accent_color", state.ui.accent_color)
    ).strip()

    if state.ui.theme not in ALLOWED_THEMES:
        state.ui.theme = "light"
        state.status.push("Invalid UI theme in settings.toml.", "warning")

    if not 0.75 <= state.ui.font_scale <= 1.5:
        state.ui.font_scale = 1.0
        state.status.push("Invalid UI font scale in settings.toml.", "warning")

    if not state.ui.accent_color:
        state.ui.accent_color = "#2563EB"
        state.status.push("Invalid UI accent color in settings.toml.", "warning")

    state.log.level = str(get_setting("app.log.level", state.log.level)).upper().strip()
    state.log.enable_console = to_bool(
        get_setting(
            "app.log.enable_console",
            get_setting("app.log.console", state.log.enable_console),
        ),
        state.log.enable_console,
    )
    state.log.buffer_capacity = to_int(
        get_setting("app.log.buffer_capacity", state.log.buffer_capacity),
        state.log.buffer_capacity,
    )
    state.log.file_path = to_path(
        get_setting("app.log.file_path", state.log.file_path),
        DEFAULT_LOG_FILE_PATH,
    )
    state.log.rotate_max_bytes = str(
        get_setting("app.log.rotate_max_bytes", state.log.rotate_max_bytes)
    ).strip()
    state.log.rotate_backup_count = to_int(
        get_setting("app.log.rotate_backup_count", state.log.rotate_backup_count),
        state.log.rotate_backup_count,
    )

    if state.log.level not in ALLOWED_LOG_LEVELS:
        state.log.level = DEFAULT_LOG_LEVEL
        state.status.push("Invalid log level in settings.toml.", "warning")

    if not MIN_BUFFER_CAPACITY <= state.log.buffer_capacity <= MAX_BUFFER_CAPACITY:
        state.log.buffer_capacity = DEFAULT_BUFFER_CAPACITY
        state.status.push("Invalid log buffer capacity in settings.toml.", "warning")

    if not _is_valid_log_rotation(state.log.rotate_max_bytes):
        state.log.rotate_max_bytes = "5 MB"
        state.status.push("Invalid log rotation size in settings.toml.", "warning")

    if not (
        MIN_ROTATE_BACKUP_COUNT
        <= state.log.rotate_backup_count
        <= MAX_ROTATE_BACKUP_COUNT
    ):
        state.log.rotate_backup_count = DEFAULT_ROTATE_BACKUP_COUNT
        state.status.push("Invalid log backup count in settings.toml.", "warning")

    state.behavior.auto_save = to_bool(
        get_setting("app.behavior.auto_save", state.behavior.auto_save),
        state.behavior.auto_save,
    )


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
