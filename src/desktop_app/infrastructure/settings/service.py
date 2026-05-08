# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/service.py
# Purpose:
# Load and save the persistent settings.toml file.
# Behavior:
# Coordinates initial settings file creation, TOML parsing, scoped AppState
# mapping, and scoped TOML persistence while delegating TOML manipulation to
# toml_document.py.
# Notes:
# Uses the official application logger. The logger subsystem is safe during early
# startup because it buffers or stays silent until final configuration is applied
# after settings are loaded.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

import tomlkit

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
)
from desktop_app.infrastructure.settings.toml_document import (
    apply_state_to_document,
    build_document_from_state,
    build_settings_text_from_state,
)

logger = logger_get_logger(__name__)


def create_settings_from_bundled_template(
    settings_path: Path,
    state: AppState,
) -> bool:
    """Create persistent settings from the bundled template.

    Args:
        settings_path: Persistent settings file path.
        state: Current application state.

    Returns:
        True when the file was created successfully.
    """
    logger.debug(
        'Creating persistent settings from bundled template: path="%s"',
        str(settings_path),
    )

    try:
        bundled_text = read_bundled_settings_text()

        if bundled_text is None:
            bundled_text = build_settings_text_from_state(state)
            logger.warning(
                "Bundled settings template not found. "
                "Generated settings from defaults."
            )

        atomic_write_text(settings_path, bundled_text)
        logger.info(
            'Persistent settings file created: path="%s"',
            str(settings_path),
        )
        return True
    except Exception:
        logger.exception("Failed to create persistent settings file")
        return False


def load_settings(
    *,
    settings_path: Path | None = None,
    state: AppState | None = None,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> bool:
    """Load settings.toml and apply values to AppState.

    Args:
        settings_path: Optional settings file path.
        state: State that receives settings values. Uses the global state when omitted.
        group: Optional settings group to load.
        property_path: Optional individual property path to load.

    Returns:
        True when loading completed successfully.
    """
    current_state = state if state is not None else get_app_state()
    path = (settings_path or resolve_default_settings_path()).expanduser().resolve()
    scope_description = _describe_scope(group=group, property_path=property_path)

    current_state.settings.file_path = path
    current_state.settings.last_error = None
    current_state.settings.last_load_ok = False

    logger.debug(
        'Settings load started: path="%s", scope="%s"',
        str(path),
        scope_description,
    )

    if not path.exists():
        current_state.status.push(
            "settings.toml was not found. Creating default settings.",
            "warning",
        )
        logger.warning(
            'Persistent settings file not found. Creating default: path="%s"',
            str(path),
        )

        if not create_settings_from_bundled_template(path, current_state):
            current_state.settings.last_error = f"Settings file not found: {path}"
            current_state.status.push(
                "settings.toml could not be created. Default settings are being used.",
                "error",
            )
            return False

    try:
        logger.debug('Reading settings file: path="%s"', str(path))
        document = tomlkit.parse(path.read_text(encoding="utf-8"))

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

        current_state.settings.last_load_ok = True
        current_state.settings.last_error = None
        current_state.status.push("Settings loaded successfully.", "success")

        logger.info(
            'Settings loaded successfully: path="%s", scope="%s"',
            str(path),
            scope_description,
        )
        return True
    except SettingsScopeError:
        raise
    except Exception as exc:
        current_state.settings.last_error = f"Failed to load settings: {exc}"
        current_state.status.push(
            "settings.toml could not be loaded. Default settings are being used.",
            "error",
        )
        logger.exception("Failed to load settings")
        return False


def load_settings_group(
    group: SettingsGroup,
    *,
    settings_path: Path | None = None,
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
    settings_path: Path | None = None,
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
    settings_path: Path | None = None,
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
    path = (
        settings_path
        or current_state.settings.file_path
        or resolve_default_settings_path()
    ).expanduser().resolve()
    scope_description = _describe_scope(group=group, property_path=property_path)

    current_state.settings.file_path = path
    current_state.settings.last_error = None
    current_state.settings.last_save_ok = False

    logger.debug(
        'Settings save started: path="%s", scope="%s"',
        str(path),
        scope_description,
    )

    try:
        if path.exists():
            logger.debug('Existing settings file found: path="%s"', str(path))
            document = tomlkit.parse(path.read_text(encoding="utf-8"))
        else:
            logger.debug("Settings file not found. Building a new document.")
            document = build_document_from_state(current_state)

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
        atomic_write_text(path, tomlkit.dumps(document))

        current_state.settings.last_save_ok = True
        current_state.status.push("Settings saved successfully.", "success")
        logger.info(
            'Settings saved successfully: path="%s", scope="%s"',
            str(path),
            scope_description,
        )
        return True
    except SettingsScopeError:
        raise
    except Exception as exc:
        current_state.settings.last_error = f"Failed to save settings: {exc}"
        current_state.status.push("settings.toml could not be saved.", "error")
        logger.exception("Failed to save settings")
        return False


def save_settings_group(
    group: SettingsGroup,
    *,
    settings_path: Path | None = None,
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
    settings_path: Path | None = None,
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
