# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test_service.py
# Purpose:
# Validate settings service load and save orchestration.
# Behavior:
# Exercises successful paths, fallback paths, scoped operations, path resolution,
# and error handling without coupling tests to low-level TOML writer internals.
# Notes:
# Tests use temporary files and AppState instances to avoid modifying the real
# user settings.toml file during development or CI execution.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
import tomlkit
from tomlkit.toml_document import TOMLDocument

from desktop_app.core.state import AppState
from desktop_app.infrastructure.settings import service
from desktop_app.infrastructure.settings.schema import SettingsGroup, SettingsScopeError


def _write_settings_file(settings_file_path: Path, content: str | None = None) -> None:
    """Write a small settings TOML file for service tests.

    Args:
        settings_file_path: Destination settings file path.
        content: Optional TOML content. A minimal valid file is used when omitted.
    """
    settings_file_path.write_text(content or '[app]\nname = "Loaded App"\n', "utf-8")


def _unwrap_document(document: TOMLDocument) -> dict[str, Any]:
    """Return a plain dictionary from a TOML document.

    Args:
        document: TOML document parsed or built with tomlkit.

    Returns:
        Plain dictionary representation used by typed assertions.
    """
    return cast(dict[str, Any], document.unwrap())


def _read_saved_settings_data(settings_file_path: Path) -> dict[str, Any]:
    """Read a saved TOML settings file as a plain dictionary.

    Args:
        settings_file_path: TOML settings file path.

    Returns:
        Plain dictionary with the saved settings content.
    """
    document = tomlkit.parse(settings_file_path.read_text(encoding="utf-8"))
    return _unwrap_document(document)


def test_build_initial_settings_document_uses_bundled_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the bundled template when it is present and valid."""
    state = AppState()

    monkeypatch.setattr(
        service, "read_bundled_settings_text", lambda: "[app]\nname='X'"
    )

    document = service.build_initial_settings_document(state)
    document_data = _unwrap_document(document)

    assert document_data["app"]["name"] == "X"


def test_build_initial_settings_document_falls_back_when_template_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build settings from AppState when no bundled template is available."""
    state = AppState()
    fallback_document = tomlkit.document()
    fallback_document["fallback"] = True

    monkeypatch.setattr(service, "read_bundled_settings_text", lambda: None)
    monkeypatch.setattr(
        service,
        "build_document_from_state",
        lambda received_state: fallback_document,
    )

    document = service.build_initial_settings_document(state)

    assert document is fallback_document


def test_build_initial_settings_document_falls_back_when_template_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build settings from AppState when the bundled TOML cannot be parsed."""
    state = AppState()
    fallback_document = tomlkit.document()
    fallback_document["fallback"] = True

    monkeypatch.setattr(service, "read_bundled_settings_text", lambda: "invalid =")
    monkeypatch.setattr(
        service,
        "build_document_from_state",
        lambda received_state: fallback_document,
    )

    document = service.build_initial_settings_document(state)

    assert document is fallback_document


def test_load_settings_uses_defaults_when_file_is_missing(tmp_path: Path) -> None:
    """Keep defaults in memory when settings.toml does not exist."""
    state = AppState()
    state.settings_validation.warnings.append("old warning")
    settings_file_path = tmp_path / "missing.toml"

    result = service.load_settings(settings_path=str(settings_file_path), state=state)

    assert result is True
    assert state.settings.file_path == settings_file_path.resolve()
    assert state.settings.file_exists is False
    assert state.settings.using_defaults is True
    assert state.settings.last_load_ok is True
    assert state.settings.last_loaded_scope == "all"
    assert state.settings.last_error is None
    assert state.settings_validation.warnings == []
    assert state.settings_validation.last_validated_scope == "all"
    assert state.settings_validation.last_validated_at is not None
    assert state.status.current_message is not None
    assert state.status.current_message.level == "info"


def test_load_settings_uses_global_state_and_default_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Use get_app_state and the default path when arguments are omitted."""
    state = AppState()
    settings_file_path = tmp_path / "default-settings.toml"

    monkeypatch.setattr(service, "get_app_state", lambda: state)
    monkeypatch.setattr(
        service,
        "resolve_default_settings_path",
        lambda: settings_file_path,
    )

    result = service.load_settings()

    assert result is True
    assert state.settings.file_path == settings_file_path.resolve()
    assert state.settings.last_loaded_scope == "all"


