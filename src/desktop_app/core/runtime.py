# -----------------------------------------------------------------------------
# File: src/desktop_app/core/runtime.py
# Purpose:
# Identify how the application is currently being executed.
# Behavior:
# Reads Python runtime information such as sys.argv, sys.executable, explicit
# startup-source hints, and PyInstaller markers to classify the startup source,
# execution mode, reload behavior, and runtime root directory.
# Notes:
# Keep this module independent from NiceGUI UI code. Optional parameters are
# available to make runtime detection testable without depending on the real
# process state.
# -----------------------------------------------------------------------------

from __future__ import annotations

import sys
from collections.abc import Sequence
from enum import StrEnum
from logging import Logger
from pathlib import Path, PureWindowsPath
from typing import Final

from desktop_app.constants import (
    APPLICATION_TITLE,
    PYPROJECT_COMMAND_NAMES,
)
from desktop_app.infrastructure.logger import logger_get_logger

logger: Logger = logger_get_logger(__name__)

ENTRY_SOURCE_HINT_GLOBAL: Final[str] = "__desktop_app_entry_source__"


class StartupSource(StrEnum):
    """Known application startup sources used in diagnostics."""

    DEVELOPMENT_RUNNER = "dev_run.py"
    PACKAGED_EXECUTABLE = "package"
    PYPROJECT_COMMAND = "pyproject command"
    MODULE_EXECUTION = "module"
    DIRECT_SCRIPT = "script"
    UNKNOWN = "unknown source"


STARTUP_SOURCE_DESCRIPTIONS: Final[dict[str, str]] = {
    StartupSource.DEVELOPMENT_RUNNER: "the development runner",
    StartupSource.PACKAGED_EXECUTABLE: "the packaged executable",
    StartupSource.PYPROJECT_COMMAND: "the pyproject command",
    StartupSource.MODULE_EXECUTION: "module execution",
    StartupSource.DIRECT_SCRIPT: "direct script execution",
}


STARTUP_SOURCE_HINTS: Final[frozenset[str]] = frozenset(
    {
        StartupSource.PYPROJECT_COMMAND,
        StartupSource.MODULE_EXECUTION,
    }
)


def is_frozen_executable(*, frozen: bool | None = None) -> bool:
    """Return whether the application is running from a frozen executable.

    Args:
        frozen: Optional explicit frozen state used by tests. When omitted,
            the value is read from sys.frozen.

    Returns:
        True when PyInstaller marks the process as frozen; otherwise False.
    """
    if frozen is not None:
        return frozen

    return bool(getattr(sys, "frozen", False))


def get_runtime_root(
    *,
    meipass: str | Path | None = None,
    executable: str | Path | None = None,
    module_file: str | Path | None = None,
    frozen: bool | None = None,
) -> Path:
    """Return the root directory used to resolve runtime files.

    Args:
        meipass: Optional PyInstaller extraction directory used by tests. When
            omitted, the value is read from sys._MEIPASS.
        executable: Optional executable path used by tests. When omitted,
            the value is read from sys.executable.
        module_file: Optional module file path used by tests. When omitted,
            this module's __file__ is used.
        frozen: Optional explicit frozen state used by tests.

    Returns:
        The PyInstaller extraction directory when available, the executable
        folder for other frozen cases, or this package directory during normal
        Python execution.
    """
    runtime_meipass = meipass
    if runtime_meipass is None:
        runtime_meipass = getattr(sys, "_MEIPASS", None)

    logger.debug("Runtime root check: sys._MEIPASS=%s", runtime_meipass)

    if runtime_meipass:
        runtime_root = Path(runtime_meipass).resolve()
        logger.debug(
            "Runtime root selected from PyInstaller extraction directory: %s",
            runtime_root,
        )
        return runtime_root

    runtime_executable = executable if executable is not None else sys.executable

    if is_frozen_executable(frozen=frozen):
        runtime_root = Path(runtime_executable).resolve().parent
        logger.debug(
            "Runtime root selected from frozen executable folder: %s",
            runtime_root,
        )
        return runtime_root

    runtime_module_file = (
        Path(module_file) if module_file is not None else Path(__file__)
    )
    runtime_root = runtime_module_file.resolve().parent.parent
    logger.debug("Runtime root selected from package root: %s", runtime_root)
    return runtime_root


