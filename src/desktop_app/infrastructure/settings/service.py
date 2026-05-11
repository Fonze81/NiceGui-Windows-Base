# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/service.py
# Purpose:
# Load and save the persistent settings.toml file.
# Behavior:
# Coordinates read-only settings loading, TOML parsing, scoped AppState mapping,
# and scoped TOML persistence while delegating TOML manipulation to
# toml_document.py.
# Notes:
# Uses the official application logger. The logger subsystem is safe during early
# startup because it buffers or stays silent until final configuration is applied
# after settings are loaded. Loading missing settings is intentionally read-only;
# settings.toml is created only by save operations.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import tomlkit
from tomlkit.exceptions import ParseError
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.file_system import atomic_write_text
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.settings.mapper import apply_settings_to_state
from desktop_app.infrastructure.settings.paths import (
    read_bundled_settings_text,
    resolve_default_settings_path,
)
from desktop_app.infrastructure.settings.schema import (
    SettingsGroup,
    SettingsScopeError,
    get_settings_scope_paths,
)
from desktop_app.infrastructure.settings.toml_document import (
    apply_state_to_document,
    build_document_from_state,
)

type SettingsPath = str | Path

logger = logger_get_logger(__name__)


def build_initial_settings_document(state: AppState) -> TOMLDocument:
    """Build the initial document used when settings.toml is first saved.

    Args:
        state: Current application state.

    Returns:
        TOML document based on the bundled template when available, otherwise on
        the current AppState defaults.
    """
    bundled_text = read_bundled_settings_text()

    if bundled_text is None:
        logger.warning(
            "Bundled settings template not found. Generated settings from defaults."
        )
        return build_document_from_state(state)

    try:
        return tomlkit.parse(bundled_text)
    except ParseError:
        logger.exception(
            "Bundled settings template could not be parsed. Generated settings "
            "from defaults."
        )
        return build_document_from_state(state)


