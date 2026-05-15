# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/components/navigation.py
# Purpose:
# Build reusable application navigation for the SPA shell.
# Behavior:
# Defines the route list used by the sidebar and renders links with active-state
# classes derived from the current UI session.
# Notes:
# Keep route metadata generic and centralized so adding a new page requires a
# small, explicit update.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from desktop_app.ui.theme import get_navigation_link_classes
from nicegui import ui

from desktop_app.core.state import ThemeName


@dataclass(frozen=True, slots=True)
class NavigationItem:
    """Describe one application navigation item.

    Attributes:
        label: Text displayed to the user.
        route: SPA route opened by the link.
        view_name: Logical view name stored in UI session state.
    """

    label: str
    route: str
    view_name: str


NAVIGATION_ITEMS: Final[tuple[NavigationItem, ...]] = (
    NavigationItem("Home", "/", "home"),
    NavigationItem("Components", "/components", "components"),
    NavigationItem("Diagnostics", "/diagnostics", "diagnostics"),
    NavigationItem("Logs", "/logs", "logs"),
    NavigationItem("Status", "/status", "status"),
    NavigationItem("Settings", "/settings", "settings"),
)


def build_navigation(*, active_view: str, theme: ThemeName) -> None:
    """Build the sidebar navigation links.

    Args:
        active_view: Logical view currently active.
        theme: Current visual theme.
    """
    with ui.column().classes("gap-1"):
        for item in NAVIGATION_ITEMS:
            ui.link(item.label, item.route).classes(
                get_navigation_link_classes(
                    theme=theme,
                    active=item.view_name == active_view,
                )
            )
