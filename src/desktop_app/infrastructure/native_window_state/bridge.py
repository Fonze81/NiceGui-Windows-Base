# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/bridge.py
# Purpose:
# Isolate direct access to NiceGUI native window objects.
# Behavior:
# Wraps NiceGUI app.native access used by startup arguments and event readers.
# Notes:
# Keep NiceGUI-specific access in this module so the rest of the package remains
# easier to test with fake app objects.
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Any

from nicegui import app


def _get_native_window_args() -> dict[str, Any]:
    """Return the mutable native window arguments dictionary.

    Returns:
        The dictionary used by NiceGUI to pass extra arguments to pywebview.
    """
    window_args = getattr(app.native, "window_args", None)
    if isinstance(window_args, dict):
        return window_args

    window_args = {}
    app.native.window_args = window_args
    return window_args
