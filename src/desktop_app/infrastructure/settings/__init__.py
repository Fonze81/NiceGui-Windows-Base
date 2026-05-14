# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/__init__.py
# Purpose:
# Define the public API for the settings package.
# Behavior:
# Re-exports the functions used by application startup and future UI callbacks
# without exposing mapper and path-resolution internals as package-level API.
# Notes:
# Other modules should prefer importing from this facade for load/save workflows.
# Internal modules exist for organization and tests, not for parallel usage paths.
# -----------------------------------------------------------------------------

from desktop_app.infrastructure.settings.mapper import build_logger_config_from_state
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

__all__: tuple[str, ...] = (
    "GROUP_PROPERTY_PATHS",
    "KNOWN_PROPERTY_PATHS",
    "SettingsGroup",
    "SettingsScopeError",
    "build_logger_config_from_state",
    "load_setting_property",
    "load_settings",
    "load_settings_group",
    "save_setting_property",
    "save_settings",
    "save_settings_group",
)
