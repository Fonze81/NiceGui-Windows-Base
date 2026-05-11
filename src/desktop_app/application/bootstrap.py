# -----------------------------------------------------------------------------
# File: src/desktop_app/application/bootstrap.py
# Purpose:
# Prepare early application startup dependencies before NiceGUI starts.
# Behavior:
# Loads persisted settings, applies native window arguments early, resolves
# runtime paths, and configures the official logging subsystem used by the app.
# Notes:
# Keep this module free of UI composition. NiceGUI page construction belongs in
# desktop_app.ui, while app.py should only orchestrate the startup sequence.
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import sys
from pathlib import Path

from desktop_app.core.runtime import is_frozen_executable
from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.logger import (
    logger_bootstrap,
    logger_enable_file_logging,
    logger_get_logger,
    resolve_log_file_path,
)
from desktop_app.infrastructure.native_window_state import (
    apply_native_window_args_from_state,
)
from desktop_app.infrastructure.settings import (
    build_logger_config_from_state,
    load_settings,
)
from desktop_app.infrastructure.settings.paths import get_pyinstaller_temp_dir

logger = logger_get_logger(__name__)


def prepare_native_window_arguments_before_main(
    *, state: AppState | None = None
) -> None:
    """Load settings and apply native window arguments before ``main`` runs.

    NiceGUI native mode reads ``app.native.window_args`` while creating the
    pywebview window. Applying these values during module import keeps
    persisted coordinates available before ``ui.run`` is called.

    Args:
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()
    if not current_state.settings.last_load_ok:
        load_settings(state=current_state)
    apply_native_window_args_from_state(state=current_state)


def configure_logging(*, state: AppState | None = None) -> Path:
    """Load settings and configure the official logging subsystem.

    Args:
        state: Optional application state. Uses the global state when omitted.

    Returns:
        The configured log file path.
    """
    current_state = state if state is not None else get_app_state()
    _resolve_runtime_paths(current_state)

    if not current_state.settings.last_load_ok:
        load_settings(state=current_state)
    current_state.paths.settings_file_path = current_state.settings.file_path

    frozen_executable = is_frozen_executable()
    log_file_path = resolve_log_file_path(
        current_state.log.file_path,
        frozen_executable=frozen_executable,
    )
    _store_log_file_path(current_state, log_file_path)

    logger_bootstrap(
        build_logger_config_from_state(
            current_state,
            file_path=log_file_path,
            enable_console=current_state.log.enable_console and not frozen_executable,
        )
    )

    _enable_file_logging(current_state)
    _log_startup_environment(current_state, log_file_path)

    return log_file_path


def _resolve_runtime_paths(state: AppState) -> None:
    """Resolve process paths needed during startup.

    Args:
        state: Application state to update.
    """
    state.paths.working_directory = Path.cwd()
    state.paths.executable_path = Path(sys.executable).resolve()
    state.paths.pyinstaller_temp_dir = get_pyinstaller_temp_dir()


def _store_log_file_path(state: AppState, log_file_path: Path) -> None:
    """Store the effective log file path in state.

    Args:
        state: Application state to update.
        log_file_path: Effective log file path resolved for this process.
    """
    state.log.effective_file_path = log_file_path
    state.paths.log_file_path = log_file_path


def _enable_file_logging(state: AppState) -> None:
    """Enable file logging and mirror the result in state.

    Args:
        state: Application state to update.
    """
    state.log.file_logging_enabled = logger_enable_file_logging()
    state.log.early_buffering_enabled = not state.log.file_logging_enabled
    if not state.log.file_logging_enabled:
        logger.warning(
            "File logging could not be enabled. Continuing without log file."
        )


def _log_startup_environment(state: AppState, log_file_path: Path) -> None:
    """Write startup diagnostics after logging is configured.

    Args:
        state: Current application state.
        log_file_path: Effective log file path used by this process.
    """
    logger.info("Logging initialized for %s.", state.meta.name)
    logger.debug("Settings file ready at: %s", state.settings.file_path)
    logger.debug("Log file ready at: %s", log_file_path)
    logger.debug("Application working directory: %s", Path.cwd())
    logger.debug("Python executable in use: %s", sys.executable)
    logger.debug("Command-line arguments received: %s", sys.argv)
    logger.debug("Frozen executable marker: %s", getattr(sys, "frozen", None))
    logger.debug(
        "PyInstaller extraction directory marker: %s",
        getattr(sys, "_MEIPASS", None),
    )
    logger.debug("Operating system process ID: %s", os.getpid())
