"""Test logger exception contracts."""

import pytest

from desktop_app.infrastructure.logger.exceptions import LoggerValidationError


# Exception contract tests.
def test_logger_validation_error_inherits_from_value_error() -> None:
    """Verify that LoggerValidationError inherits from value error."""
    assert issubclass(LoggerValidationError, ValueError)


def test_logger_validation_error_preserves_message() -> None:
    """Verify that LoggerValidationError preserves message."""
    error = LoggerValidationError("Invalid logger level.")

    assert str(error) == "Invalid logger level."


def test_logger_validation_error_can_be_caught_as_specific_exception() -> None:
    """Verify that LoggerValidationError can be caught as specific exception."""
    with pytest.raises(LoggerValidationError, match="Invalid logger level"):
        raise LoggerValidationError("Invalid logger level.")


def test_logger_validation_error_can_be_caught_as_value_error() -> None:
    """Verify that LoggerValidationError can be caught as value error."""
    with pytest.raises(ValueError, match="Invalid logger level"):
        raise LoggerValidationError("Invalid logger level.")


def test_logger_validation_error_is_public_module_symbol() -> None:
    """Verify that LoggerValidationError is public module symbol."""
    from desktop_app.infrastructure.logger import exceptions

    assert exceptions.__all__ == ("LoggerValidationError",)
