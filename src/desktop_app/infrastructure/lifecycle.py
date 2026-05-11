# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/lifecycle.py
# Purpose:
# Register application lifecycle handlers.
# Behavior:
# Centralizes NiceGUI lifecycle handler registration and updates high-level
# lifecycle fields in AppState so diagnostics can inspect runtime status without
# reading NiceGUI internals.
# Notes:
# Keep this module focused on lifecycle wiring. Handler implementation details
# should stay in their own modules, such as desktop_app.infrastructure.splash.
# Native window handlers are registered only when NiceGUI native mode is active.
# The asyncio exception handler suppresses only the known benign Windows
# connection reset raised during native window shutdown.
# -----------------------------------------------------------------------------

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from logging import Logger
from typing import Any, Final

from nicegui import app

from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger, logger_shutdown
from desktop_app.infrastructure.native_window_state import (
    persist_native_window_state_on_exit,
    restore_native_window_state_after_show,
    update_native_window_position,
    update_native_window_size,
)
from desktop_app.infrastructure.splash import register_splash_handler

logger: Final[Logger] = logger_get_logger(__name__)

WINDOWS_CONNECTION_RESET_WINERROR: Final[int] = 10054


def _is_expected_windows_connection_reset(
    exception_context: Mapping[str, object],
) -> bool:
    """Return whether an asyncio exception is expected Windows shutdown noise.

    Args:
        exception_context: Exception context received from the asyncio event loop.

    Returns:
        True when the context represents the known benign Windows connection
        reset raised while the native window connection is being closed.
    """
    exception = exception_context.get("exception")

    if not isinstance(exception, ConnectionResetError):
        return False

    if getattr(exception, "winerror", None) != WINDOWS_CONNECTION_RESET_WINERROR:
        return False

    message = str(exception_context.get("message", ""))
    handle = exception_context.get("handle")

    return "_call_connection_lost" in message or "_call_connection_lost" in repr(handle)


def _handle_asyncio_exception(
    loop: asyncio.AbstractEventLoop,
    exception_context: dict[str, Any],
) -> None:
    """Handle selected asyncio exceptions without hiding unexpected failures.

    Args:
        loop: Running asyncio event loop.
        exception_context: Exception context received from asyncio.
    """
    if _is_expected_windows_connection_reset(exception_context):
        logger.debug(
            "Suppressed expected Windows connection reset during native "
            "window shutdown."
        )
        return

    loop.default_exception_handler(exception_context)


