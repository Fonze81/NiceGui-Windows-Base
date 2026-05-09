"""Tests for defensive settings conversion helpers."""

from pathlib import Path

import pytest

from desktop_app.infrastructure.settings.conversion import (
    get_nested_value,
    to_bool,
    to_float,
    to_int,
    to_path,
    try_parse_byte_size,
)


class UnsupportedValue:
    """Represent a value unsupported by the conversion helpers."""


NestedSettings = dict[str, object]


def test_get_nested_value_returns_value_from_dotted_path() -> None:
    """Return the value when all dotted path segments exist."""
    settings: NestedSettings = {"app": {"window": {"width": 1024}}}

    result = get_nested_value(settings, "app.window.width", default=800)

    assert result == 1024


def test_get_nested_value_returns_default_when_path_segment_is_missing() -> None:
    """Return the fallback when a mapping does not contain a path segment."""
    settings: NestedSettings = {"app": {"window": {}}}

    result = get_nested_value(settings, "app.window.width", default=800)

    assert result == 800


def test_get_nested_value_returns_default_for_non_mapping_intermediate() -> None:
    """Return the fallback when traversal reaches a non-mapping value."""
    settings: NestedSettings = {"app": {"window": 1024}}

    result = get_nested_value(settings, "app.window.width", default=800)

    assert result == 800


@pytest.mark.parametrize("value", [True, "true", "1", "yes", "y", "sim", "s"])
def test_to_bool_returns_true_for_supported_true_values(value: object) -> None:
    """Convert native and text true values to True."""
    assert to_bool(value, default=False) is True


@pytest.mark.parametrize("value", [False, "false", "0", "no", "n", "nao", "não"])
def test_to_bool_returns_false_for_supported_false_values(value: object) -> None:
    """Convert native and text false values to False."""
    assert to_bool(value, default=True) is False


def test_to_bool_ignores_surrounding_spaces_and_case() -> None:
    """Normalize text before checking accepted boolean values."""
    assert to_bool(" YES ", default=False) is True
    assert to_bool(" No ", default=True) is False


@pytest.mark.parametrize("value", ["", "maybe", 1, None])
def test_to_bool_returns_default_for_unsupported_values(value: object) -> None:
    """Return the fallback when boolean conversion is unsafe."""
    assert to_bool(value, default=True) is True


@pytest.mark.parametrize("value", [42, "42", 42.9])
def test_to_int_returns_converted_integer(value: object) -> None:
    """Convert supported integer-like values."""
    assert to_int(value, default=0) == 42


def test_to_int_returns_default_for_bool() -> None:
    """Avoid treating bool as an integer because bool is a subclass of int."""
    assert to_int(True, default=7) == 7


@pytest.mark.parametrize("value", ["invalid", float("inf"), UnsupportedValue()])
def test_to_int_returns_default_when_conversion_is_unsafe(value: object) -> None:
    """Return the fallback when integer conversion is unsafe."""
    assert to_int(value, default=7) == 7


@pytest.mark.parametrize(("value", "expected"), [(1.5, 1.5), ("1.5", 1.5), (1, 1.0)])
def test_to_float_returns_converted_float(value: object, expected: float) -> None:
    """Convert supported float-like values."""
    assert to_float(value, default=0.0) == expected


def test_to_float_returns_default_for_bool() -> None:
    """Avoid treating bool as a numeric float value."""
    assert to_float(False, default=1.25) == 1.25


@pytest.mark.parametrize("value", ["invalid", UnsupportedValue()])
def test_to_float_returns_default_when_conversion_is_unsafe(value: object) -> None:
    """Return the fallback when float conversion is unsafe."""
    assert to_float(value, default=1.25) == 1.25


def test_to_path_returns_existing_path_instance() -> None:
    """Return Path instances without rebuilding them."""
    default_path = Path("default.log")
    source_path = Path("custom.log")

    result = to_path(source_path, default=default_path)

    assert result is source_path


def test_to_path_returns_stripped_string_path() -> None:
    """Convert non-empty strings to Path after trimming spaces."""
    assert to_path(" logs/app.log ", default=Path("default.log")) == Path(
        "logs/app.log"
    )


@pytest.mark.parametrize("value", ["", "   ", None, 10])
def test_to_path_returns_default_for_empty_or_unsupported_values(value: object) -> None:
    """Return the fallback for empty strings and unsupported path values."""
    default_path = Path("default.log")

    assert to_path(value, default=default_path) == default_path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (512, 512),
        ("512 B", 512),
        ("2 KB", 2048),
        ("3 MB", 3 * 1024 * 1024),
    ],
)
def test_try_parse_byte_size_returns_bytes_for_valid_values(
    value: object,
    expected: int,
) -> None:
    """Return the parsed byte count for supported byte-size values."""
    assert try_parse_byte_size(value) == expected


@pytest.mark.parametrize("value", ["invalid", 0, True, UnsupportedValue()])
def test_try_parse_byte_size_returns_none_for_invalid_values(value: object) -> None:
    """Return None instead of raising for invalid byte-size values."""
    assert try_parse_byte_size(value) is None
