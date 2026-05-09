# -----------------------------------------------------------------------------
# File: tests/test_desktop_app_main.py
# Purpose:
# Validate module execution support for the desktop_app package.
# Behavior:
# Tests that importing desktop_app.__main__ has no startup side effects and that
# both the local run helper and module execution delegate to desktop_app.app.main.
# Notes:
# These tests intentionally replace desktop_app.app.main to avoid starting the
# NiceGUI runtime during automated test execution.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import runpy
import sys

import pytest

MODULE_NAME = "desktop_app.__main__"


def test_run_delegates_to_application_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure run delegates to the application main function."""
    import desktop_app.__main__ as main_module

    calls: list[str] = []

    def fake_main() -> None:
        calls.append("called")

    monkeypatch.setattr(main_module, "main", fake_main)

    main_module.run()

    assert calls == ["called"]


def test_importing_main_module_does_not_start_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure importing desktop_app.__main__ has no startup side effect."""
    import desktop_app.app as app_module

    calls: list[str] = []

    def fake_main() -> None:
        calls.append("called")

    monkeypatch.setattr(app_module, "main", fake_main)
    sys.modules.pop(MODULE_NAME, None)

    imported_module = importlib.import_module(MODULE_NAME)

    assert imported_module.__name__ == MODULE_NAME
    assert calls == []


def test_module_execution_delegates_to_application_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure python -m desktop_app delegates to the application main function."""
    import desktop_app.app as app_module

    calls: list[str] = []

    def fake_main() -> None:
        calls.append("called")

    monkeypatch.setattr(app_module, "main", fake_main)
    sys.modules.pop(MODULE_NAME, None)

    module_globals = runpy.run_module("desktop_app", run_name="__main__")

    assert calls == ["called"]
    assert "run" in module_globals
