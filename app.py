from nicegui import native, ui

ui.label("Hello, NiceGUI!")

ui.run(native=True, reload=False, port=native.find_open_port())
