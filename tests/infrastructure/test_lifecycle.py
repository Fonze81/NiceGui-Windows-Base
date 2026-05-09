# -----------------------------------------------------------------------------
# File: tests/infrastructure/test_lifecycle.py
# Purpose:
# Validate NiceGUI lifecycle wiring and runtime state updates.
# Behavior:
# Uses small fakes for NiceGUI app registration, asyncio loops, and the module
# logger so lifecycle behavior can be tested without opening a UI runtime.
# Notes:
# These tests intentionally cover private handlers because lifecycle.py is an
# integration wiring module whose public behavior is produced by registered
# callbacks.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from desktop_app.core.state import get_app_state, reset_app_state

LifecycleCallback = Callable[..., None]


@dataclass(slots=True)
class LoggedCall:
    """Represent one logger call captured during a test."""

    level: str
    message: str
    args: tuple[object, ...] = field(default_factory=tuple)
    kwargs: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class FakeLogger:
    """Capture lifecycle log calls without using real logging handlers."""

    calls: list[LoggedCall] = field(default_factory=list)

    def debug(self, message: str, *args: object, **kwargs: object) -> None:
        """Capture a debug log call."""
        self.calls.append(LoggedCall("debug", message, args, kwargs))

    def info(self, message: str, *args: object, **kwargs: object) -> None:
        """Capture an info log call."""
        self.calls.append(LoggedCall("info", message, args, kwargs))

    def error(self, message: str, *args: object, **kwargs: object) -> None:
        """Capture an error log call."""
        self.calls.append(LoggedCall("error", message, args, kwargs))


@dataclass(slots=True)
class FakeNativeApp:
    """Capture native window event handler registrations."""

    handlers: dict[str, list[LifecycleCallback]] = field(default_factory=dict)

    def on(self, event_name: str, callback: LifecycleCallback) -> None:
        """Register a native event callback."""
        self.handlers.setdefault(event_name, []).append(callback)


@dataclass(slots=True)
class FakeNiceGuiApp:
    """Capture generic NiceGUI event handler registrations."""

    native: FakeNativeApp = field(default_factory=FakeNativeApp)
    startup_handlers: list[LifecycleCallback] = field(default_factory=list)
    shutdown_handlers: list[LifecycleCallback] = field(default_factory=list)
    connect_handlers: list[LifecycleCallback] = field(default_factory=list)
    disconnect_handlers: list[LifecycleCallback] = field(default_factory=list)
    exception_handlers: list[LifecycleCallback] = field(default_factory=list)
    page_exception_handlers: list[LifecycleCallback] = field(default_factory=list)

    def on_startup(self, callback: LifecycleCallback) -> None:
        """Register an application startup callback."""
        self.startup_handlers.append(callback)

    def on_shutdown(self, callback: LifecycleCallback) -> None:
        """Register an application shutdown callback."""
        self.shutdown_handlers.append(callback)

    def on_connect(self, callback: LifecycleCallback) -> None:
        """Register a client connection callback."""
        self.connect_handlers.append(callback)

    def on_disconnect(self, callback: LifecycleCallback) -> None:
        """Register a client disconnection callback."""
        self.disconnect_handlers.append(callback)

    def on_exception(self, callback: LifecycleCallback) -> None:
        """Register an application exception callback."""
        self.exception_handlers.append(callback)

    def on_page_exception(self, callback: LifecycleCallback) -> None:
        """Register a page exception callback."""
        self.page_exception_handlers.append(callback)


@dataclass(slots=True)
class FakeEventLoop:
    """Capture asyncio exception handler behavior."""

    exception_handler: Callable[[Any, dict[str, Any]], None] | None = None
    default_contexts: list[dict[str, Any]] = field(default_factory=list)

    def set_exception_handler(
        self,
        handler: Callable[[Any, dict[str, Any]], None],
    ) -> None:
        """Store the configured asyncio exception handler."""
        self.exception_handler = handler

    def default_exception_handler(self, context: dict[str, Any]) -> None:
        """Store contexts delegated to the default exception handler."""
        self.default_contexts.append(context)


@dataclass(slots=True)
class FakeWindowsConnectionResetError(ConnectionResetError):
    """ConnectionResetError variant with a Windows winerror attribute."""

    winerror: int


