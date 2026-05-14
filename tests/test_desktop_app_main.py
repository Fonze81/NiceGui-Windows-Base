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
from desktop_app.core.runtime import ENTRY_SOURCE_HINT_GLOBAL, StartupSource


def test_run_executes_app_module_with_main_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Execute desktop_app.app as __main__ with sys alteration enabled."""
    run_module_mock = Mock()

    monkeypatch.setattr(package_main.runpy, "run_module", run_module_mock)
    monkeypatch.setattr(package_main.sys, "argv", ["__main__.py"])

    package_main.run()

    run_module_mock.assert_called_once_with(
        "desktop_app.app",
        run_name="__main__",
        alter_sys=True,
        init_globals={
            ENTRY_SOURCE_HINT_GLOBAL: StartupSource.MODULE_EXECUTION,
        },
    )


def test_run_preserves_pyproject_command_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve installed-command source before runpy changes argv."""
    run_module_mock = Mock()

    monkeypatch.setattr(package_main.runpy, "run_module", run_module_mock)
    monkeypatch.setattr(package_main.sys, "argv", ["nicegui-windows-base.exe"])

    package_main.run()

    run_module_mock.assert_called_once_with(
        "desktop_app.app",
        run_name="__main__",
        alter_sys=True,
        init_globals={
            ENTRY_SOURCE_HINT_GLOBAL: StartupSource.PYPROJECT_COMMAND,
        },
    )
