# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/components/cards.py
# Purpose:
# Provide reusable card components for template pages.
# Behavior:
# Builds simple informational and metric cards with consistent spacing and text
# hierarchy.
# Notes:
# Cards must remain generic so they can be reused by projects created from this
# template without domain-specific wording.
# -----------------------------------------------------------------------------

from __future__ import annotations

from nicegui import ui

from desktop_app.core.state import ThemeName
from desktop_app.ui.theme import get_muted_text_classes, get_section_card_classes


def build_info_card(*, title: str, description: str, theme: ThemeName) -> None:
    """Build an informational card.

    Args:
        title: Card title.
        description: Card body text.
        theme: Current visual theme.
    """
    with ui.card().classes(get_section_card_classes(theme)):
        ui.label(title).classes("text-base font-semibold")
        ui.label(description).classes(get_muted_text_classes(theme))


def build_metric_card(
    *, label: str, value: str, help_text: str, theme: ThemeName
) -> None:
    """Build a compact metric card.

    Args:
        label: Metric label.
        value: Metric value.
        help_text: Supporting text shown below the value.
        theme: Current visual theme.
    """
    with ui.card().classes(get_section_card_classes(theme)):
        ui.label(label).classes("text-xs font-semibold uppercase tracking-wide")
        ui.label(value).classes("text-2xl font-bold")
        ui.label(help_text).classes(get_muted_text_classes(theme))