@pytest.fixture()
def lifecycle_module(monkeypatch: pytest.MonkeyPatch) -> Generator[ModuleType]:
    """Load lifecycle.py with a fake NiceGUI app and isolated state."""
    fake_app = FakeNiceGuiApp()
    fake_logger = FakeLogger()
    fake_nicegui_module = SimpleNamespace(app=fake_app)

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)
    sys.modules.pop("desktop_app.infrastructure.splash", None)
    sys.modules.pop("desktop_app.infrastructure.lifecycle", None)

    module = importlib.import_module("desktop_app.infrastructure.lifecycle")
    monkeypatch.setattr(module, "logger", fake_logger)

    yield module

    sys.modules.pop("desktop_app.infrastructure.lifecycle", None)
    sys.modules.pop("desktop_app.infrastructure.splash", None)
    reset_app_state()


def test_is_expected_windows_connection_reset_accepts_message_match(
    lifecycle_module: ModuleType,
) -> None:
    """Expected Windows native shutdown noise is detected from context message."""
    context = {
        "exception": FakeWindowsConnectionResetError(10054),
        "message": "Exception in callback _call_connection_lost",
    }

    assert lifecycle_module._is_expected_windows_connection_reset(context) is True


def test_is_expected_windows_connection_reset_accepts_handle_repr_match(
    lifecycle_module: ModuleType,
) -> None:
    """Expected Windows native shutdown noise is detected from handle repr."""
    context = {
        "exception": FakeWindowsConnectionResetError(10054),
        "handle": "<Handle _call_connection_lost>",
    }

    assert lifecycle_module._is_expected_windows_connection_reset(context) is True


@pytest.mark.parametrize(
    "context",
    [
        {},
        {"exception": RuntimeError("boom")},
        {"exception": FakeWindowsConnectionResetError(10053)},
        {"exception": FakeWindowsConnectionResetError(10054)},
    ],
)
def test_is_expected_windows_connection_reset_rejects_unexpected_contexts(
    lifecycle_module: ModuleType,
    context: dict[str, object],
) -> None:
    """Unexpected asyncio contexts are not suppressed."""
    assert lifecycle_module._is_expected_windows_connection_reset(context) is False


def test_handle_asyncio_exception_suppresses_expected_windows_shutdown_noise(
    lifecycle_module: ModuleType,
) -> None:
    """Known Windows native shutdown noise is not delegated to default handling."""
    fake_loop = FakeEventLoop()
    context = {
        "exception": FakeWindowsConnectionResetError(10054),
        "message": "Exception in callback _call_connection_lost",
    }

    lifecycle_module._handle_asyncio_exception(fake_loop, context)

    assert fake_loop.default_contexts == []
    assert lifecycle_module.logger.calls[-1].level == "debug"


def test_handle_asyncio_exception_delegates_unexpected_context(
    lifecycle_module: ModuleType,
) -> None:
    """Unexpected asyncio contexts are delegated to default loop handling."""
    fake_loop = FakeEventLoop()
    context = {"exception": RuntimeError("boom")}

    lifecycle_module._handle_asyncio_exception(fake_loop, context)

    assert fake_loop.default_contexts == [context]


def test_configure_asyncio_exception_handler_logs_when_no_loop_is_running(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The asyncio handler setup is skipped safely when no loop is active."""

    def raise_no_running_loop() -> None:
        """Simulate asyncio.get_running_loop outside an event loop."""
        raise RuntimeError("no running event loop")

    monkeypatch.setattr(
        lifecycle_module.asyncio,
        "get_running_loop",
        raise_no_running_loop,
    )

    lifecycle_module._configure_asyncio_exception_handler()

    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "debug",
        "Asyncio exception handler was not installed; no loop is running.",
    )


def test_configure_asyncio_exception_handler_installs_handler(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The asyncio handler setup installs the module exception handler."""
    fake_loop = FakeEventLoop()
    monkeypatch.setattr(
        lifecycle_module.asyncio,
        "get_running_loop",
        lambda: fake_loop,
    )

    lifecycle_module._configure_asyncio_exception_handler()

    assert fake_loop.exception_handler is lifecycle_module._handle_asyncio_exception
    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "debug",
        "Asyncio exception handler installed.",
    )


