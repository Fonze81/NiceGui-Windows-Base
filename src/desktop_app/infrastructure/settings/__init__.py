# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/__init__.py
# Purpose:
# Define the public API for the settings package.
# Behavior:
# Re-exports the small set of functions used by application startup and future
# UI callbacks without exposing the internal package organization.
# Notes:
# Other modules should prefer importing from this file. Internal modules exist
# for organization and tests, not to create parallel usage paths.
# -----------------------------------------------------------------------------

from desktop_app.infrastructure.settings.constants import SETTINGS_FILE_NAME
from desktop_app.infrastructure.settings.mapper import (
    apply_setting_property_to_state,
    apply_settings_to_state,
    build_logger_config_from_state,
)
from desktop_app.infrastructure.settings.paths import resolve_default_settings_path
from desktop_app.infrastructure.settings.schema import (
    GROUP_PROPERTY_PATHS,
    KNOWN_PROPERTY_PATHS,
    SettingsGroup,
    SettingsScopeError,
)
from desktop_app.infrastructure.settings.service import (
    load_setting_property,
    load_settings,
    load_settings_group,
    save_setting_property,
    save_settings,
    save_settings_group,
)

__all__ = [
    "GROUP_PROPERTY_PATHS",
    "KNOWN_PROPERTY_PATHS",
    "SETTINGS_FILE_NAME",
    "SettingsGroup",
    "SettingsScopeError",
    "apply_setting_property_to_state",
    "apply_settings_to_state",
    "build_logger_config_from_state",
    "load_setting_property",
    "load_settings",
    "load_settings_group",
    "resolve_default_settings_path",
    "save_setting_property",
    "save_settings",
    "save_settings_group",
]
