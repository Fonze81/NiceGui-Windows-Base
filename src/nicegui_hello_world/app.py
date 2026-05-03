# -----------------------------------------------------------------------------
# File: src/nicegui_hello_world/app.py
# Purpose:
# Define the minimal NiceGUI Hello World application entry point.
# Behavior:
# Builds the main UI and starts NiceGUI in native mode by default. Development
# scripts can request development mode, which runs the same UI in web mode with
# reload enabled.
# Notes:
# Uses pywebview through NiceGUI native mode. The explicit root function avoids
# NiceGUI script mode issues when the app is packaged as an executable.
# -----------------------------------------------------------------------------

import sys
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path

from nicegui import native, ui

APP_ICON_FILENAME = "app_icon.ico"


def create_ui(*, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        startup_message: Startup diagnostic message shown in the page.
    """
    ui.label("Hello, NiceGUI!")
    ui.label(startup_message)


def is_packaged() -> bool:
    """Return whether the application is running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


def get_app_icon_path() -> str:
    """Return the application icon path for normal and packaged execution.

    Returns:
        Absolute path to the application icon file.
    """
    if is_packaged():
        base_path = Path(sys._MEIPASS)
        return str(base_path / "nicegui_hello_world" / "assets" / APP_ICON_FILENAME)

    return str(Path(__file__).parent / "assets" / APP_ICON_FILENAME)


def identify_startup_source(*, development_mode: bool) -> str:
    """Identify how the application was started.

    Args:
        development_mode: Whether startup was requested by the development runner.

    Returns:
        A readable startup source name for diagnostic output.
    """
    if development_mode:
        return "dev_run.py"

    if is_packaged():
        return "package"

    entry_name = Path(sys.argv[0]).name.lower()

    if entry_name in {"nicegui-hello-world", "nicegui-hello-world.exe"}:
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
) -> str:
    """Build the startup diagnostic message.

    Args:
        startup_source: Source used to start the application.
        native_mode: Whether the application is running in native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.

    Returns:
        The startup diagnostic message used by the terminal and UI.
    """
    mode_name = "native" if native_mode else "web"
    reload_status = "active" if reload_enabled else "inactive"

    return (
        "Initializing NiceGUI Hello World "
        f"from {startup_source} in {mode_name} mode "
        f"with reload {reload_status}."
    )


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    if development_mode:
        native_mode = False
        reload_enabled = True
    else:
        native_mode = True
        reload_enabled = False

    startup_source = identify_startup_source(development_mode=development_mode)
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
    )

    print(startup_message)

    ui.run(
        partial(create_ui, startup_message=startup_message),
        native=native_mode,
        reload=reload_enabled,
        title="NiceGUI Hello World",
        favicon=get_app_icon_path(),
        port=native.find_open_port(),
    )


if __name__ == "__main__":
    freeze_support()
    main()
