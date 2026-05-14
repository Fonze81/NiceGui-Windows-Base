# -----------------------------------------------------------------------------
# File: tests/test_app.py
# Purpose:
# Validate the top-level NiceGUI application entry point.
# Behavior:
# Imports app.py with a fake NiceGUI module and monkeypatched startup helpers so
# tests can exercise main() without starting a real server or desktop window.
# Notes:
# Keep these tests focused on orchestration. Runtime-context, run-option, and SPA
# routing details are covered by focused application and UI package tests.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import reset_app_state


class FakeUi:
    """Capture NiceGUI ui.run calls without starting NiceGUI."""

    def __init__(self) -> None:
        """Initialize an empty call history."""
        self.run_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def run(self, *args: object, **kwargs: object) -> None:
        """Record one ui.run call."""
        self.run_calls.append((args, kwargs))


@pytest.fixture()
def app_module(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, FakeUi]:
    """Import desktop_app.app with deterministic startup dependencies."""
    fake_ui = FakeUi()
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui = SimpleNamespace(
        app=SimpleNamespace(native=fake_native),
        native=SimpleNamespace(find_open_port=lambda: 54321),
        ui=fake_ui,
    )
    prepare_calls: list[str] = []

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui)

    for module_name in (
        "desktop_app.app",
        "desktop_app.application.bootstrap",
        "desktop_app.application.run_options",
        "desktop_app.application.runtime_context",
        "desktop_app.infrastructure.lifecycle",
        "desktop_app.infrastructure.native_window_state",
        "desktop_app.ui.router",
    ):
        sys.modules.pop(module_name, None)

    bootstrap = importlib.import_module("desktop_app.application.bootstrap")
    monkeypatch.setattr(
        bootstrap,
        "prepare_native_window_arguments_before_main",
        lambda: prepare_calls.append("prepare"),
    )
    monkeypatch.setattr(
        bootstrap,
        "configure_logging",
        lambda *, state: Path("app.log"),
    )

    module = importlib.import_module("desktop_app.app")

    assert prepare_calls == ["prepare"]

    yield module, fake_ui

    sys.modules.pop("desktop_app.app", None)
    reset_app_state()


def test_main_orchestrates_runtime_startup(
    app_module: tuple[ModuleType, FakeUi],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main resolves runtime context, registers SPA routes, and runs NiceGUI."""
    module, fake_ui = app_module
    context = SimpleNamespace(
        startup_source="dev_run.py",
        startup_message="NiceGui Windows Base is starting.",
        native_mode=False,
        reload_enabled=True,
        port=8080,
        icon_path="app.ico",
        splash_image_path="splash.png",
    )
    lifecycle_calls: list[bool] = []
    run_option_states: list[object] = []
    registered_routes: list[dict[str, str]] = []

    monkeypatch.setattr(
        module,
        "resolve_runtime_launch_context",
        lambda *, development_mode, state, entry_source_hint=None: context,
    )
    monkeypatch.setattr(
        module,
        "register_lifecycle_handlers",
        lambda *, native_mode: lifecycle_calls.append(native_mode),
    )
    monkeypatch.setattr(
        module,
        "build_ui_run_options",
        lambda context, *, state: run_option_states.append(state) or {"native": False},
    )
    monkeypatch.setattr(
        module,
        "register_spa_routes",
        lambda *, application_name, startup_message: registered_routes.append(
            {
                "application_name": application_name,
                "startup_message": startup_message,
            }
        ),
    )

    module.main(development_mode=True)

    assert lifecycle_calls == [False]
    assert len(run_option_states) == 1
    assert registered_routes == [
        {
            "application_name": "NiceGui Windows Base",
            "startup_message": context.startup_message,
        }
    ]
    assert fake_ui.run_calls == [((), {"native": False})]
