# -----------------------------------------------------------------------------
# File: dev_run.py
# Purpose:
# Run the NiceGUI application in browser-based development mode.
# Behavior:
# Starts the same UI used by the native application, but with native mode disabled
# and automatic reload enabled to speed up interface development.
# Notes:
# Use this script only during development. Normal execution and packaging should
# keep using the project command or the packaging script.
# -----------------------------------------------------------------------------

from nicegui import ui

from nicegui_hello_world.app import create_ui


def main() -> None:
    """Run the application in browser-based development mode."""
    ui.run(create_ui, native=False, reload=True, title="NiceGUI Hello World")


if __name__ == "__main__":
    main()
