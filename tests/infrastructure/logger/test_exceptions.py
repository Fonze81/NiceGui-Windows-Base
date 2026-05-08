import pytest

from desktop_app.infrastructure.logger.exceptions import LoggerValidationError


def test_logger_validation_error_inherits_from_value_error() -> None:
    assert issubclass(LoggerValidationError, ValueError)


def test_logger_validation_error_preserves_message() -> None:
    error = LoggerValidationError("Invalid logger level.")

    assert str(error) == "Invalid logger level."


def test_logger_validation_error_can_be_caught_as_specific_exception() -> None:
    with pytest.raises(LoggerValidationError, match="Invalid logger level"):
        raise LoggerValidationError("Invalid logger level.")


def test_logger_validation_error_can_be_caught_as_value_error() -> None:
    with pytest.raises(ValueError, match="Invalid logger level"):
        raise LoggerValidationError("Invalid logger level.")


def test_logger_validation_error_is_public_module_symbol() -> None:
    from desktop_app.infrastructure.logger import exceptions

    assert exceptions.__all__ == ("LoggerValidationError",)
