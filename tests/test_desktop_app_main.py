# -----------------------------------------------------------------------------
# File: tests/test___main__.py
# Purpose:
# Validate package module execution routing.
# Behavior:
# Verifies that desktop_app.__main__ delegates execution to desktop_app.app using
# __main__ semantics, preserving the same startup path used by direct app.py
# execution.
# Notes:
# The test mocks runpy.run_module to avoid starting NiceGUI or executing the real
# application entry point.
# -----------------------------------------------------------------------------

from __future__ import annotations

from unittest.mock import Mock

import pytest

import desktop_app.__main__ as package_main


def test_run_executes_app_module_with_main_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Execute desktop_app.app as __main__ with sys alteration enabled."""
    run_module_mock = Mock()

    monkeypatch.setattr(package_main.runpy, "run_module", run_module_mock)

    package_main.run()

    run_module_mock.assert_called_once_with(
        "desktop_app.app",
        run_name="__main__",
        alter_sys=True,
    )
