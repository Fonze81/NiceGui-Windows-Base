# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state.py
# Purpose:
# Capture, restore, and persist native desktop window geometry.
# Behavior:
# Normalizes persisted coordinates against the current monitor work area, applies
# all startup geometry through NiceGUI native window arguments before ui.run,
# keeps native startup arguments synchronized with normalized state, and saves
# the window settings group during application exit.
# Notes:
# NiceGUI delegates native windows to pywebview and forwards native events as
# NativeEventArguments objects. Startup window information must have a single
# source of truth: app.native.window_args. Do not also pass size or fullscreen
# values through ui.run, because multiple sources can create backend-dependent
# ordering issues. Native event dictionaries are preferred over window
# attributes because they carry the real width, height, x, and y values reported
# by pywebview.
# -----------------------------------------------------------------------------

from __future__ import annotations

import ctypes
import inspect
from collections.abc import Callable, Iterable
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from typing import Any, Final, cast

from nicegui import app

from desktop_app.core.state import AppState, WindowState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.settings import save_settings_group

logger: Final[Logger] = logger_get_logger(__name__)

_MIN_WINDOW_WIDTH: Final[int] = 400
_MIN_WINDOW_HEIGHT: Final[int] = 300
_MAX_START_POSITION_RATIO: Final[float] = 0.90
_MIN_VISIBLE_EDGE_RATIO: Final[float] = 0.10

_X_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("x", "left")
_Y_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("y", "top")
_WIDTH_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("width", "inner_width")
_HEIGHT_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("height", "inner_height")


@dataclass(frozen=True, slots=True)
class MonitorWorkArea:
    """Represent a Windows monitor work area in virtual-screen coordinates."""

    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        """Return the work-area width."""
        return self.right - self.left

    @property
    def height(self) -> int:
        """Return the work-area height."""
        return self.bottom - self.top


def apply_native_window_args_from_state(*, state: AppState | None = None) -> None:
    """Apply native pywebview arguments from AppState before ``main`` runs.

    NiceGUI native mode reads ``app.native.window_args`` while creating the
    pywebview window. Position values must be assigned as early as possible,
    before the application entry point starts ``ui.run``. Persisted values are
    normalized first so monitor changes do not leave the window off screen.

    Args:
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()
    normalize_persisted_window_geometry(state=current_state)
    _sync_native_window_args_from_state(current_state)


def _sync_native_window_args_from_state(current_state: AppState) -> None:
    """Synchronize NiceGUI native window arguments with AppState.

    Args:
        current_state: Application state containing normalized window values.
    """
    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)

    window_args = _get_native_window_args()
    window_args["width"] = width
    window_args["height"] = height
    window_args["fullscreen"] = current_state.window.fullscreen
    window_args.pop("hidden", None)

    if current_state.window.persist_state:
        window_args["x"] = current_state.window.x
        window_args["y"] = current_state.window.y
    else:
        window_args.pop("x", None)
        window_args.pop("y", None)

    logger.debug(
        "Native window arguments synchronized from state: size=(%s, %s), "
        "position=(%s, %s), fullscreen=%s, persist_state=%s.",
        width,
        height,
        window_args.get("x"),
        window_args.get("y"),
        current_state.window.fullscreen,
        current_state.window.persist_state,
    )


def normalize_persisted_window_geometry(*, state: AppState | None = None) -> bool:
    """Normalize persisted native window geometry before restoration.

    The persisted window position can become invalid when the user removes,
    changes, or reorders monitors. This function keeps the window anchored to a
    visible part of the selected monitor work area without resizing the saved
    width or height.
    When persistence is disabled, persisted geometry is reset to defaults and
    saved so stale values are not reused later.

    Args:
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when the in-memory state was changed.
    """
    current_state = state if state is not None else get_app_state()

    if not current_state.window.persist_state:
        changed = _reset_window_geometry_to_defaults(current_state.window)
        if changed:
            _save_normalized_window_group(current_state)
        return changed

    safe_x, safe_y, safe_width, safe_height = _normalize_window_geometry(
        x=current_state.window.x,
        y=current_state.window.y,
        width=current_state.window.width,
        height=current_state.window.height,
    )

    changed = _assign_if_different(current_state.window, "width", safe_width)
    changed = (
        _assign_if_different(current_state.window, "height", safe_height) or changed
    )
    changed = _assign_if_different(current_state.window, "x", safe_x) or changed
    changed = _assign_if_different(current_state.window, "y", safe_y) or changed

    if changed:
        _save_normalized_window_group(current_state)
        _sync_native_window_args_from_state(current_state)

    return changed


def apply_initial_native_window_options(
    ui_run_options: dict[str, Any],
    *,
    state: AppState | None = None,
) -> None:
    """Prepare native window startup arguments before ``ui.run`` starts.

    Window geometry has a single startup source of truth: ``app.native.window_args``.
    This function intentionally does not add ``window_size``, ``fullscreen``,
    ``window_position``, or other window-related keys to ``ui_run_options``.
    Keeping those values out of ``ui.run`` avoids conflicts between NiceGUI run
    options and pywebview native creation arguments.

    Args:
        ui_run_options: Mutable options dictionary passed to ``ui.run``. It is
            accepted for compatibility with the app startup flow and is not
            modified with window geometry values.
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()

    apply_native_window_args_from_state(state=current_state)

    window_args = _get_native_window_args()
    logger.debug(
        "Native window startup prepared through app.native.window_args only: "
        "size=(%s, %s), position=(%s, %s), fullscreen=%s, persist_state=%s.",
        window_args.get("width"),
        window_args.get("height"),
        window_args.get("x"),
        window_args.get("y"),
        window_args.get("fullscreen"),
        current_state.window.persist_state,
    )


