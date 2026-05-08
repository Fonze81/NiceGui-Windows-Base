# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/byte_size.py
# Purpose:
# Parse human-readable byte-size values used by infrastructure configuration.
# Behavior:
# Converts integer byte counts and strings such as "5 MB" or "512KB" into a
# positive integer number of bytes.
# Notes:
# Keep this module independent from logger-specific exceptions so logger and
# settings code can reuse the same parser with their own error handling policy.
# -----------------------------------------------------------------------------

from __future__ import annotations

import re

_SIZE_UNITS_TO_BYTES = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 * 1024,
    "GB": 1024 * 1024 * 1024,
}

_SIZE_PATTERN = re.compile(r"^\s*(\d+)\s*([KMG]?B)\s*$", re.IGNORECASE)


def parse_byte_size(value: int | str) -> int:
    """Convert a byte-size value to an integer number of bytes.

    Args:
        value: Size as integer bytes or text such as "5 MB".

    Returns:
        Positive integer number of bytes.

    Raises:
        TypeError: If the value type is not supported.
        ValueError: If the value format is invalid or not positive.
    """
    if isinstance(value, bool):
        raise TypeError("Byte size must be an int or a string, not bool.")

    if isinstance(value, int):
        if value < 1:
            raise ValueError("Byte size must be greater than zero.")
        return value

    if isinstance(value, str):
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Byte size string must not be empty.")

        match = _SIZE_PATTERN.match(normalized_value)
        if match is None:
            raise ValueError(
                "Byte size string must use a valid format such as "
                "'5 MB', '512KB' or '1 GB'."
            )

        numeric_value = int(match.group(1))
        unit = match.group(2).upper()
        size_in_bytes = numeric_value * _SIZE_UNITS_TO_BYTES[unit]

        if size_in_bytes < 1:
            raise ValueError("Byte size must be greater than zero.")

        return size_in_bytes

    raise TypeError("Byte size must be an int or a string.")
