# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/status.py
# Purpose:
# Build the application status history page.
# Behavior:
# Renders the current status message and recent in-memory status history for
# support diagnostics inside the shared application shell.
# Notes:
# Status history is in-memory only and intentionally avoids domain-specific data.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.application.status import build_status_history_snapshot
from desktop_app.core.state import StatusLevel, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.feedback import build_empty_state, build_status_badge
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes

logger: Final[Logger] = logger_get_logger(__name__)

_STATUS_TONE_BY_LEVEL: Final[dict[StatusLevel, str]] = {
    "info": "info",
    "success": "success",
    "warning": "warning",
    "error": "error",
}


def build_status_page() -> None:
    """Build the status history page."""
    state = get_app_state()
    state.ui_session.active_view = "status"
    state.ui_session.last_page_built_at = datetime.now()

    logger.debug("Building the status page for a client request.")

    status_items = build_status_history_snapshot(state)

    build_page_header(
        title="Application status",
        description="Inspect recent in-memory status messages for this run.",
        eyebrow="Runtime feedback",
        theme=state.ui.theme,
    )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Current status",
            description="Latest status message published by application services.",
            theme=state.ui.theme,
        )
        if state.status.current_message is not None:
            message = state.status.current_message
            build_status_badge(
                message.level.title(),
                tone=_STATUS_TONE_BY_LEVEL[message.level],
            )
            ui.label(message.text).classes(get_muted_text_classes(state.ui.theme))
        else:
            build_empty_state(
                title="No current status",
                description="No service has published a current status message yet.",
                theme=state.ui.theme,
            )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Recent history",
            description="Newest status messages are shown first.",
            theme=state.ui.theme,
        )
        if not status_items:
            build_empty_state(
                title="No status history",
                description="Status messages will appear here after service actions.",
                theme=state.ui.theme,
            )
        else:
            with ui.column().classes("gap-3"):
                for item in status_items:
                    with ui.row().classes("w-full items-start justify-between gap-4"):
                        with ui.column().classes("gap-0"):
                            ui.label(item.text).classes("font-medium")
                            ui.label(item.created_at_text).classes(
                                get_muted_text_classes(state.ui.theme)
                            )
                        build_status_badge(
                            item.level.title(),
                            tone=_STATUS_TONE_BY_LEVEL[item.level],
                        )

    logger.debug("Status page built successfully for the client request.")
