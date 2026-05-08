from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar, cast

import pytest

from desktop_app.infrastructure.logger import service
from desktop_app.infrastructure.logger.config import LoggerConfig


class FakeBootstrapper:
    """Test double for LoggerBootstrapper.

    The fake records calls made by the service module without creating real
    handlers, files, or logger infrastructure side effects.
    """

    instances: ClassVar[list[FakeBootstrapper]] = []

    def __init__(self, config: LoggerConfig) -> None:
        self.config = config
        self.root_logger = logging.getLogger("desktop_app")
        self.is_bootstrapped = False
        self.bootstrap_call_count = 0
        self.shutdown_call_count = 0
        self.enable_file_logging_result = True
        self.updated_configs: list[LoggerConfig] = []
        self.file_logging_paths: list[Path | str | None] = []
        self.__class__.instances.append(self)

    def bootstrap(self) -> logging.Logger:
        """Record bootstrap execution and return the fake root logger.

        Returns:
            Fake root logger used by the tests.
        """
        self.is_bootstrapped = True
        self.bootstrap_call_count += 1
        return self.root_logger

    def update_config(self, config: LoggerConfig) -> None:
        """Record a configuration update.

        Args:
            config: New logger configuration requested by the service.
        """
        self.config = config
        self.updated_configs.append(config)

    def enable_file_logging(self, file_path: Path | str | None = None) -> bool:
        """Record file logging activation.

        Args:
            file_path: Optional file path forwarded by the service.

        Returns:
            Configured fake result for file logging activation.
        """
        self.file_logging_paths.append(file_path)
        return self.enable_file_logging_result

    def shutdown(self) -> None:
        """Record shutdown execution."""
        self.shutdown_call_count += 1


@pytest.fixture(autouse=True)
def reset_global_bootstrapper(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Reset the service singleton before and after each test.

    Args:
        monkeypatch: Pytest helper used to isolate module-level state.

    Yields:
        None while the test executes.
    """
    monkeypatch.setattr(service, "_logger_bootstrapper", None)
    yield
    monkeypatch.setattr(service, "_logger_bootstrapper", None)


@pytest.fixture()
def fake_bootstrapper_type(monkeypatch: pytest.MonkeyPatch) -> type[FakeBootstrapper]:
    """Replace the real bootstrapper with a test double.

    Args:
        monkeypatch: Pytest helper used to replace the bootstrapper class.

    Returns:
        Fake bootstrapper class used by the test.
    """
    FakeBootstrapper.instances.clear()
    monkeypatch.setattr(service, "LoggerBootstrapper", FakeBootstrapper)
    return FakeBootstrapper


def test_logger_create_bootstrapper_uses_memory_only_default_config(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_create_bootstrapper())

    assert isinstance(bootstrapper, fake_bootstrapper_type)
    assert bootstrapper.config.enable_console is False


def test_logger_create_bootstrapper_uses_provided_config(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    config = LoggerConfig(enable_console=True)

    bootstrapper = cast(
        FakeBootstrapper,
        service.logger_create_bootstrapper(config=config),
    )

    assert isinstance(bootstrapper, fake_bootstrapper_type)
    assert bootstrapper.config is config


def test_logger_get_bootstrapper_creates_single_global_instance(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    first_bootstrapper = service.logger_get_bootstrapper()
    second_bootstrapper = service.logger_get_bootstrapper()

    assert first_bootstrapper is second_bootstrapper
    assert len(fake_bootstrapper_type.instances) == 1


def test_logger_bootstrap_creates_bootstrapper_with_config(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    config = LoggerConfig()

    logger = service.logger_bootstrap(config=config)

    bootstrapper = fake_bootstrapper_type.instances[0]
    assert bootstrapper.config is config
    assert bootstrapper.bootstrap_call_count == 1
    assert logger is bootstrapper.root_logger


def test_logger_bootstrap_updates_existing_bootstrapper_config(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    config = LoggerConfig()

    logger = service.logger_bootstrap(config=config)

    assert bootstrapper.updated_configs == [config]
    assert bootstrapper.bootstrap_call_count == 1
    assert logger is bootstrapper.root_logger
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_bootstrap_keeps_existing_config_when_config_is_omitted(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())

    service.logger_bootstrap()

    assert bootstrapper.updated_configs == []
    assert bootstrapper.bootstrap_call_count == 1
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_get_logger_bootstraps_early_and_returns_root_logger(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    logger = service.logger_get_logger()

    bootstrapper = fake_bootstrapper_type.instances[0]
    assert bootstrapper.bootstrap_call_count == 1
    assert logger is bootstrapper.root_logger


def test_logger_get_logger_returns_root_logger_by_root_name(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    bootstrapper.is_bootstrapped = True

    logger = service.logger_get_logger("desktop_app")

    assert bootstrapper.bootstrap_call_count == 0
    assert logger is bootstrapper.root_logger
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_get_logger_returns_absolute_child_logger(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    bootstrapper.is_bootstrapped = True

    logger = service.logger_get_logger("desktop_app.feature")

    assert logger is logging.getLogger("desktop_app.feature")
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_get_logger_returns_relative_child_logger(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    bootstrapper.is_bootstrapped = True

    logger = service.logger_get_logger("feature")

    assert logger.name == "desktop_app.feature"
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_update_config_creates_bootstrapper_when_missing(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    config = LoggerConfig()

    service.logger_update_config(config)

    bootstrapper = fake_bootstrapper_type.instances[0]
    assert bootstrapper.config is config
    assert bootstrapper.updated_configs == []


def test_logger_update_config_updates_existing_bootstrapper(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    config = LoggerConfig()

    service.logger_update_config(config)

    assert bootstrapper.updated_configs == [config]
    assert bootstrapper.config is config
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_enable_file_logging_delegates_to_bootstrapper(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    log_file_path = Path("logs/app.log")

    result = service.logger_enable_file_logging(log_file_path)

    assert result is True
    assert bootstrapper.file_logging_paths == [log_file_path]
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_enable_file_logging_returns_false_when_activation_fails(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())
    bootstrapper.enable_file_logging_result = False

    result = service.logger_enable_file_logging()

    assert result is False
    assert bootstrapper.file_logging_paths == [None]
    assert fake_bootstrapper_type.instances == [bootstrapper]


def test_logger_shutdown_does_nothing_when_bootstrapper_is_missing(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    service.logger_shutdown()

    assert fake_bootstrapper_type.instances == []


def test_logger_shutdown_releases_bootstrapper(
    fake_bootstrapper_type: type[FakeBootstrapper],
) -> None:
    bootstrapper = cast(FakeBootstrapper, service.logger_get_bootstrapper())

    service.logger_shutdown()

    assert bootstrapper.shutdown_call_count == 1
    assert service._logger_bootstrapper is None
    assert fake_bootstrapper_type.instances == [bootstrapper]
