# -----------------------------------------------------------------------------
# File: src/nicegui_hello_world/__main__.py
# Purpose:
# Provide module execution support for the NiceGUI Hello World package.
# Behavior:
# Delegates `python -m nicegui_hello_world` to the main application entry point.
# Notes:
# Keep this file intentionally small; application logic belongs in app.py.
# -----------------------------------------------------------------------------

from nicegui_hello_world.app import main

if __name__ == "__main__":
    main()
