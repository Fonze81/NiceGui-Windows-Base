"""Test logger-local byte-size parsing."""

from typing import Any, cast

import pytest

from desktop_app.infrastructure.logger.byte_size import parse_byte_size


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, 1),
        (1024, 1024),
        ("1 B", 1),
        ("1B", 1),
        ("512 KB", 512 * 1024),
        ("512KB", 512 * 1024),
        ("5 MB", 5 * 1024 * 1024),
        ("5MB", 5 * 1024 * 1024),
        ("1 GB", 1024 * 1024 * 1024),
        ("1GB", 1024 * 1024 * 1024),
        ("  2 mb  ", 2 * 1024 * 1024),
        ("3 kB", 3 * 1024),
    ],
)
def test_parse_byte_size_returns_expected_bytes(
    value: int | str,
    expected: int,
) -> None:
    """Return byte counts for valid integer and string values."""
    assert parse_byte_size(value) == expected


@pytest.mark.parametrize("value", [0, -1, -1024])
def test_parse_byte_size_rejects_non_positive_integer(value: int) -> None:
    """Reject integer byte counts lower than one."""
    with pytest.raises(ValueError, match="greater than zero"):
        parse_byte_size(value)


@pytest.mark.parametrize("value", [True, False])
def test_parse_byte_size_rejects_bool(value: bool) -> None:
    """Reject bool values even though bool is a subclass of int."""
    with pytest.raises(TypeError, match="not bool"):
        parse_byte_size(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_parse_byte_size_rejects_empty_string(value: str) -> None:
    """Reject empty or whitespace-only strings."""
    with pytest.raises(ValueError, match="must not be empty"):
        parse_byte_size(value)


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "KB",
        "1 TB",
        "1.5 MB",
        "-1 MB",
        "1 bytes",
        "MB 1",
        "one MB",
        "1 M",
    ],
)
def test_parse_byte_size_rejects_invalid_string_format(value: str) -> None:
    """Reject strings that do not match the supported byte-size format."""
    with pytest.raises(ValueError, match="must use a valid format"):
        parse_byte_size(value)


def test_parse_byte_size_rejects_zero_string_value() -> None:
    """Reject string values that resolve to zero bytes."""
    with pytest.raises(ValueError, match="greater than zero"):
        parse_byte_size("0 B")


@pytest.mark.parametrize("value", [None, 1.5, object(), [], {}])
def test_parse_byte_size_rejects_unsupported_types(value: object) -> None:
    """Reject values that are neither int nor str."""
    with pytest.raises(TypeError, match="must be an int or a string"):
        parse_byte_size(cast(Any, value))
