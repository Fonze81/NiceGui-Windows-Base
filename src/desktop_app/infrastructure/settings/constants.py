# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/constants.py
# Purpose:
# Store constants used by the settings package.
# Behavior:
# Defines the persistent settings file name, root override environment variable,
# and accepted values used while reading user-edited settings.toml files.
# Notes:
# Keep this module small so repeated literal values do not spread across the
# settings package.
# -----------------------------------------------------------------------------

from __future__ import annotations

SETTINGS_FILE_NAME = "settings.toml"
APP_ROOT_ENV_VAR = "DESKTOP_APP_ROOT"

ALLOWED_LOG_LEVELS = {
    "CRITICAL",
    "ERROR",
    "WARNING",
    "WARN",
    "INFO",
    "DEBUG",
    "NOTSET",
}

ALLOWED_THEMES = {"light", "dark", "system"}
