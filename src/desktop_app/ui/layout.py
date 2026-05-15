# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/layout.py
# Purpose:
# Compose the shared NiceGUI single-page application shell.
# Behavior:
# Updates transient UI session state, applies the selected visual theme, renders
# reusable navigation chrome, and mounts ui.sub_pages for page content.
# Notes:
# The layout should stay independent from page business logic. Add new views by
# updating the page route table in ui/pages/routes.py and the navigation metadata
# in ui/components/navigation.py.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.navigation import build_navigation
from desktop_app.ui.pages.routes import build_sub_page_routes
from desktop_app.ui.theme import (
    CONTENT_CLASSES,
    PAGE_CONTAINER_CLASSES,
    get_app_bar_classes,
    get_body_classes,
    get_muted_text_classes,
    get_shell_classes,
    get_sidebar_classes,
)

logger: Final[Logger] = logger_get_logger(__name__)


def build_app_layout(*, application_name: str, startup_message: str) -> None:
    """Build the shared SPA layout.

    Args:
        application_name: Application name passed to sub-page routes.
        startup_message: Startup diagnostic message passed to page routes.
    """
    state = get_app_state()
    state.ui_session.last_page_built_at = datetime.now()
    state.ui_session.is_busy = False
    state.ui_session.busy_message = None

    logger.debug("Building the SPA shell for a client request.")

    ui.query("body").classes(get_body_classes(state.ui.theme))

    with ui.column().classes(get_shell_classes(state.ui.theme)):
        _build_app_bar(application_name=application_name)

        with ui.row().classes("w-full items-start gap-6 p-6"):
            with ui.card().classes(get_sidebar_classes(state.ui.theme)):
                ui.label("Navigation").classes(
                    "px-3 text-xs font-semibold uppercase tracking-wide"
                )
                build_navigation(
                    active_view=state.ui_session.active_view,
                    theme=state.ui.theme,
                )

            with (
                ui.column().classes(CONTENT_CLASSES),
                ui.column().classes(PAGE_CONTAINER_CLASSES),
            ):
                ui.sub_pages(
                    build_sub_page_routes(
                        application_name=application_name,
                        startup_message=startup_message,
                    )
                )

    logger.debug("SPA shell built successfully for the client request.")


def _build_app_bar(*, application_name: str) -> None:
    """Build the top application bar.

    Args:
        application_name: Application name displayed in the shell.
    """
    state = get_app_state()

    with (
        ui.row().classes(get_app_bar_classes(state.ui.theme)),
        ui.column().classes("gap-0"),
    ):
        ui.label(application_name).classes("text-lg font-bold tracking-tight")
        ui.label("Reusable desktop application template").classes(
            get_muted_text_classes(state.ui.theme)
        )
