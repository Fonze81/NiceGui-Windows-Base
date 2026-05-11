# -----------------------------------------------------------------------------
# File: tests/test_app.py
# Purpose:
# Validate the top-level NiceGUI application entry point.
# Behavior:
# Imports app.py with a fake NiceGUI module and monkeypatched startup helpers so
# tests can exercise main() without starting a real server or desktop window.
# Notes:
# Keep these tests focused on orchestration. Runtime-context and run-option
# details are covered by application package tests.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from functools import partial
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

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
    """main resolves runtime context and forwards final options to ui.run."""
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

    monkeypatch.setattr(
        module,
        "resolve_runtime_launch_context",
        lambda *, development_mode, state: context,
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

    def fake_build_main_page(**_kwargs: Any) -> None:
        """Stand in for UI composition."""

    monkeypatch.setattr(module, "build_main_page", fake_build_main_page)

    module.main(development_mode=True)

    assert lifecycle_calls == [False]
    assert len(run_option_states) == 1
    assert len(fake_ui.run_calls) == 1
    args, kwargs = fake_ui.run_calls[0]
    assert kwargs == {"native": False}
    assert len(args) == 1
    page_callback = args[0]
    assert isinstance(page_callback, partial)
    assert page_callback.func is fake_build_main_page
    assert page_callback.keywords == {
        "application_name": "NiceGui Windows Base",
        "startup_message": context.startup_message,
    }
