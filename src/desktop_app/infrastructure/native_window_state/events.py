# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/events.py
# Purpose:
# Read native window event payloads and update AppState window fields.
# Behavior:
# Accepts NiceGUI NativeEventArguments, direct coordinate pairs, and window-like
# objects so lifecycle handlers remain resilient to pywebview payload changes.
# Notes:
# Event helpers only update in-memory state. Persistence is handled separately
# by persistence.py during shutdown or normalized startup recovery.
# -----------------------------------------------------------------------------

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable
from logging import Logger
from typing import Final, cast

from desktop_app.core.state import AppState, get_app_state
from desktop_app.infrastructure.logger import logger_get_logger
from desktop_app.infrastructure.native_window_state.assignment import (
    _assign_if_different,
)
from desktop_app.infrastructure.native_window_state.bridge import app
from desktop_app.infrastructure.native_window_state.defaults import (
    HEIGHT_ATTRIBUTE_NAMES,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    WIDTH_ATTRIBUTE_NAMES,
    X_ATTRIBUTE_NAMES,
    Y_ATTRIBUTE_NAMES,
)

logger: Final[Logger] = logger_get_logger(__name__)


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
            width = _read_int_attribute(native_window, WIDTH_ATTRIBUTE_NAMES)
            height = _read_int_attribute(native_window, HEIGHT_ATTRIBUTE_NAMES)

    was_updated = False
    if width is not None and width >= MIN_WINDOW_WIDTH:
        was_updated = (
            _assign_if_different(current_state.window, "width", width) or was_updated
        )
    if height is not None and height >= MIN_WINDOW_HEIGHT:
        was_updated = (
            _assign_if_different(current_state.window, "height", height) or was_updated
        )

    if was_updated:
        logger.debug(
            "Native window size updated from event payload: width=%s, height=%s.",
            current_state.window.width,
            current_state.window.height,
        )

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
            x = _read_int_attribute(native_window, X_ATTRIBUTE_NAMES)
            y = _read_int_attribute(native_window, Y_ATTRIBUTE_NAMES)

    was_updated = False
    if x is not None:
        was_updated = _assign_if_different(current_state.window, "x", x) or was_updated
    if y is not None:
        was_updated = _assign_if_different(current_state.window, "y", y) or was_updated

    if was_updated:
        logger.debug(
            "Native window position updated from event payload: x=%s, y=%s.",
            current_state.window.x,
            current_state.window.y,
        )

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
        if width >= MIN_WINDOW_WIDTH:
            was_updated = (
                _assign_if_different(current_state.window, "width", width)
                or was_updated
            )
        if height >= MIN_WINDOW_HEIGHT:
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

    return was_updated


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
        *X_ATTRIBUTE_NAMES,
        *Y_ATTRIBUTE_NAMES,
        *WIDTH_ATTRIBUTE_NAMES,
        *HEIGHT_ATTRIBUTE_NAMES,
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
