# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/geometry.py
# Purpose:
# Normalize persisted window geometry against available Windows monitor areas.
# Behavior:
# Reads monitor work areas through the Win32 API when available and adjusts only
# window coordinates when persisted positions would make the window hard to
# recover after monitor changes.
# Notes:
# Width and height are preserved during monitor visibility correction. This
# matches the project requirement that monitor recovery should not resize the
# saved window dimensions.
# -----------------------------------------------------------------------------

from __future__ import annotations

import ctypes
from ctypes import wintypes
from logging import Logger
from typing import Final

from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state.defaults import (
    MAX_START_POSITION_RATIO,
    MIN_VISIBLE_EDGE_RATIO,
)
from desktop_app.infrastructure.native_window_state.models import MonitorWorkArea

logger: Final[Logger] = logger_get_logger(__name__)


def _normalize_window_geometry(
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    """Normalize persisted geometry against the current monitor layout.

    Args:
        x: Persisted horizontal window position in virtual-screen coordinates.
        y: Persisted vertical window position in virtual-screen coordinates.
        width: Persisted window width.
        height: Persisted window height.

    Returns:
        Safe ``x``, ``y``, ``width``, and ``height`` values. Monitor correction
        changes only ``x`` and ``y``; width and height are preserved.
    """
    safe_width = int(width)
    safe_height = int(height)

    work_areas = _get_windows_monitor_work_areas()
    if not work_areas:
        logger.debug(
            "Native window position was not clamped to monitors; "
            "no work area was found."
        )
        return x, y, safe_width, safe_height

    work_area = _select_relevant_work_area(
        x=x,
        y=y,
        width=safe_width,
        height=safe_height,
        work_areas=work_areas,
    )
    safe_x = _clamp_axis_position(
        position=x,
        size=safe_width,
        available_start=work_area.left,
        available_size=work_area.width,
    )
    safe_y = _clamp_axis_position(
        position=y,
        size=safe_height,
        available_start=work_area.top,
        available_size=work_area.height,
    )

    if (safe_x, safe_y, safe_width, safe_height) != (x, y, width, height):
        logger.info(
            "Persisted native window geometry adjusted to visible monitor area: "
            "original=(%s, %s, %s, %s), adjusted=(%s, %s, %s, %s), "
            "work_area=(%s, %s, %s, %s).",
            x,
            y,
            width,
            height,
            safe_x,
            safe_y,
            safe_width,
            safe_height,
            work_area.left,
            work_area.top,
            work_area.right,
            work_area.bottom,
        )

    return safe_x, safe_y, safe_width, safe_height


def _select_relevant_work_area(
    *,
    x: int,
    y: int,
    width: int,
    height: int,
    work_areas: tuple[MonitorWorkArea, ...],
) -> MonitorWorkArea:
    """Select the monitor work area most relevant to a persisted window.

    Args:
        x: Persisted horizontal window position.
        y: Persisted vertical window position.
        width: Persisted window width.
        height: Persisted window height.
        work_areas: Available monitor work areas.

    Returns:
        The work area that overlaps the window the most, or the nearest work
        area when the window is completely outside all monitors.
    """
    best_area = max(
        work_areas,
        key=lambda area: _intersection_area(
            left_a=x,
            top_a=y,
            right_a=x + width,
            bottom_a=y + height,
            left_b=area.left,
            top_b=area.top,
            right_b=area.right,
            bottom_b=area.bottom,
        ),
    )
    if (
        _intersection_area(
            left_a=x,
            top_a=y,
            right_a=x + width,
            bottom_a=y + height,
            left_b=best_area.left,
            top_b=best_area.top,
            right_b=best_area.right,
            bottom_b=best_area.bottom,
        )
        > 0
    ):
        return best_area

    return min(
        work_areas,
        key=lambda area: _squared_distance_between_centers(
            x + width // 2,
            y + height // 2,
            area.left + area.width // 2,
            area.top + area.height // 2,
        ),
    )


def _intersection_area(
    *,
    left_a: int,
    top_a: int,
    right_a: int,
    bottom_a: int,
    left_b: int,
    top_b: int,
    right_b: int,
    bottom_b: int,
) -> int:
    """Return the intersection area between two rectangles."""
    intersection_width = max(0, min(right_a, right_b) - max(left_a, left_b))
    intersection_height = max(0, min(bottom_a, bottom_b) - max(top_a, top_b))
    return intersection_width * intersection_height


def _squared_distance_between_centers(
    first_x: int,
    first_y: int,
    second_x: int,
    second_y: int,
) -> int:
    """Return squared distance between two points without using floats."""
    return (first_x - second_x) ** 2 + (first_y - second_y) ** 2


def _clamp_axis_position(
    *,
    position: int,
    size: int,
    available_start: int,
    available_size: int,
) -> int:
    """Clamp one persisted window coordinate to the expected visible range.

    The rule preserves the window size and only changes the coordinate when the
    saved position would make the window hard to recover:

    * if the start coordinate is beyond 90% of the work area, move it back to
      the 90% mark;
    * if the end edge is before the first 10% of the work area, move the window
      to the beginning of that work area.

    Args:
        position: Persisted coordinate for one axis.
        size: Window size on the same axis.
        available_start: Start coordinate of the monitor work area on the axis.
        available_size: Available monitor work-area size on the same axis.

    Returns:
        Coordinate adjusted to keep a recoverable visible part of the window.
    """
    if available_size <= 0:
        return position

    maximum_start_position = available_start + round(
        available_size * MAX_START_POSITION_RATIO
    )
    minimum_visible_edge = available_start + round(
        available_size * MIN_VISIBLE_EDGE_RATIO
    )

    if position > maximum_start_position:
        return maximum_start_position

    if position + size < minimum_visible_edge:
        return available_start

    return position


def _get_windows_monitor_work_areas() -> tuple[MonitorWorkArea, ...]:
    """Return Windows monitor work areas in virtual-screen coordinates.

    Returns:
        A tuple of monitor work areas excluding taskbars. An empty tuple is
        returned when monitor detection is unavailable or fails.
    """
    try:
        user32 = ctypes.windll.user32
    except AttributeError:
        logger.debug("Windows monitor detection is unavailable on this platform.")
        return ()

    monitors: list[MonitorWorkArea] = []

    class Rect(ctypes.Structure):
        _fields_ = [
            ("left", wintypes.LONG),
            ("top", wintypes.LONG),
            ("right", wintypes.LONG),
            ("bottom", wintypes.LONG),
        ]

    class MonitorInfo(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", Rect),
            ("rcWork", Rect),
            ("dwFlags", wintypes.DWORD),
        ]

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(Rect),
        wintypes.LPARAM,
    )

    user32.GetMonitorInfoW.argtypes = [
        wintypes.HMONITOR,
        ctypes.POINTER(MonitorInfo),
    ]
    user32.GetMonitorInfoW.restype = wintypes.BOOL
    user32.EnumDisplayMonitors.argtypes = [
        wintypes.HDC,
        ctypes.c_void_p,
        monitor_enum_proc,
        wintypes.LPARAM,
    ]
    user32.EnumDisplayMonitors.restype = wintypes.BOOL

    def collect_monitor(
        monitor_handle: int,
        _device_context: int,
        _rect: object,
        _data: int,
    ) -> int:
        """Collect one monitor work area from the Windows callback."""
        monitor_info = MonitorInfo()
        monitor_info.cbSize = ctypes.sizeof(MonitorInfo)
        if not user32.GetMonitorInfoW(monitor_handle, ctypes.byref(monitor_info)):
            logger.debug("Windows monitor info lookup failed for a monitor.")
            return 1

        work = monitor_info.rcWork
        work_area = MonitorWorkArea(
            left=int(work.left),
            top=int(work.top),
            right=int(work.right),
            bottom=int(work.bottom),
        )
        if work_area.width > 0 and work_area.height > 0:
            monitors.append(work_area)
        return 1

    callback = monitor_enum_proc(collect_monitor)

    try:
        result = user32.EnumDisplayMonitors(0, 0, callback, 0)
    except Exception:
        logger.debug("Windows monitor work-area detection failed.", exc_info=True)
        return ()

    if not result:
        logger.debug("Windows monitor work-area detection returned no result.")
        return ()

    return tuple(monitors)
