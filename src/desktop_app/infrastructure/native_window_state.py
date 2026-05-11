# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state.py
# Purpose:
# Capture, restore, and persist native desktop window geometry.
# Behavior:
# Applies persisted geometry before NiceGUI starts when possible, reapplies it
# after the native window is shown, updates AppState from native resize and move
# event payloads, and saves the window settings group during application exit.
# Notes:
# NiceGUI delegates native windows to pywebview and forwards native events as
# NativeEventArguments objects. Some backends ignore initial x/y values passed
# through creation arguments, so this module also performs explicit move and
# resize calls after the native window is available. Native event dictionaries
# are preferred over window attributes because they carry the real width, height,
# x, and y values reported by pywebview.
# -----------------------------------------------------------------------------

from __future__ import annotations

import ctypes
from collections.abc import Iterable
from dataclasses import dataclass, fields
from datetime import datetime
from logging import Logger
from typing import Any, Final

from nicegui import app

from desktop_app.core.state import AppState, WindowState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.settings import save_settings_group

logger: Final[Logger] = logger_get_logger(__name__)

_MIN_WINDOW_WIDTH: Final[int] = 400
_MIN_WINDOW_HEIGHT: Final[int] = 300
_SCREEN_LOWER_VISIBLE_RATIO: Final[float] = 0.10
_SCREEN_UPPER_POSITION_RATIO: Final[float] = 0.90

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

    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)

    window_args = _get_native_window_args()
    window_args["width"] = width
    window_args["height"] = height
    if current_state.window.persist_state:
        window_args["x"] = current_state.window.x
        window_args["y"] = current_state.window.y
    else:
        window_args.pop("x", None)
        window_args.pop("y", None)

    logger.debug(
        "Native window arguments applied from state: size=(%s, %s), "
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
    changes, or reorders monitors. This function keeps at least part of the
    window in the available screen area before any native position is applied.
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

    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)
    changed = _assign_if_different(current_state.window, "width", width)
    changed = _assign_if_different(current_state.window, "height", height) or changed

    safe_x, safe_y = _clamp_window_position_to_visible_area(
        current_state.window.x,
        current_state.window.y,
        width,
        height,
    )
    changed = _assign_if_different(current_state.window, "x", safe_x) or changed
    changed = _assign_if_different(current_state.window, "y", safe_y) or changed

    if changed:
        _save_normalized_window_group(current_state)

    return changed


def apply_initial_native_window_options(
    ui_run_options: dict[str, Any],
    *,
    state: AppState | None = None,
) -> None:
    """Apply initial native window options before ``ui.run`` starts.

    NiceGUI accepts the initial size and fullscreen state through ``ui.run``.
    Native pywebview creation arguments are also populated as a best effort,
    but some Windows backends may ignore initial x/y values. For that reason,
    ``restore_native_window_state_after_show`` must still run when the native
    window emits the ``shown`` event.

    Args:
        ui_run_options: Mutable options dictionary passed to ``ui.run``.
        state: Optional application state. Uses the global state when omitted.
    """
    current_state = state if state is not None else get_app_state()
    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)

    ui_run_options["window_size"] = (width, height)
    ui_run_options["fullscreen"] = current_state.window.fullscreen

    apply_native_window_args_from_state(state=current_state)
    window_args = _get_native_window_args()

    logger.debug(
        "Native window options prepared: size=(%s, %s), position=(%s, %s), "
        "fullscreen=%s, persist_state=%s.",
        width,
        height,
        window_args.get("x"),
        window_args.get("y"),
        current_state.window.fullscreen,
        current_state.window.persist_state,
    )


def restore_native_window_state_after_show(
    *event_args: object,
    state: AppState | None = None,
) -> bool:
    """Restore persisted geometry after the native window is available.

    Args:
        event_args: Native lifecycle event arguments received from NiceGUI.
        state: Optional application state. Uses the global state when omitted.

    Returns:
        True when at least one native move or resize operation was requested.
    """
    current_state = state if state is not None else get_app_state()

    if not current_state.window.persist_state:
        logger.debug("Native window geometry restore skipped by settings.")
        return False

    native_window = _select_native_window(event_args)
    if native_window is None:
        logger.debug("Native window geometry restore skipped; no window available.")
        return False

    width = _coerce_window_width(current_state.window.width)
    height = _coerce_window_height(current_state.window.height)
    moved = _call_window_method(
        native_window,
        "move",
        current_state.window.x,
        current_state.window.y,
    )
    resized = _call_window_method(native_window, "resize", width, height)

    if moved or resized:
        logger.debug(
            "Native window geometry restored after show: x=%s, y=%s, "
            "width=%s, height=%s.",
            current_state.window.x,
            current_state.window.y,
            width,
            height,
        )

    return moved or resized


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
    current_state.window.last_saved_at = datetime.now()

    saved = save_settings_group("window", state=current_state)
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

    available_field_names = {field.name for field in fields(WindowState)}
    for field_name in reset_field_names:
        if field_name not in available_field_names:
            continue
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


