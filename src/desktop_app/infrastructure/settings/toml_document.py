# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/toml_document.py
# Purpose:
# Build and update TOML documents used by settings.toml.
# Behavior:
# Creates required TOML tables, writes AppState values into known keys, and
# preserves comments and unknown keys when an existing document is saved again.
# It can update all settings, one settings group, or one individual property.
# Notes:
# This module only manipulates in-memory TOML documents. Disk writes are handled
# by shared file-system helpers.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, cast

import tomlkit
from tomlkit.items import Table
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState
from desktop_app.infrastructure.settings.schema import (
    SettingsGroup,
    get_legacy_paths_for_scope,
    get_settings_scope_paths,
)


def ensure_toml_table(root: TOMLDocument | Table, key: str) -> Table:
    """Ensure that a TOML key contains a table.

    Args:
        root: TOML document or table where the key is checked.
        key: Key that must contain a table.

    Returns:
        Existing or newly created TOML table.
    """
    current_value = root.get(key)

    if isinstance(current_value, Table):
        return current_value

    table = tomlkit.table()
    root[key] = table
    return table


def set_toml_value(document: TOMLDocument, dotted_path: str, value: Any) -> None:
    """Set a TOML value selected by a dotted path.

    Args:
        document: TOML document to update.
        dotted_path: Dotted key path.
        value: Value assigned to the target key.
    """
    parts = dotted_path.split(".")
    cursor: TOMLDocument | Table = document

    for part in parts[:-1]:
        cursor = ensure_toml_table(cursor, part)

    cursor[parts[-1]] = value


def remove_toml_value(document: TOMLDocument, dotted_path: str) -> None:
    """Remove a known TOML key that should no longer be written.

    Args:
        document: TOML document to update.
        dotted_path: Dotted key path to remove.
    """
    parts = dotted_path.split(".")
    cursor: object = document

    for part in parts[:-1]:
        if not isinstance(cursor, MutableMapping) or part not in cursor:
            return

        next_cursor = cursor[part]

        if not isinstance(next_cursor, MutableMapping):
            return

        cursor = next_cursor

    mapping_cursor = cast(MutableMapping[str, Any], cursor)
    mapping_cursor.pop(parts[-1], None)


def normalize_path_for_toml(file_path: Path) -> str:
    """Return a path string suitable for TOML files.

    Args:
        file_path: Path to serialize.

    Returns:
        Path string with forward slashes for stable cross-platform TOML output.
    """
    return file_path.as_posix()


def apply_state_to_document(
    document: TOMLDocument,
    state: AppState,
    *,
    group: SettingsGroup | None = None,
    property_path: str | None = None,
) -> None:
    """Update a TOML document with values from the application state.

    Args:
        document: TOML document to update.
        state: Application state used as source.
        group: Optional settings group to save.
        property_path: Optional individual property path to save.
    """
    property_paths = get_settings_scope_paths(group=group, property_path=property_path)

    for legacy_path in get_legacy_paths_for_scope(property_paths):
        remove_toml_value(document, legacy_path)

    for selected_path in property_paths:
        apply_state_property_to_document(document, state, selected_path)


def apply_state_property_to_document(
    document: TOMLDocument,
    state: AppState,
    property_path: str,
) -> None:
    """Update one TOML property with a value from the application state.

    Args:
        document: TOML document to update.
        state: Application state used as source.
        property_path: Supported property path to save.
    """
    set_toml_value(
        document,
        property_path,
        get_state_property_value(state, property_path),
    )


def get_state_property_value(state: AppState, property_path: str) -> Any:
    """Return one TOML-compatible value from AppState.

    Args:
        state: Application state used as source.
        property_path: Supported property path to read.

    Returns:
        TOML-compatible value for the property path.
    """
    if property_path == "app.name":
        return state.meta.name
    if property_path == "app.version":
        return state.meta.version
    if property_path == "app.language":
        return state.meta.language
    if property_path == "app.first_run":
        return state.meta.first_run

    if property_path == "app.window.x":
        return state.window.x
    if property_path == "app.window.y":
        return state.window.y
    if property_path == "app.window.width":
        return state.window.width
    if property_path == "app.window.height":
        return state.window.height
    if property_path == "app.window.maximized":
        return state.window.maximized
    if property_path == "app.window.fullscreen":
        return state.window.fullscreen
    if property_path == "app.window.monitor":
        return state.window.monitor
    if property_path == "app.window.storage_key":
        return state.window.storage_key

    if property_path == "app.ui.theme":
        return state.ui.theme
    if property_path == "app.ui.font_scale":
        return state.ui.font_scale
    if property_path == "app.ui.dense_mode":
        return state.ui.dense_mode
    if property_path == "app.ui.accent_color":
        return state.ui.accent_color

    if property_path == "app.log.level":
        return state.log.level
    if property_path == "app.log.enable_console":
        return state.log.enable_console
    if property_path == "app.log.buffer_capacity":
        return state.log.buffer_capacity
    if property_path == "app.log.file_path":
        return normalize_path_for_toml(state.log.file_path)
    if property_path == "app.log.rotate_max_bytes":
        return state.log.rotate_max_bytes
    if property_path == "app.log.rotate_backup_count":
        return state.log.rotate_backup_count

    if property_path == "app.behavior.auto_save":
        return state.behavior.auto_save

    raise ValueError(f"Unsupported settings property path: {property_path!r}.")


def build_document_from_state(state: AppState) -> TOMLDocument:
    """Build a minimal TOML document from application state.

    Args:
        state: Application state used as source.

    Returns:
        TOML document containing known settings keys.
    """
    document = tomlkit.document()
    apply_state_to_document(document, state)
    return document


def build_settings_text_from_state(state: AppState) -> str:
    """Build TOML text from application state.

    Args:
        state: Application state used as source.

    Returns:
        TOML text containing known settings keys.
    """
    return tomlkit.dumps(build_document_from_state(state))
