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

from collections.abc import Callable, MutableMapping
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.items import Table
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState
from desktop_app.infrastructure.settings.schema import (
    SettingsGroup,
    get_legacy_paths_for_scope,
    get_settings_scope_paths,
)

type TomlScalar = str | int | float | bool
type StateValueReader = Callable[[AppState], TomlScalar]


_STATE_VALUE_READERS: dict[str, StateValueReader] = {
    "app.name": lambda state: state.meta.name,
    "app.version": lambda state: state.meta.version,
    "app.language": lambda state: state.meta.language,
    "app.first_run": lambda state: state.meta.first_run,
    "app.window.x": lambda state: state.window.x,
    "app.window.y": lambda state: state.window.y,
    "app.window.width": lambda state: state.window.width,
    "app.window.height": lambda state: state.window.height,
    "app.window.maximized": lambda state: state.window.maximized,
    "app.window.fullscreen": lambda state: state.window.fullscreen,
    "app.window.monitor": lambda state: state.window.monitor,
    "app.window.storage_key": lambda state: state.window.storage_key,
    "app.ui.theme": lambda state: state.ui.theme,
    "app.ui.font_scale": lambda state: state.ui.font_scale,
    "app.ui.dense_mode": lambda state: state.ui.dense_mode,
    "app.ui.accent_color": lambda state: state.ui.accent_color,
    "app.log.level": lambda state: state.log.level,
    "app.log.enable_console": lambda state: state.log.enable_console,
    "app.log.buffer_capacity": lambda state: state.log.buffer_capacity,
    "app.log.file_path": lambda state: normalize_path_for_toml(
        state.log.file_path,
    ),
    "app.log.rotate_max_bytes": lambda state: state.log.rotate_max_bytes,
    "app.log.rotate_backup_count": lambda state: state.log.rotate_backup_count,
    "app.behavior.auto_save": lambda state: state.behavior.auto_save,
}


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


def set_toml_value(
    document: TOMLDocument,
    dotted_path: str,
    value: TomlScalar,
) -> None:
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
    """Remove a TOML value selected by a dotted path when it exists.

    Args:
        document: TOML document to update.
        dotted_path: Dotted key path to remove.
    """
    parts = dotted_path.split(".")
    cursor: Any = document

    for part in parts[:-1]:
        if not isinstance(cursor, MutableMapping) or part not in cursor:
            return

        cursor = cursor[part]

    if isinstance(cursor, MutableMapping):
        cursor.pop(parts[-1], None)


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


def get_state_property_value(state: AppState, property_path: str) -> TomlScalar:
    """Return one TOML-compatible value from AppState.

    Args:
        state: Application state used as source.
        property_path: Supported property path to read.

    Returns:
        TOML-compatible value for the property path.

    Raises:
        ValueError: If the property path is not supported by this writer.
    """
    try:
        value_reader = _STATE_VALUE_READERS[property_path]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported settings property path: {property_path!r}."
        ) from exc

    return value_reader(state)


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
