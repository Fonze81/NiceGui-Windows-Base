# -----------------------------------------------------------------------------
# File: tests/infrastructure/test_splash.py
# Purpose:
# Validate the optional PyInstaller splash screen integration.
# Behavior:
# Uses fake modules to test splash loading and closing without requiring the
# real NiceGUI package during test collection.
# Notes:
# The pyi_splash module only exists in packaged builds, so tests must cover
# missing-module, failure, and success paths without opening a graphical UI.
# -----------------------------------------------------------------------------

from __future__ import annotations

import sys
from collections.abc import Callable
from types import SimpleNamespace

import pytest

# Ensure the splash module can be imported in test environments where NiceGUI
# is not installed yet. When the real NiceGUI package exists, it is not replaced.
_fake_nicegui_app = SimpleNamespace(on_connect=lambda _callback: None)
sys.modules.setdefault("nicegui", SimpleNamespace(app=_fake_nicegui_app))

from desktop_app.core.state import AppState  # noqa: E402
from desktop_app.infrastructure import splash  # noqa: E402


class FakeSplashModule:
    """Test double for the optional PyInstaller splash module."""

    def __init__(self) -> None:
        """Initialize the fake module with no close calls."""
        self.close_call_count = 0

    def close(self) -> None:
        """Record a successful splash close call."""
        self.close_call_count += 1


class FailingSplashModule:
    """Test double that simulates a failing splash close call."""

    def close(self) -> None:
        """Raise the same kind of unexpected error handled by production code."""
        raise RuntimeError("Splash close failed.")


@pytest.fixture
def app_state(monkeypatch: pytest.MonkeyPatch) -> AppState:
    """Provide isolated application state and splash globals for each test."""
    state = AppState()

    monkeypatch.setattr(splash, "get_app_state", lambda: state)
    monkeypatch.setattr(splash, "_splash_module", None)
    monkeypatch.setattr(splash, "_splash_close_attempted", False)

    return state


def test_load_splash_module_skips_import_when_not_frozen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not import pyi_splash during normal Python execution."""
    monkeypatch.setattr(splash, "is_frozen_executable", lambda: False)

    def fail_import(module_name: str) -> object:
        raise AssertionError(f"Unexpected import attempt: {module_name}")

    monkeypatch.setattr(splash.importlib, "import_module", fail_import)

    assert splash.load_splash_module() is None


def test_load_splash_module_returns_none_when_optional_module_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Continue startup when PyInstaller does not expose pyi_splash."""
    monkeypatch.setattr(splash, "is_frozen_executable", lambda: True)

    def raise_import_error(module_name: str) -> object:
        raise ImportError(f"No module named {module_name}")

    monkeypatch.setattr(splash.importlib, "import_module", raise_import_error)

    assert splash.load_splash_module() is None


def test_load_splash_module_returns_none_when_import_fails_unexpectedly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Continue startup when the optional splash import raises an unknown error."""
    monkeypatch.setattr(splash, "is_frozen_executable", lambda: True)

    def raise_runtime_error(module_name: str) -> object:
        raise RuntimeError(f"Failed to import {module_name}")

    monkeypatch.setattr(splash.importlib, "import_module", raise_runtime_error)

    assert splash.load_splash_module() is None


def test_load_splash_module_returns_imported_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return the imported PyInstaller splash module in frozen execution."""
    fake_module = FakeSplashModule()

    monkeypatch.setattr(splash, "is_frozen_executable", lambda: True)
    monkeypatch.setattr(
        splash.importlib,
        "import_module",
        lambda module_name: fake_module,
    )

    assert splash.load_splash_module() is fake_module


def test_close_splash_once_skips_when_close_was_already_attempted(
    app_state: AppState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Avoid multiple close attempts during client reconnects."""
    monkeypatch.setattr(splash, "_splash_close_attempted", True)

    splash.close_splash_once()

    assert app_state.lifecycle.splash_close_attempted is False
    assert app_state.lifecycle.splash_closed is False


def test_close_splash_once_marks_attempt_when_no_module_was_loaded(
    app_state: AppState,
) -> None:
    """Record the close attempt even when there is no splash module."""
    splash.close_splash_once()

    assert app_state.lifecycle.splash_close_attempted is True
    assert app_state.lifecycle.splash_closed is False


def test_close_splash_once_closes_loaded_module(app_state: AppState) -> None:
    """Close the loaded PyInstaller splash module successfully."""
    fake_module = FakeSplashModule()
    splash._splash_module = fake_module

    splash.close_splash_once()

    assert fake_module.close_call_count == 1
    assert app_state.lifecycle.splash_close_attempted is True
    assert app_state.lifecycle.splash_closed is True


def test_close_splash_once_keeps_closed_state_false_when_close_fails(
    app_state: AppState,
) -> None:
    """Keep diagnostics accurate when the splash module raises during close."""
    splash._splash_module = FailingSplashModule()

    splash.close_splash_once()

    assert app_state.lifecycle.splash_close_attempted is True
    assert app_state.lifecycle.splash_closed is False


def test_register_splash_handler_skips_registration_when_no_module_is_loaded(
    app_state: AppState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not register a NiceGUI callback when pyi_splash is unavailable."""
    monkeypatch.setattr(splash, "load_splash_module", lambda: None)

    def fail_on_connect(callback: Callable[[], None]) -> None:
        raise AssertionError(f"Unexpected callback registration: {callback}")

    monkeypatch.setattr(splash.app, "on_connect", fail_on_connect)

    splash.register_splash_handler()

    assert splash._splash_module is None
    assert app_state.lifecycle.splash_registered is False


def test_register_splash_handler_registers_close_callback(
    app_state: AppState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Register the one-time close callback when pyi_splash is available."""
    fake_module = FakeSplashModule()
    registered_callbacks: list[Callable[[], None]] = []

    monkeypatch.setattr(splash, "load_splash_module", lambda: fake_module)
    monkeypatch.setattr(splash.app, "on_connect", registered_callbacks.append)

    splash.register_splash_handler()

    assert splash._splash_module is fake_module
    assert registered_callbacks == [splash.close_splash_once]
    assert app_state.lifecycle.splash_registered is True