def test_load_settings_applies_existing_file_with_group_scope(tmp_path: Path) -> None:
    """Apply only the selected settings group from an existing file."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(settings_file_path, '[app]\n[app.ui]\ntheme = "dark"\n')

    result = service.load_settings_group(
        "ui",
        settings_path=settings_file_path,
        state=state,
    )

    assert result is True
    assert state.ui.theme == "dark"
    assert state.settings.file_exists is True
    assert state.settings.using_defaults is False
    assert state.settings.last_load_ok is True
    assert state.settings.last_loaded_scope == "group:ui"
    assert state.status.current_message is not None
    assert state.status.current_message.level == "success"


def test_load_setting_property_applies_existing_file_property(tmp_path: Path) -> None:
    """Apply only one selected settings property from an existing file."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(settings_file_path, "[app]\n[app.ui]\nfont_scale = 1.25\n")

    result = service.load_setting_property(
        "app.ui.font_scale",
        settings_path=settings_file_path,
        state=state,
    )

    assert result is True
    assert state.ui.font_scale == 1.25
    assert state.settings.last_loaded_scope == "property:app.ui.font_scale"


def test_load_settings_returns_false_when_file_cannot_be_parsed(tmp_path: Path) -> None:
    """Report a controlled failure when TOML parsing fails."""
    state = AppState()
    settings_file_path = tmp_path / "invalid.toml"
    _write_settings_file(settings_file_path, "invalid =")

    result = service.load_settings(settings_path=settings_file_path, state=state)

    assert result is False
    assert state.settings.last_load_ok is False
    assert state.settings.using_defaults is True
    assert state.settings.last_error is not None
    assert state.settings.last_error.startswith("Failed to load settings:")
    assert state.status.current_message is not None
    assert state.status.current_message.level == "error"


