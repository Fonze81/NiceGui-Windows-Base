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

from typing import Any

from nicegui import app

from desktop_app.infrastructure.logger import logger_get_logger, logger_shutdown
from desktop_app.infrastructure.splash import register_splash_handler

logger = logger_get_logger(__name__)


def _log_exception_event(message: str, args: tuple[Any, ...]) -> None:
    """Log a NiceGUI exception event with traceback when available.

    Args:
        message: Human-readable event message.
        args: Event arguments that may contain an exception instance.
    """
    exception = next((arg for arg in args if isinstance(arg, BaseException)), None)

    if exception is None:
        logger.error("%s No exception object was provided by NiceGUI.", message)
        return

    logger.error(
        "%s %s: %s",
        message,
        type(exception).__name__,
        exception,
        exc_info=(type(exception), exception, exception.__traceback__),
    )


def _handle_application_started(*_args: Any) -> None:
    """Handle the NiceGUI application startup event."""
    logger.info("NiceGUI runtime started.")


def _handle_application_shutdown(*_args: Any) -> None:
    """Handle the NiceGUI application shutdown event."""
    logger.info("Application shutdown completed.")
    logger_shutdown()


def _handle_client_disconnected(*_args: Any) -> None:
    """Handle the NiceGUI client disconnect event."""
    logger.info("Client disconnected from the application.")


def _handle_application_exception(*args: Any) -> None:
    """Handle a general NiceGUI application exception event."""
    _log_exception_event(
        "NiceGUI reported an application-level exception.",
        args,
    )


def _handle_page_exception(*args: Any) -> None:
    """Handle a NiceGUI page exception event."""
    _log_exception_event(
        "NiceGUI reported a page-level exception.",
        args,
    )


def _handle_native_window_shown(*_args: Any) -> None:
    """Handle the native window shown event."""
    logger.info("Native window opened.")


def _handle_native_window_loaded(*_args: Any) -> None:
    """Handle the native window loaded event."""
    logger.info("Native window finished loading.")


def _handle_native_window_minimized(*_args: Any) -> None:
    """Handle the native window minimized event."""
    logger.info("The native window was minimized by the user.")


def _handle_native_window_maximized(*_args: Any) -> None:
    """Handle the native window maximized event."""
    logger.info("The native window was maximized by the user.")


def _handle_native_window_restored(*_args: Any) -> None:
    """Handle the native window restored event."""
    logger.info("The native window was restored by the user.")


def _handle_native_window_resized(*_args: Any) -> None:
    """Handle the native window resized event."""
    logger.debug("The native window was resized.")


def _handle_native_window_moved(*_args: Any) -> None:
    """Handle the native window moved event."""
    logger.debug("The native window was moved.")


def _handle_native_window_closed(*_args: Any) -> None:
    """Handle the native window closed event."""
    logger.info("The native window was closed by the user.")


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
