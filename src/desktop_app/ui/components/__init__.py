# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/components/__init__.py
# Purpose:
# Expose reusable NiceGUI UI component helpers.
# Behavior:
# Provides a compact package facade so pages can import shared UI builders from
# one place without depending on internal module structure.
# Notes:
# Keep component helpers generic and domain-neutral because this project is a
# reusable desktop application template.
# -----------------------------------------------------------------------------

from desktop_app.ui.components.cards import build_info_card, build_metric_card
from desktop_app.ui.components.feedback import build_empty_state, build_status_badge
from desktop_app.ui.components.navigation import NAVIGATION_ITEMS, build_navigation
from desktop_app.ui.components.page import build_page_header, build_section_header

__all__: tuple[str, ...] = (
    "NAVIGATION_ITEMS",
    "build_empty_state",
    "build_info_card",
    "build_metric_card",
    "build_navigation",
    "build_page_header",
    "build_section_header",
    "build_status_badge",
)