def test_load_settings_reraises_scope_error_from_mapper(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Do not hide scope errors raised while applying parsed settings."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(settings_file_path)

    def raise_scope_error(*args: Any, **kwargs: Any) -> None:
        """Raise a scope error from a patched mapper call."""
        raise SettingsScopeError("invalid scope")

    monkeypatch.setattr(service, "apply_settings_to_state", raise_scope_error)

    with pytest.raises(SettingsScopeError, match="invalid scope"):
        service.load_settings(settings_path=settings_file_path, state=state)


def test_load_settings_rejects_invalid_group_before_filesystem_fallback(
    tmp_path: Path,
) -> None:
    """Reject an unsupported load group before reading the filesystem."""
    state = AppState()
    settings_file_path = tmp_path / "missing.toml"
    invalid_group = cast(SettingsGroup, "invalid")

    with pytest.raises(SettingsScopeError, match="Unsupported settings group"):
        service.load_settings(
            settings_path=settings_file_path,
            state=state,
            group=invalid_group,
        )


def test_load_settings_rejects_unknown_property_before_filesystem_fallback(
    tmp_path: Path,
) -> None:
    """Reject an unsupported load property before reading the filesystem."""
    state = AppState()
    settings_file_path = tmp_path / "missing.toml"

    with pytest.raises(SettingsScopeError, match="Unsupported settings property path"):
        service.load_settings(
            settings_path=settings_file_path,
            state=state,
            property_path="app.unknown",
        )


def test_load_settings_rejects_mixed_group_and_property_before_fallback(
    tmp_path: Path,
) -> None:
    """Reject load calls that mix group and property scopes."""
    state = AppState()
    settings_file_path = tmp_path / "missing.toml"

    with pytest.raises(SettingsScopeError, match="Use either a settings group"):
        service.load_settings(
            settings_path=settings_file_path,
            state=state,
            group="ui",
            property_path="app.ui.theme",
        )


def test_save_settings_updates_existing_file_with_explicit_path(tmp_path: Path) -> None:
    """Save the selected AppState values to an existing settings file."""
    state = AppState()
    state.meta.name = "Saved App"
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(settings_file_path)

    result = service.save_settings(settings_path=str(settings_file_path), state=state)

    assert result is True
    saved_data = _read_saved_settings_data(settings_file_path)
    assert saved_data["app"]["name"] == "Saved App"
    assert state.settings.file_path == settings_file_path.resolve()
    assert state.settings.file_exists is True
    assert state.settings.using_defaults is False
    assert state.settings.last_save_ok is True
    assert state.settings.last_saved_scope == "all"
    assert state.status.current_message is not None
    assert state.status.current_message.level == "success"


def test_save_settings_uses_state_path_when_explicit_path_is_missing(
    tmp_path: Path,
) -> None:
    """Reuse the path already stored in AppState when saving settings."""
    state = AppState()
    settings_file_path = tmp_path / "state-settings.toml"
    state.settings.file_path = settings_file_path

    result = service.save_settings(state=state)

    assert result is True
    assert settings_file_path.exists()
    assert state.settings.file_path == settings_file_path.resolve()


def test_save_settings_uses_global_state_and_default_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Use get_app_state and default path when save arguments are omitted."""
    state = AppState()
    settings_file_path = tmp_path / "default-settings.toml"

    monkeypatch.setattr(service, "get_app_state", lambda: state)
    monkeypatch.setattr(
        service,
        "resolve_default_settings_path",
        lambda: settings_file_path,
    )

    result = service.save_settings()

    assert result is True
    assert settings_file_path.exists()
    assert state.settings.file_path == settings_file_path.resolve()


def test_save_settings_group_updates_only_selected_group(tmp_path: Path) -> None:
    """Save one settings group using the public group wrapper."""
    state = AppState()
    state.ui.theme = "dark"
    state.log.level = "DEBUG"
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(
        settings_file_path,
        '[app]\n[app.ui]\ntheme = "light"\n[app.log]\nlevel = "INFO"\n',
    )

    result = service.save_settings_group(
        "ui",
        settings_path=settings_file_path,
        state=state,
    )

    assert result is True
    saved_data = _read_saved_settings_data(settings_file_path)
    assert saved_data["app"]["ui"]["theme"] == "dark"
    assert saved_data["app"]["log"]["level"] == "INFO"
    assert state.settings.last_saved_scope == "group:ui"


def test_save_setting_property_updates_only_selected_property(tmp_path: Path) -> None:
    """Save one settings property using the public property wrapper."""
    state = AppState()
    state.ui.accent_color = "#111111"
    state.ui.theme = "dark"
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(
        settings_file_path,
        ('[app]\n[app.ui]\naccent_color = "#2563EB"\ntheme = "light"\n'),
    )

    result = service.save_setting_property(
        "app.ui.accent_color",
        settings_path=settings_file_path,
        state=state,
    )

    assert result is True
    saved_data = _read_saved_settings_data(settings_file_path)
    assert saved_data["app"]["ui"]["accent_color"] == "#111111"
    assert saved_data["app"]["ui"]["theme"] == "light"
    assert state.settings.last_saved_scope == "property:app.ui.accent_color"


def test_save_settings_returns_false_when_write_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Report a controlled failure when atomic writing fails."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"

    def fail_write(*args: Any, **kwargs: Any) -> None:
        """Raise an I/O error from a patched write operation."""
        raise OSError("disk full")

    monkeypatch.setattr(service, "atomic_write_text", fail_write)

    result = service.save_settings(settings_path=settings_file_path, state=state)

    assert result is False
    assert state.settings.last_save_ok is False
    assert state.settings.last_error == "Failed to save settings: disk full"
    assert state.status.current_message is not None
    assert state.status.current_message.level == "error"


def test_save_settings_reraises_scope_error_from_document_writer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Do not hide scope errors raised while applying state to TOML."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"
    _write_settings_file(settings_file_path)

    def raise_scope_error(*args: Any, **kwargs: Any) -> None:
        """Raise a scope error from a patched TOML writer call."""
        raise SettingsScopeError("invalid save scope")

    monkeypatch.setattr(service, "apply_state_to_document", raise_scope_error)

    with pytest.raises(SettingsScopeError, match="invalid save scope"):
        service.save_settings(settings_path=settings_file_path, state=state)


def test_save_settings_rejects_invalid_group_before_writing(tmp_path: Path) -> None:
    """Reject an unsupported save group before writing to the filesystem."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"
    invalid_group = cast(SettingsGroup, "invalid")

    with pytest.raises(SettingsScopeError, match="Unsupported settings group"):
        service.save_settings(
            settings_path=settings_file_path,
            state=state,
            group=invalid_group,
        )

    assert not settings_file_path.exists()


def test_save_settings_rejects_unknown_property_before_writing(tmp_path: Path) -> None:
    """Reject an unsupported save property before writing to the filesystem."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"

    with pytest.raises(SettingsScopeError, match="Unsupported settings property path"):
        service.save_settings(
            settings_path=settings_file_path,
            state=state,
            property_path="app.unknown",
        )

    assert not settings_file_path.exists()


def test_save_settings_rejects_mixed_group_and_property_before_writing(
    tmp_path: Path,
) -> None:
    """Reject save calls that mix group and property scopes."""
    state = AppState()
    settings_file_path = tmp_path / "settings.toml"

    with pytest.raises(SettingsScopeError, match="Use either a settings group"):
        service.save_settings(
            settings_path=settings_file_path,
            state=state,
            group="ui",
            property_path="app.ui.theme",
        )

    assert not settings_file_path.exists()
