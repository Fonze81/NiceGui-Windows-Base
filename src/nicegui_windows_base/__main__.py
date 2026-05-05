# -----------------------------------------------------------------------------
# File: src/nicegui_windows_base/__main__.py
# Purpose:
# Provide module execution support for the NiceGui Windows Base package.
# Behavior:
# Delegates `python -m nicegui_windows_base` to the main application entry point.
# Notes:
# Keep this file intentionally small; application logic belongs in app.py.
# -----------------------------------------------------------------------------

from nicegui_windows_base.app import main

if __name__ == "__main__":
    main()