def get_nicegui_modes(*, development_mode: bool) -> tuple[bool, bool]:
    """Return NiceGUI native and reload settings.

    Args:
        development_mode: Whether to run in browser development mode.

    Returns:
        A tuple containing native mode and reload status.
    """
    if development_mode:
        logger.debug(
            "Runtime mode selected for development: web mode with reload enabled."
        )
        return False, True

    logger.debug(
        "Runtime mode selected for normal use: native mode with reload disabled."
    )
    return True, False


def detect_entry_source_hint(
    *,
    argv: Sequence[str] | None = None,
    pyproject_command_names: Sequence[str] = PYPROJECT_COMMAND_NAMES,
) -> StartupSource:
    """Detect the original wrapper source before runpy alters sys.argv.

    Args:
        argv: Optional argument list used by tests. When omitted, sys.argv is
            used.
        pyproject_command_names: Command names created by pyproject.toml.

    Returns:
        Startup source hint for wrapper-based execution.
    """
    runtime_argv = argv if argv is not None else sys.argv

    if not runtime_argv:
        logger.debug("Entry source hint defaulted to module execution: argv is empty.")
        return StartupSource.MODULE_EXECUTION

    entry_name = _extract_entry_name(runtime_argv[0])
    normalized_entry_name = _normalize_console_script_name(entry_name)
    normalized_command_names = {
        _normalize_console_script_name(command_name)
        for command_name in pyproject_command_names
    }

    logger.debug("Original wrapper entry point detected: %s", entry_name)
    logger.debug(
        "Normalized pyproject command names for wrapper detection: %s",
        sorted(normalized_command_names),
    )

    if normalized_entry_name in normalized_command_names:
        logger.debug("Entry source hint classified as pyproject command.")
        return StartupSource.PYPROJECT_COMMAND

    logger.debug("Entry source hint classified as module execution.")
    return StartupSource.MODULE_EXECUTION


def normalize_startup_source_hint(entry_source_hint: object) -> StartupSource | None:
    """Return a trusted startup source hint or None.

    Args:
        entry_source_hint: Value received from runpy init globals or tests.

    Returns:
        A startup source enum when the hint is supported; otherwise None.
    """
    if isinstance(entry_source_hint, StartupSource):
        if entry_source_hint in STARTUP_SOURCE_HINTS:
            return entry_source_hint
        return None

    if isinstance(entry_source_hint, str):
        try:
            startup_source = StartupSource(entry_source_hint)
        except ValueError:
            logger.debug(
                "Ignored unsupported startup source hint: %s",
                entry_source_hint,
            )
            return None

        if startup_source in STARTUP_SOURCE_HINTS:
            return startup_source

    return None


def detect_startup_source(
    *,
    development_mode: bool,
    argv: Sequence[str] | None = None,
    frozen: bool | None = None,
    pyproject_command_names: Sequence[str] = PYPROJECT_COMMAND_NAMES,
    entry_source_hint: object = None,
) -> str:
    """Detect how the application was started.

    Args:
        development_mode: Whether startup was requested by the development
            runner.
        argv: Optional argument list used by tests. When omitted, sys.argv is
            used.
        frozen: Optional explicit frozen state used by tests.
        pyproject_command_names: Command names created by pyproject.toml.
        entry_source_hint: Optional startup source captured before runpy changed
            sys.argv.

    Returns:
        A readable startup source name for diagnostic output.
    """
    logger.debug(
        "Startup source detection started: development_mode=%s",
        development_mode,
    )

    if development_mode:
        logger.debug("Startup source classified as development runner.")
        return StartupSource.DEVELOPMENT_RUNNER

    if is_frozen_executable(frozen=frozen):
        logger.debug("Startup source classified as packaged executable.")
        return StartupSource.PACKAGED_EXECUTABLE

    normalized_hint = normalize_startup_source_hint(entry_source_hint)
    if normalized_hint is not None:
        logger.debug(
            "Startup source classified from preserved hint: %s",
            normalized_hint,
        )
        return normalized_hint

    runtime_argv = argv if argv is not None else sys.argv

    if not runtime_argv:
        logger.debug("Startup source could not be detected because argv is empty.")
        return StartupSource.UNKNOWN

    entry_name = _extract_entry_name(runtime_argv[0])
    normalized_command_names = {
        _normalize_console_script_name(name) for name in pyproject_command_names
    }

    logger.debug("Startup entry point detected: %s", entry_name)
    logger.debug("Known pyproject command names: %s", sorted(normalized_command_names))

    if _normalize_console_script_name(entry_name) in normalized_command_names:
        logger.debug("Startup source classified as pyproject command.")
        return StartupSource.PYPROJECT_COMMAND

    if entry_name == "__main__.py":
        logger.debug("Startup source classified as module execution.")
        return StartupSource.MODULE_EXECUTION

    if entry_name == "app.py":
        logger.debug("Startup source classified as direct script execution.")
        return StartupSource.DIRECT_SCRIPT

    logger.debug("Startup source classified from entry point name: %s", entry_name)
    return entry_name or StartupSource.UNKNOWN


