# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test_toml_document.py
# Purpose:
# Validate settings TOML document creation and scoped state persistence.
# Behavior:
# Exercises table creation, dotted-path writes, legacy key cleanup, path
# normalization, full document generation, scoped saves, and unsupported paths.
# Notes:
# These tests intentionally use real AppState instances and tomlkit documents to
# keep coverage close to the production behavior without touching the file system.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, cast

import pytest
import tomlkit
from tomlkit.items import Table
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState
from desktop_app.infrastructure.settings import toml_document as toml_document_module
from desktop_app.infrastructure.settings.schema import ALL_PROPERTY_PATHS
from desktop_app.infrastructure.settings.toml_document import (
    apply_state_property_to_document,
    apply_state_to_document,
    build_document_from_state,
    build_settings_text_from_state,
    ensure_toml_table,
    get_state_property_value,
    normalize_path_for_toml,
    remove_toml_value,
    set_toml_value,
)

type TomlMapping = MutableMapping[str, Any]


def build_custom_state() -> AppState:
    """Return an application state with non-default persisted values.

    Returns:
        AppState configured with distinct values for every persisted property.
    """
    state = AppState()
    state.meta.name = "Test App"
    state.meta.version = "9.8.7"
    state.meta.language = "pt-BR"
    state.meta.first_run = False

    state.window.x = 11
    state.window.y = 22
    state.window.width = 1280
    state.window.height = 800
    state.window.maximized = True
    state.window.fullscreen = False
    state.window.monitor = 2
    state.window.persist_state = False
    state.window.storage_key = "custom_window_key"

    state.ui.theme = "dark"
    state.ui.font_scale = 1.25
    state.ui.dense_mode = True
    state.ui.accent_color = "#ABCDEF"

    state.log.level = "DEBUG"
    state.log.enable_console = False
    state.log.buffer_capacity = 123
    state.log.file_path = Path("runtime") / "logs" / "custom.log"
    state.log.rotate_max_bytes = "10 MB"
    state.log.rotate_backup_count = 7

    state.behavior.auto_save = False
    return state


def get_toml_value(document: TOMLDocument, dotted_path: str) -> Any:
    """Return a value from a TOML document using a dotted path.

    Args:
        document: TOML document to inspect.
        dotted_path: Dotted key path to read.

    Returns:
        Value stored in the selected path.
    """
    cursor = cast(TomlMapping, document)
    parts = dotted_path.split(".")

    for part in parts[:-1]:
        cursor = cast(TomlMapping, cursor[part])

    return cursor[parts[-1]]


def has_toml_value(document: TOMLDocument, dotted_path: str) -> bool:
    """Return whether a TOML document contains a dotted path.

    Args:
        document: TOML document to inspect.
        dotted_path: Dotted key path to check.

    Returns:
        True when the selected path exists; otherwise, False.
    """
    cursor = cast(TomlMapping, document)
    parts = dotted_path.split(".")

    for part in parts[:-1]:
        next_value = cursor.get(part)
        if not isinstance(next_value, MutableMapping):
            return False

        cursor = cast(TomlMapping, next_value)

    return parts[-1] in cursor


def test_ensure_toml_table_returns_existing_table() -> None:
    """Ensure an existing table is reused instead of replaced."""
    document = tomlkit.document()
    existing_table = tomlkit.table()
    existing_table["name"] = "Existing"
    document["app"] = existing_table

    result = ensure_toml_table(document, "app")

    assert result is existing_table
    assert get_toml_value(document, "app.name") == "Existing"


def test_ensure_toml_table_replaces_non_table_value() -> None:
    """Ensure scalar values are replaced when a table is required."""
    document = tomlkit.document()
    document["app"] = "invalid"

    result = ensure_toml_table(document, "app")

    assert isinstance(result, Table)
    assert get_toml_value(document, "app") is result


def test_set_toml_value_creates_nested_tables() -> None:
    """Set a nested TOML value through a dotted path."""
    document = tomlkit.document()

    set_toml_value(document, "app.window.width", 1440)

    assert get_toml_value(document, "app.window.width") == 1440


def test_remove_toml_value_removes_existing_nested_key() -> None:
    """Remove an existing nested TOML value while preserving sibling keys."""
    document = tomlkit.parse(
        """
        [app.log]
        name = "legacy"
        level = "INFO"
        """
    )

    remove_toml_value(document, "app.log.name")

    assert not has_toml_value(document, "app.log.name")
    assert get_toml_value(document, "app.log.level") == "INFO"


def test_remove_toml_value_ignores_missing_path() -> None:
    """Ignore missing nested paths without raising errors."""
    document = tomlkit.parse(
        """
        [app.ui]
        theme = "light"
        """
    )

    remove_toml_value(document, "app.log.console")

    assert get_toml_value(document, "app.ui.theme") == "light"


def test_remove_toml_value_ignores_non_mapping_parent() -> None:
    """Ignore removal when an intermediate value is not a mapping."""
    document = tomlkit.document()
    document["app"] = "not-a-table"

    remove_toml_value(document, "app.log.console")

    assert get_toml_value(document, "app") == "not-a-table"


def test_normalize_path_for_toml_uses_forward_slashes() -> None:
    """Normalize paths for stable TOML output."""
    assert normalize_path_for_toml(Path("logs") / "app.log") == "logs/app.log"


