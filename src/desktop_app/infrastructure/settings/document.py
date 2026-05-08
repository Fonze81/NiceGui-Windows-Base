# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/document.py
# Purpose:
# Build and update TOML documents used by settings.toml.
# Behavior:
# Creates required TOML tables, writes AppState values into known keys, and
# preserves comments and unknown keys when an existing document is saved again.
# Notes:
# Disk writes use a temporary file and atomic replacement to reduce the risk of
# corrupting settings.toml if the process stops during persistence.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.items import Table
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState


def ensure_parent_dir(file_path: Path) -> None:
    """Ensure that the parent directory for a file exists.

    Args:
        file_path: File path that will be written.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(file_path: Path, content: str) -> None:
    """Write text using an atomic file replacement.

    Args:
        file_path: Final destination file.
        content: Text content to write.
    """
    ensure_parent_dir(file_path)

    temporary_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    temporary_path.write_text(content, encoding="utf-8")
    temporary_path.replace(file_path)


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


def apply_state_to_document(document: TOMLDocument, state: AppState) -> None:
    """Update a TOML document with values from the application state.

    Args:
        document: TOML document to update.
        state: Application state used as source.
    """
    set_toml_value(document, "app.name", state.meta.name)
    set_toml_value(document, "app.version", state.meta.version)
    set_toml_value(document, "app.language", state.meta.language)
    set_toml_value(document, "app.first_run", state.meta.first_run)

    set_toml_value(document, "app.window.x", state.window.x)
    set_toml_value(document, "app.window.y", state.window.y)
    set_toml_value(document, "app.window.width", state.window.width)
    set_toml_value(document, "app.window.height", state.window.height)
    set_toml_value(document, "app.window.maximized", state.window.maximized)
    set_toml_value(document, "app.window.fullscreen", state.window.fullscreen)
    set_toml_value(document, "app.window.monitor", state.window.monitor)
    set_toml_value(document, "app.window.storage_key", state.window.storage_key)

    set_toml_value(document, "app.ui.theme", state.ui.theme)
    set_toml_value(document, "app.ui.font_scale", state.ui.font_scale)
    set_toml_value(document, "app.ui.dense_mode", state.ui.dense_mode)
    set_toml_value(document, "app.ui.accent_color", state.ui.accent_color)

    remove_toml_value(document, "app.log.name")
    remove_toml_value(document, "app.log.console")
    set_toml_value(document, "app.log.level", state.log.level)
    set_toml_value(document, "app.log.enable_console", state.log.enable_console)
    set_toml_value(document, "app.log.buffer_capacity", state.log.buffer_capacity)
    set_toml_value(
        document,
        "app.log.file_path",
        normalize_path_for_toml(state.log.file_path),
    )
    set_toml_value(document, "app.log.rotate_max_bytes", state.log.rotate_max_bytes)
    set_toml_value(
        document,
        "app.log.rotate_backup_count",
        state.log.rotate_backup_count,
    )

    set_toml_value(document, "app.behavior.auto_save", state.behavior.auto_save)


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
