# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/service.py
# Purpose:
# Load and save the persistent settings.toml file.
# Behavior:
# Coordinates initial settings file creation, TOML parsing, AppState mapping, and
# TOML persistence while delegating document manipulation to document.py.
# Notes:
# This is the operational facade for the settings package. It does not create log
# handlers and does not contain UI rules.
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
from pathlib import Path

import tomlkit

from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.settings.diagnostics import (
    log_debug,
    log_exception,
    log_info,
    log_warning,
)
from desktop_app.infrastructure.settings.document import (
    apply_state_to_document,
    atomic_write_text,
    build_document_from_state,
    build_settings_text_from_state,
)
from desktop_app.infrastructure.settings.mapper import apply_settings_to_state
from desktop_app.infrastructure.settings.paths import (
    default_settings_path,
    read_bundled_settings_text,
)


def create_settings_from_bundled_template(
    settings_path: Path,
    state: AppState,
    logger: logging.Logger | None,
) -> bool:
    """Create persistent settings from the bundled template.

    Args:
        settings_path: Persistent settings file path.
        state: Current application state.
        logger: Optional logger for diagnostics.

    Returns:
        True when the file was created successfully.
    """
    log_debug(
        logger,
        'Creating persistent settings from bundled template: path="%s"',
        str(settings_path),
    )

    try:
        bundled_text = read_bundled_settings_text()

        if bundled_text is None:
            bundled_text = build_settings_text_from_state(state)
            log_warning(
                logger,
                (
                    "Bundled settings template not found. "
                    "Generated settings from defaults."
                ),
            )

        atomic_write_text(settings_path, bundled_text)
        log_info(
            logger,
            'Persistent settings file created: path="%s"',
            str(settings_path),
        )
        return True
    except Exception:
        log_exception(logger, "Failed to create persistent settings file")
        return False


def load_settings(
    *,
    settings_path: Path | None = None,
    state: AppState | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """Load settings.toml and apply values to AppState.

    Args:
        settings_path: Optional settings file path.
        state: State that receives settings values. Uses the global state when omitted.
        logger: Optional logger for diagnostics.

    Returns:
        True when loading completed successfully.
    """
    current_state = state if state is not None else get_app_state()
    path = (settings_path or default_settings_path()).expanduser().resolve()

    current_state.settings.file_path = path
    current_state.settings.last_error = None
    current_state.settings.last_load_ok = False

    log_debug(logger, 'Settings load started: path="%s"', str(path))

    if not path.exists():
        current_state.status.push(
            "settings.toml was not found. Creating default settings.",
            "warning",
        )
        log_warning(
            logger,
            'Persistent settings file not found. Creating default: path="%s"',
            str(path),
        )

        if not create_settings_from_bundled_template(path, current_state, logger):
            current_state.settings.last_error = f"Settings file not found: {path}"
            current_state.status.push(
                "settings.toml could not be created. Default settings are being used.",
                "error",
            )
            return False

    try:
        log_debug(logger, 'Reading settings file: path="%s"', str(path))
        document = tomlkit.parse(path.read_text(encoding="utf-8"))

        log_debug(logger, "Applying settings document to AppState.")
        apply_settings_to_state(current_state, document)

        current_state.settings.last_load_ok = True
        current_state.settings.last_error = None
        current_state.status.push("Settings loaded successfully.", "success")

        log_info(logger, 'Settings loaded successfully: path="%s"', str(path))
        return True
    except Exception as exc:
        current_state.settings.last_error = f"Failed to load settings: {exc}"
        current_state.status.push(
            "settings.toml could not be loaded. Default settings are being used.",
            "error",
        )
        log_exception(logger, "Failed to load settings")
        return False


def save_settings(
    *,
    settings_path: Path | None = None,
    state: AppState | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """Save the current AppState to settings.toml.

    Args:
        settings_path: Optional settings file path.
        state: State used as source. Uses the global state when omitted.
        logger: Optional logger for diagnostics.

    Returns:
        True when saving completed successfully.
    """
    current_state = state if state is not None else get_app_state()
    path = (
        settings_path or current_state.settings.file_path or default_settings_path()
    ).expanduser().resolve()

    current_state.settings.file_path = path
    current_state.settings.last_error = None
    current_state.settings.last_save_ok = False

    log_debug(logger, 'Settings save started: path="%s"', str(path))

    try:
        if path.exists():
            log_debug(logger, 'Existing settings file found: path="%s"', str(path))
            document = tomlkit.parse(path.read_text(encoding="utf-8"))
        else:
            log_debug(logger, "Settings file not found. Building a new document.")
            document = build_document_from_state(current_state)

        log_debug(logger, "Applying AppState to settings document.")
        apply_state_to_document(document, current_state)
        atomic_write_text(path, tomlkit.dumps(document))

        current_state.settings.last_save_ok = True
        current_state.status.push("Settings saved successfully.", "success")
        log_info(logger, 'Settings saved successfully: path="%s"', str(path))
        return True
    except Exception as exc:
        current_state.settings.last_error = f"Failed to save settings: {exc}"
        current_state.status.push("settings.toml could not be saved.", "error")
        log_exception(logger, "Failed to save settings")
        return False
