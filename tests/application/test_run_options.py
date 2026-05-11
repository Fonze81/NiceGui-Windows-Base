# -----------------------------------------------------------------------------
# File: tests/application/test_run_options.py
# Purpose:
# Validate NiceGUI ui.run option construction.
# Behavior:
# Uses a fake NiceGUI module so native window startup options can be tested
# without opening a real desktop window.
# Notes:
# Window geometry must remain in app.native.window_args and must not be passed
# through ui.run options.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import AppState, reset_app_state


@pytest.fixture()
def run_options_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load run_options.py with a fake NiceGUI native object."""
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui_module = SimpleNamespace(
        app=SimpleNamespace(native=fake_native),
        native=SimpleNamespace(find_open_port=lambda: 54321),
    )

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)
    sys.modules.pop("desktop_app.infrastructure.native_window_state", None)
    sys.modules.pop("desktop_app.application.run_options", None)

    module = importlib.import_module("desktop_app.application.run_options")

    yield module

    sys.modules.pop("desktop_app.application.run_options", None)
    sys.modules.pop("desktop_app.infrastructure.native_window_state", None)
    reset_app_state()


def test_build_ui_run_options_keeps_window_geometry_out_of_ui_run(
    run_options_module: ModuleType,
) -> None:
    """Native geometry is applied only through app.native.window_args."""
    state = AppState()
    state.window.x = 120
    state.window.y = 140
    state.window.width = 1024
    state.window.height = 768
    context = run_options_module.RuntimeLaunchContext(
        startup_source="pyproject command",
        startup_message="Starting",
        native_mode=True,
        reload_enabled=False,
        port=8123,
        icon_path="app.ico",
        splash_image_path="splash.png",
    )

    options = run_options_module.build_ui_run_options(context, state=state)

    assert options == {
        "native": True,
        "reload": False,
        "title": "NiceGui Windows Base",
        "favicon": "app.ico",
        "port": 8123,
        "host": "127.0.0.1",
    }
    assert "window_size" not in options
    assert "fullscreen" not in options
    assert run_options_module.apply_initial_native_window_options.__globals__[
        "app"
    ].native.window_args == {
        "width": 1024,
        "height": 768,
        "fullscreen": False,
        "x": 120,
        "y": 140,
    }


def test_build_ui_run_options_adds_reload_options_for_development(
    run_options_module: ModuleType,
) -> None:
    """Reload options are added only when reload is enabled."""
    state = AppState()
    context = run_options_module.RuntimeLaunchContext(
        startup_source="dev_run.py",
        startup_message="Starting",
        native_mode=False,
        reload_enabled=True,
        port=8000,
        icon_path="app.ico",
        splash_image_path="splash.png",
    )

    options = run_options_module.build_ui_run_options(context, state=state)

    assert options["native"] is False
    assert options["reload"] is True
    assert options["uvicorn_reload_dirs"] == "src"
    assert options["uvicorn_reload_includes"] == "*.py"
    assert "window_size" not in options
    assert "fullscreen" not in options
