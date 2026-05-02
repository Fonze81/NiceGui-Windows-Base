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
from pathlib import Path

from nicegui import native, ui


def create_ui() -> None:
    """Build the main NiceGUI interface."""
    ui.label("Hello, NiceGUI!")


def is_packaged() -> bool:
    """Return whether the application is running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


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
    mode_name = "native" if native_mode else "web"
    reload_status = "active" if reload_enabled else "inactive"

    print(
        "Initializing NiceGUI Hello World "
        f"from {startup_source} in {mode_name} mode "
        f"with reload {reload_status}."
    )

    ui.run(
        create_ui,
        native=native_mode,
        reload=reload_enabled,
        title="NiceGUI Hello World",
        port=native.find_open_port(),
    )


if __name__ == "__main__":
    main()