def test_get_state_property_value_returns_every_supported_value() -> None:
    """Read every persisted property path from AppState."""
    state = build_custom_state()

    expected_values = {
        "app.name": "Test App",
        "app.version": "9.8.7",
        "app.language": "pt-BR",
        "app.first_run": False,
        "app.window.x": 11,
        "app.window.y": 22,
        "app.window.width": 1280,
        "app.window.height": 800,
        "app.window.maximized": True,
        "app.window.fullscreen": False,
        "app.window.monitor": 2,
        "app.window.persist_state": False,
        "app.window.storage_key": "custom_window_key",
        "app.ui.theme": "dark",
        "app.ui.font_scale": 1.25,
        "app.ui.dense_mode": True,
        "app.ui.accent_color": "#ABCDEF",
        "app.log.level": "DEBUG",
        "app.log.enable_console": False,
        "app.log.buffer_capacity": 123,
        "app.log.file_path": "runtime/logs/custom.log",
        "app.log.rotate_max_bytes": "10 MB",
        "app.log.rotate_backup_count": 7,
        "app.behavior.auto_save": False,
    }

    assert set(expected_values) == set(ALL_PROPERTY_PATHS)
    assert {
        path: get_state_property_value(state, path) for path in ALL_PROPERTY_PATHS
    } == expected_values


def test_get_state_property_value_rejects_unsupported_path() -> None:
    """Reject unsupported paths with a clear exception."""
    with pytest.raises(ValueError, match="Unsupported settings property path"):
        get_state_property_value(AppState(), "app.unknown")


def test_apply_state_property_to_document_updates_one_property() -> None:
    """Write one selected state property into the TOML document."""
    document = tomlkit.document()
    state = build_custom_state()

    apply_state_property_to_document(document, state, "app.ui.theme")

    assert get_toml_value(document, "app.ui.theme") == "dark"
    assert not has_toml_value(document, "app.log")


def test_apply_state_to_document_writes_all_properties_and_removes_legacy_keys() -> (
    None
):
    """Write all supported properties and remove legacy keys."""
    document = tomlkit.parse(
        """
        [app]
        unknown = "preserved"

        [app.log]
        name = "legacy-name"
        console = true
        custom = "preserved"
        """
    )
    state = build_custom_state()

    apply_state_to_document(document, state)

    assert get_toml_value(document, "app.unknown") == "preserved"
    assert get_toml_value(document, "app.log.custom") == "preserved"
    assert not has_toml_value(document, "app.log.name")
    assert not has_toml_value(document, "app.log.console")
    assert get_toml_value(document, "app.name") == "Test App"
    assert get_toml_value(document, "app.window.width") == 1280
    assert get_toml_value(document, "app.ui.theme") == "dark"
    assert get_toml_value(document, "app.log.file_path") == "runtime/logs/custom.log"
    assert get_toml_value(document, "app.behavior.auto_save") is False


def test_apply_state_to_document_writes_only_selected_group() -> None:
    """Write only the selected settings group."""
    document = tomlkit.document()
    state = build_custom_state()

    apply_state_to_document(document, state, group="ui")

    assert get_toml_value(document, "app.ui.theme") == "dark"
    assert get_toml_value(document, "app.ui.font_scale") == 1.25
    assert not has_toml_value(document, "app.log")


def test_apply_state_to_document_writes_one_selected_property() -> None:
    """Write only one selected settings property."""
    document = tomlkit.document()
    state = build_custom_state()

    apply_state_to_document(document, state, property_path="app.log.level")

    assert get_toml_value(document, "app.log.level") == "DEBUG"
    assert not has_toml_value(document, "app.ui")


def test_apply_state_to_document_removes_log_legacy_keys_for_log_property() -> None:
    """Remove log legacy keys even when saving one log property."""
    document = tomlkit.parse(
        """
        [app.log]
        name = "legacy"
        console = false
        custom = "preserved"
        """
    )
    state = build_custom_state()

    apply_state_to_document(document, state, property_path="app.log.level")

    assert not has_toml_value(document, "app.log.name")
    assert not has_toml_value(document, "app.log.console")
    assert get_toml_value(document, "app.log.custom") == "preserved"
    assert get_toml_value(document, "app.log.level") == "DEBUG"


def test_build_document_from_state_returns_toml_document() -> None:
    """Build a complete TOML document from AppState."""
    document = build_document_from_state(build_custom_state())

    assert isinstance(document, TOMLDocument)
    assert get_toml_value(document, "app.name") == "Test App"
    assert get_toml_value(document, "app.behavior.auto_save") is False


def test_build_settings_text_from_state_returns_serialized_toml() -> None:
    """Serialize AppState into TOML text."""
    settings_text = build_settings_text_from_state(build_custom_state())

    assert 'name = "Test App"' in settings_text
    assert 'file_path = "runtime/logs/custom.log"' in settings_text
    assert "auto_save = false" in settings_text


def test_apply_state_to_document_handles_empty_scope_without_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Handle an empty property scope without changing the TOML document."""
    state = AppState()
    document = tomlkit.document()
    document["existing"] = "value"

    monkeypatch.setattr(
        toml_document_module,
        "get_settings_scope_paths",
        lambda *, group=None, property_path=None: (),
    )

    toml_document_module.apply_state_to_document(document, state)

    document_data = cast(dict[str, Any], document.unwrap())

    assert document_data == {"existing": "value"}
