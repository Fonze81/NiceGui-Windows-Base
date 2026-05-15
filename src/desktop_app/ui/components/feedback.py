# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/components/feedback.py
# Purpose:
# Provide generic feedback components for NiceGUI pages.
# Behavior:
# Builds status badges and empty-state blocks with consistent visual language.
# Notes:
# Feedback components must not perform side effects. Page callbacks or services
# own any required state changes.
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Literal

from nicegui import ui

from desktop_app.core.state import ThemeName
from desktop_app.ui.theme import get_muted_text_classes

BadgeTone = Literal["neutral", "success", "warning", "error", "info"]

_BADGE_CLASSES: dict[BadgeTone, str] = {
    "neutral": "bg-slate-100 text-slate-700",
    "success": "bg-emerald-50 text-emerald-700",
    "warning": "bg-amber-50 text-amber-700",
    "error": "bg-red-50 text-red-700",
    "info": "bg-blue-50 text-blue-700",
}
_BADGE_BASE_CLASSES = "inline-flex rounded-full px-3 py-1 text-xs font-semibold"


def build_status_badge(text: str, *, tone: BadgeTone = "neutral") -> None:
    """Build a small status badge.

    Args:
        text: Badge text.
        tone: Visual severity tone.
    """
    ui.label(text).classes(f"{_BADGE_BASE_CLASSES} {_BADGE_CLASSES[tone]}")


def build_empty_state(*, title: str, description: str, theme: ThemeName) -> None:
    """Build an empty-state block.

    Args:
        title: Empty-state title.
        description: Supporting empty-state description.
        theme: Current visual theme.
    """
    with ui.column().classes(
        "items-center justify-center gap-2 rounded-2xl p-8 text-center"
    ):
        ui.label(title).classes("text-lg font-semibold")
        ui.label(description).classes(get_muted_text_classes(theme))
