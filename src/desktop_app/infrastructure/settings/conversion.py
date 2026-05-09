# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/settings/conversion.py
# Purpose:
# Convert external settings values into safe application values.
# Behavior:
# Provides small conversion helpers for TOML values and dotted-path lookups in
# mapping structures. Invalid user-edited values fall back instead of stopping
# the application startup.
# Notes:
# Settings can be edited manually, so conversion functions must be defensive and
# avoid raising for normal invalid user input.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import cast

from desktop_app.infrastructure.byte_size import parse_byte_size


def get_nested_value[T](
    mapping: Mapping[str, object],
    path: str,
    default: T,
) -> object | T:
    """Return a mapping value selected by a dotted path.

    Args:
        mapping: Source mapping.
        path: Dotted path such as "app.window.width".
        default: Value returned when any path segment is missing.

    Returns:
        Found value or the provided default.
    """
    current_value: object = mapping

    for path_part in path.split("."):
        if not isinstance(current_value, Mapping):
            return default

        current_mapping = cast(Mapping[str, object], current_value)
        if path_part not in current_mapping:
            return default

        current_value = current_mapping[path_part]

    return current_value


def to_bool(value: object, default: bool) -> bool:
    """Convert an external value to bool.

    Args:
        value: Raw TOML value.
        default: Fallback used when conversion is unsafe.

    Returns:
        Converted boolean or fallback.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized_value = value.strip().lower()

        if normalized_value in {"true", "1", "yes", "y", "sim", "s"}:
            return True

        if normalized_value in {"false", "0", "no", "n", "nao", "não"}:
            return False

    return default


def to_int(value: object, default: int) -> int:
    """Convert an external value to int.

    Args:
        value: Raw TOML value.
        default: Fallback used when conversion fails.

    Returns:
        Converted integer or fallback.
    """
    if isinstance(value, bool):
        return default

    if not isinstance(value, int | float | str):
        return default

    try:
        return int(value)
    except (OverflowError, ValueError):
        return default


def to_float(value: object, default: float) -> float:
    """Convert an external value to float.

    Args:
        value: Raw TOML value.
        default: Fallback used when conversion fails.

    Returns:
        Converted float or fallback.
    """
    if isinstance(value, bool):
        return default

    if not isinstance(value, int | float | str):
        return default

    try:
        return float(value)
    except ValueError:
        return default


def to_path(value: object, default: Path) -> Path:
    """Convert an external value to Path.

    Args:
        value: Raw TOML value.
        default: Fallback used when the value is empty or unsupported.

    Returns:
        Converted path or fallback.
    """
    if isinstance(value, Path):
        return value

    if isinstance(value, str) and value.strip():
        return Path(value.strip())

    return default


def try_parse_byte_size(value: object) -> int | None:
    """Convert a byte-size value without raising for invalid settings.

    Args:
        value: Size as integer bytes or text such as "5 MB".

    Returns:
        Integer size in bytes, or None when conversion is unsafe.
    """
    if not isinstance(value, int | str):
        return None

    try:
        return parse_byte_size(value)
    except (TypeError, ValueError):
        return None
