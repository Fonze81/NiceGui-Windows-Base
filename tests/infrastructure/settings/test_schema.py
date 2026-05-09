# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test_schema.py
# Purpose:
# Validate settings schema scope selection and legacy path cleanup rules.
# Behavior:
# Exercises group selection, property selection, invalid scope errors, and legacy
# TOML key lookup without touching the filesystem or application state.
# Notes:
# These tests intentionally target the schema module in isolation because it is
# the source of truth used by settings mappers and TOML document writers.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Iterator
from typing import cast

import pytest

from desktop_app.infrastructure.settings.schema import (
    ALL_PROPERTY_PATHS,
    GROUP_PROPERTY_PATHS,
    KNOWN_PROPERTY_PATHS,
    LEGACY_PROPERTY_PATHS_BY_GROUP,
    SettingsGroup,
    SettingsScopeError,
    get_legacy_paths_for_scope,
    get_settings_group_paths,
    get_settings_scope_paths,
)


def iter_log_scope_paths() -> Iterator[str]:
    """Yield log settings paths to verify iterable input handling.

    Yields:
        Known log property paths selected for a scoped save operation.
    """
    yield "app.log.level"
    yield "app.log.file_path"


def test_all_property_paths_preserve_group_order() -> None:
    """Ensure the flattened schema follows the declared group order."""
    expected_paths = tuple(
        property_path
        for group_paths in GROUP_PROPERTY_PATHS.values()
        for property_path in group_paths
    )

    assert expected_paths == ALL_PROPERTY_PATHS


def test_known_property_paths_match_all_property_paths() -> None:
    """Ensure the known-path lookup contains every editable property once."""
    assert frozenset(ALL_PROPERTY_PATHS) == KNOWN_PROPERTY_PATHS
    assert len(KNOWN_PROPERTY_PATHS) == len(ALL_PROPERTY_PATHS)


def test_get_settings_group_paths_returns_selected_group_paths() -> None:
    """Return only the property paths declared for the requested group."""
    assert get_settings_group_paths("ui") == GROUP_PROPERTY_PATHS["ui"]


def test_get_settings_group_paths_rejects_unknown_group() -> None:
    """Raise a clear error when a runtime caller provides an unknown group."""
    unsupported_group = cast(SettingsGroup, "unknown")

    with pytest.raises(SettingsScopeError) as exc_info:
        get_settings_group_paths(unsupported_group)

    assert "Unsupported settings group: 'unknown'." in str(exc_info.value)
    assert "Valid groups: behavior, log, meta, ui, window." in str(exc_info.value)


def test_get_settings_scope_paths_rejects_group_and_property_path_together() -> None:
    """Reject ambiguous scopes that select a group and one property together."""
    with pytest.raises(SettingsScopeError) as exc_info:
        get_settings_scope_paths(group="log", property_path="app.log.level")

    assert str(exc_info.value) == (
        "Use either a settings group or an individual property path, not both."
    )


def test_get_settings_scope_paths_returns_normalized_property_path() -> None:
    """Trim a valid property path before returning the selected scope."""
    assert get_settings_scope_paths(property_path="  app.log.level  ") == (
        "app.log.level",
    )


def test_get_settings_scope_paths_rejects_unknown_property_path() -> None:
    """Raise a clear error for unsupported individual property paths."""
    with pytest.raises(SettingsScopeError) as exc_info:
        get_settings_scope_paths(property_path="app.log.unknown")

    assert str(exc_info.value) == (
        "Unsupported settings property path: 'app.log.unknown'."
    )


def test_get_settings_scope_paths_rejects_blank_property_path() -> None:
    """Reject blank paths after whitespace normalization."""
    with pytest.raises(SettingsScopeError) as exc_info:
        get_settings_scope_paths(property_path="   ")

    assert str(exc_info.value) == "Unsupported settings property path: '   '."


def test_get_settings_scope_paths_returns_group_paths() -> None:
    """Return the paths for a selected settings group."""
    assert get_settings_scope_paths(group="window") == GROUP_PROPERTY_PATHS["window"]


def test_get_settings_scope_paths_returns_all_paths_when_scope_is_omitted() -> None:
    """Return the full editable schema when no scoped selection is requested."""
    assert get_settings_scope_paths() == ALL_PROPERTY_PATHS


def test_get_legacy_paths_for_scope_returns_log_legacy_paths() -> None:
    """Return legacy TOML keys when the current save scope touches log settings."""
    assert get_legacy_paths_for_scope(("app.log.level",)) == (
        "app.log.name",
        "app.log.console",
    )


def test_get_legacy_paths_for_scope_accepts_iterables() -> None:
    """Accept any iterable of selected paths, including generators."""
    assert get_legacy_paths_for_scope(iter_log_scope_paths()) == (
        "app.log.name",
        "app.log.console",
    )


def test_get_legacy_paths_for_scope_returns_empty_tuple_for_non_legacy_group() -> None:
    """Return no legacy cleanup paths for groups without legacy keys."""
    assert get_legacy_paths_for_scope(("app.ui.theme",)) == ()


def test_legacy_property_path_mapping_is_limited_to_log_group() -> None:
    """Document the only currently supported legacy cleanup mapping."""
    assert LEGACY_PROPERTY_PATHS_BY_GROUP == {
        "log": (
            "app.log.name",
            "app.log.console",
        )
    }
