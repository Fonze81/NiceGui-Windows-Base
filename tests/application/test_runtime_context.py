# -----------------------------------------------------------------------------
# File: tests/application/test_runtime_context.py
# Purpose:
# Validate runtime launch context resolution.
# Behavior:
# Uses monkeypatched runtime and asset helpers so context resolution can be
# tested without depending on the current process entry point.
# Notes:
# These tests focus on state updates and port selection, not NiceGUI startup.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import AppState, reset_app_state


@pytest.fixture()
def runtime_context_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load runtime_context.py with a fake NiceGUI native module."""
    fake_native = SimpleNamespace(find_open_port=lambda: 54321)
    fake_nicegui_module = SimpleNamespace(native=fake_native)

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)
    sys.modules.pop("desktop_app.application.runtime_context", None)

    module = importlib.import_module("desktop_app.application.runtime_context")

    yield module

    sys.modules.pop("desktop_app.application.runtime_context", None)
    reset_app_state()


def test_get_runtime_port_uses_dynamic_port_for_native_mode(
    runtime_context_module: ModuleType,
) -> None:
    """Native mode receives a dynamic available port."""
    assert runtime_context_module.get_runtime_port(native_mode=True) == 54321


def test_get_runtime_port_uses_default_port_for_web_mode(
    runtime_context_module: ModuleType,
) -> None:
    """Web development mode receives the stable development port."""
    assert runtime_context_module.get_runtime_port(native_mode=False) == 8080


def test_resolve_runtime_launch_context_updates_state(
    monkeypatch: pytest.MonkeyPatch,
    runtime_context_module: ModuleType,
) -> None:
    """Resolved runtime values are returned and mirrored in AppState."""
    state = AppState()
    monkeypatch.setattr(
        runtime_context_module,
        "get_nicegui_modes",
        lambda *, development_mode: (False, True),
    )
    monkeypatch.setattr(
        runtime_context_module,
        "detect_startup_source",
        lambda *, development_mode, entry_source_hint=None: (
            entry_source_hint or "dev_run.py"
        ),
    )
    monkeypatch.setattr(
        runtime_context_module,
        "get_runtime_port",
        lambda *, native_mode: 7777,
    )
    monkeypatch.setattr(
        runtime_context_module,
        "get_application_icon_path",
        lambda: r"C:\app\app_icon.ico",
    )
    monkeypatch.setattr(
        runtime_context_module,
        "resolve_asset_path",
        lambda asset_filename: rf"C:\app\assets\{asset_filename}",
    )

    context = runtime_context_module.resolve_runtime_launch_context(
        development_mode=True,
        state=state,
        entry_source_hint="module",
    )

    assert context.startup_source == "module"
    assert context.native_mode is False
    assert context.reload_enabled is True
    assert context.port == 7777
    assert context.icon_path == r"C:\app\app_icon.ico"
    assert context.splash_image_path.endswith("splash_light.png")
    assert state.runtime.startup_source == context.startup_source
    assert state.runtime.startup_message == context.startup_message
    assert state.runtime.native_mode is False
    assert state.runtime.reload_enabled is True
    assert state.runtime.port == 7777
    assert str(state.assets.icon_path) == r"C:\app\app_icon.ico"
