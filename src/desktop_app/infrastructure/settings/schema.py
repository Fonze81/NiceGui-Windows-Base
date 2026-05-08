# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/schema.py
# Purpose:
# Define the editable settings schema used by load and save operations.
# Behavior:
# Centralizes supported settings groups and property paths so mapper and TOML
# document writers can apply the same scope rules without duplicating path lists.
# Notes:
# Keep this module free of file I/O and AppState access. It only describes the
# settings schema and validates requested scopes.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

SettingsGroup = Literal["meta", "window", "ui", "log", "behavior"]

GROUP_PROPERTY_PATHS: dict[SettingsGroup, tuple[str, ...]] = {
    "meta": (
        "app.name",
        "app.version",
        "app.language",
        "app.first_run",
    ),
    "window": (
        "app.window.x",
        "app.window.y",
        "app.window.width",
        "app.window.height",
        "app.window.maximized",
        "app.window.fullscreen",
        "app.window.monitor",
        "app.window.storage_key",
    ),
    "ui": (
        "app.ui.theme",
        "app.ui.font_scale",
        "app.ui.dense_mode",
        "app.ui.accent_color",
    ),
    "log": (
        "app.log.level",
        "app.log.enable_console",
        "app.log.buffer_capacity",
        "app.log.file_path",
        "app.log.rotate_max_bytes",
        "app.log.rotate_backup_count",
    ),
    "behavior": ("app.behavior.auto_save",),
}

ALL_PROPERTY_PATHS: tuple[str, ...] = tuple(
    property_path
    for group_property_paths in GROUP_PROPERTY_PATHS.values()
    for property_path in group_property_paths
)

KNOWN_PROPERTY_PATHS = frozenset(ALL_PROPERTY_PATHS)

LEGACY_PROPERTY_PATHS_BY_GROUP: dict[SettingsGroup, tuple[str, ...]] = {
    "log": (
        "app.log.name",
        "app.log.console",
    )
}


class SettingsScopeError(ValueError):
    """Represent an invalid settings group or property path request."""


def get_settings_group_paths(group: SettingsGroup) -> tuple[str, ...]:
    """Return property paths for one settings group.

    Args:
        group: Settings group name.

    Returns:
        Known property paths for the group.

    Raises:
        SettingsScopeError: If the group is not supported.
    """
    try:
        return GROUP_PROPERTY_PATHS[group]
    except KeyError as exc:
        valid_groups = ", ".join(sorted(GROUP_PROPERTY_PATHS))
        raise SettingsScopeError(
            f"Unsupported settings group: {group!r}. Valid groups: {valid_groups}."
        ) from exc


def get_settings_scope_paths(
    *,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> tuple[str, ...]:
    """Return property paths selected by a settings scope.

    Args:
        group: Optional settings group to load or save.
        property_path: Optional individual property path to load or save.

    Returns:
        Property paths selected by the provided scope.

    Raises:
        SettingsScopeError: If both group and property_path are provided, or when
            the requested group or property path is not supported.
    """
    if group is not None and property_path is not None:
        raise SettingsScopeError(
            "Use either a settings group or an individual property path, not both."
        )

    if property_path is not None:
        normalized_property_path = property_path.strip()
        if normalized_property_path not in KNOWN_PROPERTY_PATHS:
            raise SettingsScopeError(
                f"Unsupported settings property path: {property_path!r}."
            )

        return (normalized_property_path,)

    if group is not None:
        return get_settings_group_paths(group)

    return ALL_PROPERTY_PATHS


def get_legacy_paths_for_scope(property_paths: Iterable[str]) -> tuple[str, ...]:
    """Return legacy property paths that should be removed for a save scope.

    Args:
        property_paths: Property paths selected for the current save operation.

    Returns:
        Legacy property paths to remove before writing selected properties.
    """
    selected_paths = set(property_paths)
    legacy_paths: list[str] = []

    for group, group_paths in GROUP_PROPERTY_PATHS.items():
        if selected_paths.intersection(group_paths):
            legacy_paths.extend(LEGACY_PROPERTY_PATHS_BY_GROUP.get(group, ()))

    return tuple(legacy_paths)