def test_log_exception_event_logs_missing_exception(
    lifecycle_module: ModuleType,
) -> None:
    """NiceGUI exception events without exception objects are logged clearly."""
    lifecycle_module._log_exception_event("Message.", ("not an exception",))

    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "error",
        "%s No exception object was provided by NiceGUI.",
        ("Message.",),
    )


def test_log_exception_event_logs_exception_with_traceback(
    lifecycle_module: ModuleType,
) -> None:
    """NiceGUI exception events preserve traceback information."""
    exception = ValueError("invalid value")

    lifecycle_module._log_exception_event("Message.", ("ignored", exception))

    log_call = lifecycle_module.logger.calls[-1]
    assert log_call.level == "error"
    assert log_call.message == "%s %s: %s"
    assert log_call.args == ("Message.", "ValueError", exception)
    assert log_call.kwargs["exc_info"] == (
        ValueError,
        exception,
        exception.__traceback__,
    )


def test_application_started_updates_state_and_configures_asyncio_handler(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Application startup updates lifecycle state and configures asyncio."""
    configured = False

    def mark_configured() -> None:
        """Record that asyncio configuration was requested."""
        nonlocal configured
        configured = True

    monkeypatch.setattr(
        lifecycle_module,
        "_configure_asyncio_exception_handler",
        mark_configured,
    )

    lifecycle_module._handle_application_started()

    assert get_app_state().lifecycle.runtime_started is True
    assert configured is True
    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "info",
        "NiceGUI runtime started.",
    )


def test_application_shutdown_updates_state_and_stops_logger(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Application shutdown updates lifecycle state and shuts down logging."""
    shutdown_called = False

    def mark_shutdown_called() -> None:
        """Record that logger shutdown was requested."""
        nonlocal shutdown_called
        shutdown_called = True

    monkeypatch.setattr(lifecycle_module, "logger_shutdown", mark_shutdown_called)

    lifecycle_module._handle_application_shutdown()

    assert get_app_state().lifecycle.shutdown_started is True
    assert get_app_state().lifecycle.shutdown_completed is True
    assert shutdown_called is True
    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "info",
        "Application shutdown completed.",
    )


def test_client_connection_handlers_update_state(lifecycle_module: ModuleType) -> None:
    """Client connect and disconnect events update lifecycle state."""
    lifecycle_module._handle_client_connected()
    assert get_app_state().lifecycle.client_connected is True

    lifecycle_module._handle_client_disconnected()
    assert get_app_state().lifecycle.client_connected is False


