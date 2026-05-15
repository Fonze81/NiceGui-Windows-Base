# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/diagnostics.py
# Purpose:
# Build the runtime diagnostics page.
# Behavior:
# Renders diagnostics sections produced by application services so the page stays
# focused on NiceGUI composition.
# Notes:
# Diagnostics must not expose secrets. Keep values technical and avoid showing
# confidential business data when this template is reused.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.application.diagnostics import (
    DiagnosticSection,
    build_diagnostics_sections,
)
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.cards import build_metric_card
from desktop_app.ui.components.feedback import build_status_badge
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes

logger: Final[Logger] = logger_get_logger(__name__)


def _render_diagnostic_section(section: DiagnosticSection, *, theme: str) -> None:
    """Render a diagnostics section.

    Args:
        section: Diagnostics section to render.
        theme: Active visual theme.
    """
    with ui.card().classes(get_section_card_classes(theme)):
        build_section_header(
            title=section.title,
            description=section.description,
            theme=theme,
        )
        with ui.column().classes("gap-2"):
            for item in section.items:
                with ui.row().classes("w-full items-start justify-between gap-4"):
                    ui.label(item.label).classes("font-medium")
                    ui.label(item.value).classes(get_muted_text_classes(theme))


def build_diagnostics_page() -> None:
    """Build the runtime diagnostics page."""
    state = get_app_state()
    state.ui_session.active_view = "diagnostics"
    state.ui_session.last_page_built_at = datetime.now()

    logger.debug("Building the diagnostics page for a client request.")

    sections = build_diagnostics_sections(state)

    build_page_header(
        title="Runtime diagnostics",
        description="Inspect the current process state without opening a debugger.",
        eyebrow="Support",
        theme=state.ui.theme,
    )

    with ui.row().classes("w-full items-stretch gap-6"):
        build_metric_card(
            label="Runtime",
            value="Native" if state.runtime.native_mode else "Web",
            help_text="Current NiceGUI execution mode.",
            theme=state.ui.theme,
        )
        build_metric_card(
            label="Port",
            value=str(state.runtime.port),
            help_text="HTTP port selected for this run.",
            theme=state.ui.theme,
        )
        build_metric_card(
            label="Logging",
            value="Enabled" if state.log.file_logging_enabled else "Pending",
            help_text="File logging status for this process.",
            theme=state.ui.theme,
        )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Lifecycle status",
            description="Important lifecycle flags as compact support badges.",
            theme=state.ui.theme,
        )
        with ui.row().classes("flex-wrap gap-2"):
            build_status_badge(
                (
                    "Handlers registered"
                    if state.lifecycle.handlers_registered
                    else "Handlers pending"
                ),
                tone="success" if state.lifecycle.handlers_registered else "warning",
            )
            build_status_badge(
                (
                    "Client connected"
                    if state.lifecycle.client_connected
                    else "No active client"
                ),
                tone="success" if state.lifecycle.client_connected else "neutral",
            )
            build_status_badge(
                (
                    "Native window loaded"
                    if state.lifecycle.native_window_loaded
                    else "Window loading pending"
                ),
                tone="success" if state.lifecycle.native_window_loaded else "neutral",
            )

    for section in sections:
        _render_diagnostic_section(section, theme=state.ui.theme)

    logger.debug("Diagnostics page built successfully for the client request.")