def describe_startup_source(startup_source: str) -> str:
    """Return a readable startup source description.

    Args:
        startup_source: Source used to start the application.

    Returns:
        Human-readable startup source description for logs and status messages.
    """
    return STARTUP_SOURCE_DESCRIPTIONS.get(startup_source, startup_source)


def describe_runtime_mode(*, native_mode: bool, reload_enabled: bool) -> str:
    """Return a readable runtime mode description.

    Args:
        native_mode: Whether the application runs in NiceGUI native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.

    Returns:
        Human-readable runtime mode description for logs.
    """
    mode_name = "native mode" if native_mode else "web mode"
    reload_status = "enabled" if reload_enabled else "disabled"
    return f"{mode_name} with reload {reload_status}"


def build_startup_message(
    *,
    startup_source: str,
    native_mode: bool,
    reload_enabled: bool,
    application_title: str = APPLICATION_TITLE,
) -> str:
    """Build the startup diagnostic message.

    Args:
        startup_source: Source used to start the application.
        native_mode: Whether the application is running in native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.
        application_title: Human-readable application title.

    Returns:
        The startup diagnostic message used by the terminal and UI.
    """
    mode_name = "native" if native_mode else "web"
    reload_status = "enabled" if reload_enabled else "disabled"
    source_description = describe_startup_source(startup_source)

    message = (
        f"{application_title} is starting from {source_description} "
        f"in {mode_name} mode with reload {reload_status}."
    )

    logger.debug("Startup status message prepared: %s", message)
    return message


def get_startup_message(
    *,
    development_mode: bool,
    argv: Sequence[str] | None = None,
    frozen: bool | None = None,
    application_title: str = APPLICATION_TITLE,
    pyproject_command_names: Sequence[str] = PYPROJECT_COMMAND_NAMES,
    entry_source_hint: object = None,
) -> str:
    """Return the complete startup diagnostic message.

    Args:
        development_mode: Whether startup was requested by the development
            runner.
        argv: Optional argument list used by tests. When omitted, sys.argv is
            used.
        frozen: Optional explicit frozen state used by tests.
        application_title: Human-readable application title.
        pyproject_command_names: Command names created by pyproject.toml.
        entry_source_hint: Optional startup source captured before runpy changed
            sys.argv.

    Returns:
        The startup diagnostic message already formatted for terminal and UI.
    """
    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(
        development_mode=development_mode,
        argv=argv,
        frozen=frozen,
        pyproject_command_names=pyproject_command_names,
        entry_source_hint=entry_source_hint,
    )

    return build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=application_title,
    )


def _extract_entry_name(entry_point: str) -> str:
    """Return a normalized executable or script name from an argv entry.

    Args:
        entry_point: Raw argv entry that may contain a Windows or POSIX path.

    Returns:
        Lowercase file name without parent directories, or an empty string when
        the entry is blank.
    """
    normalized_entry_point = entry_point.strip()
    if not normalized_entry_point:
        return ""

    return PureWindowsPath(normalized_entry_point).name.lower()


def _normalize_console_script_name(entry_name: str) -> str:
    """Return a comparable console script name.

    Args:
        entry_name: File name, executable name, or configured command name.

    Returns:
        Lowercase command name without common wrapper suffixes.
    """
    normalized_name = PureWindowsPath(entry_name.strip()).name.lower()
    for suffix in (".exe", ".py", ".cmd", ".bat"):
        normalized_name = normalized_name.removesuffix(suffix)
    return normalized_name.removesuffix("-script")
