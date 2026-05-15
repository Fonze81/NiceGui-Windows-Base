# -----------------------------------------------------------------------------
# File: src/desktop_app/application/diagnostics.py
# Purpose:
# Build support diagnostics snapshots from the current application state.
# Behavior:
# Converts AppState values into small immutable records that UI pages can render
# without knowing where each runtime value is stored.
# Notes:
# Keep this module free of NiceGUI imports. Diagnostics must not expose secrets;
# only stable technical metadata should be included here.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from desktop_app.core.state import AppState

_MISSING_VALUE: Final[str] = "Not resolved"


@dataclass(frozen=True, slots=True)
class DiagnosticItem:
    """Represent one diagnostic label/value pair.

    Attributes:
        label: User-facing diagnostic label.
        value: User-facing diagnostic value.
    """

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class DiagnosticSection:
    """Represent a group of related diagnostics.

    Attributes:
        title: User-facing section title.
        description: Short explanation shown above the rows.
        items: Ordered diagnostic items.
    """

    title: str
    description: str
    items: tuple[DiagnosticItem, ...]


def create_diagnostic_item(label: str, value: object) -> DiagnosticItem:
    """Create a diagnostic item from any displayable value.

    Args:
        label: User-facing diagnostic label.
        value: Value converted to text for display.

    Returns:
        Diagnostic item with a string value.
    """
    return DiagnosticItem(label=label, value=str(value))


def format_optional_path(path: Path | None) -> str:
    """Return a readable path value for diagnostics.

    Args:
        path: Optional path value.

    Returns:
        String path or a fallback label.
    """
    return str(path) if path is not None else _MISSING_VALUE


def format_enabled(value: bool) -> str:
    """Return a readable enabled/disabled value.

    Args:
        value: Boolean flag.

    Returns:
        Enabled or Disabled.
    """
    return "Enabled" if value else "Disabled"


def format_yes_no(value: bool) -> str:
    """Return a readable yes/no value.

    Args:
        value: Boolean flag.

    Returns:
        Yes or No.
    """
    return "Yes" if value else "No"


def format_file_status(path: Path | None) -> str:
    """Return a readable file-system status for a path.

    Args:
        path: Optional file path.

    Returns:
        Diagnostic file status.
    """
    if path is None:
        return _MISSING_VALUE

    if path.is_file():
        return "File found"

    if path.exists():
        return "Path exists but is not a file"

    return "File not found"


def build_runtime_section(state: AppState) -> DiagnosticSection:
    """Build runtime diagnostics.

    Args:
        state: Application state used as source.

    Returns:
        Runtime diagnostic section.
    """
    item = create_diagnostic_item
    runtime_mode = "Native" if state.runtime.native_mode else "Web"

    return DiagnosticSection(
        title="Runtime",
        description="Execution mode and startup values resolved for this run.",
        items=(
            item("Application", f"{state.meta.name} {state.meta.version}"),
            item("Startup source", state.runtime.startup_source or _MISSING_VALUE),
            item("Runtime mode", runtime_mode),
            item("Reload", format_enabled(state.runtime.reload_enabled)),
            item("Port", state.runtime.port),
            item("Theme", state.ui.theme),
            item("Dense mode", format_enabled(state.ui.dense_mode)),
        ),
    )


def build_path_section(state: AppState) -> DiagnosticSection:
    """Build path diagnostics.

    Args:
        state: Application state used as source.

    Returns:
        Path diagnostic section.
    """
    item = create_diagnostic_item
    settings_path = state.settings.file_path
    log_path = state.log.effective_file_path

    return DiagnosticSection(
        title="Runtime paths",
        description="Effective process, settings, asset, and log paths.",
        items=(
            item("Settings file", format_optional_path(settings_path)),
            item("Settings status", format_file_status(settings_path)),
            item("Log file", format_optional_path(log_path)),
            item("Log file status", format_file_status(log_path)),
            item(
                "Working directory",
                format_optional_path(state.paths.working_directory),
            ),
            item("Executable", format_optional_path(state.paths.executable_path)),
            item("Icon", format_optional_path(state.assets.icon_path)),
            item("Page image", format_optional_path(state.assets.page_image_path)),
            item("Splash image", format_optional_path(state.assets.splash_image_path)),
        ),
    )


def build_lifecycle_section(state: AppState) -> DiagnosticSection:
    """Build lifecycle diagnostics.

    Args:
        state: Application state used as source.

    Returns:
        Lifecycle diagnostic section.
    """
    item = create_diagnostic_item
    lifecycle = state.lifecycle

    return DiagnosticSection(
        title="Lifecycle",
        description="High-level lifecycle flags captured during this process.",
        items=(
            item("Handlers registered", format_yes_no(lifecycle.handlers_registered)),
            item(
                "Native handlers",
                format_yes_no(lifecycle.native_handlers_registered),
            ),
            item("Runtime started", format_yes_no(lifecycle.runtime_started)),
            item("Client connected", format_yes_no(lifecycle.client_connected)),
            item("Native window opened", format_yes_no(lifecycle.native_window_opened)),
            item("Native window loaded", format_yes_no(lifecycle.native_window_loaded)),
            item(
                "Window state persisted",
                format_yes_no(lifecycle.native_window_state_persisted),
            ),
            item("Splash registered", format_yes_no(lifecycle.splash_registered)),
            item("Splash closed", format_yes_no(lifecycle.splash_closed)),
        ),
    )


def build_logging_section(state: AppState) -> DiagnosticSection:
    """Build logging diagnostics.

    Args:
        state: Application state used as source.

    Returns:
        Logging diagnostic section.
    """
    item = create_diagnostic_item

    return DiagnosticSection(
        title="Logging",
        description="Logger configuration and runtime file logging status.",
        items=(
            item("Level", state.log.level),
            item("Console", format_enabled(state.log.enable_console)),
            item("File logging", format_enabled(state.log.file_logging_enabled)),
            item("Early buffering", format_enabled(state.log.early_buffering_enabled)),
            item("Configured file", format_optional_path(state.log.file_path)),
            item("Effective file", format_optional_path(state.log.effective_file_path)),
            item("Rotation size", state.log.rotate_max_bytes),
            item("Rotation backups", state.log.rotate_backup_count),
        ),
    )


def build_settings_section(state: AppState) -> DiagnosticSection:
    """Build settings diagnostics.

    Args:
        state: Application state used as source.

    Returns:
        Settings diagnostic section.
    """
    item = create_diagnostic_item
    settings = state.settings

    return DiagnosticSection(
        title="Settings",
        description="Latest settings load and save metadata.",
        items=(
            item("Using defaults", format_yes_no(settings.using_defaults)),
            item("File exists", format_yes_no(settings.file_exists)),
            item("Last load", format_yes_no(settings.last_load_ok)),
            item("Loaded scope", settings.last_loaded_scope or _MISSING_VALUE),
            item("Last save", format_yes_no(settings.last_save_ok)),
            item("Saved scope", settings.last_saved_scope or _MISSING_VALUE),
            item("Last error", settings.last_error or "None"),
        ),
    )


def build_diagnostics_sections(state: AppState) -> tuple[DiagnosticSection, ...]:
    """Build the full diagnostics snapshot for rendering.

    Args:
        state: Application state used as source.

    Returns:
        Ordered diagnostic sections.
    """
    return (
        build_runtime_section(state),
        build_path_section(state),
        build_lifecycle_section(state),
        build_logging_section(state),
        build_settings_section(state),
    )
