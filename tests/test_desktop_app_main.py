# -----------------------------------------------------------------------------
# File: tests/test_desktop_app_main.py
# Purpose:
# Validate module execution support for the desktop_app package.
# Behavior:
# Tests that importing desktop_app.__main__ has no startup side effects and that
# the run helper executes desktop_app.app through runpy with __main__ semantics.
# Notes:
# These tests patch runpy.run_module to avoid starting the NiceGUI runtime during
# automated test execution.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path
from typing import Any

import pytest

MODULE_NAME = "desktop_app.__main__"


def test_run_executes_application_module_as_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure run executes desktop_app.app with script semantics."""
    import desktop_app.__main__ as main_module

    calls: list[tuple[str, str | None, bool]] = []

    def fake_run_module(
        mod_name: str,
        *,
        run_name: str | None = None,
        alter_sys: bool = False,
    ) -> dict[str, Any]:
        """Capture runpy.run_module arguments."""
        calls.append((mod_name, run_name, alter_sys))
        return {"__name__": run_name}

    monkeypatch.setattr(main_module.runpy, "run_module", fake_run_module)

    main_module.run()

    assert calls == [("desktop_app.app", "__main__", True)]


def test_importing_main_module_does_not_start_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure importing desktop_app.__main__ has no startup side effect."""
    calls: list[str] = []

    def fake_run_module(*_args: object, **_kwargs: object) -> dict[str, Any]:
        """Record unexpected application execution attempts."""
        calls.append("called")
        return {}

    sys.modules.pop(MODULE_NAME, None)
    monkeypatch.setattr(runpy, "run_module", fake_run_module)

    imported_module = importlib.import_module(MODULE_NAME)

    assert imported_module.__name__ == MODULE_NAME
    assert calls == []


def test_script_execution_invokes_run_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure executing __main__.py as a script delegates to runpy."""
    calls: list[tuple[str, str | None, bool]] = []

    def fake_run_module(
        mod_name: str,
        *,
        run_name: str | None = None,
        alter_sys: bool = False,
    ) -> dict[str, Any]:
        """Capture runpy.run_module arguments from script execution."""
        calls.append((mod_name, run_name, alter_sys))
        return {"__name__": run_name}

    monkeypatch.setattr(runpy, "run_module", fake_run_module)
    module_path = Path(__file__).parents[1] / "src" / "desktop_app" / "__main__.py"

    module_globals = runpy.run_path(str(module_path), run_name="__main__")

    assert calls == [("desktop_app.app", "__main__", True)]
    assert "run" in module_globals
