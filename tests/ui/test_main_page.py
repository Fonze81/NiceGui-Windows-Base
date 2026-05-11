# -----------------------------------------------------------------------------
# File: tests/ui/test_main_page.py
# Purpose:
# Validate the main NiceGUI page builder.
# Behavior:
# Uses a small fake NiceGUI UI object to verify page composition without opening
# a browser, desktop window, or real NiceGUI client.
# Notes:
# These tests focus on UI state updates and asset usage, not Tailwind rendering.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from desktop_app.core.state import reset_app_state


class FakeElement:
    """Minimal chainable context manager returned by fake UI calls."""

    def __init__(self, ui: FakeUi, name: str, value: object | None = None) -> None:
        """Store the element creation call."""
        self._ui = ui
        self.name = name
        self.value = value

    def classes(self, class_names: str) -> FakeElement:
        """Record assigned CSS classes and return the same element."""
        self._ui.calls.append(("classes", self.name, class_names))
        return self

    def __enter__(self) -> FakeElement:
        """Enter a fake context manager."""
        self._ui.calls.append(("enter", self.name, self.value))
        return self

    def __exit__(self, *_args: object) -> None:
        """Exit a fake context manager."""
        self._ui.calls.append(("exit", self.name, self.value))


class FakeUi:
    """Small subset of NiceGUI's UI API used by main_page.py."""

    def __init__(self) -> None:
        """Initialize an empty call history."""
        self.calls: list[tuple[str, object, object | None]] = []

    def query(self, selector: str) -> FakeElement:
        """Record a body query."""
        self.calls.append(("query", selector, None))
        return FakeElement(self, "query", selector)

    def column(self) -> FakeElement:
        """Record a column creation."""
        self.calls.append(("column", None, None))
        return FakeElement(self, "column")

    def card(self) -> FakeElement:
        """Record a card creation."""
        self.calls.append(("card", None, None))
        return FakeElement(self, "card")

    def image(self, image_path: str) -> FakeElement:
        """Record an image creation."""
        self.calls.append(("image", image_path, None))
        return FakeElement(self, "image", image_path)

    def label(self, text: str) -> FakeElement:
        """Record a label creation."""
        self.calls.append(("label", text, None))
        return FakeElement(self, "label", text)


@pytest.fixture()
def main_page_module(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, FakeUi]:
    """Import main_page.py with a fake NiceGUI UI module."""
    fake_ui = FakeUi()
    fake_nicegui = SimpleNamespace(ui=fake_ui)

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui)
    sys.modules.pop("desktop_app.ui.main_page", None)

    module = importlib.import_module("desktop_app.ui.main_page")

    yield module, fake_ui

    sys.modules.pop("desktop_app.ui.main_page", None)
    reset_app_state()


def test_build_main_page_updates_session_state_and_uses_page_asset(
    main_page_module: tuple[ModuleType, FakeUi],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The main page updates transient state and renders expected content."""
    module, fake_ui = main_page_module
    state = reset_app_state()
    page_image_path = r"C:\app\assets\page_image.png"

    monkeypatch.setattr(module, "resolve_asset_path", lambda _filename: page_image_path)

    module.build_main_page(
        application_name="NiceGui Windows Base",
        startup_message="Application started.",
    )

    assert state.ui_session.active_view == "home"
    assert state.ui_session.last_page_built_at is not None
    assert state.ui_session.is_busy is False
    assert state.ui_session.busy_message is None
    assert state.assets.page_image_path == Path(page_image_path)
    assert ("query", "body", None) in fake_ui.calls
    assert ("image", page_image_path, None) in fake_ui.calls
    assert ("label", "NiceGui Windows Base", None) in fake_ui.calls
    assert ("label", "Application started.", None) in fake_ui.calls
