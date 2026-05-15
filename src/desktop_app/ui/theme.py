# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/theme.py
# Purpose:
# Centralize reusable visual classes for the application shell and pages.
# Behavior:
# Provides small helpers that translate UI preferences into Tailwind class
# strings consumed by NiceGUI components.
# Notes:
# Keep this module free of NiceGUI imports so visual decisions can be tested as
# plain Python values and reused by pages without creating UI side effects.
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Final

from desktop_app.core.state import ThemeName

LIGHT_BODY_CLASSES: Final[str] = "bg-slate-100 text-slate-950"
DARK_BODY_CLASSES: Final[str] = "bg-slate-950 text-slate-100"

SHELL_CLASSES: Final[str] = "min-h-screen w-full bg-slate-100 text-slate-950"
DARK_SHELL_CLASSES: Final[str] = "min-h-screen w-full bg-slate-950 text-slate-100"

APP_BAR_CLASSES: Final[str] = (
    "sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-6 py-4 backdrop-blur"
)
DARK_APP_BAR_CLASSES: Final[str] = (
    "sticky top-0 z-10 border-b border-slate-800 bg-slate-950/95 px-6 py-4 "
    "backdrop-blur"
)

SIDEBAR_CLASSES: Final[str] = (
    "w-full shrink-0 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm lg:w-72"
)
DARK_SIDEBAR_CLASSES: Final[str] = (
    "w-full shrink-0 rounded-2xl border border-slate-800 bg-slate-900 p-3 "
    "shadow-sm lg:w-72"
)

CONTENT_CLASSES: Final[str] = "min-w-0 flex-1"
PAGE_CONTAINER_CLASSES: Final[str] = "mx-auto flex w-full max-w-6xl flex-col gap-6"
PAGE_HEADER_CLASSES: Final[str] = (
    "rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
)
DARK_PAGE_HEADER_CLASSES: Final[str] = (
    "rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-sm"
)
SECTION_CARD_CLASSES: Final[str] = (
    "rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
)
DARK_SECTION_CARD_CLASSES: Final[str] = (
    "rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-sm"
)
NAV_LINK_CLASSES: Final[str] = (
    "w-full rounded-xl px-3 py-2 text-left text-sm font-medium text-slate-600 "
    "transition hover:bg-slate-100 hover:text-slate-950"
)
DARK_NAV_LINK_CLASSES: Final[str] = (
    "w-full rounded-xl px-3 py-2 text-left text-sm font-medium text-slate-300 "
    "transition hover:bg-slate-800 hover:text-white"
)
ACTIVE_NAV_LINK_CLASSES: Final[str] = (
    "w-full rounded-xl bg-blue-50 px-3 py-2 text-left text-sm font-semibold "
    "text-blue-700"
)
DARK_ACTIVE_NAV_LINK_CLASSES: Final[str] = (
    "w-full rounded-xl bg-blue-950 px-3 py-2 text-left text-sm font-semibold "
    "text-blue-200"
)
MUTED_TEXT_CLASSES: Final[str] = "text-sm leading-relaxed text-slate-500"
DARK_MUTED_TEXT_CLASSES: Final[str] = "text-sm leading-relaxed text-slate-400"


def is_dark_theme(theme: ThemeName) -> bool:
    """Return whether the current visual theme should use dark classes.

    Args:
        theme: User-selected theme preference.

    Returns:
        True when dark classes should be used.
    """
    return theme == "dark"


def get_body_classes(theme: ThemeName) -> str:
    """Return body classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes applied to the page body.
    """
    return DARK_BODY_CLASSES if is_dark_theme(theme) else LIGHT_BODY_CLASSES


def get_shell_classes(theme: ThemeName) -> str:
    """Return shell container classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for the application shell root.
    """
    return DARK_SHELL_CLASSES if is_dark_theme(theme) else SHELL_CLASSES


def get_app_bar_classes(theme: ThemeName) -> str:
    """Return application bar classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for the top application bar.
    """
    return DARK_APP_BAR_CLASSES if is_dark_theme(theme) else APP_BAR_CLASSES


def get_sidebar_classes(theme: ThemeName) -> str:
    """Return navigation sidebar classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for the navigation sidebar.
    """
    return DARK_SIDEBAR_CLASSES if is_dark_theme(theme) else SIDEBAR_CLASSES


def get_page_header_classes(theme: ThemeName) -> str:
    """Return page header card classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for page headers.
    """
    return DARK_PAGE_HEADER_CLASSES if is_dark_theme(theme) else PAGE_HEADER_CLASSES


def get_section_card_classes(theme: ThemeName) -> str:
    """Return section card classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for content cards.
    """
    return DARK_SECTION_CARD_CLASSES if is_dark_theme(theme) else SECTION_CARD_CLASSES


def get_navigation_link_classes(*, theme: ThemeName, active: bool) -> str:
    """Return navigation link classes for the selected theme and state.

    Args:
        theme: User-selected theme preference.
        active: Whether the link represents the current view.

    Returns:
        Tailwind classes for one navigation link.
    """
    if active:
        return (
            DARK_ACTIVE_NAV_LINK_CLASSES
            if is_dark_theme(theme)
            else ACTIVE_NAV_LINK_CLASSES
        )

    return DARK_NAV_LINK_CLASSES if is_dark_theme(theme) else NAV_LINK_CLASSES


def get_muted_text_classes(theme: ThemeName) -> str:
    """Return muted text classes for the selected theme.

    Args:
        theme: User-selected theme preference.

    Returns:
        Tailwind classes for secondary text.
    """
    return DARK_MUTED_TEXT_CLASSES if is_dark_theme(theme) else MUTED_TEXT_CLASSES
