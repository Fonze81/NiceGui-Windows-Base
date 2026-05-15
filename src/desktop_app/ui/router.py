# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/router.py
# Purpose:
# Register the NiceGUI single-page application routes.
# Behavior:
# Declares the root page, a catch-all page route, and a browser favicon route.
# Root and catch-all routes render the same SPA shell, while ui.sub_pages selects
# the active in-page route without a full server-side page replacement.
# Notes:
# Keep this module focused on route registration. Layout composition belongs in
# ui/layout.py, and page-specific content belongs in ui/pages.
# -----------------------------------------------------------------------------

from __future__ import annotations

from logging import Logger
from typing import Final

from fastapi.responses import FileResponse
from nicegui import app, ui

from desktop_app.infrastructure.asset_paths import get_application_icon_path
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.layout import build_app_layout

logger: Final[Logger] = logger_get_logger(__name__)


def register_spa_routes(*, application_name: str, startup_message: str) -> None:
    """Register the SPA entry routes.

    Args:
        application_name: Application name shown in the shared layout.
        startup_message: Startup diagnostic message shown by the index page.
    """
    logger.debug("Registering NiceGUI SPA root, favicon, and catch-all routes.")

    @app.get("/favicon.ico", include_in_schema=False)
    def _serve_favicon() -> FileResponse:
        """Serve the browser favicon request from the bundled application icon."""
        return FileResponse(get_application_icon_path())

    @ui.page("/")
    @ui.page("/{_:path}")
    def _build_spa_shell(_: str = "") -> None:
        """Build the SPA shell for the current client route.

        Args:
            _: Catch-all path segment provided by NiceGUI for non-root routes.
        """
        build_app_layout(
            application_name=application_name,
            startup_message=startup_message,
        )
