# -----------------------------------------------------------------------------
# File: src/desktop_app/core/runtime.py
# Purpose:
# Identify how the application is currently being executed.
# Behavior:
# Reads Python runtime information such as sys.argv, sys.executable, and
# PyInstaller markers to classify the startup source, execution mode, reload
# behavior, and runtime root directory.
# Notes:
# Keep this module independent from NiceGUI UI code. Optional parameters are
# available to make runtime detection testable without depending on the real
# process state.
# -----------------------------------------------------------------------------

import logging
import sys
from collections.abc import Sequence
from pathlib import Path

logger = logging.getLogger(__name__)

APPLICATION_TITLE = "NiceGui Windows Base"
PYPROJECT_COMMAND_NAMES = ("nicegui-windows-base", "nicegui-windows-base.exe")


def is_frozen_executable(*, frozen: bool | None = None) -> bool:
    """Return whether the application is running from a frozen executable.

    Args:
        frozen: Optional explicit frozen state used by tests. When omitted,
            the value is read from sys.frozen.

    Returns:
        True when PyInstaller marks the process as frozen; otherwise False.
    """
    result = frozen if frozen is not None else bool(getattr(sys, "frozen", False))

    return result


def get_runtime_root(
    *,
    meipass: str | None = None,
    executable: str | None = None,
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

    logger.debug("Detected sys._MEIPASS: %s", runtime_meipass)

    if runtime_meipass:
        runtime_root = Path(runtime_meipass).resolve()
        logger.debug("Runtime root resolved from sys._MEIPASS: %s", runtime_root)
        return runtime_root

    runtime_executable = executable or sys.executable

    if is_frozen_executable(frozen=frozen):
        runtime_root = Path(runtime_executable).resolve().parent
        logger.debug("Runtime root resolved from executable parent: %s", runtime_root)
        return runtime_root

    runtime_module_file = (
        Path(module_file) if module_file is not None else Path(__file__)
    )
    runtime_root = runtime_module_file.resolve().parent.parent
    logger.debug("Runtime root resolved from package root: %s", runtime_root)
    return runtime_root


def get_nicegui_modes(*, development_mode: bool) -> tuple[bool, bool]:
    """Return NiceGUI native and reload settings.

    Args:
        development_mode: Whether to run in browser development mode.

    Returns:
        A tuple containing native mode and reload status.
    """
    if development_mode:
        logger.debug("NiceGUI mode resolved: native=False, reload=True")
        return False, True

    logger.debug("NiceGUI mode resolved: native=True, reload=False")
    return True, False


def detect_startup_source(
    *,
    development_mode: bool,
    argv: Sequence[str] | None = None,
    frozen: bool | None = None,
    pyproject_command_names: Sequence[str] = PYPROJECT_COMMAND_NAMES,
) -> str:
    """Detect how the application was started.

    Args:
        development_mode: Whether startup was requested by the development
            runner.
        argv: Optional argument list used by tests. When omitted, sys.argv is
            used.
        frozen: Optional explicit frozen state used by tests.
        pyproject_command_names: Command names created by pyproject.toml.

    Returns:
        A readable startup source name for diagnostic output.
    """
    logger.debug("Detecting startup source: development_mode=%s", development_mode)

    if development_mode:
        return "dev_run.py"

    if is_frozen_executable(frozen=frozen):
        return "package"

    runtime_argv = argv if argv is not None else sys.argv

    if not runtime_argv:
        logger.debug("Startup source could not be detected because argv is empty.")
        return "unknown source"

    entry_name = Path(runtime_argv[0]).name.lower()
    normalized_command_names = {name.lower() for name in pyproject_command_names}

    logger.debug("Startup entry name: %s", entry_name)
    logger.debug("Known pyproject command names: %s", sorted(normalized_command_names))

    if entry_name in normalized_command_names:
        return "pyproject command"

    if entry_name == "__main__.py":
        return "module"

    if entry_name == "app.py":
        return "script"

    return entry_name or "unknown source"


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
    reload_status = "active" if reload_enabled else "inactive"

    message = (
        f"Initializing {application_title} "
        f"from {startup_source} in {mode_name} mode "
        f"with reload {reload_status}."
    )

    logger.debug("Startup message built: %s", message)
    return message


def get_startup_message(
    *,
    development_mode: bool,
    argv: Sequence[str] | None = None,
    frozen: bool | None = None,
    application_title: str = APPLICATION_TITLE,
    pyproject_command_names: Sequence[str] = PYPROJECT_COMMAND_NAMES,
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

    Returns:
        The startup diagnostic message already formatted for terminal and UI.
    """
    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(
        development_mode=development_mode,
        argv=argv,
        frozen=frozen,
        pyproject_command_names=pyproject_command_names,
    )

    return build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
        application_title=application_title,
    )
