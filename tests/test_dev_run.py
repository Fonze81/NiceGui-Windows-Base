# -----------------------------------------------------------------------------
# File: tests/test_dev_run.py
# Purpose:
# Validate the development runner entry-point guard.
# Behavior:
# Executes dev_run.py with different module names and verifies that the
# application main function is called only for supported development execution
# contexts.
# Notes:
# The real desktop_app.app module is replaced with a fake module to avoid
# starting NiceGUI, opening UI windows, or loading application runtime side
# effects during this focused entry-point test.
# -----------------------------------------------------------------------------

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV_RUN_PATH = PROJECT_ROOT / "dev_run.py"


@pytest.fixture
def fake_main(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Provide a fake desktop_app.app.main function for entry-point tests.

    Args:
        monkeypatch: Pytest fixture used to isolate sys.modules changes.

    Returns:
        Mock replacing desktop_app.app.main.
    """
    main_mock = Mock()

    package_module = ModuleType("desktop_app")
    package_module.__dict__["__path__"] = []

    app_module = ModuleType("desktop_app.app")
    app_module.__dict__["main"] = main_mock

    monkeypatch.setitem(sys.modules, "desktop_app", package_module)
    monkeypatch.setitem(sys.modules, "desktop_app.app", app_module)

    return main_mock


@pytest.mark.parametrize("run_name", ["__main__", "__mp_main__"])
def test_dev_run_starts_application_in_development_mode(
    fake_main: Mock,
    run_name: str,
) -> None:
    """Call main in development mode for supported execution names."""
    runpy.run_path(str(DEV_RUN_PATH), run_name=run_name)

    fake_main.assert_called_once_with(development_mode=True)


def test_dev_run_does_not_start_application_when_imported(fake_main: Mock) -> None:
    """Do not call main when the file is imported as a normal module."""
    runpy.run_path(str(DEV_RUN_PATH), run_name="dev_run")

    fake_main.assert_not_called()
