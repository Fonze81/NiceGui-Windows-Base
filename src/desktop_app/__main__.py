# -----------------------------------------------------------------------------
# File: src/desktop_app/__main__.py
# Purpose:
# Provide module execution support for the NiceGui Windows Base package.
# Behavior:
# Executes desktop_app.app with __main__ semantics so `python -m desktop_app`
# uses the same Windows-safe entry point as direct app.py execution.
# Notes:
# Keep this file intentionally small. Application startup belongs in app.py; this
# module only routes package execution to that entry point.
# -----------------------------------------------------------------------------

from __future__ import annotations

import runpy


def run() -> None:
    """Execute the application module as the current process entry point."""
    runpy.run_module("desktop_app.app", run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    run()
