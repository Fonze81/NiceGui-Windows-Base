"""Tests for native window monitor geometry helpers."""

from __future__ import annotations

from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


def test_clamp_axis_position_ignores_invalid_available_size(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid monitor axis sizes leave the persisted coordinate unchanged."""
    assert (
        native_window_state_module.geometry._clamp_axis_position(
            position=42,
            size=100,
            available_start=0,
            available_size=0,
        )
        == 42
    )


def test_get_windows_monitor_work_areas_reads_win32_work_areas(
    native_window_state_module: ModuleType,
    install_fake_win32_monitor_api: Any,
) -> None:
    """Windows monitor enumeration returns valid work areas."""
    install_fake_win32_monitor_api(
        native_window_state_module,
        work_areas={1: (0, 0, 1000, 800), 2: (1920, 0, 3840, 1040)},
    )

    work_areas = native_window_state_module.geometry._get_windows_monitor_work_areas()

    assert work_areas == (
        native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),
        native_window_state_module.models.MonitorWorkArea(1920, 0, 3840, 1040),
    )


def test_get_windows_monitor_work_areas_skips_monitor_info_failures(
    native_window_state_module: ModuleType,
    install_fake_win32_monitor_api: Any,
) -> None:
    """Monitor handles without work area data are ignored."""
    install_fake_win32_monitor_api(
        native_window_state_module,
        work_areas={1: (0, 0, 1000, 800), 2: (0, 0, 0, 0)},
    )

    work_areas = native_window_state_module.geometry._get_windows_monitor_work_areas()

    assert work_areas == (
        native_window_state_module.models.MonitorWorkArea(0, 0, 1000, 800),
    )


def test_get_windows_monitor_work_areas_returns_empty_on_enum_failure(
    native_window_state_module: ModuleType,
    install_fake_win32_monitor_api: Any,
) -> None:
    """A failed Win32 enumeration result is treated as unavailable monitors."""
    install_fake_win32_monitor_api(native_window_state_module, enum_result=0)

    assert native_window_state_module.geometry._get_windows_monitor_work_areas() == ()


def test_get_windows_monitor_work_areas_returns_empty_on_enum_exception(
    native_window_state_module: ModuleType,
    install_fake_win32_monitor_api: Any,
) -> None:
    """Win32 monitor API exceptions do not break application startup."""
    install_fake_win32_monitor_api(native_window_state_module, enum_raises=True)

    assert native_window_state_module.geometry._get_windows_monitor_work_areas() == ()


def test_get_windows_monitor_work_areas_keeps_valid_monitors_after_info_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    assignable_callable_cls: type,
) -> None:
    """A monitor info failure does not prevent later valid monitors from loading."""

    def winfunctype_factory(*_args: object) -> Any:
        """Return a callback adapter matching ctypes.WINFUNCTYPE."""
        return lambda callback: callback

    def get_monitor_info(monitor_handle: int, monitor_info_pointer: object) -> int:
        """Fail the first fake monitor and populate the second one."""
        if monitor_handle == 1:
            return 0

        monitor_info = monitor_info_pointer._obj
        monitor_info.rcWork.left = 10
        monitor_info.rcWork.top = 20
        monitor_info.rcWork.right = 1010
        monitor_info.rcWork.bottom = 820
        return 1

    def enum_display_monitors(
        _hdc: object,
        _clip_rect: object,
        callback: Any,
        _data: object,
    ) -> int:
        """Enumerate one failing monitor and one valid monitor."""
        callback(1, 0, None, 0)
        callback(2, 0, None, 0)
        return 1

    fake_user32 = SimpleNamespace(
        GetMonitorInfoW=assignable_callable_cls(get_monitor_info),
        EnumDisplayMonitors=assignable_callable_cls(enum_display_monitors),
    )

    monkeypatch.setattr(
        native_window_state_module.geometry.ctypes,
        "WINFUNCTYPE",
        winfunctype_factory,
        raising=False,
    )
    monkeypatch.setattr(
        native_window_state_module.geometry.ctypes,
        "windll",
        SimpleNamespace(user32=fake_user32),
        raising=False,
    )

    assert native_window_state_module.geometry._get_windows_monitor_work_areas() == (
        native_window_state_module.models.MonitorWorkArea(10, 20, 1010, 820),
    )
