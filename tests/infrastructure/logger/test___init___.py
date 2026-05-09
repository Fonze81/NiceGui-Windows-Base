"""Test the public API exported by the logger package."""

from desktop_app.infrastructure import logger as logger_api
from desktop_app.infrastructure.logger.bootstrapper import LoggerBootstrapper
from desktop_app.infrastructure.logger.config import LoggerConfig
from desktop_app.infrastructure.logger.exceptions import LoggerValidationError
from desktop_app.infrastructure.logger.paths import resolve_log_file_path
from desktop_app.infrastructure.logger.service import (
    logger_bootstrap,
    logger_create_bootstrapper,
    logger_enable_file_logging,
    logger_get_bootstrapper,
    logger_get_logger,
    logger_shutdown,
    logger_update_config,
)

# Keep this tuple aligned with the package __all__ contract.
EXPECTED_PUBLIC_API: tuple[str, ...] = (
    "LoggerBootstrapper",
    "LoggerConfig",
    "LoggerValidationError",
    "logger_bootstrap",
    "logger_create_bootstrapper",
    "logger_enable_file_logging",
    "logger_get_bootstrapper",
    "logger_get_logger",
    "resolve_log_file_path",
    "logger_shutdown",
    "logger_update_config",
)


# Public API contract tests.
def test_logger_package_exports_expected_public_api() -> None:
    """Verify that the logger package exports expected public API."""
    assert logger_api.__all__ == EXPECTED_PUBLIC_API


def test_logger_package_public_api_is_immutable_tuple() -> None:
    """Verify that the logger package public API is immutable tuple."""
    assert isinstance(logger_api.__all__, tuple)


def test_logger_package_exports_all_declared_symbols() -> None:
    """Verify that the logger package exports all declared symbols."""
    for symbol_name in logger_api.__all__:
        assert hasattr(logger_api, symbol_name)


def test_logger_package_reexports_expected_objects() -> None:
    """Verify that the logger package reexports expected objects."""
    assert logger_api.LoggerBootstrapper is LoggerBootstrapper
    assert logger_api.LoggerConfig is LoggerConfig
    assert logger_api.LoggerValidationError is LoggerValidationError
    assert logger_api.logger_bootstrap is logger_bootstrap
    assert logger_api.logger_create_bootstrapper is logger_create_bootstrapper
    assert logger_api.logger_enable_file_logging is logger_enable_file_logging
    assert logger_api.logger_get_bootstrapper is logger_get_bootstrapper
    assert logger_api.logger_get_logger is logger_get_logger
    assert logger_api.resolve_log_file_path is resolve_log_file_path
    assert logger_api.logger_shutdown is logger_shutdown
    assert logger_api.logger_update_config is logger_update_config
