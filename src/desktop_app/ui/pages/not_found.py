# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/not_found.py
# Purpose:
# Build the SPA fallback page for unknown in-application routes.
# Behavior:
# Updates the active UI view and renders a small recovery message with a link
# back to the index route.
# Notes:
# This page keeps unknown SPA routes inside the application shell instead of
# exposing a blank or unstyled route to the user.
# -----------------------------------------------------------------------------

from __future__ import annotations

from nicegui import ui

from desktop_app.core.state import get_app_state


def build_not_found_page() -> None:
    """Build the fallback route for unknown SPA paths."""
    state = get_app_state()
    state.ui_session.active_view = "not_found"

    with ui.card():
        ui.label("Page not found")
        ui.label("The requested application page is not available.")
        ui.link("Back to Home", "/")
