# -----------------------------------------------------------------------------
# File: src/desktop_app/__main__.py
# Purpose:
# Provide installed-command and module execution support for the application.
# Behavior:
# Captures the original entry source before runpy executes desktop_app.app with
# __main__ semantics, preserving the startup path needed by native window args.
# Notes:
# Keep this file intentionally small. Application startup belongs in app.py; this
# module only preserves wrapper context and routes execution to that entry point.
# -----------------------------------------------------------------------------

from __future__ import annotations

import runpy
import sys

from desktop_app.core.runtime import (
    ENTRY_SOURCE_HINT_GLOBAL,
    detect_entry_source_hint,
)


def run() -> None:
    """Execute the application module as the current process entry point."""
    runpy.run_module(
        "desktop_app.app",
        run_name="__main__",
        alter_sys=True,
        init_globals={
            ENTRY_SOURCE_HINT_GLOBAL: detect_entry_source_hint(argv=sys.argv),
        },
    )


if __name__ == "__main__":
    run()