def load_settings(
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> bool:
    """Load settings.toml and apply values to AppState.

    Missing settings.toml is treated as a successful read-only load that keeps
    default values in memory. The file is created only by save operations.

    Args:
        settings_path: Optional settings file path.
        state: State that receives settings values. Uses the global state when omitted.
        group: Optional settings group to load.
        property_path: Optional individual property path to load.

    Returns:
        True when loading completed successfully.
    """
    current_state = state if state is not None else get_app_state()
    settings_file_path = _resolve_load_path(settings_path)
    scope_description = _describe_scope(group=group, property_path=property_path)

    # Validate scope even when the file does not exist, so invalid API usage does
    # not get hidden by the default-settings fallback path.
    get_settings_scope_paths(group=group, property_path=property_path)

    _mark_load_started(current_state, settings_file_path, scope_description)

    logger.debug(
        'Settings load started: path="%s", scope="%s"',
        str(settings_file_path),
        scope_description,
    )

    if not settings_file_path.exists():
        _mark_missing_file_load(current_state, scope_description)
        logger.info(
            'Settings file not found. Using in-memory defaults: path="%s", scope="%s"',
            str(settings_file_path),
            scope_description,
        )
        return True

    try:
        logger.debug('Reading settings file: path="%s"', str(settings_file_path))
        document = tomlkit.parse(settings_file_path.read_text(encoding="utf-8"))

        logger.debug(
            'Applying settings document to AppState: scope="%s"',
            scope_description,
        )
        apply_settings_to_state(
            current_state,
            document,
            group=group,
            property_path=property_path,
        )

        _mark_load_succeeded(current_state, scope_description)
        logger.info(
            'Settings loaded successfully: path="%s", scope="%s"',
            str(settings_file_path),
            scope_description,
        )
        return True
    except SettingsScopeError:
        raise
    except Exception as exc:
        _mark_load_failed(current_state, exc)
        logger.exception("Failed to load settings")
        return False


def load_settings_group(
    group: SettingsGroup,
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
) -> bool:
    """Load one settings group from settings.toml.

    Args:
        group: Settings group to load.
        settings_path: Optional settings file path.
        state: State that receives settings values. Uses the global state when omitted.

    Returns:
        True when loading completed successfully.
    """
    return load_settings(
        settings_path=settings_path,
        state=state,
        group=group,
    )


def load_setting_property(
    property_path: str,
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
) -> bool:
    """Load one settings property from settings.toml.

    Args:
        property_path: Individual settings property path to load.
        settings_path: Optional settings file path.
        state: State that receives settings values. Uses the global state when omitted.

    Returns:
        True when loading completed successfully.
    """
    return load_settings(
        settings_path=settings_path,
        state=state,
        property_path=property_path,
    )


def save_settings(
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> bool:
    """Save the current AppState to settings.toml.

    Args:
        settings_path: Optional settings file path.
        state: State used as source. Uses the global state when omitted.
        group: Optional settings group to save.
        property_path: Optional individual property path to save.

    Returns:
        True when saving completed successfully.
    """
    current_state = state if state is not None else get_app_state()
    settings_file_path = _resolve_save_path(settings_path, current_state)
    scope_description = _describe_scope(group=group, property_path=property_path)

    # Validate scope before touching the filesystem.
    get_settings_scope_paths(group=group, property_path=property_path)

    _mark_save_started(current_state, settings_file_path)

    logger.debug(
        'Settings save started: path="%s", scope="%s"',
        str(settings_file_path),
        scope_description,
    )

    try:
        if settings_file_path.exists():
            logger.debug(
                'Existing settings file found: path="%s"',
                str(settings_file_path),
            )
            document = tomlkit.parse(settings_file_path.read_text(encoding="utf-8"))
        else:
            logger.debug(
                "Settings file not found. Building initial document for first save."
            )
            document = build_initial_settings_document(current_state)

        logger.debug(
            'Applying AppState to settings document: scope="%s"',
            scope_description,
        )
        apply_state_to_document(
            document,
            current_state,
            group=group,
            property_path=property_path,
        )
        atomic_write_text(settings_file_path, tomlkit.dumps(document))

        _mark_save_succeeded(current_state, scope_description)
        logger.info(
            'Settings saved successfully: path="%s", scope="%s"',
            str(settings_file_path),
            scope_description,
        )
        return True
    except SettingsScopeError:
        raise
    except Exception as exc:
        _mark_save_failed(current_state, exc)
        logger.exception("Failed to save settings")
        return False


def save_settings_group(
    group: SettingsGroup,
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
) -> bool:
    """Save one settings group to settings.toml.

    Args:
        group: Settings group to save.
        settings_path: Optional settings file path.
        state: State used as source. Uses the global state when omitted.

    Returns:
        True when saving completed successfully.
    """
    return save_settings(
        settings_path=settings_path,
        state=state,
        group=group,
    )


def save_setting_property(
    property_path: str,
    *,
    settings_path: SettingsPath | None = None,
    state: AppState | None = None,
) -> bool:
    """Save one settings property to settings.toml.

    Args:
        property_path: Individual settings property path to save.
        settings_path: Optional settings file path.
        state: State used as source. Uses the global state when omitted.

    Returns:
        True when saving completed successfully.
    """
    return save_settings(
        settings_path=settings_path,
        state=state,
        property_path=property_path,
    )


def _resolve_load_path(settings_path: SettingsPath | None) -> Path:
    """Resolve the settings path used by load operations.

    Args:
        settings_path: Explicit settings file path, when provided.

    Returns:
        Absolute settings file path.
    """
    selected_path = settings_path

    if selected_path is None:
        selected_path = resolve_default_settings_path()

    return Path(selected_path).expanduser().resolve()


def _resolve_save_path(
    settings_path: SettingsPath | None,
    state: AppState,
) -> Path:
    """Resolve the settings path used by save operations.

    Args:
        settings_path: Explicit settings file path, when provided.
        state: Application state that may contain the latest settings path.

    Returns:
        Absolute settings file path.
    """
    if settings_path is not None:
        selected_path: SettingsPath = settings_path
    elif state.settings.file_path is not None:
        selected_path = state.settings.file_path
    else:
        selected_path = resolve_default_settings_path()

    return Path(selected_path).expanduser().resolve()


def _mark_load_started(
    state: AppState,
    settings_file_path: Path,
    scope_description: str,
) -> None:
    """Update state metadata before a settings load attempt.

    Args:
        state: Application state to update.
        settings_file_path: Effective settings file path.
        scope_description: Human-readable scope description.
    """
    state.settings.file_path = settings_file_path
    state.settings.file_exists = settings_file_path.exists()
    state.settings.last_error = None
    state.settings.last_load_ok = False
    state.settings_validation.warnings.clear()
    state.settings_validation.last_validated_scope = scope_description
    state.settings_validation.last_validated_at = datetime.now()


def _mark_missing_file_load(state: AppState, scope_description: str) -> None:
    """Update state metadata when settings.toml does not exist.

    Args:
        state: Application state to update.
        scope_description: Human-readable scope description.
    """
    state.settings.using_defaults = True
    state.settings.last_load_ok = True
    state.settings.last_loaded_scope = scope_description
    state.status.push(
        "settings.toml was not found. Default settings are being used.",
        "info",
    )


def _mark_load_succeeded(state: AppState, scope_description: str) -> None:
    """Update state metadata after a successful settings load.

    Args:
        state: Application state to update.
        scope_description: Human-readable scope description.
    """
    state.settings.file_exists = True
    state.settings.using_defaults = False
    state.settings.last_load_ok = True
    state.settings.last_loaded_scope = scope_description
    state.settings.last_error = None
    state.status.push("Settings loaded successfully.", "success")


def _mark_load_failed(state: AppState, error: Exception) -> None:
    """Update state metadata after a failed settings load.

    Args:
        state: Application state to update.
        error: Exception raised during the load operation.
    """
    state.settings.last_error = f"Failed to load settings: {error}"
    state.settings.using_defaults = True
    state.status.push(
        "settings.toml could not be loaded. Default settings are being used.",
        "error",
    )


def _mark_save_started(state: AppState, settings_file_path: Path) -> None:
    """Update state metadata before a settings save attempt.

    Args:
        state: Application state to update.
        settings_file_path: Effective settings file path.
    """
    state.settings.file_path = settings_file_path
    state.settings.last_error = None
    state.settings.last_save_ok = False


def _mark_save_succeeded(state: AppState, scope_description: str) -> None:
    """Update state metadata after a successful settings save.

    Args:
        state: Application state to update.
        scope_description: Human-readable scope description.
    """
    state.settings.file_exists = True
    state.settings.using_defaults = False
    state.settings.last_save_ok = True
    state.settings.last_saved_scope = scope_description
    state.status.push("Settings saved successfully.", "success")


def _mark_save_failed(state: AppState, error: Exception) -> None:
    """Update state metadata after a failed settings save.

    Args:
        state: Application state to update.
        error: Exception raised during the save operation.
    """
    state.settings.last_error = f"Failed to save settings: {error}"
    state.status.push("settings.toml could not be saved.", "error")


def _describe_scope(
    *,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> str:
    """Return a readable scope description for logs.

    Args:
        group: Optional settings group.
        property_path: Optional individual property path.

    Returns:
        Scope description for diagnostic logs.
    """
    if property_path is not None:
        return f"property:{property_path}"

    if group is not None:
        return f"group:{group}"

    return "all"
