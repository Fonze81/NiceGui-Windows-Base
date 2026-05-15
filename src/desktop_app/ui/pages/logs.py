# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/logs.py
# Purpose:
# Build a lightweight runtime log viewer page.
# Behavior:
# Requests a bounded log snapshot from application services and renders the
# latest entries for support diagnostics.
# Notes:
# Keep log reading bounded. Do not stream or watch files from the UI thread until
# there is a clear product need and an asynchronous design.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Final

from nicegui import ui

from desktop_app.application.log_reader import LogSnapshot, read_log_snapshot
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.feedback import build_empty_state, build_status_badge
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes

logger: Final[Logger] = logger_get_logger(__name__)


def _render_log_source(snapshot: LogSnapshot, *, theme: str) -> None:
    """Render log source metadata.

    Args:
        snapshot: Log snapshot metadata.
        theme: Active visual theme.
    """
    with ui.card().classes(get_section_card_classes(theme)):
        build_section_header(
            title="Log source",
            description=(
                "The viewer reads a bounded number of lines to avoid loading "
                "large files."
            ),
            theme=theme,
        )
        with ui.row().classes("flex-wrap gap-2"):
            build_status_badge(
                "Log file found" if snapshot.exists else "Log file unavailable",
                tone="success" if snapshot.exists else "warning",
            )
            build_status_badge(
                f"Limit: {snapshot.max_lines} lines",
                tone="info",
            )
        ui.label(
            str(snapshot.path) if snapshot.path else "Log file is not available."
        ).classes(get_muted_text_classes(theme))


def _render_log_content(snapshot: LogSnapshot, *, theme: str) -> None:
    """Render log lines or a useful empty state.

    Args:
        snapshot: Log snapshot to render.
        theme: Active visual theme.
    """
    with ui.card().classes(get_section_card_classes(theme)):
        if snapshot.error is not None:
            build_empty_state(
                title="Log file could not be read",
                description=snapshot.error,
                theme=theme,
            )
            return

        if snapshot.has_lines:
            ui.label(f"Showing the latest {snapshot.line_count} log lines.").classes(
                get_muted_text_classes(theme)
            )
            ui.code("\n".join(snapshot.lines)).classes(
                "max-h-96 w-full overflow-auto rounded-xl p-4 text-xs"
            )
            return

        build_empty_state(
            title="No log entries available",
            description=(
                "Start the application with file logging enabled to populate this view."
            ),
            theme=theme,
        )


def build_logs_page() -> None:
    """Build the runtime log viewer page."""
    state = get_app_state()
    state.ui_session.active_view = "logs"
    state.ui_session.last_page_built_at = datetime.now()

    logger.debug("Building the logs page for a client request.")

    snapshot = read_log_snapshot(state=state)

    build_page_header(
        title="Runtime logs",
        description=(
            "Inspect the latest application log entries without leaving the UI."
        ),
        eyebrow="Observability",
        theme=state.ui.theme,
    )

    _render_log_source(snapshot, theme=state.ui.theme)
    _render_log_content(snapshot, theme=state.ui.theme)

    logger.debug("Logs page built successfully for the client request.")
