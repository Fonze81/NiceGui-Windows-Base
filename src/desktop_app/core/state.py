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
# NiceGUI UI. Settings persistence belongs to infrastructure/settings. NiceGUI
# binding is intentionally kept outside this module so core state remains a
# plain Python data model.
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

type StatusLevel = Literal["info", "success", "warning", "error"]
type ThemeName = Literal["light", "dark", "system"]


def _create_warning_list() -> list[str]:
    """Create a typed list for settings validation warnings.

    Returns:
        Empty warning list.
    """
    return []


def _create_status_history() -> list[StatusMessage]:
    """Create a typed list for status message history.

    Returns:
        Empty status history list.
    """
    return []


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
        startup_message: Startup message shared by terminal, logs, and UI.
        native_mode: Whether the current process runs in NiceGUI native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.
        port: HTTP port selected for the current NiceGUI runtime.
    """

    startup_source: str | None = None
    startup_message: str | None = None
    native_mode: bool = True
    reload_enabled: bool = False
    port: int = DEFAULT_WEB_PORT


@dataclass(slots=True)
class RuntimePathsState:
    """Store effective runtime paths resolved during startup.

    Attributes:
        settings_file_path: Effective settings.toml path used by this process.
        log_file_path: Effective log file path used by this process.
        executable_path: Python executable or packaged executable path.
        working_directory: Current working directory during startup.
        pyinstaller_temp_dir: PyInstaller extraction directory when available.
    """

    settings_file_path: Path | None = None
    log_file_path: Path | None = None
    executable_path: Path | None = None
    working_directory: Path | None = None
    pyinstaller_temp_dir: Path | None = None


@dataclass(slots=True)
class WindowState:
    """Store persisted and runtime native window preferences.

    Attributes:
        x: Preferred horizontal window position.
        y: Preferred vertical window position.
        width: Preferred window width.
        height: Preferred window height.
        maximized: Whether the window should start maximized.
        fullscreen: Whether the window should start in fullscreen mode.
        monitor: Preferred monitor index.
        persist_state: Whether native window geometry should be saved on exit.
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
    persist_state: bool = True
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
class UiSessionState:
    """Store transient UI session values.

    Attributes:
        active_view: Logical view currently displayed by the application.
        is_busy: Whether the UI is performing a blocking or long-running action.
        busy_message: Optional user-facing message for the active busy state.
        last_page_built_at: Last time the SPA shell was built for a client.
        last_interaction_at: Last time a UI interaction updated the session state.
    """

    active_view: str = "home"
    is_busy: bool = False
    busy_message: str | None = None
    last_page_built_at: datetime | None = None
    last_interaction_at: datetime | None = None


@dataclass(slots=True)
class AssetState:
    """Store resolved asset paths used by the current runtime.

    Attributes:
        icon_path: Application icon path passed to NiceGUI.
        page_image_path: Image path shown in the index page.
        splash_image_path: Splash image path used by the packaged executable.
    """

    icon_path: Path | None = None
    page_image_path: Path | None = None
    splash_image_path: Path | None = None


