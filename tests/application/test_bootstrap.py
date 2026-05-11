# -----------------------------------------------------------------------------
# File: tests/application/test_bootstrap.py
# Purpose:
# Validate early application bootstrap helpers.
# Behavior:
# Imports bootstrap.py with fake NiceGUI objects and monkeypatches settings,
# native window preparation, runtime paths, and logger activation.
# Notes:
# These tests keep app startup deterministic and avoid opening NiceGUI windows.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import AppState, reset_app_state
from desktop_app.infrastructure.logger import LoggerConfig


@pytest.fixture()
def bootstrap_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import bootstrap.py with a minimal fake NiceGUI module."""
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui = SimpleNamespace(app=SimpleNamespace(native=fake_native))

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui)
    for module_name in (
        "desktop_app.application.bootstrap",
        "desktop_app.infrastructure.native_window_state",
    ):
        sys.modules.pop(module_name, None)

    module = importlib.import_module("desktop_app.application.bootstrap")

    yield module

    for module_name in (
        "desktop_app.application.bootstrap",
        "desktop_app.infrastructure.native_window_state",
    ):
        sys.modules.pop(module_name, None)
    reset_app_state()


def test_prepare_native_window_arguments_loads_settings_once(
    bootstrap_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings are loaded before native window arguments are synchronized."""
    state = AppState()
    calls: list[str] = []

    def load_settings(*, state: AppState) -> bool:
        """Record settings loading and mark state as loaded."""
        calls.append("load")
        state.settings.last_load_ok = True
        return True

    def apply_native_window_args_from_state(*, state: AppState) -> None:
        """Record native argument preparation."""
        calls.append("apply")

    monkeypatch.setattr(bootstrap_module, "load_settings", load_settings)
    monkeypatch.setattr(
        bootstrap_module,
        "apply_native_window_args_from_state",
        apply_native_window_args_from_state,
    )

    bootstrap_module.prepare_native_window_arguments_before_main(state=state)

    assert calls == ["load", "apply"]


def test_prepare_native_window_arguments_skips_loading_when_already_loaded(
    bootstrap_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Already-loaded settings are not loaded again before native preparation."""
    state = AppState()
    state.settings.last_load_ok = True
    calls: list[str] = []

    def fail_load_settings(*, state: AppState) -> bool:
        """Fail if settings loading is unexpectedly repeated."""
        raise AssertionError("load_settings should not be called")

    monkeypatch.setattr(bootstrap_module, "load_settings", fail_load_settings)
    monkeypatch.setattr(
        bootstrap_module,
        "apply_native_window_args_from_state",
        lambda *, state: calls.append("apply"),
    )

    bootstrap_module.prepare_native_window_arguments_before_main(state=state)

    assert calls == ["apply"]


def test_configure_logging_resolves_paths_and_enables_file_logging(
    bootstrap_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Logger configuration uses settings values and resolved runtime paths."""
    state = AppState()
    settings_path = tmp_path / "settings.toml"
    log_file_path = tmp_path / "logs" / "app.log"
    configs: list[LoggerConfig] = []

    def load_settings(*, state: AppState) -> bool:
        """Populate settings metadata used by configure_logging."""
        state.settings.last_load_ok = True
        state.settings.file_path = settings_path
        state.log.file_path = Path("logs/app.log")
        return True

    monkeypatch.setattr(bootstrap_module, "load_settings", load_settings)
    monkeypatch.setattr(bootstrap_module, "get_pyinstaller_temp_dir", lambda: tmp_path)
    monkeypatch.setattr(bootstrap_module, "is_frozen_executable", lambda: False)
    monkeypatch.setattr(
        bootstrap_module,
        "resolve_log_file_path",
        lambda file_path, *, frozen_executable: log_file_path,
    )
    monkeypatch.setattr(bootstrap_module, "logger_bootstrap", configs.append)
    monkeypatch.setattr(bootstrap_module, "logger_enable_file_logging", lambda: True)

    resolved_path = bootstrap_module.configure_logging(state=state)

    assert resolved_path == log_file_path
    assert state.settings.file_path == settings_path
    assert state.paths.settings_file_path == settings_path
    assert state.paths.log_file_path == log_file_path
    assert state.log.effective_file_path == log_file_path
    assert state.log.file_logging_enabled is True
    assert state.log.early_buffering_enabled is False
    assert configs
    assert configs[0].file_path == log_file_path
    assert configs[0].enable_console is True
    assert state.paths.working_directory is not None
    assert state.paths.executable_path is not None
    assert state.paths.pyinstaller_temp_dir == tmp_path


def test_configure_logging_disables_console_for_frozen_executable(
    bootstrap_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Packaged execution disables console logging even when settings enable it."""
    state = AppState()
    state.settings.last_load_ok = True
    state.settings.file_path = tmp_path / "settings.toml"
    log_file_path = tmp_path / "app.log"
    configs: list[LoggerConfig] = []

    monkeypatch.setattr(bootstrap_module, "get_pyinstaller_temp_dir", lambda: None)
    monkeypatch.setattr(bootstrap_module, "is_frozen_executable", lambda: True)
    monkeypatch.setattr(
        bootstrap_module,
        "resolve_log_file_path",
        lambda file_path, *, frozen_executable: log_file_path,
    )
    monkeypatch.setattr(bootstrap_module, "logger_bootstrap", configs.append)
    monkeypatch.setattr(bootstrap_module, "logger_enable_file_logging", lambda: False)

    resolved_path = bootstrap_module.configure_logging(state=state)

    assert resolved_path == log_file_path
    assert state.log.file_logging_enabled is False
    assert state.log.early_buffering_enabled is True
    assert configs[0].enable_console is False
