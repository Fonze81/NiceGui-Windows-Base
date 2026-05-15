# -----------------------------------------------------------------------------
# File: tests/infrastructure/native_window_state/conftest.py
# Purpose:
# Provide shared fixtures for native window state package tests.
# Behavior:
# Loads the native_window_state package with a fake NiceGUI app and exposes fake
# native window objects so tests can run without opening a real desktop window.
# Notes:
# These fixtures keep native integration tests deterministic and prevent real UI
# or settings I/O unless a test explicitly monkeypatches persistence behavior.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from desktop_app.core.state import reset_app_state


@dataclass(slots=True)
class FakeWindow:
    """Represent the subset of pywebview window API used by the app."""

    x: int = 10
    y: int = 20
    width: int = 1200
    height: int = 800
    moves: list[tuple[int, int]] = field(default_factory=list)
    resizes: list[tuple[int, int]] = field(default_factory=list)
    show_calls: int = 0
    maximize_calls: int = 0

    def move(self, x: int, y: int) -> None:
        """Record a native move request."""
        self.moves.append((x, y))
        self.x = x
        self.y = y

    def resize(self, width: int, height: int) -> None:
        """Record a native resize request."""
        self.resizes.append((width, height))
        self.width = width
        self.height = height

    def show(self) -> None:
        """Record a native show request."""
        self.show_calls += 1

    def maximize(self) -> None:
        """Record a native maximize request."""
        self.maximize_calls += 1


class AssignableCallable:
    """Wrap a callable while allowing ctypes-style attributes."""

    def __init__(self, implementation: Callable[..., object]) -> None:
        """Store the wrapped implementation."""
        self._implementation = implementation

    def __call__(self, *args: object) -> object:
        """Delegate the call to the wrapped implementation."""
        return self._implementation(*args)


class AsyncNativeWindowProxy:
    """Expose async NiceGUI native window geometry methods for tests."""

    def __init__(
        self,
        *,
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Store geometry values returned by async methods."""
        self._position = position
        self._size = size

    async def get_position(self) -> tuple[int, int] | None:
        """Return the configured native window position."""
        return self._position

    async def get_size(self) -> tuple[int, int] | None:
        """Return the configured native window size."""
        return self._size


class PartialAsyncNativeWindowProxy:
    """Expose optional async geometry values for branch-specific refresh tests."""

    def __init__(
        self,
        *,
        position: tuple[int, int] | None,
        size: tuple[int, int] | None,
    ) -> None:
        """Store optional geometry values."""
        self._position = position
        self._size = size

    async def get_position(self) -> tuple[int, int] | None:
        """Return the configured optional position."""
        return self._position

    async def get_size(self) -> tuple[int, int] | None:
        """Return the configured optional size."""
        return self._size


class BrokenNativeWindowProxy:
    """Expose a native window method that raises during geometry refresh."""

    def get_position(self) -> tuple[int, int]:
        """Raise to simulate a failing native proxy call."""
        raise RuntimeError("native proxy failed")


class SyncNativeWindowProxy:
    """Expose synchronous geometry methods accepted by the proxy helper."""

    def get_size(self) -> tuple[int, int]:
        """Return a synchronous native window size pair."""
        return 1440, 900


def _clear_native_window_state_modules() -> None:
    """Remove the native window state package and submodules from sys.modules."""
    package_name = "desktop_app.infrastructure.native_window_state"
    for module_name in tuple(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            sys.modules.pop(module_name, None)


@pytest.fixture()
def native_window_state_module(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[ModuleType]:
    """Load the native_window_state package with a fake NiceGUI app object."""
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui_module = SimpleNamespace(app=SimpleNamespace(native=fake_native))

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)
    _clear_native_window_state_modules()

    module = importlib.import_module("desktop_app.infrastructure.native_window_state")
    importlib.import_module("desktop_app.infrastructure.native_window_state.arguments")
    importlib.import_module("desktop_app.infrastructure.native_window_state.bridge")
    importlib.import_module("desktop_app.infrastructure.native_window_state.events")
    importlib.import_module("desktop_app.infrastructure.native_window_state.geometry")
    importlib.import_module("desktop_app.infrastructure.native_window_state.models")
    importlib.import_module(
        "desktop_app.infrastructure.native_window_state.persistence"
    )
    importlib.import_module("desktop_app.infrastructure.native_window_state.service")

    yield module

    _clear_native_window_state_modules()
    reset_app_state()


@pytest.fixture()
def fake_window_cls() -> type[FakeWindow]:
    """Return the fake native window class."""
    return FakeWindow


@pytest.fixture()
def assignable_callable_cls() -> type[AssignableCallable]:
    """Return the assignable callable helper class."""
    return AssignableCallable


@pytest.fixture()
def async_native_window_proxy_cls() -> type[AsyncNativeWindowProxy]:
    """Return the async native window proxy class."""
    return AsyncNativeWindowProxy


@pytest.fixture()
def partial_async_native_window_proxy_cls() -> type[PartialAsyncNativeWindowProxy]:
    """Return the partial async native window proxy class."""
    return PartialAsyncNativeWindowProxy


@pytest.fixture()
def broken_native_window_proxy_cls() -> type[BrokenNativeWindowProxy]:
    """Return the broken native window proxy class."""
    return BrokenNativeWindowProxy


@pytest.fixture()
def sync_native_window_proxy_cls() -> type[SyncNativeWindowProxy]:
    """Return the synchronous native window proxy class."""
    return SyncNativeWindowProxy


@pytest.fixture()
def install_fake_win32_monitor_api(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., None]:
    """Return a helper that installs a fake Win32 monitor API."""

    def install(
        native_window_state_module: ModuleType,
        *,
        work_areas: dict[int, tuple[int, int, int, int]] | None = None,
        enum_result: int = 1,
        enum_raises: bool = False,
    ) -> None:
        """Install fake ctypes monitor functions on the geometry module."""
        selected_work_areas = work_areas or {1: (0, 0, 1000, 800)}

        def winfunctype_factory(*_args: object) -> Any:
            """Return a callback adapter matching ctypes.WINFUNCTYPE."""
            return lambda callback: callback

        def get_monitor_info(
            monitor_handle: int,
            monitor_info_pointer: object,
        ) -> int:
            """Populate monitor information for one fake monitor handle."""
            if monitor_handle not in selected_work_areas:
                return 0

            monitor_info = monitor_info_pointer._obj
            left, top, right, bottom = selected_work_areas[monitor_handle]
            monitor_info.rcWork.left = left
            monitor_info.rcWork.top = top
            monitor_info.rcWork.right = right
            monitor_info.rcWork.bottom = bottom
            return 1

        def enum_display_monitors(
            _hdc: object,
            _clip_rect: object,
            callback: Any,
            _data: object,
        ) -> int:
            """Invoke the callback for all configured fake monitor handles."""
            if enum_raises:
                raise OSError("monitor enumeration failed")

            for monitor_handle in selected_work_areas:
                callback(monitor_handle, 0, None, 0)
            return enum_result

        fake_user32 = SimpleNamespace(
            GetMonitorInfoW=AssignableCallable(get_monitor_info),
            EnumDisplayMonitors=AssignableCallable(enum_display_monitors),
        )
        fake_windll = SimpleNamespace(user32=fake_user32)

        monkeypatch.setattr(
            native_window_state_module.geometry.ctypes,
            "WINFUNCTYPE",
            winfunctype_factory,
            raising=False,
        )
        monkeypatch.setattr(
            native_window_state_module.geometry.ctypes,
            "windll",
            fake_windll,
            raising=False,
        )

    return install
