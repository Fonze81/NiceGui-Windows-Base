# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/index.py
# Purpose:
# Build the index NiceGUI page shown by the application.
# Behavior:
# Updates transient UI session state, resolves the page illustration asset, and
# composes a reusable landing page inside the shared application shell.
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
from desktop_app.ui.components.cards import build_info_card
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes

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

    logger.debug("Building the index page for a client request.")

    build_page_header(
        title=application_name,
        description="A reusable native and web Windows application template.",
        eyebrow="Application shell",
        theme=state.ui.theme,
    )

    with ui.row().classes("w-full items-stretch gap-6"):
        with ui.card().classes(get_section_card_classes(state.ui.theme)):
            page_image_path = resolve_asset_path(PAGE_IMAGE_FILENAME)
            state.assets.page_image_path = Path(page_image_path)
            logger.debug("Page image resolved for the index page: %s", page_image_path)
            ui.image(page_image_path).classes("h-44 w-44 rounded-2xl object-contain")

        with ui.card().classes(f"flex-1 {get_section_card_classes(state.ui.theme)}"):
            build_section_header(
                title="Startup status",
                description=(
                    "The same diagnostic message is shown in logs, terminal, and UI."
                ),
                theme=state.ui.theme,
            )
            ui.label(startup_message).classes("mt-2 text-sm leading-relaxed")

    with ui.row().classes("w-full items-stretch gap-6"):
        build_info_card(
            title="SPA navigation",
            description=(
                "The shell keeps navigation, layout, and pages separated for reuse."
            ),
            theme=state.ui.theme,
        )
        build_info_card(
            title="Packaged execution",
            description=(
                "Assets, logging, settings, and native window state work in "
                "packaged builds."
            ),
            theme=state.ui.theme,
        )
        build_info_card(
            title="Maintainable foundation",
            description=(
                "Pages use shared components instead of duplicating visual structure."
            ),
            theme=state.ui.theme,
        )

    ui.label(
        "Use the navigation menu to inspect components, diagnostics, logs, "
        "and settings."
    ).classes(get_muted_text_classes(state.ui.theme))

    logger.debug("Index page built successfully for the client request.")
