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

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_SIZE_UNITS_TO_BYTES = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 * 1024,
    "GB": 1024 * 1024 * 1024,
}

_SIZE_PATTERN = re.compile(r"^\s*(\d+)\s*([KMG]?B)\s*$", re.IGNORECASE)


def deep_get(mapping: Mapping[str, Any], path: str, default: Any) -> Any:
    """Return a mapping value selected by a dotted path.

    Args:
        mapping: Source mapping.
        path: Dotted path such as "app.window.width".
        default: Value returned when any path segment is missing.

    Returns:
        Found value or the provided default.
    """
    cursor: Any = mapping

    for part in path.split("."):
        if not isinstance(cursor, Mapping) or part not in cursor:
            return default

        cursor = cursor[part]

    return cursor


def to_bool(value: Any, default: bool) -> bool:
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
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "y", "sim", "s"}:
            return True

        if normalized in {"false", "0", "no", "n", "nao", "não"}:
            return False

    return default


def to_int(value: Any, default: int) -> int:
    """Convert an external value to int.

    Args:
        value: Raw TOML value.
        default: Fallback used when conversion fails.

    Returns:
        Converted integer or fallback.
    """
    if isinstance(value, bool):
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value: Any, default: float) -> float:
    """Convert an external value to float.

    Args:
        value: Raw TOML value.
        default: Fallback used when conversion fails.

    Returns:
        Converted float or fallback.
    """
    if isinstance(value, bool):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_path(value: Any, default: Path) -> Path:
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


def parse_size_to_bytes(value: int | str) -> int | None:
    """Convert a byte size value to an integer number of bytes.

    Args:
        value: Size as integer bytes or text such as "5 MB".

    Returns:
        Integer size in bytes, or None when conversion is unsafe.
    """
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value > 0 else None

    if isinstance(value, str):
        match = _SIZE_PATTERN.match(value)
        if match is None:
            return None

        numeric_value = int(match.group(1))
        unit = match.group(2).upper()
        size_in_bytes = numeric_value * _SIZE_UNITS_TO_BYTES[unit]
        return size_in_bytes if size_in_bytes > 0 else None

    return None
