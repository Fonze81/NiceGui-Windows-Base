# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/lifecycle.py
# Purpose:
# Register application lifecycle handlers.
# Behavior:
# Centralizes NiceGUI lifecycle handler registration so the application entry
# point does not need to know every individual infrastructure handler.
# Notes:
# Keep this module focused on lifecycle wiring. Handler implementation details
# should stay in their own modules, such as desktop_app.infrastructure.splash.
# The generic and native window handlers are intentionally simple because this
# project is also used as a template for future applications.
# -----------------------------------------------------------------------------

import logging
from typing import Any

from nicegui import app

from desktop_app.infrastructure.splash import register_splash_handler

logger = logging.getLogger(__name__)


def _handle_application_started(*_args: Any) -> None:
    """Handle the NiceGUI application startup event."""
    logger.info("NiceGUI runtime started.")


def _handle_application_shutdown(*_args: Any) -> None:
    """Handle the NiceGUI application shutdown event."""
    logger.info("Application shutdown completed.")


def _handle_client_disconnected(*_args: Any) -> None:
    """Handle the NiceGUI client disconnect event."""
    logger.info("Client disconnected from the application.")


def _handle_application_exception(*_args: Any) -> None:
    """Handle a general NiceGUI application exception event."""
    logger.error("NiceGUI reported an application-level exception.")


def _handle_page_exception(*_args: Any) -> None:
    """Handle a NiceGUI page exception event."""
    logger.error("NiceGUI reported a page-level exception.")


def _handle_native_window_shown(*_args: Any) -> None:
    """Handle the native window shown event."""
    logger.info("Native window opened.")


def _handle_native_window_loaded(*_args: Any) -> None:
    """Handle the native window loaded event."""
    logger.info("Native window finished loading.")


def _handle_native_window_minimized(*_args: Any) -> None:
    """Handle the native window minimized event."""
    logger.info("Native window minimized by the user.")


def _handle_native_window_maximized(*_args: Any) -> None:
    """Handle the native window maximized event."""
    logger.info("Native window maximized by the user.")


def _handle_native_window_restored(*_args: Any) -> None:
    """Handle the native window restored event."""
    logger.info("Native window restored by the user.")


def _handle_native_window_resized(*_args: Any) -> None:
    """Handle the native window resized event."""
    logger.info("Native window resized.")


def _handle_native_window_moved(*_args: Any) -> None:
    """Handle the native window moved event."""
    logger.info("Native window moved.")


def _handle_native_window_closed(*_args: Any) -> None:
    """Handle the native window closed event."""
    logger.info("Native window closed by the user.")


def _handle_native_file_drop(*_args: Any) -> None:
    """Handle files dropped on the native window."""
    logger.info("Files were dropped on the native window.")


def _register_application_handlers() -> None:
    """Register generic NiceGUI application lifecycle handlers."""
    app.on_startup(_handle_application_started)
    app.on_shutdown(_handle_application_shutdown)
    app.on_disconnect(_handle_client_disconnected)
    app.on_exception(_handle_application_exception)
    app.on_page_exception(_handle_page_exception)


def _register_native_window_handlers() -> None:
    """Register native window lifecycle handlers."""
    app.native.on("shown", _handle_native_window_shown)
    app.native.on("loaded", _handle_native_window_loaded)
    app.native.on("minimized", _handle_native_window_minimized)
    app.native.on("maximized", _handle_native_window_maximized)
    app.native.on("restored", _handle_native_window_restored)
    app.native.on("resized", _handle_native_window_resized)
    app.native.on("moved", _handle_native_window_moved)
    app.native.on("closed", _handle_native_window_closed)
    app.native.on("drop", _handle_native_file_drop)


def register_lifecycle_handlers() -> None:
    """Register application lifecycle handlers."""
    logger.debug("Registering lifecycle handlers.")

    _register_application_handlers()
    _register_native_window_handlers()
    register_splash_handler()

    logger.debug("Lifecycle handlers registered.")
