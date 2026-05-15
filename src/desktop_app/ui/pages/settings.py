# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/settings.py
# Purpose:
# Build the template settings page.
# Behavior:
# Displays persisted preferences and delegates updates to application services.
# Notes:
# Keep callbacks small and delegate persistence to application/preferences.
# Avoid adding domain-specific settings to this generic template page.
# -----------------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from logging import Logger
from typing import Any, Final

from nicegui import ui

from desktop_app.application.preferences import (
    update_accent_color_preference,
    update_auto_save_preference,
    update_dense_mode_preference,
    update_font_scale_preference,
    update_theme_preference,
)
from desktop_app.constants import ALLOWED_THEMES
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.components.feedback import build_status_badge
from desktop_app.ui.components.page import build_page_header, build_section_header
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes

logger: Final[Logger] = logger_get_logger(__name__)


def _get_event_value(event: Any, default: object) -> object:
    """Return the value carried by a NiceGUI event.

    Args:
        event: NiceGUI event object.
        default: Fallback value when the event has no value attribute.

    Returns:
        Event value or fallback.
    """
    return getattr(event, "value", default)


def build_settings_page() -> None:
    """Build the settings page."""
    state = get_app_state()
    state.ui_session.active_view = "settings"
    state.ui_session.last_page_built_at = datetime.now()

    logger.debug("Building the settings page for a client request.")

    build_page_header(
        title="Settings",
        description="Adjust reusable template preferences backed by settings.toml.",
        eyebrow="Preferences",
        theme=state.ui.theme,
    )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Visual preferences",
            description="Changes are persisted through application services.",
            theme=state.ui.theme,
        )
        ui.select(
            options=sorted(ALLOWED_THEMES),
            value=state.ui.theme,
            label="Theme",
            on_change=lambda event: update_theme_preference(
                str(_get_event_value(event, state.ui.theme))
            ),
        ).classes("w-full max-w-sm")
        ui.number(
            label="Font scale",
            value=state.ui.font_scale,
            min=0.8,
            max=1.4,
            step=0.05,
            on_change=lambda event: update_font_scale_preference(
                _get_event_value(event, state.ui.font_scale)
            ),
        ).classes("w-full max-w-sm")
        ui.input(
            label="Accent color",
            value=state.ui.accent_color,
            on_change=lambda event: update_accent_color_preference(
                str(_get_event_value(event, state.ui.accent_color))
            ),
        ).classes("w-full max-w-sm")
        ui.switch(
            "Dense mode",
            value=state.ui.dense_mode,
            on_change=lambda event: update_dense_mode_preference(
                bool(_get_event_value(event, state.ui.dense_mode))
            ),
        )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Behavior preferences",
            description="General template behavior that is safe to persist.",
            theme=state.ui.theme,
        )
        ui.switch(
            "Auto-save settings",
            value=state.behavior.auto_save,
            on_change=lambda event: update_auto_save_preference(
                bool(_get_event_value(event, state.behavior.auto_save))
            ),
        )

    with ui.card().classes(get_section_card_classes(state.ui.theme)):
        build_section_header(
            title="Current settings state",
            description="Useful when validating settings loading and saving.",
            theme=state.ui.theme,
        )
        with ui.row().classes("flex-wrap gap-2"):
            build_status_badge(
                (
                    "Settings file loaded"
                    if state.settings.last_load_ok
                    else "Using defaults"
                ),
                tone="success" if state.settings.last_load_ok else "warning",
            )
            build_status_badge(
                "Last save succeeded" if state.settings.last_save_ok else "No save yet",
                tone="success" if state.settings.last_save_ok else "neutral",
            )
        ui.label(
            str(state.settings.file_path)
            if state.settings.file_path
            else "Settings path was not resolved yet."
        ).classes(get_muted_text_classes(state.ui.theme))

    logger.debug("Settings page built successfully for the client request.")
