# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/splash.py
# Purpose:
# Manage the optional PyInstaller splash screen integration.
# Behavior:
# Dynamically imports the PyInstaller pyi_splash module only when the application
# is running as a frozen executable, then registers a NiceGUI connection handler
# to close the splash screen once the first client connects.
# Notes:
# The pyi_splash module does not exist during normal Python execution. Import
# failures are expected outside compatible packaged builds and must not stop the
# application. High-level splash state is mirrored in AppState for diagnostics.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
from typing import Protocol, cast

from nicegui import app

from desktop_app.constants import PYINSTALLER_SPLASH_MODULE
from desktop_app.core.runtime import is_frozen_executable
from desktop_app.core.state import get_app_state
from desktop_app.infrastructure.logger import logger_get_logger

logger = logger_get_logger(__name__)


class _SplashModule(Protocol):
    """Define the PyInstaller splash module behavior used by this module."""

    def close(self) -> None:
        """Close the active PyInstaller splash screen."""


_splash_module: _SplashModule | None = None
_splash_close_attempted = False


def load_splash_module() -> _SplashModule | None:
    """Load the optional PyInstaller splash module when available.

    Returns:
        Imported PyInstaller splash module, or None when unavailable.
    """
    if not is_frozen_executable():
        logger.debug(
            "PyInstaller splash import skipped because the application is not "
            "running as a frozen executable."
        )
        return None

    try:
        imported_module = importlib.import_module(PYINSTALLER_SPLASH_MODULE)
    except ImportError:
        logger.debug(
            "PyInstaller splash module is unavailable; startup will continue "
            "without a splash close handler."
        )
        return None
    except Exception:
        logger.exception(
            "PyInstaller splash module import failed; startup will continue "
            "without a splash close handler."
        )
        return None

    logger.debug(
        "PyInstaller splash module loaded; it will be closed after the first "
        "client connects."
    )
    return cast(_SplashModule, imported_module)


def close_splash_once() -> None:
    """Close the PyInstaller splash screen at most once."""
    global _splash_close_attempted

    state = get_app_state()

    if _splash_close_attempted:
        logger.debug("Splash close skipped because it was already attempted.")
        return

    _splash_close_attempted = True
    state.lifecycle.splash_close_attempted = True

    if _splash_module is None:
        logger.debug("Splash close skipped because no splash module was loaded.")
        return

    logger.debug("Closing PyInstaller splash screen.")

    try:
        _splash_module.close()
    except Exception:
        logger.exception("Failed to close the PyInstaller splash screen.")
        return

    state.lifecycle.splash_closed = True
    logger.debug("PyInstaller splash screen closed.")


def register_splash_handler() -> None:
    """Register a handler to close the PyInstaller splash on first client connect."""
    global _splash_module

    state = get_app_state()
    _splash_module = load_splash_module()

    if _splash_module is None:
        state.lifecycle.splash_registered = False
        logger.debug(
            "Splash close handler not registered because no splash module was loaded."
        )
        return

    app.on_connect(close_splash_once)
    state.lifecycle.splash_registered = True
    logger.debug(
        "PyInstaller splash close handler registered for the first client connection."
    )
