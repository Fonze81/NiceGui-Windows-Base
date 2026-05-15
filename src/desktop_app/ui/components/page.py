# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/components/page.py
# Purpose:
# Provide reusable page structure helpers for NiceGUI pages.
# Behavior:
# Builds standardized page headers and section headers used by the application
# shell pages.
# Notes:
# Keep these helpers small and visual only. They should not read settings, write
# files, or update business state.
# -----------------------------------------------------------------------------

from __future__ import annotations

from nicegui import ui

from desktop_app.core.state import ThemeName
from desktop_app.ui.theme import get_muted_text_classes, get_page_header_classes


def build_page_header(
    *,
    title: str,
    description: str,
    theme: ThemeName,
    eyebrow: str | None = None,
) -> None:
    """Build a standardized page header.

    Args:
        title: Main page title.
        description: Short page description.
        theme: Current visual theme.
        eyebrow: Optional small label above the title.
    """
    with ui.card().classes(get_page_header_classes(theme)):
        if eyebrow:
            ui.label(eyebrow).classes(
                "text-xs font-semibold uppercase tracking-wide text-blue-600"
            )
        ui.label(title).classes("text-3xl font-bold tracking-tight")
        ui.label(description).classes(get_muted_text_classes(theme))


def build_section_header(
    *, title: str, description: str | None, theme: ThemeName
) -> None:
    """Build a reusable section header inside a content card.

    Args:
        title: Section title.
        description: Optional section description.
        theme: Current visual theme.
    """
    ui.label(title).classes("text-lg font-semibold")
    if description:
        ui.label(description).classes(get_muted_text_classes(theme))
