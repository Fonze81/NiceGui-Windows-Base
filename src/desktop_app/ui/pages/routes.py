# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/pages/routes.py
# Purpose:
# Define the NiceGUI sub-page route table for the SPA shell.
# Behavior:
# Builds route callables with the runtime context required by page builders and
# returns them to ui.sub_pages.
# Notes:
# Keep route declarations centralized so new SPA pages do not require changes in
# app.py or the shared layout.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from functools import partial

from desktop_app.ui.pages.index import build_index_page
from desktop_app.ui.pages.not_found import build_not_found_page

PageBuilder = Callable[..., None]


def build_sub_page_routes(
    *,
    application_name: str,
    startup_message: str,
) -> dict[str, PageBuilder]:
    """Build the route table consumed by ``ui.sub_pages``.

    Args:
        application_name: Application name passed to pages that need it.
        startup_message: Startup diagnostic message passed to pages that show
            runtime feedback.

    Returns:
        Mapping between SPA route patterns and page builder callables.
    """
    return {
        "/": partial(
            build_index_page,
            application_name=application_name,
            startup_message=startup_message,
        ),
        "/{_:path}": build_not_found_page,
    }
