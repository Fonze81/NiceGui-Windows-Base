# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/index.py
# Purpose:
# Build the index NiceGUI page shown by the application.
# Behavior:
# Updates transient UI session state, resolves the page illustration asset, and
# composes the centered card shown when a client connects.
# Notes:
# Keep this module focused on UI composition. Startup, logging, lifecycle, and
# persistence logic belong in the application and infrastructure packages.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Final

from nicegui import ui

from desktop_app.constants import PAGE_IMAGE_FILENAME
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.asset_paths import resolve_asset_path
from desktop_app.infrastructure.logger import logger_get_logger

logger: Final[Logger] = logger_get_logger(__name__)


def build_index_page(*, application_name: str, startup_message: str) -> None:
    """Build the index NiceGUI interface.

    Args:
        application_name: Application name shown in the page.
        startup_message: Startup diagnostic message shown in the page.
    """
    state = get_app_state()
    state.ui_session.active_view = "home"
    state.ui_session.last_page_built_at = datetime.now()
    state.ui_session.is_busy = False
    state.ui_session.busy_message = None

    logger.info("Building the index page for the connected client.")

    ui.query("body").classes("bg-slate-100")

    with (
        ui.column().classes(
            "fixed inset-0 items-center justify-center "
            "bg-gradient-to-br from-slate-50 via-white to-blue-50 p-6"
        ),
        ui.card().classes(
            "w-full max-w-2xl items-center gap-5 rounded-2xl p-8 text-center shadow-xl"
        ),
    ):
        page_image_path = resolve_asset_path(PAGE_IMAGE_FILENAME)
        state.assets.page_image_path = Path(page_image_path)
        logger.debug("Page image resolved for the index page: %s", page_image_path)

        ui.image(page_image_path).classes("h-40 w-40 rounded-2xl object-contain")

        ui.label(application_name).classes(
            "text-4xl font-bold tracking-tight text-slate-800"
        )
        ui.label("A minimal native and web Windows base template.").classes(
            "text-base text-slate-500"
        )

        with ui.card().classes(
            "w-full rounded-xl bg-slate-50 p-4 text-left shadow-none"
        ):
            ui.label("Startup status").classes(
                "text-sm font-semibold uppercase tracking-wide text-slate-500"
            )
            ui.label(startup_message).classes(
                "mt-1 text-sm leading-relaxed text-slate-700"
            )

    logger.info("Index page built successfully.")
