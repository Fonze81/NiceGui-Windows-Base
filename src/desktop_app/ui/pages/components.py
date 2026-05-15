# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/components.py
# Purpose:
# Build the reusable component catalog page.
# Behavior:
# Shows the shared UI building blocks used by the template so maintainers can
# validate the application identity in light and dark themes.
# Notes:
# This page is intentionally domain-neutral. It documents available template
# components through live examples instead of referencing external design systems.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.cards import build_info_card, build_metric_card
from desktop_app.ui.components.feedback import build_empty_state, build_status_badge
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_section_card_classes

logger: Final[Logger] = logger_get_logger(__name__)


def build_components_page() -> None:
    """Build the component catalog page."""
    state = get_app_state()
    state.ui_session.active_view = "components"
    state.ui_session.last_page_built_at = datetime.now()

    logger.debug("Building the components page for a client request.")

    build_page_header(
        title="Component catalog",
        description="Reusable UI blocks available to pages created from this template.",
        eyebrow="Design foundation",
        theme=state.ui.theme,
    )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Status badges",
            description="Use badges for compact state indicators.",
            theme=state.ui.theme,
        )
        with ui.row().classes("flex-wrap gap-2"):
            build_status_badge("Neutral")
            build_status_badge("Ready", tone="success")
            build_status_badge("Review", tone="warning")
            build_status_badge("Blocked", tone="error")
            build_status_badge("Info", tone="info")

    with ui.row().classes("w-full items-stretch gap-6"):
        build_info_card(
            title="Information card",
            description="Use this component for concise explanatory content.",
            theme=state.ui.theme,
        )
        build_metric_card(
            label="Version",
            value=state.meta.version,
            help_text="Current application template version.",
            theme=state.ui.theme,
        )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Empty state",
            description=(
                "Use this when a page has no records or no configured data yet."
            ),
            theme=state.ui.theme,
        )
        build_empty_state(
            title="No data available",
            description="Add data or configure an integration to populate this area.",
            theme=state.ui.theme,
        )

    logger.debug("Components page built successfully for the client request.")
