# -----------------------------------------------------------------------------
# File: src/desktop_app/application/preferences.py
# Purpose:
# Update persisted template preferences from UI callbacks.
# Behavior:
# Validates simple preference values, updates AppState, persists the appropriate
# settings group, and pushes user-facing status messages.
# Notes:
# Keep NiceGUI event handling outside this module. UI pages should pass plain
# values so these helpers remain easy to test.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from typing import Final, cast

from desktop_app.constants import ALLOWED_THEMES
from desktop_app.core.state import AppState, StatusLevel, ThemeName, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.settings import save_settings_group
from desktop_app.infrastructure.settings.schema import SettingsGroup

logger: Final[Logger] = logger_get_logger(__name__)
MIN_FONT_SCALE: Final[float] = 0.8
MAX_FONT_SCALE: Final[float] = 1.4


@dataclass(frozen=True, slots=True)
class PreferenceUpdateResult:
    """Represent the result of a preference update.

    Attributes:
        accepted: Whether the provided value passed validation.
        saved: Whether the accepted value was persisted successfully.
        message: User-facing status message.
        level: Visual status level for the message.
    """

    accepted: bool
    saved: bool
    message: str
    level: StatusLevel


_INVALID_RESULT = PreferenceUpdateResult(
    accepted=False,
    saved=False,
    message="Preference value was not accepted.",
    level="warning",
)


def update_theme_preference(
    theme: str,
    *,
    state: AppState | None = None,
) -> PreferenceUpdateResult:
    """Update and persist the selected UI theme.

    Args:
        theme: Theme selected by the user.
        state: Application state to update. Uses the global state when omitted.

    Returns:
        Preference update result.
    """
    normalized_theme = theme.strip().lower()
    if normalized_theme not in ALLOWED_THEMES:
        logger.warning("Unsupported UI theme selected: %s", theme)
        return _push_result(state, _INVALID_RESULT)

    current_state = state if state is not None else get_app_state()
    current_state.ui.theme = cast(ThemeName, normalized_theme)
    return _persist_group(
        current_state,
        "ui",
        success_message="UI settings saved successfully.",
        error_message="UI settings could not be saved.",
    )


def update_dense_mode_preference(
    enabled: bool,
    *,
    state: AppState | None = None,
) -> PreferenceUpdateResult:
    """Update and persist the dense mode preference.

    Args:
        enabled: Whether compact spacing should be preferred.
        state: Application state to update. Uses the global state when omitted.

    Returns:
        Preference update result.
    """
    current_state = state if state is not None else get_app_state()
    current_state.ui.dense_mode = enabled
    return _persist_group(
        current_state,
        "ui",
        success_message="UI settings saved successfully.",
        error_message="UI settings could not be saved.",
    )


def update_font_scale_preference(
    font_scale: object,
    *,
    state: AppState | None = None,
) -> PreferenceUpdateResult:
    """Update and persist the UI font scale preference.

    Args:
        font_scale: User-provided font scale value.
        state: Application state to update. Uses the global state when omitted.

    Returns:
        Preference update result.
    """
    current_state = state if state is not None else get_app_state()
    parsed_scale = _parse_font_scale(font_scale)
    if parsed_scale is None:
        logger.warning("Unsupported UI font scale selected: %s", font_scale)
        return _push_result(current_state, _INVALID_RESULT)

    current_state.ui.font_scale = parsed_scale
    return _persist_group(
        current_state,
        "ui",
        success_message="UI settings saved successfully.",
        error_message="UI settings could not be saved.",
    )


def update_accent_color_preference(
    accent_color: str,
    *,
    state: AppState | None = None,
) -> PreferenceUpdateResult:
    """Update and persist the UI accent color preference.

    Args:
        accent_color: Hex color selected by the user.
        state: Application state to update. Uses the global state when omitted.

    Returns:
        Preference update result.
    """
    current_state = state if state is not None else get_app_state()
    normalized_color = accent_color.strip().upper()
    if not _is_hex_color(normalized_color):
        logger.warning("Unsupported UI accent color selected: %s", accent_color)
        return _push_result(current_state, _INVALID_RESULT)

    current_state.ui.accent_color = normalized_color
    return _persist_group(
        current_state,
        "ui",
        success_message="UI settings saved successfully.",
        error_message="UI settings could not be saved.",
    )


def update_auto_save_preference(
    enabled: bool,
    *,
    state: AppState | None = None,
) -> PreferenceUpdateResult:
    """Update and persist the auto-save behavior preference.

    Args:
        enabled: Whether automatic persistence should remain enabled.
        state: Application state to update. Uses the global state when omitted.

    Returns:
        Preference update result.
    """
    current_state = state if state is not None else get_app_state()
    current_state.behavior.auto_save = enabled
    return _persist_group(
        current_state,
        "behavior",
        success_message="Behavior settings saved successfully.",
        error_message="Behavior settings could not be saved.",
    )


def _persist_group(
    state: AppState,
    group: SettingsGroup,
    *,
    success_message: str,
    error_message: str,
) -> PreferenceUpdateResult:
    """Persist a settings group and push a status message.

    Args:
        state: Application state used for persistence.
        group: Settings group to save.
        success_message: Message used when persistence succeeds.
        error_message: Message used when persistence fails.

    Returns:
        Preference update result.
    """
    saved = save_settings_group(group, state=state)
    message = success_message if saved else error_message
    level: StatusLevel = "success" if saved else "error"
    return _push_result(
        state,
        PreferenceUpdateResult(
            accepted=True,
            saved=saved,
            message=message,
            level=level,
        ),
    )


def _push_result(
    state: AppState | None,
    result: PreferenceUpdateResult,
) -> PreferenceUpdateResult:
    """Push the result message to state when possible.

    Args:
        state: Optional application state.
        result: Result to publish.

    Returns:
        The same result instance.
    """
    current_state = state if state is not None else get_app_state()
    current_state.status.push(result.message, result.level)
    return result


def _parse_font_scale(value: object) -> float | None:
    """Parse and validate a font scale value.

    Args:
        value: Raw user value.

    Returns:
        Valid font scale or None.
    """
    if isinstance(value, bool):
        return None

    if not isinstance(value, int | float | str):
        return None

    try:
        parsed_value = float(value)
    except ValueError:
        return None

    if MIN_FONT_SCALE <= parsed_value <= MAX_FONT_SCALE:
        return parsed_value

    return None


def _is_hex_color(value: str) -> bool:
    """Return whether a value is a simple hex color.

    Args:
        value: Candidate color value.

    Returns:
        True when the value uses #RRGGBB format.
    """
    if len(value) != 7 or not value.startswith("#"):
        return False

    return all(character in "0123456789ABCDEF" for character in value[1:])
