# -----------------------------------------------------------------------------
# File: dev_run.py
# Purpose:
# Run the NiceGUI application in browser-based development mode.
# Behavior:
# Requests development mode from the main application entry point. In development
# mode, the application runs in web mode with reload enabled to speed up
# interface development.
# Notes:
# Use this script only during development. The __mp_main__ guard is required by
# NiceGUI reload mode on Windows because reload uses multiprocessing.
# -----------------------------------------------------------------------------

from desktop_app.app import main

if __name__ in {"__main__", "__mp_main__"}:
    main(development_mode=True)
