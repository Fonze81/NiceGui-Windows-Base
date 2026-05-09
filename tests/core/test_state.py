# -----------------------------------------------------------------------------
# File: tests/core/test_state.py
# Purpose:
# Validate the application runtime state model.
# Behavior:
# Exercises dataclass defaults, status message history handling, and the
# controlled process-wide AppState singleton API.
# Notes:
# The tests reset the singleton before and after each case so no test leaks
# mutable process state into another test.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from desktop_app import constants
from desktop_app.core import state as state_module
from desktop_app.core.state import (
    AppState,
    StatusMessage,
    StatusState,
    get_app_state,
    reset_app_state,
    set_app_state,
)


@pytest.fixture(autouse=True)
def reset_state_singleton() -> Iterator[None]:
    """Reset the process-wide application state around every test."""
    reset_app_state()
    yield
    reset_app_state()


def test_app_state_builds_expected_default_groups() -> None:
    """Create an AppState with all default nested state groups."""
    app_state = AppState()

    assert app_state.meta.name == constants.APPLICATION_TITLE
    assert app_state.meta.version == constants.APPLICATION_VERSION
    assert app_state.meta.language == "en-US"
    assert app_state.meta.first_run is True

    assert app_state.runtime.startup_source is None
    assert app_state.runtime.startup_message is None
    assert app_state.runtime.native_mode is True
    assert app_state.runtime.reload_enabled is False
    assert app_state.runtime.port == constants.DEFAULT_WEB_PORT

    assert app_state.paths.settings_file_path is None
    assert app_state.paths.log_file_path is None
    assert app_state.paths.executable_path is None
    assert app_state.paths.working_directory is None
    assert app_state.paths.pyinstaller_temp_dir is None

    assert app_state.window.x == 100
    assert app_state.window.y == 100
    assert app_state.window.width == 1024
    assert app_state.window.height == 720
    assert app_state.window.maximized is False
    assert app_state.window.fullscreen is False
    assert app_state.window.monitor == 0
    assert app_state.window.storage_key == "nicegui_windows_base_window_state"
    assert app_state.window.last_saved_at is None

    assert app_state.ui.theme == "light"
    assert app_state.ui.font_scale == 1.0
    assert app_state.ui.dense_mode is False
    assert app_state.ui.accent_color == "#2563EB"

    assert app_state.ui_session.active_view == "home"
    assert app_state.ui_session.is_busy is False
    assert app_state.ui_session.busy_message is None
    assert app_state.ui_session.last_page_built_at is None
    assert app_state.ui_session.last_interaction_at is None

    assert app_state.assets.icon_path is None
    assert app_state.assets.page_image_path is None
    assert app_state.assets.splash_image_path is None

    assert app_state.log.level == constants.DEFAULT_LOG_LEVEL
    assert app_state.log.enable_console is True
    assert app_state.log.buffer_capacity == constants.DEFAULT_BUFFER_CAPACITY
    assert app_state.log.file_path == constants.DEFAULT_LOG_FILE_PATH
    assert app_state.log.rotate_max_bytes == "5 MB"
    assert app_state.log.rotate_backup_count == constants.DEFAULT_ROTATE_BACKUP_COUNT
    assert app_state.log.file_logging_enabled is False
    assert app_state.log.early_buffering_enabled is True
    assert app_state.log.effective_file_path is None

    assert app_state.behavior.auto_save is True

    assert app_state.settings.file_path is None
    assert app_state.settings.file_exists is False
    assert app_state.settings.using_defaults is True
    assert app_state.settings.last_loaded_scope is None
    assert app_state.settings.last_saved_scope is None
    assert app_state.settings.last_load_ok is False
    assert app_state.settings.last_save_ok is False
    assert app_state.settings.last_error is None

    assert app_state.settings_validation.warnings == []
    assert app_state.settings_validation.last_validated_scope is None
    assert app_state.settings_validation.last_validated_at is None

    assert app_state.lifecycle.handlers_registered is False
    assert app_state.lifecycle.native_handlers_registered is False
    assert app_state.lifecycle.runtime_started is False
    assert app_state.lifecycle.client_connected is False
    assert app_state.lifecycle.native_window_opened is False
    assert app_state.lifecycle.native_window_loaded is False
    assert app_state.lifecycle.native_window_minimized is False
    assert app_state.lifecycle.native_window_maximized is False
    assert app_state.lifecycle.native_window_closed is False
    assert app_state.lifecycle.splash_registered is False
    assert app_state.lifecycle.splash_close_attempted is False
    assert app_state.lifecycle.splash_closed is False
    assert app_state.lifecycle.shutdown_started is False
    assert app_state.lifecycle.shutdown_completed is False

    assert app_state.status.current_message is None
    assert app_state.status.history == []
    assert app_state.status.max_history == 50


