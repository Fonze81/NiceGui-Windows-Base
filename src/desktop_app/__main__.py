# -----------------------------------------------------------------------------
# File: src/desktop_app/__main__.py
# Purpose:
# Provide module execution support for the NiceGui Windows Base package.
# Behavior:
# Delegates `python -m desktop_app` to the main application entry point.
# Notes:
# Keep this file intentionally small; application logic belongs in app.py.
# -----------------------------------------------------------------------------

from desktop_app.app import main


def run() -> None:
    """Run the application entry point."""
    main()


if __name__ == "__main__":
    run()
