# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/layout.py
# Purpose:
# Compose the shared NiceGUI single-page application shell.
# Behavior:
# Updates transient UI session state, applies global page styling and dark mode,
# renders the common application header, and mounts ui.sub_pages for content.
# Notes:
# The layout should stay independent from page business logic. Add new views by
# updating the page route table in ui/pages/routes.py.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.pages.routes import build_sub_page_routes

logger: Final[Logger] = logger_get_logger(__name__)


def build_app_layout(*, application_name: str, startup_message: str) -> None:
    """Build the shared SPA layout.

    Args:
        application_name: Application name shown in the shared header.
        startup_message: Startup diagnostic message passed to page routes.
    """
    state = get_app_state()
    state.ui_session.last_page_built_at = datetime.now()
    state.ui_session.is_busy = False
    state.ui_session.busy_message = None

    logger.info("Building the SPA layout for the connected client.")

    ui.sub_pages(
        build_sub_page_routes(
            application_name=application_name,
            startup_message=startup_message,
        )
    )

    logger.info("SPA layout built successfully.")