@dataclass(slots=True)
class LogState:
    """Store configurable logging preferences and runtime status.

    Attributes:
        level: Minimum log level name.
        enable_console: Whether logs should also be emitted to the console.
        buffer_capacity: Maximum early records kept before file logging is active.
        file_path: Relative or absolute log file path configured by settings.
        rotate_max_bytes: Maximum log file size before rotation.
        rotate_backup_count: Number of rotated log files to keep.
        file_logging_enabled: Whether file logging was enabled during startup.
        early_buffering_enabled: Whether early memory buffering is still expected.
        effective_file_path: Resolved runtime log file path.
    """

    level: str = DEFAULT_LOG_LEVEL
    enable_console: bool = True
    buffer_capacity: int = DEFAULT_BUFFER_CAPACITY
    file_path: Path = DEFAULT_LOG_FILE_PATH
    rotate_max_bytes: str = "5 MB"
    rotate_backup_count: int = DEFAULT_ROTATE_BACKUP_COUNT
    file_logging_enabled: bool = False
    early_buffering_enabled: bool = True
    effective_file_path: Path | None = None


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
        file_exists: Whether settings.toml existed during the latest load/save.
        using_defaults: Whether the state currently relies on in-memory defaults.
        last_loaded_scope: Latest settings scope loaded successfully.
        last_saved_scope: Latest settings scope saved successfully.
        last_load_ok: Whether the latest load attempt completed successfully.
        last_save_ok: Whether the latest save attempt completed successfully.
        last_error: Last settings-related error message, when available.
    """

    file_path: Path | None = None
    file_exists: bool = False
    using_defaults: bool = True
    last_loaded_scope: str | None = None
    last_saved_scope: str | None = None
    last_load_ok: bool = False
    last_save_ok: bool = False
    last_error: str | None = None


@dataclass(slots=True)
class SettingsValidationState:
    """Store latest settings validation warnings.

    Attributes:
        warnings: Warning messages from the latest settings load operation.
        last_validated_scope: Settings scope validated most recently.
        last_validated_at: Timestamp of the latest validation attempt.
    """

    warnings: list[str] = field(default_factory=_create_warning_list)
    last_validated_scope: str | None = None
    last_validated_at: datetime | None = None


@dataclass(slots=True)
class LifecycleState:
    """Store high-level application lifecycle status.

    Attributes:
        handlers_registered: Whether generic lifecycle handlers were registered.
        native_handlers_registered: Whether native window handlers were registered.
        runtime_started: Whether NiceGUI startup event was received.
        client_connected: Whether at least one client is currently connected.
        native_window_opened: Whether the native window was shown.
        native_window_loaded: Whether the native window finished loading.
        native_window_minimized: Whether the native window is currently minimized.
        native_window_maximized: Whether the native window is currently maximized.
        native_window_closed: Whether the native window was closed.
        native_window_state_persisted: Whether native window state was saved on exit.
        splash_registered: Whether a splash close handler was registered.
        splash_close_attempted: Whether closing the splash was attempted.
        splash_closed: Whether the splash screen was closed successfully.
        shutdown_started: Whether application shutdown handling started.
        shutdown_completed: Whether application shutdown handling completed.
    """

    handlers_registered: bool = False
    native_handlers_registered: bool = False
    runtime_started: bool = False
    client_connected: bool = False
    native_window_opened: bool = False
    native_window_loaded: bool = False
    native_window_minimized: bool = False
    native_window_maximized: bool = False
    native_window_closed: bool = False
    native_window_state_persisted: bool = False
    splash_registered: bool = False
    splash_close_attempted: bool = False
    splash_closed: bool = False
    shutdown_started: bool = False
    shutdown_completed: bool = False


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
    history: list[StatusMessage] = field(default_factory=_create_status_history)
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
        self._trim_history()
        return message

    def clear(self) -> None:
        """Clear the current status message while preserving history."""
        self.current_message = None

    def _trim_history(self) -> None:
        """Limit retained status messages to the configured capacity."""
        if self.max_history <= 0:
            self.history.clear()
            return

        if len(self.history) > self.max_history:
            del self.history[: -self.max_history]


@dataclass(slots=True)
class AppState:
    """Represent the central mutable application state.

    Attributes:
        meta: User-facing application metadata.
        runtime: Values resolved for the current process.
        paths: Effective runtime paths resolved during startup.
        window: Window size and position preferences.
        ui: Visual interface preferences.
        ui_session: Transient UI session state.
        assets: Resolved asset paths for diagnostics.
        log: Logging preferences and runtime status.
        behavior: General behavior preferences.
        settings: Settings file runtime metadata.
        settings_validation: Latest settings validation warnings.
        lifecycle: High-level application lifecycle status.
        status: Current and recent application messages.
    """

    meta: AppMetaState = field(default_factory=AppMetaState)
    runtime: RuntimeState = field(default_factory=RuntimeState)
    paths: RuntimePathsState = field(default_factory=RuntimePathsState)
    window: WindowState = field(default_factory=WindowState)
    ui: UiState = field(default_factory=UiState)
    ui_session: UiSessionState = field(default_factory=UiSessionState)
    assets: AssetState = field(default_factory=AssetState)
    log: LogState = field(default_factory=LogState)
    behavior: BehaviorState = field(default_factory=BehaviorState)
    settings: SettingsState = field(default_factory=SettingsState)
    settings_validation: SettingsValidationState = field(
        default_factory=SettingsValidationState
    )
    lifecycle: LifecycleState = field(default_factory=LifecycleState)
    status: StatusState = field(default_factory=StatusState)


_app_state: AppState | None = None


def get_app_state() -> AppState:
    """Return the process-wide application state instance.

    Returns:
        Shared AppState instance for the current process.
    """
    global _app_state

    if _app_state is None:
        _app_state = AppState()

    return _app_state


def set_app_state(state: AppState) -> None:
    """Replace the process-wide application state instance.

    Args:
        state: New AppState instance.
    """
    global _app_state

    _app_state = state


def reset_app_state() -> AppState:
    """Reset the process-wide state to default values.

    Returns:
        Newly created default AppState instance.
    """
    global _app_state

    _app_state = AppState()
    return _app_state