def _clamp_window_position_to_visible_area(
    x: int,
    y: int,
    width: int,
    height: int,
) -> tuple[int, int]:
    """Clamp a window position so it remains reachable on current monitors.

    Args:
        x: Persisted horizontal window position in virtual-screen coordinates.
        y: Persisted vertical window position in virtual-screen coordinates.
        width: Persisted window width.
        height: Persisted window height.

    Returns:
        Safe ``x`` and ``y`` values. When Windows monitor detection fails, the
        original coordinates are returned unchanged.
    """
    work_areas = _get_windows_monitor_work_areas()
    if not work_areas:
        logger.debug(
            "Native window position was not clamped; no monitor work area found."
        )
        return x, y

    work_area = _select_relevant_work_area(
        x=x,
        y=y,
        width=width,
        height=height,
        work_areas=work_areas,
    )
    safe_x = _clamp_axis_position(
        position=x,
        size=width,
        available_start=work_area.left,
        available_size=work_area.width,
    )
    safe_y = _clamp_axis_position(
        position=y,
        size=height,
        available_start=work_area.top,
        available_size=work_area.height,
    )

    if safe_x != x or safe_y != y:
        logger.info(
            "Persisted native window position adjusted to visible monitor area: "
            "original=(%s, %s), adjusted=(%s, %s), "
            "work_area=(%s, %s, %s, %s).",
            x,
            y,
            safe_x,
            safe_y,
            work_area.left,
            work_area.top,
            work_area.right,
            work_area.bottom,
        )

    return safe_x, safe_y


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
    """Clamp one persisted window axis using monitor-aware guard rails.

    Args:
        position: Persisted coordinate for one axis.
        size: Window size on the same axis.
        available_start: Start coordinate of the monitor work area on the axis.
        available_size: Available monitor work-area size on the same axis.

    Returns:
        Coordinate clamped to the allowed visible range.
    """
    lower_limit = available_start + round(available_size * _SCREEN_LOWER_VISIBLE_RATIO)
    upper_limit = available_start + round(available_size * _SCREEN_UPPER_POSITION_RATIO)

    if position > upper_limit:
        return upper_limit

    if position + size < lower_limit:
        return lower_limit

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
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    class MonitorInfo(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", Rect),
            ("rcWork", Rect),
            ("dwFlags", ctypes.c_ulong),
        ]

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(Rect),
        ctypes.c_double,
    )

    def collect_monitor(
        monitor_handle: int,
        _device_context: int,
        _rect: ctypes.POINTER(Rect),
        _data: float,
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

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_pair(event_args: Iterable[object]) -> tuple[int | None, int | None]:
    """Extract the first integer pair from event arguments.

    Args:
        event_args: Event arguments received from pywebview through NiceGUI.

    Returns:
        A pair of integers when available, otherwise ``None`` values.
    """
    values: list[int] = []
    for event_arg in event_args:
        value = _coerce_optional_int(event_arg)
        if value is not None:
            values.append(value)

        if len(values) == 2:
            return values[0], values[1]

    return None, None


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
        if raw_value is None:
            continue

        try:
            return int(raw_value)
        except (TypeError, ValueError):
            logger.debug(
                "Ignored non-integer native window attribute: %s=%r.",
                attribute_name,
                raw_value,
            )

    return None


def _call_window_method(window: object, method_name: str, *args: int) -> bool:
    """Call a native window method when it exists.

    Args:
        window: Native window candidate.
        method_name: Method name to call.
        args: Integer arguments passed to the method.

    Returns:
        True when the method existed and was called successfully.
    """
    method = getattr(window, method_name, None)
    if not callable(method):
        logger.debug("Native window method is unavailable: %s.", method_name)
        return False

    try:
        method(*args)
    except Exception:
        logger.exception("Native window method failed: %s.", method_name)
        return False

    return True


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
