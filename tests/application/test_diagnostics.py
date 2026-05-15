# -----------------------------------------------------------------------------
# File: tests/application/test_diagnostics.py
# Purpose:
# Validate application diagnostics snapshot generation.
# Behavior:
# Exercises formatting helpers and section builders without importing NiceGUI.
# Notes:
# Diagnostics tests keep support data generation independent from UI rendering.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

from desktop_app.application.diagnostics import (
    build_diagnostics_sections,
    format_enabled,
    format_file_status,
    format_optional_path,
    format_yes_no,
)
from desktop_app.core.state import AppState


def test_format_helpers_return_readable_values(tmp_path: Path) -> None:
    """Formatting helpers return stable support labels."""
    log_file = tmp_path / "app.log"
    log_file.write_text("log", encoding="utf-8")
    directory = tmp_path / "logs"
    directory.mkdir()

    assert format_optional_path(log_file) == str(log_file)
    assert format_optional_path(None) == "Not resolved"
    assert format_enabled(True) == "Enabled"
    assert format_enabled(False) == "Disabled"
    assert format_yes_no(True) == "Yes"
    assert format_yes_no(False) == "No"
    assert format_file_status(None) == "Not resolved"
    assert format_file_status(log_file) == "File found"
    assert format_file_status(directory) == "Path exists but is not a file"
    assert format_file_status(tmp_path / "missing.log") == "File not found"


def test_build_diagnostics_sections_returns_grouped_state_snapshot(
    tmp_path: Path,
) -> None:
    """Diagnostics sections expose grouped application state."""
    log_file = tmp_path / "app.log"
    log_file.write_text("one", encoding="utf-8")
    state = AppState()
    state.meta.name = "Example"
    state.meta.version = "1.2.3"
    state.runtime.startup_source = "tests"
    state.runtime.native_mode = False
    state.runtime.port = 8123
    state.log.effective_file_path = log_file
    state.settings.last_loaded_scope = "all"
    state.lifecycle.handlers_registered = True

    sections = build_diagnostics_sections(state)

    assert [section.title for section in sections] == [
        "Runtime",
        "Runtime paths",
        "Lifecycle",
        "Logging",
        "Settings",
    ]
    runtime_items = {item.label: item.value for item in sections[0].items}
    path_items = {item.label: item.value for item in sections[1].items}
    lifecycle_items = {item.label: item.value for item in sections[2].items}

    assert runtime_items["Application"] == "Example 1.2.3"
    assert runtime_items["Startup source"] == "tests"
    assert runtime_items["Runtime mode"] == "Web"
    assert runtime_items["Port"] == "8123"
    assert path_items["Log file status"] == "File found"
    assert lifecycle_items["Handlers registered"] == "Yes"
