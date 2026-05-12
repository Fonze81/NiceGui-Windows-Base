# -----------------------------------------------------------------------------
# File: tests/ui/test_pages_and_router.py
# Purpose:
# Validate NiceGUI SPA layout, page builders, and route registration.
# Behavior:
# Uses a small fake NiceGUI UI object so page composition can be exercised
# without starting a real NiceGUI server or browser client.
# Notes:
# These tests focus on state updates and route wiring instead of visual rendering.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest

from desktop_app.core.state import get_app_state, reset_app_state


@dataclass(slots=True)
class FakeElement:
    """Represent a chainable NiceGUI element used by page tests."""

    ui: FakeUi
    kind: str
    args: tuple[object, ...] = field(default_factory=tuple)

    def classes(self, class_names: str) -> FakeElement:
        """Record class assignments and keep the element chainable."""
        self.ui.class_calls.append((self.kind, class_names))
        return self

    def __enter__(self) -> FakeElement:
        """Enter a fake NiceGUI container context."""
        self.ui.context_stack.append(self.kind)
        return self

    def __exit__(self, *_args: object) -> None:
        """Exit a fake NiceGUI container context."""
        self.ui.context_stack.pop()


@dataclass(slots=True)
class FakeUi:
    """Capture the NiceGUI UI API used by the SPA modules."""

    query_selectors: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)
    class_calls: list[tuple[str, str]] = field(default_factory=list)
    sub_page_routes: dict[str, Callable[..., None]] | None = None
    page_routes: list[tuple[str, Callable[..., None]]] = field(default_factory=list)
    context_stack: list[str] = field(default_factory=list)

    def query(self, selector: str) -> FakeElement:
        """Record a CSS selector query."""
        self.query_selectors.append(selector)
        return FakeElement(self, "query", (selector,))

    def column(self) -> FakeElement:
        """Return a fake column container."""
        return FakeElement(self, "column")

    def card(self) -> FakeElement:
        """Return a fake card container."""
        return FakeElement(self, "card")

    def image(self, source: str) -> FakeElement:
        """Record an image element."""
        self.images.append(source)
        return FakeElement(self, "image", (source,))

    def label(self, text: str) -> FakeElement:
        """Record a label element."""
        self.labels.append(text)
        return FakeElement(self, "label", (text,))

    def link(self, text: str, target: str) -> FakeElement:
        """Record a link element."""
        self.links.append((text, target))
        return FakeElement(self, "link", (text, target))

    def sub_pages(self, routes: dict[str, Callable[..., None]]) -> None:
        """Record the registered sub-page route table."""
        self.sub_page_routes = routes

    def page(self, route: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
        """Return a decorator that records page registrations."""

        def decorator(callback: Callable[..., None]) -> Callable[..., None]:
            """Record and return the decorated page callback."""
            self.page_routes.append((route, callback))
            return callback

        return decorator


@pytest.fixture()
def fake_ui(monkeypatch: pytest.MonkeyPatch) -> Generator[FakeUi]:
    """Install a fake NiceGUI UI module and clear imported UI modules."""
    ui = FakeUi()
    fake_nicegui_module = SimpleNamespace(ui=ui)

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)

    for module_name in (
        "desktop_app.ui.router",
        "desktop_app.ui.layout",
        "desktop_app.ui.pages.routes",
        "desktop_app.ui.pages.index",
        "desktop_app.ui.pages.not_found",
    ):
        sys.modules.pop(module_name, None)

    yield ui

    for module_name in (
        "desktop_app.ui.router",
        "desktop_app.ui.layout",
        "desktop_app.ui.pages.routes",
        "desktop_app.ui.pages.index",
        "desktop_app.ui.pages.not_found",
    ):
        sys.modules.pop(module_name, None)
    reset_app_state()


def test_build_index_page_updates_state_and_composes_content(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The index page updates UI state and renders the expected content."""
    module = importlib.import_module("desktop_app.ui.pages.index")
    image_path = tmp_path / "page_image.png"
    monkeypatch.setattr(module, "resolve_asset_path", lambda _name: str(image_path))

    module.build_index_page(
        application_name="Example App",
        startup_message="Started from tests.",
    )

    state = get_app_state()
    assert state.ui_session.active_view == "home"
    assert state.ui_session.last_page_built_at is not None
    assert state.ui_session.is_busy is False
    assert state.ui_session.busy_message is None
    assert state.assets.page_image_path == image_path
    assert fake_ui.query_selectors == ["body"]
    assert fake_ui.images == [str(image_path)]
    assert "Example App" in fake_ui.labels
    assert "Started from tests." in fake_ui.labels
    assert fake_ui.context_stack == []


def test_build_not_found_page_updates_state_and_renders_recovery_link(
    fake_ui: FakeUi,
) -> None:
    """The fallback page sets the active view and renders a home link."""
    module = importlib.import_module("desktop_app.ui.pages.not_found")

    module.build_not_found_page()

    assert get_app_state().ui_session.active_view == "not_found"
    assert fake_ui.labels == [
        "Page not found",
        "The requested application page is not available.",
    ]
    assert fake_ui.links == [("Back to Home", "/")]
    assert fake_ui.context_stack == []


def test_build_sub_page_routes_returns_home_and_fallback_routes(
    fake_ui: FakeUi,
) -> None:
    """The sub-page route table binds index context and fallback page."""
    module = importlib.import_module("desktop_app.ui.pages.routes")

    routes = module.build_sub_page_routes(
        application_name="Example App",
        startup_message="Started.",
    )

    assert set(routes) == {"/", "/{_:path}"}
    routes["/"]()
    assert "Example App" in fake_ui.labels
    assert "Started." in fake_ui.labels


def test_build_app_layout_mounts_sub_pages_and_updates_session(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shared layout resets busy state and mounts generated sub-pages."""
    module = importlib.import_module("desktop_app.ui.layout")
    expected_routes = {"/": lambda: None}
    state = get_app_state()
    state.ui_session.is_busy = True
    state.ui_session.busy_message = "Working"

    monkeypatch.setattr(
        module,
        "build_sub_page_routes",
        lambda *, application_name, startup_message: expected_routes,
    )

    module.build_app_layout(
        application_name="Example App",
        startup_message="Started.",
    )

    assert state.ui_session.last_page_built_at is not None
    assert state.ui_session.is_busy is False
    assert state.ui_session.busy_message is None
    assert fake_ui.sub_page_routes == expected_routes


def test_register_spa_routes_registers_root_and_catch_all_pages(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The SPA router registers both entry routes and builds the shell."""
    module = importlib.import_module("desktop_app.ui.router")
    layout_calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        module,
        "build_app_layout",
        lambda *, application_name, startup_message: layout_calls.append(
            (application_name, startup_message)
        ),
    )

    module.register_spa_routes(
        application_name="Example App",
        startup_message="Started.",
    )

    assert [route for route, _callback in fake_ui.page_routes] == ["/{_:path}", "/"]
    callback = fake_ui.page_routes[-1][1]
    callback()

    assert layout_calls == [("Example App", "Started.")]
