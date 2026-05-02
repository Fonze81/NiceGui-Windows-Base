# -----------------------------------------------------------------------------
# File: dev_run.py
# Purpose:
# Run the NiceGUI application in browser-based development mode.
# Behavior:
# Starts the same UI used by the native application, but with native mode disabled
# and automatic reload enabled to speed up interface development.
# Notes:
# Use this script only during development. The __mp_main__ guard is required by
# NiceGUI reload mode on Windows because reload uses multiprocessing.
# -----------------------------------------------------------------------------

from nicegui import ui

from nicegui_hello_world.app import create_ui


def main() -> None:
    """Run the application in browser-based development mode."""
    ui.run(create_ui, native=False, reload=True, title="NiceGUI Hello World")


if __name__ in {"__main__", "__mp_main__"}:
    main()
