# -----------------------------------------------------------------------------
# File: src/desktop_app/ui/router.py
# Purpose:
# Register the NiceGUI single-page application routes.
# Behavior:
# Declares the static assets route, browser favicon route, root page, and
# catch-all page route. Root and catch-all routes render the same SPA shell,
# while ui.sub_pages selects the active in-page route without a full server-side
# page replacement.
# Notes:
# Keep this module focused on route registration. Layout composition belongs in
# ui/layout.py, and page-specific content belongs in ui/pages.
# -----------------------------------------------------------------------------

from __future__ import annotations

from importlib import import_module
from logging import Logger
from typing import Any, Final

from fastapi.responses import FileResponse
from nicegui import ui

from desktop_app.infrastructure.asset_paths import (
    STATIC_ASSETS_ROUTE,
    get_application_icon_path,
    get_assets_directory_path,
)
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.ui.layout import build_app_layout

logger: Final[Logger] = logger_get_logger(__name__)
_static_asset_routes_registered = False


def register_spa_routes(*, application_name: str, startup_message: str) -> None:
    """Register the SPA entry routes.

    Args:
        application_name: Application name shown in the shared layout.
        startup_message: Startup diagnostic message shown by the index page.
    """
    logger.debug("Registering NiceGUI SPA root, favicon, and catch-all routes.")

    _register_static_asset_routes()

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


def _register_static_asset_routes() -> None:
    """Register stable static routes when the real NiceGUI app is available."""
    global _static_asset_routes_registered

    if _static_asset_routes_registered:
        logger.debug(
            "Static asset routes already registered; skipping duplicate setup."
        )
        return

    nicegui_app = _get_nicegui_app()
    if nicegui_app is None:
        logger.debug(
            "NiceGUI app object is unavailable; static asset routes "
            "were not registered."
        )
        return

    nicegui_app.add_static_files(STATIC_ASSETS_ROUTE, get_assets_directory_path())

    @nicegui_app.get("/favicon.ico", include_in_schema=False)
    def _serve_favicon() -> FileResponse:
        """Serve the browser favicon request from the bundled application icon."""
        return FileResponse(get_application_icon_path())

    _static_asset_routes_registered = True
    logger.debug("Static asset and favicon routes registered.")


def _get_nicegui_app() -> Any | None:
    """Return the NiceGUI app object when available.

    Tests replace the NiceGUI module with a lightweight UI fake that does not
    expose ``app``. In that situation, SPA page registration can still be tested
    while static application routes are skipped.
    """
    nicegui_module = import_module("nicegui")
    return getattr(nicegui_module, "app", None)