def test_nested_mutable_defaults_are_independent() -> None:
    """Ensure mutable default factories do not leak between AppState objects."""
    first_state = AppState()
    second_state = AppState()

    first_state.status.push("Loaded", "success")
    first_state.settings_validation.warnings.append("Missing optional value.")

    assert [message.text for message in first_state.status.history] == ["Loaded"]
    assert first_state.settings_validation.warnings == ["Missing optional value."]
    assert second_state.status.history == []
    assert second_state.settings_validation.warnings == []


def test_path_fields_accept_path_instances() -> None:
    """Store concrete Path values in runtime and logging state fields."""
    app_state = AppState()
    settings_path = Path("settings.toml")
    log_path = Path("logs/app.log")
    executable_path = Path("app.exe")
    working_directory = Path(".")
    pyinstaller_temp_dir = Path("_MEI000001")
    icon_path = Path("assets/app_icon.ico")
    page_image_path = Path("assets/page_image.png")
    splash_image_path = Path("assets/splash_light.png")

    app_state.paths.settings_file_path = settings_path
    app_state.paths.log_file_path = log_path
    app_state.paths.executable_path = executable_path
    app_state.paths.working_directory = working_directory
    app_state.paths.pyinstaller_temp_dir = pyinstaller_temp_dir
    app_state.log.file_path = log_path
    app_state.log.effective_file_path = log_path
    app_state.settings.file_path = settings_path
    app_state.assets.icon_path = icon_path
    app_state.assets.page_image_path = page_image_path
    app_state.assets.splash_image_path = splash_image_path

    assert app_state.paths.settings_file_path == settings_path
    assert app_state.paths.log_file_path == log_path
    assert app_state.paths.executable_path == executable_path
    assert app_state.paths.working_directory == working_directory
    assert app_state.paths.pyinstaller_temp_dir == pyinstaller_temp_dir
    assert app_state.log.file_path == log_path
    assert app_state.log.effective_file_path == log_path
    assert app_state.settings.file_path == settings_path
    assert app_state.assets.icon_path == icon_path
    assert app_state.assets.page_image_path == page_image_path
    assert app_state.assets.splash_image_path == splash_image_path


def test_status_message_uses_default_level_and_creation_time() -> None:
    """Create a standalone status message with default values."""
    before_creation = datetime.now()

    message = StatusMessage(text="Ready")

    after_creation = datetime.now()
    assert message.text == "Ready"
    assert message.level == "info"
    assert before_creation <= message.created_at <= after_creation


def test_status_push_sets_current_message_and_appends_history() -> None:
    """Add a status message and expose it as the current message."""
    status = StatusState()
    before_creation = datetime.now()

    message = status.push("Saved successfully", "success")

    after_creation = datetime.now()
    assert message.text == "Saved successfully"
    assert message.level == "success"
    assert before_creation <= message.created_at <= after_creation
    assert status.current_message is message
    assert status.history == [message]


def test_status_push_trims_history_to_maximum_capacity() -> None:
    """Keep only the most recent status messages when capacity is exceeded."""
    status = StatusState(max_history=2)
    first_message = status.push("First")
    second_message = status.push("Second", "warning")
    third_message = status.push("Third", "error")

    assert status.current_message is third_message
    assert first_message not in status.history
    assert status.history == [second_message, third_message]
    assert [message.text for message in status.history] == ["Second", "Third"]


@pytest.mark.parametrize("max_history", [0, -1])
def test_status_push_clears_history_when_capacity_is_not_positive(
    max_history: int,
) -> None:
    """Avoid retaining historical messages when history capacity is disabled."""
    status = StatusState(max_history=max_history)

    message = status.push("Transient message")

    assert status.current_message is message
    assert status.history == []


def test_status_clear_removes_current_message_and_preserves_history() -> None:
    """Clear the current status without deleting diagnostic history."""
    status = StatusState()
    message = status.push("Running", "info")

    status.clear()

    assert status.current_message is None
    assert status.history == [message]


def test_get_app_state_creates_and_reuses_singleton() -> None:
    """Create the singleton lazily and return the same object afterward."""
    state_module._APP_STATE = None

    first_state = get_app_state()
    second_state = get_app_state()

    assert first_state is second_state


def test_set_app_state_replaces_singleton() -> None:
    """Replace the process-wide state with an explicit AppState instance."""
    custom_state = AppState()
    custom_state.meta.name = "Custom App"

    set_app_state(custom_state)

    assert get_app_state() is custom_state
    assert get_app_state().meta.name == "Custom App"


def test_reset_app_state_replaces_existing_singleton() -> None:
    """Create a fresh default singleton and discard previous mutations."""
    custom_state = AppState()
    custom_state.meta.name = "Custom App"
    set_app_state(custom_state)

    new_state = reset_app_state()

    assert new_state is get_app_state()
    assert new_state is not custom_state
    assert new_state.meta.name == constants.APPLICATION_TITLE