def update_native_window_size(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Update AppState from a native resize event.

    NiceGUI forwards pywebview native events as a ``NativeEventArguments``
    object whose ``args`` dictionary contains ``width`` and ``height``. Raw
    integer pairs and native window attributes are still accepted to keep the
    helper easy to test and resilient to future backend changes.

    Args:
        event_args: Native resize event arguments. Expected production payload
            shape is ``NativeEventArguments(args={"width": ..., "height": ...})``.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when width or height was updated.
    """
    current_state = state if state is not None else get_app_state()
    width, height = _extract_pair_by_keys(event_args, "width", "height")

    if width is None or height is None:
        width, height = _extract_pair(event_args)

    if width is None or height is None:
        native_window = _select_native_window(event_args)
        if native_window is not None:
            width = _read_int_attribute(native_window, _WIDTH_ATTRIBUTE_NAMES)
            height = _read_int_attribute(native_window, _HEIGHT_ATTRIBUTE_NAMES)

    was_updated = False
    if width is not None and width >= _MIN_WINDOW_WIDTH:
        current_state.window.width = width
        was_updated = True
    if height is not None and height >= _MIN_WINDOW_HEIGHT:
        current_state.window.height = height
        was_updated = True

    if was_updated:
        logger.debug(
            "Native window size updated: width=%s, height=%s.",
            current_state.window.width,
            current_state.window.height,
        )
    else:
        logger.debug("Native window size was not updated from event payload.")

    return was_updated


def update_native_window_position(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Update AppState from a native move event.

    NiceGUI forwards pywebview native events as a ``NativeEventArguments``
    object whose ``args`` dictionary contains ``x`` and ``y``. Raw integer
    pairs and native window attributes are still accepted to keep the helper
    easy to test and resilient to future backend changes.

    Args:
        event_args: Native move event arguments. Expected production payload
            shape is ``NativeEventArguments(args={"x": ..., "y": ...})``.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when x or y was updated.
    """
    current_state = state if state is not None else get_app_state()
    x, y = _extract_pair_by_keys(event_args, "x", "y")

    if x is None or y is None:
        x, y = _extract_pair(event_args)

    if x is None or y is None:
        native_window = _select_native_window(event_args)
        if native_window is not None:
            x = _read_int_attribute(native_window, _X_ATTRIBUTE_NAMES)
            y = _read_int_attribute(native_window, _Y_ATTRIBUTE_NAMES)

    was_updated = False
    if x is not None:
        current_state.window.x = x
        was_updated = True
    if y is not None:
        current_state.window.y = y
        was_updated = True

    if was_updated:
        logger.debug(
            "Native window position updated: x=%s, y=%s.",
            current_state.window.x,
            current_state.window.y,
        )
    else:
        logger.debug("Native window position was not updated from event payload.")

    return was_updated


def update_native_window_state(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Update AppState from the current native window when possible.

    Args:
        event_args: Native lifecycle event arguments received from NiceGUI.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when at least one geometry field was updated.
    """
    current_state = state if state is not None else get_app_state()
    native_window = _select_native_window(event_args)

    if native_window is None:
        logger.debug("Native window state was not updated; no window object found.")
        return False

    position_updated = update_native_window_position(native_window, state=current_state)
    size_updated = update_native_window_size(native_window, state=current_state)
    return position_updated or size_updated


async def refresh_native_window_state_from_proxy(
    *,
    state: AppState | None = None,
) -> bool:
    """Refresh AppState from the NiceGUI native main window proxy.

    NiceGUI forwards ``moved`` events with x/y and ``resized`` events with
    width/height, but a resize from the left or top border can also change the
    window position. The main window proxy exposes asynchronous
    ``get_position`` and ``get_size`` calls, so event handlers can use this
    helper after move and resize events to persist the complete geometry.

    Args:
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when at least one geometry field was updated.
    """
    current_state = state if state is not None else get_app_state()
    native_window = getattr(app.native, "main_window", None)

    if native_window is None:
        logger.debug("Native window proxy state was not refreshed; no window found.")
        return False

    position = await _request_native_window_pair(native_window, "get_position")
    size = await _request_native_window_pair(native_window, "get_size")

    was_updated = False
    if position is not None:
        x, y = position
        was_updated = _assign_if_different(current_state.window, "x", x) or was_updated
        was_updated = _assign_if_different(current_state.window, "y", y) or was_updated

    if size is not None:
        width, height = size
        if width >= _MIN_WINDOW_WIDTH:
            was_updated = (
                _assign_if_different(current_state.window, "width", width)
                or was_updated
            )
        if height >= _MIN_WINDOW_HEIGHT:
            was_updated = (
                _assign_if_different(current_state.window, "height", height)
                or was_updated
            )

    if was_updated:
        logger.debug(
            "Native window state refreshed from proxy: "
            "x=%s, y=%s, width=%s, height=%s.",
            current_state.window.x,
            current_state.window.y,
            current_state.window.width,
            current_state.window.height,
        )
    else:
        logger.debug("Native window proxy refresh did not change geometry.")

    return was_updated


def persist_native_window_state_on_exit(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Persist native window geometry during application exit.

    Args:
        event_args: Native lifecycle event arguments received from NiceGUI.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when the settings file was saved successfully or persistence is
        disabled; False when saving was attempted and failed.
    """
    current_state = state if state is not None else get_app_state()

    if not current_state.window.persist_state:
        logger.info("Native window state persistence is disabled by settings.")
        return True

    update_native_window_state(*event_args, state=current_state)
    return _save_native_window_group(current_state)


def _save_native_window_group(state: AppState) -> bool:
    """Persist the current native window group to settings.toml.

    Args:
        state: Application state whose window group should be saved.

    Returns:
        True when the settings file was saved successfully.
    """
    state.window.last_saved_at = datetime.now()
    saved = save_settings_group("window", state=state)
    if saved:
        logger.info("Native window state persisted successfully.")
        return True

    logger.warning("Native window state could not be persisted.")
    return False


def _reset_window_geometry_to_defaults(window_state: WindowState) -> bool:
    """Reset persisted geometry fields to WindowState defaults.

    Args:
        window_state: Mutable window state to reset.

    Returns:
        True when at least one value was changed.
    """
    defaults = WindowState()
    changed = False
    reset_field_names = (
        "x",
        "y",
        "width",
        "height",
        "maximized",
        "fullscreen",
        "monitor",
    )

    for field_name in reset_field_names:
        changed = (
            _assign_if_different(
                window_state,
                field_name,
                getattr(defaults, field_name),
            )
            or changed
        )

    return changed


def _assign_if_different(target: object, attribute_name: str, value: object) -> bool:
    """Assign an attribute only when its value changes.

    Args:
        target: Mutable object that owns the attribute.
        attribute_name: Name of the attribute to update.
        value: New value to assign.

    Returns:
        True when assignment changed the previous value.
    """
    if getattr(target, attribute_name) == value:
        return False

    setattr(target, attribute_name, value)
    return True


def _save_normalized_window_group(state: AppState) -> bool:
    """Save normalized window settings after startup validation.

    Args:
        state: Application state whose window group should be saved.

    Returns:
        True when the settings file was saved successfully.
    """
    state.window.last_saved_at = datetime.now()
    saved = save_settings_group("window", state=state)
    if saved:
        logger.info("Normalized native window settings saved successfully.")
        return True

    logger.warning("Normalized native window settings could not be saved.")
    return False


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
        available_size * _MAX_START_POSITION_RATIO
    )
    minimum_visible_edge = available_start + round(
        available_size * _MIN_VISIBLE_EDGE_RATIO
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


async def _request_native_window_pair(
    native_window: object,
    method_name: str,
) -> tuple[int, int] | None:
    """Request an integer pair from a NiceGUI native window proxy.

    Args:
        native_window: NiceGUI native main window proxy.
        method_name: Async method name to call on the proxy.

    Returns:
        A pair of integers when the proxy returns valid geometry, otherwise
        None.
    """
    method = getattr(native_window, method_name, None)
    if not callable(method):
        logger.debug("Native window proxy does not expose %s.", method_name)
        return None

    try:
        request_pair = cast(Callable[[], object], method)
        raw_pair = request_pair()
        if inspect.isawaitable(raw_pair):
            raw_pair = await raw_pair
    except Exception:
        logger.debug("Native window proxy %s call failed.", method_name, exc_info=True)
        return None

    return _coerce_pair(raw_pair)


def _get_native_window_args() -> dict[str, Any]:
    """Return the mutable native window arguments dictionary.

    Returns:
        The dictionary used by NiceGUI to pass extra arguments to pywebview.
    """
    window_args = getattr(app.native, "window_args", None)
    if isinstance(window_args, dict):
        return window_args

    window_args = {}
    app.native.window_args = window_args
    return window_args


def _select_native_window(event_args: Iterable[object]) -> object | None:
    """Return the best available native window object.

    Args:
        event_args: Event arguments that may include a native window object.

    Returns:
        Native window object when one can be found.
    """
    for event_arg in event_args:
        if _looks_like_window(event_arg):
            return event_arg

    main_window = getattr(app.native, "main_window", None)
    if _looks_like_window(main_window):
        return main_window

    return None


def _looks_like_window(value: object | None) -> bool:
    """Return whether a value exposes geometry attributes or methods.

    Args:
        value: Candidate object.

    Returns:
        True when the value looks like a native window object.
    """
    if value is None:
        return False

    attribute_names = (
        *_X_ATTRIBUTE_NAMES,
        *_Y_ATTRIBUTE_NAMES,
        *_WIDTH_ATTRIBUTE_NAMES,
        *_HEIGHT_ATTRIBUTE_NAMES,
    )
    return any(hasattr(value, name) for name in attribute_names) or any(
        callable(getattr(value, method_name, None))
        for method_name in ("move", "resize")
    )


def _extract_pair_by_keys(
    event_args: Iterable[object],
    first_key: str,
    second_key: str,
) -> tuple[int | None, int | None]:
    """Extract an integer pair from NativeEventArguments-like payloads.

    Args:
        event_args: Event arguments received from NiceGUI.
        first_key: First dictionary key to read.
        second_key: Second dictionary key to read.

    Returns:
        A pair of integers when both values are available, otherwise
        ``None`` values.
    """
    for event_arg in event_args:
        args = getattr(event_arg, "args", None)
        if not isinstance(args, dict):
            continue

        first_value = _coerce_optional_int(args.get(first_key))
        second_value = _coerce_optional_int(args.get(second_key))
        if first_value is not None and second_value is not None:
            return first_value, second_value

    return None, None


def _coerce_optional_int(value: object) -> int | None:
    """Convert a value to int when it represents a valid geometry number.

    Args:
        value: Candidate geometry value.

    Returns:
        Integer value when conversion succeeds, otherwise None.
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        stripped_value = value.strip()
        if not stripped_value:
            return None

        try:
            return int(stripped_value)
        except ValueError:
            return None

    return None


def _extract_pair(event_args: Iterable[object]) -> tuple[int | None, int | None]:
    """Extract the first integer pair from event arguments.

    Args:
        event_args: Event arguments received from pywebview through NiceGUI.

    Returns:
        A pair of integers when available, otherwise ``None`` values.
    """
    direct_pair = _coerce_pair(event_args)
    if direct_pair is not None:
        return direct_pair

    for event_arg in event_args:
        args_pair = _coerce_pair(getattr(event_arg, "args", None))
        if args_pair is not None:
            return args_pair

    return None, None


def _coerce_pair(value: object) -> tuple[int, int] | None:
    """Convert a two-item iterable to an integer pair when possible.

    Args:
        value: Candidate pair value.

    Returns:
        Integer pair when both values are valid geometry numbers, otherwise
        None.
    """
    if isinstance(value, dict | str | bytes) or not isinstance(value, Iterable):
        return None

    values: list[int] = []
    for item in value:
        coerced_value = _coerce_optional_int(item)
        if coerced_value is None:
            return None
        values.append(coerced_value)
        if len(values) > 2:
            return None

    if len(values) != 2:
        return None

    return values[0], values[1]


def _read_int_attribute(value: object, attribute_names: Iterable[str]) -> int | None:
    """Read the first integer-like attribute from an object.

    Args:
        value: Source object.
        attribute_names: Candidate attribute names.

    Returns:
        Integer value when an attribute exists and can be converted, otherwise
        None.
    """
    for attribute_name in attribute_names:
        raw_value = getattr(value, attribute_name, None)
        coerced_value = _coerce_optional_int(raw_value)
        if coerced_value is not None:
            return coerced_value

        if raw_value is not None:
            logger.debug(
                "Ignored non-integer native window attribute: %s=%r.",
                attribute_name,
                raw_value,
            )

    return None


def _coerce_window_width(value: int) -> int:
    """Return a safe persisted window width.

    Args:
        value: Candidate width.

    Returns:
        Width clamped to the minimum accepted value.
    """
    return max(int(value), _MIN_WINDOW_WIDTH)


def _coerce_window_height(value: int) -> int:
    """Return a safe persisted window height.

    Args:
        value: Candidate height.

    Returns:
        Height clamped to the minimum accepted value.
    """
    return max(int(value), _MIN_WINDOW_HEIGHT)