def test_exception_handlers_delegate_to_exception_logger(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Application and page exception handlers reuse the shared logger helper."""
    calls: list[tuple[str, tuple[object, ...]]] = []

    def capture_exception_event(
        event_message: str,
        event_args: tuple[object, ...],
    ) -> None:
        """Record delegated exception events."""
        calls.append((event_message, event_args))

    monkeypatch.setattr(
        lifecycle_module,
        "_log_exception_event",
        capture_exception_event,
    )
    exception = RuntimeError("boom")

    lifecycle_module._handle_application_exception("context", exception)
    lifecycle_module._handle_page_exception(exception)

    assert calls == [
        (
            "NiceGUI reported an application-level exception.",
            ("context", exception),
        ),
        ("NiceGUI reported a page-level exception.", (exception,)),
    ]


def test_native_window_handlers_update_state(lifecycle_module: ModuleType) -> None:
    """Native window callbacks keep high-level lifecycle state synchronized."""
    state = get_app_state()

    lifecycle_module._handle_native_window_shown()
    assert state.lifecycle.native_window_opened is True
    assert state.lifecycle.native_window_closed is False

    lifecycle_module._handle_native_window_loaded()
    assert state.lifecycle.native_window_loaded is True

    lifecycle_module._handle_native_window_minimized()
    assert state.lifecycle.native_window_minimized is True
    assert state.lifecycle.native_window_maximized is False

    lifecycle_module._handle_native_window_maximized()
    assert state.lifecycle.native_window_maximized is True
    assert state.lifecycle.native_window_minimized is False

    lifecycle_module._handle_native_window_restored()
    assert state.lifecycle.native_window_maximized is False
    assert state.lifecycle.native_window_minimized is False

    lifecycle_module._handle_native_window_closed()
    assert state.lifecycle.native_window_closed is True
    assert state.lifecycle.native_window_opened is False


def test_debug_only_native_window_handlers_log_events(
    lifecycle_module: ModuleType,
) -> None:
    """Resize and move callbacks emit debug diagnostics only."""
    lifecycle_module._handle_native_window_resized()
    lifecycle_module._handle_native_window_moved()

    assert lifecycle_module.logger.calls[-2:] == [
        LoggedCall("debug", "The native window was resized."),
        LoggedCall("debug", "The native window was moved."),
    ]


def test_native_file_drop_logs_event(lifecycle_module: ModuleType) -> None:
    """Native file-drop events are logged for operational diagnostics."""
    lifecycle_module._handle_native_file_drop("file.txt")

    assert lifecycle_module.logger.calls[-1] == LoggedCall(
        "info",
        "Files were dropped on the native window.",
    )


def test_register_application_handlers(lifecycle_module: ModuleType) -> None:
    """Generic NiceGUI lifecycle callbacks are registered on the app object."""
    fake_app = lifecycle_module.app

    lifecycle_module._register_application_handlers()

    assert fake_app.startup_handlers == [lifecycle_module._handle_application_started]
    assert fake_app.shutdown_handlers == [lifecycle_module._handle_application_shutdown]
    assert fake_app.connect_handlers == [lifecycle_module._handle_client_connected]
    assert fake_app.disconnect_handlers == [
        lifecycle_module._handle_client_disconnected
    ]
    assert fake_app.exception_handlers == [
        lifecycle_module._handle_application_exception
    ]
    assert fake_app.page_exception_handlers == [lifecycle_module._handle_page_exception]


def test_register_native_window_handlers(lifecycle_module: ModuleType) -> None:
    """Native window callbacks are registered for all supported native events."""
    fake_native = lifecycle_module.app.native

    lifecycle_module._register_native_window_handlers()

    assert fake_native.handlers == {
        "shown": [lifecycle_module._handle_native_window_shown],
        "loaded": [lifecycle_module._handle_native_window_loaded],
        "minimized": [lifecycle_module._handle_native_window_minimized],
        "maximized": [lifecycle_module._handle_native_window_maximized],
        "restored": [lifecycle_module._handle_native_window_restored],
        "resized": [lifecycle_module._handle_native_window_resized],
        "moved": [lifecycle_module._handle_native_window_moved],
        "closed": [lifecycle_module._handle_native_window_closed],
        "drop": [lifecycle_module._handle_native_file_drop],
    }


def test_register_lifecycle_handlers_in_native_mode(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Native mode registers generic, native, and splash lifecycle handlers."""
    splash_registered = False

    def mark_splash_registered() -> None:
        """Record that splash registration was requested."""
        nonlocal splash_registered
        splash_registered = True

    monkeypatch.setattr(
        lifecycle_module,
        "register_splash_handler",
        mark_splash_registered,
    )

    lifecycle_module.register_lifecycle_handlers(native_mode=True)

    state = get_app_state()
    assert state.lifecycle.handlers_registered is True
    assert state.lifecycle.native_handlers_registered is True
    assert splash_registered is True
    assert lifecycle_module.app.startup_handlers == [
        lifecycle_module._handle_application_started
    ]
    assert "shown" in lifecycle_module.app.native.handlers


def test_register_lifecycle_handlers_in_web_mode(
    lifecycle_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Web mode registers only generic and splash lifecycle handlers."""
    splash_registered = False

    def mark_splash_registered() -> None:
        """Record that splash registration was requested."""
        nonlocal splash_registered
        splash_registered = True

    monkeypatch.setattr(
        lifecycle_module,
        "register_splash_handler",
        mark_splash_registered,
    )

    lifecycle_module.register_lifecycle_handlers(native_mode=False)

    state = get_app_state()
    assert state.lifecycle.handlers_registered is True
    assert state.lifecycle.native_handlers_registered is False
    assert splash_registered is True
    assert lifecycle_module.app.native.handlers == {}
