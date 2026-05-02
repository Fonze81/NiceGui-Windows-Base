# -----------------------------------------------------------------------------
# File: src/nicegui_hello_world/app.py
# Purpose:
# Define the minimal NiceGUI Hello World application entry point.
# Behavior:
# Builds the main UI through an explicit root function and runs NiceGUI in native
# mode with reload disabled for compatibility with packaged execution.
# Notes:
# Uses pywebview through NiceGUI native mode. The explicit root function avoids
# NiceGUI script mode issues when the app is packaged as an executable.
# -----------------------------------------------------------------------------

from nicegui import native, ui


def create_ui() -> None:
    """Build the main NiceGUI interface."""
    ui.label("Hello, NiceGUI!")


def main() -> None:
    """Run the NiceGUI application."""
    ui.run(create_ui, native=True, reload=False, port=native.find_open_port())


if __name__ == "__main__":
    main()
