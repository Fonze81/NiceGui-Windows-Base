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
    apply_settings_to_state,
    build_logger_config_from_state,
)
from desktop_app.infrastructure.settings.paths import default_settings_path
from desktop_app.infrastructure.settings.service import load_settings, save_settings

__all__ = [
    "SETTINGS_FILE_NAME",
    "apply_settings_to_state",
    "build_logger_config_from_state",
    "default_settings_path",
    "load_settings",
    "save_settings",
]
