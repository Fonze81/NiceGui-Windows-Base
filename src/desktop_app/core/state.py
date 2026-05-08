# -----------------------------------------------------------------------------
# File: src/desktop_app/core/state.py
# Purpose:
# Define the application runtime state model.
# Behavior:
# Groups mutable application state into focused dataclasses and exposes a small
# controlled singleton API for modules that need access to the current process
# state.
# Notes:
# This module must not read files, write files, configure logging, or access the
# NiceGUI UI. Settings persistence belongs to infrastructure/settings.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from desktop_app.constants import (
    APPLICATION_TITLE,
    APPLICATION_VERSION,
    DEFAULT_BUFFER_CAPACITY,
    DEFAULT_LOG_FILE_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_ROTATE_BACKUP_COUNT,
    DEFAULT_WEB_PORT,
)

StatusLevel = Literal["info", "success", "warning", "error"]
ThemeName = Literal["light", "dark", "system"]


@dataclass(slots=True)
class AppMetaState:
    """Store user-facing application metadata and preferences.

    Attributes:
        name: Human-readable application name.
        version: Informational application version.
        language: Default interface language.
        first_run: Whether the persisted settings still represent first-run state.
    """

    name: str = APPLICATION_TITLE
    version: str = APPLICATION_VERSION
    language: str = "en-US"
    first_run: bool = True


@dataclass(slots=True)
class RuntimeState:
    """Store values resolved for the current process execution.

    Attributes:
        startup_source: Resolved startup source, such as package or module.
        native_mode: Whether the current process runs in NiceGUI native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.
        port: HTTP port selected for the current NiceGUI runtime.
    """

    startup_source: str | None = None
    native_mode: bool = True
    reload_enabled: bool = False
    port: int = DEFAULT_WEB_PORT


@dataclass(slots=True)
class WindowState:
    """Store future native window size and position preferences.

    Attributes:
        x: Preferred horizontal window position.
        y: Preferred vertical window position.
        width: Preferred window width.
        height: Preferred window height.
        maximized: Whether the window should start maximized.
        fullscreen: Whether the window should start in fullscreen mode.
        monitor: Preferred monitor index.
        storage_key: Key reserved for future local UI persistence.
        last_saved_at: Last time the window state was persisted.
    """

    x: int = 100
    y: int = 100
    width: int = 1024
    height: int = 720
    maximized: bool = False
    fullscreen: bool = False
    monitor: int = 0
    storage_key: str = "nicegui_windows_base_window_state"
    last_saved_at: datetime | None = None


@dataclass(slots=True)
class UiState:
    """Store visual interface preferences.

    Attributes:
        theme: Preferred visual theme.
        font_scale: Global font scale multiplier.
        dense_mode: Whether compact spacing should be preferred.
        accent_color: Main interface accent color.
    """

    theme: ThemeName = "light"
    font_scale: float = 1.0
    dense_mode: bool = False
    accent_color: str = "#2563EB"


@dataclass(slots=True)
class LogState:
    """Store configurable logging preferences and runtime status.

    Attributes:
        level: Minimum log level name.
        enable_console: Whether logs should also be emitted to the console.
        buffer_capacity: Maximum early records kept before file logging is active.
        file_path: Relative or absolute log file path.
        rotate_max_bytes: Maximum log file size before rotation.
        rotate_backup_count: Number of rotated log files to keep.
        file_logging_enabled: Whether file logging was enabled during startup.
    """

    level: str = DEFAULT_LOG_LEVEL
    enable_console: bool = True
    buffer_capacity: int = DEFAULT_BUFFER_CAPACITY
    file_path: Path = DEFAULT_LOG_FILE_PATH
    rotate_max_bytes: str = "5 MB"
    rotate_backup_count: int = DEFAULT_ROTATE_BACKUP_COUNT
    file_logging_enabled: bool = False


@dataclass(slots=True)
class BehaviorState:
    """Store general application behavior preferences.

    Attributes:
        auto_save: Whether state changes should be persisted automatically.
    """

    auto_save: bool = True


@dataclass(slots=True)
class SettingsState:
    """Store settings file runtime metadata.

    Attributes:
        file_path: Effective settings file path used by the application.
        last_load_ok: Whether the latest load attempt completed successfully.
        last_save_ok: Whether the latest save attempt completed successfully.
        last_error: Last settings-related error message, when available.
    """

    file_path: Path | None = None
    last_load_ok: bool = False
    last_save_ok: bool = False
    last_error: str | None = None


@dataclass(slots=True)
class StatusMessage:
    """Represent one application status message.

    Attributes:
        text: User-facing status text.
        level: Visual severity level.
        created_at: Message creation timestamp.
    """

    text: str
    level: StatusLevel = "info"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class StatusState:
    """Store current and recent status messages.

    Attributes:
        current_message: Message currently relevant to the UI.
        history: Recent messages kept for diagnostics or a future status area.
        max_history: Maximum number of messages retained in memory.
    """

    current_message: StatusMessage | None = None
    history: list[StatusMessage] = field(default_factory=list)
    max_history: int = 50

    def push(self, text: str, level: StatusLevel = "info") -> StatusMessage:
        """Create and store a status message.

        Args:
            text: User-facing status text.
            level: Visual severity level.

        Returns:
            Created status message.
        """
        message = StatusMessage(text=text, level=level)
        self.current_message = message
        self.history.append(message)

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        return message

    def clear(self) -> None:
        """Clear the current status message while preserving history."""
        self.current_message = None


@dataclass(slots=True)
class AppState:
    """Represent the central mutable application state.

    Attributes:
        meta: User-facing application metadata.
        runtime: Values resolved for the current process.
        window: Window size and position preferences.
        ui: Visual interface preferences.
        log: Logging preferences and runtime status.
        behavior: General behavior preferences.
        settings: Settings file runtime metadata.
        status: Current and recent application messages.
    """

    meta: AppMetaState = field(default_factory=AppMetaState)
    runtime: RuntimeState = field(default_factory=RuntimeState)
    window: WindowState = field(default_factory=WindowState)
    ui: UiState = field(default_factory=UiState)
    log: LogState = field(default_factory=LogState)
    behavior: BehaviorState = field(default_factory=BehaviorState)
    settings: SettingsState = field(default_factory=SettingsState)
    status: StatusState = field(default_factory=StatusState)


_APP_STATE: AppState | None = None


def get_app_state() -> AppState:
    """Return the process-wide application state instance.

    Returns:
        Shared AppState instance for the current process.
    """
    global _APP_STATE

    if _APP_STATE is None:
        _APP_STATE = AppState()

    return _APP_STATE


def set_app_state(state: AppState) -> None:
    """Replace the process-wide application state instance.

    Args:
        state: New AppState instance.
    """
    global _APP_STATE

    _APP_STATE = state


def reset_app_state() -> AppState:
    """Reset the process-wide state to default values.

    Returns:
        Newly created default AppState instance.
    """
    global _APP_STATE

    _APP_STATE = AppState()
    return _APP_STATE
