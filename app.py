from nicegui import native, ui


def create_ui() -> None:
    """Build the main NiceGUI interface."""
    ui.label("Hello, NiceGUI!")


ui.run(
    create_ui,
    native=True,
    reload=False,
    port=native.find_open_port(),
)