def _configure_asyncio_exception_handler() -> None:
    """Configure the asyncio exception handler for the running event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.debug("Asyncio exception handler was not installed; no loop is running.")
        return

    loop.set_exception_handler(_handle_asyncio_exception)
    logger.debug("Asyncio exception handler installed.")


def _log_exception_event(event_message: str, event_args: tuple[object, ...]) -> None:
    """Log a NiceGUI exception event with traceback when available.

    Args:
        event_message: Human-readable event message.
        event_args: Event arguments that may contain an exception instance.
    """
    exception = next(
        (arg for arg in event_args if isinstance(arg, BaseException)), None
    )

    if exception is None:
        logger.error("%s No exception object was provided by NiceGUI.", event_message)
        return

    logger.error(
        "%s %s: %s",
        event_message,
        type(exception).__name__,
        exception,
        exc_info=(type(exception), exception, exception.__traceback__),
    )


def _handle_application_started(*_args: object) -> None:
    """Handle the NiceGUI application startup event."""
    state = get_app_state()
    state.lifecycle.runtime_started = True
    _configure_asyncio_exception_handler()
    logger.info("NiceGUI runtime started.")


def _handle_application_shutdown(*event_args: object) -> None:
    """Handle the NiceGUI application shutdown event."""
    state = get_app_state()
    state.lifecycle.shutdown_started = True

    if state.runtime.native_mode:
        persist_native_window_state_on_exit(*event_args, state=state)

    logger.info("Application shutdown completed.")
    state.lifecycle.shutdown_completed = True
    logger_shutdown()


def _handle_client_connected(*_args: object) -> None:
    """Handle the NiceGUI client connect event."""
    get_app_state().lifecycle.client_connected = True
    logger.info("Client connected to the application.")


def _handle_client_disconnected(*_args: object) -> None:
    """Handle the NiceGUI client disconnect event."""
    get_app_state().lifecycle.client_connected = False
    logger.info("Client disconnected from the application.")


def _handle_application_exception(*event_args: object) -> None:
    """Handle a general NiceGUI application exception event."""
    _log_exception_event(
        "NiceGUI reported an application-level exception.",
        event_args,
    )


def _handle_page_exception(*event_args: object) -> None:
    """Handle a NiceGUI page exception event."""
    _log_exception_event(
        "NiceGUI reported a page-level exception.",
        event_args,
    )


def _handle_native_window_shown(*event_args: object) -> None:
    """Handle the native window shown event."""
    state = get_app_state()
    state.lifecycle.native_window_opened = True
    state.lifecycle.native_window_closed = False
    restore_native_window_state_after_show(*event_args, state=state)
    logger.info("Native window opened.")


def _handle_native_window_loaded(*event_args: object) -> None:
    """Handle the native window loaded event."""
    state = get_app_state()
    state.lifecycle.native_window_loaded = True
    restore_native_window_state_after_show(*event_args, state=state)
    logger.info("Native window finished loading.")


def _handle_native_window_minimized(*_args: object) -> None:
    """Handle the native window minimized event."""
    state = get_app_state()
    state.lifecycle.native_window_minimized = True
    state.lifecycle.native_window_maximized = False
    logger.info("The native window was minimized by the user.")


def _handle_native_window_maximized(*_args: object) -> None:
    """Handle the native window maximized event."""
    state = get_app_state()
    state.lifecycle.native_window_maximized = True
    state.lifecycle.native_window_minimized = False
    logger.info("The native window was maximized by the user.")


def _handle_native_window_restored(*_args: object) -> None:
    """Handle the native window restored event."""
    state = get_app_state()
    state.lifecycle.native_window_maximized = False
    state.lifecycle.native_window_minimized = False
    logger.info("The native window was restored by the user.")


def _handle_native_window_resized(*event_args: object) -> None:
    """Handle the native window resized event."""
    update_native_window_size(*event_args)
    logger.debug("The native window was resized.")


def _handle_native_window_moved(*event_args: object) -> None:
    """Handle the native window moved event."""
    update_native_window_position(*event_args)
    logger.debug("The native window was moved.")


def _handle_native_window_closed(*event_args: object) -> None:
    """Handle the native window closed event."""
    state = get_app_state()
    state.lifecycle.native_window_closed = True
    state.lifecycle.native_window_opened = False
    persist_native_window_state_on_exit(*event_args, state=state)
    logger.info("The native window was closed by the user.")


def _handle_native_file_drop(*_args: object) -> None:
    """Handle files dropped on the native window."""
    logger.info("Files were dropped on the native window.")


def _register_application_handlers() -> None:
    """Register generic NiceGUI application lifecycle handlers."""
    app.on_startup(_handle_application_started)
    app.on_shutdown(_handle_application_shutdown)
    app.on_connect(_handle_client_connected)
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


def register_lifecycle_handlers(*, native_mode: bool) -> None:
    """Register application lifecycle handlers.

    Args:
        native_mode: Whether NiceGUI will run with a native desktop window.
    """
    state = get_app_state()
    logger.debug("Registering lifecycle handlers.")

    _register_application_handlers()
    state.lifecycle.handlers_registered = True

    if native_mode:
        _register_native_window_handlers()
        state.lifecycle.native_handlers_registered = True
        logger.debug("Native window lifecycle handlers registered.")
    else:
        state.lifecycle.native_handlers_registered = False
        logger.debug(
            "Native window lifecycle handlers skipped because web mode is active."
        )

    register_splash_handler()

    logger.debug("Lifecycle handlers registered.")
