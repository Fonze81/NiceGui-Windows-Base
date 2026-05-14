# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test___init___.py
# Purpose:
# Validate the public API exposed by the settings package.
# Behavior:
# Imports the package facade and verifies that each exported symbol points to
# the expected implementation module object.
# Notes:
# These tests intentionally avoid testing the internal behavior of each imported
# function. They protect the package boundary and keep implementation tests in
# the modules that own the behavior.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import desktop_app.infrastructure.settings as settings
from desktop_app.infrastructure.settings import mapper, schema, service

EXPECTED_PUBLIC_API: tuple[str, ...] = (
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

REMOVED_COMPATIBILITY_API: tuple[str, ...] = (
    "SETTINGS_FILE_NAME",
    "apply_setting_property_to_state",
    "apply_settings_to_state",
    "resolve_default_settings_path",
)

EXPECTED_EXPORTS: Mapping[str, Any] = {
    "GROUP_PROPERTY_PATHS": schema.GROUP_PROPERTY_PATHS,
    "KNOWN_PROPERTY_PATHS": schema.KNOWN_PROPERTY_PATHS,
    "SettingsGroup": schema.SettingsGroup,
    "SettingsScopeError": schema.SettingsScopeError,
    "build_logger_config_from_state": mapper.build_logger_config_from_state,
    "load_setting_property": service.load_setting_property,
    "load_settings": service.load_settings,
    "load_settings_group": service.load_settings_group,
    "save_setting_property": service.save_setting_property,
    "save_settings": service.save_settings,
    "save_settings_group": service.save_settings_group,
}


def test_settings_package_exports_expected_public_api() -> None:
    """Ensure the settings facade exposes the expected public names."""
    assert settings.__all__ == EXPECTED_PUBLIC_API


def test_settings_package_does_not_reexport_internal_helpers() -> None:
    """Ensure mapper and path helpers stay out of the package facade."""
    for symbol_name in REMOVED_COMPATIBILITY_API:
        assert symbol_name not in settings.__all__
        assert not hasattr(settings, symbol_name)


def test_settings_package_re_exports_expected_objects() -> None:
    """Ensure public names are direct re-exports from their owner modules."""
    for public_name, expected_object in EXPECTED_EXPORTS.items():
        assert getattr(settings, public_name) is expected_object
