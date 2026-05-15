# -----------------------------------------------------------------------------
# File: tests/ui/test_pages_and_router.py
# Purpose:
# Validate NiceGUI SPA layout, page builders, component helpers, and route wiring.
# Behavior:
# Uses a small fake NiceGUI UI object so page composition can be exercised
# without starting a real NiceGUI server or browser client.
# Notes:
# These tests focus on state updates, route wiring, and bounded helper logic
# instead of visual rendering in a browser.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from desktop_app.core.state import get_app_state, reset_app_state

UI_MODULE_NAMES: tuple[str, ...] = (
    "desktop_app.ui.router",
    "desktop_app.ui.layout",
    "desktop_app.ui.theme",
    "desktop_app.ui.components",
    "desktop_app.ui.components.cards",
    "desktop_app.ui.components.feedback",
    "desktop_app.ui.components.navigation",
    "desktop_app.ui.components.page",
    "desktop_app.ui.pages.routes",
    "desktop_app.ui.pages.components",
    "desktop_app.ui.pages.diagnostics",
    "desktop_app.ui.pages.index",
    "desktop_app.ui.pages.logs",
    "desktop_app.ui.pages.not_found",
    "desktop_app.ui.pages.settings",
    "desktop_app.ui.pages.status",
)


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

    def props(self, props_text: str) -> FakeElement:
        """Record prop assignments and keep the element chainable."""
        self.ui.prop_calls.append((self.kind, props_text))
        return self

    def __enter__(self) -> FakeElement:
        """Enter a fake NiceGUI container context."""
        self.ui.context_stack.append(self.kind)
        return self

    def __exit__(self, *_args: object) -> None:
        """Exit a fake NiceGUI container context."""
        self.ui.context_stack.pop()


@dataclass(slots=True)
class FakeApp:
    """Capture the NiceGUI app API used by the router module."""

    static_files: list[tuple[str, str]] = field(default_factory=list)
    get_routes: list[tuple[str, bool]] = field(default_factory=list)
    get_callbacks: list[Callable[..., object]] = field(default_factory=list)

    def add_static_files(self, route: str, local_directory: str) -> None:
        """Record a static files route registration."""
        self.static_files.append((route, local_directory))

    def get(
        self,
        route: str,
        *,
        include_in_schema: bool = True,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Return a decorator that records FastAPI GET route registrations."""

        def decorator(callback: Callable[..., object]) -> Callable[..., object]:
            """Record and return the decorated GET callback."""
            self.get_routes.append((route, include_in_schema))
            self.get_callbacks.append(callback)
            return callback

        return decorator


@dataclass(slots=True)
class FakeUi:
    """Capture the NiceGUI UI API used by the SPA modules."""

    query_selectors: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)
    codes: list[str] = field(default_factory=list)
    buttons: list[tuple[str, Callable[..., object] | None]] = field(
        default_factory=list
    )
    selects: list[dict[str, object]] = field(default_factory=list)
    numbers: list[dict[str, object]] = field(default_factory=list)
    inputs: list[dict[str, object]] = field(default_factory=list)
    switches: list[dict[str, object]] = field(default_factory=list)
    class_calls: list[tuple[str, str]] = field(default_factory=list)
    prop_calls: list[tuple[str, str]] = field(default_factory=list)
    sub_page_routes: dict[str, Callable[..., None]] | None = None
    page_routes: list[tuple[str, Callable[..., None]]] = field(default_factory=list)
    context_stack: list[str] = field(default_factory=list)
    app: FakeApp = field(default_factory=FakeApp)

    def query(self, selector: str) -> FakeElement:
        """Record a CSS selector query."""
        self.query_selectors.append(selector)
        return FakeElement(self, "query", (selector,))

    def column(self) -> FakeElement:
        """Return a fake column container."""
        return FakeElement(self, "column")

    def row(self) -> FakeElement:
        """Return a fake row container."""
        return FakeElement(self, "row")

    def card(self) -> FakeElement:
        """Return a fake card container."""
        return FakeElement(self, "card")

    def image(self, source: str) -> FakeElement:
        """Record an image element."""
        self.images.append(source)
        return FakeElement(self, "image", (source,))

    def label(self, text: object) -> FakeElement:
        """Record a label element."""
        self.labels.append(str(text))
        return FakeElement(self, "label", (text,))

    def link(self, text: str, target: str) -> FakeElement:
        """Record a link element."""
        self.links.append((text, target))
        return FakeElement(self, "link", (text, target))

    def code(self, content: str) -> FakeElement:
        """Record a code block."""
        self.codes.append(content)
        return FakeElement(self, "code", (content,))

    def button(
        self,
        text: str,
        on_click: Callable[..., object] | None = None,
    ) -> FakeElement:
        """Record a button element."""
        self.buttons.append((text, on_click))
        return FakeElement(self, "button", (text,))

    def select(
        self,
        *,
        options: list[str],
        value: str,
        label: str,
        on_change: Callable[..., object] | None = None,
    ) -> FakeElement:
        """Record a select element."""
        self.selects.append(
            {
                "options": options,
                "value": value,
                "label": label,
                "on_change": on_change,
            }
        )
        return FakeElement(self, "select", (label,))

    def number(
        self,
        *,
        label: str,
        value: float,
        min: float,
        max: float,
        step: float,
        on_change: Callable[..., object] | None = None,
    ) -> FakeElement:
        """Record a number input element."""
        self.numbers.append(
            {
                "label": label,
                "value": value,
                "min": min,
                "max": max,
                "step": step,
                "on_change": on_change,
            }
        )
        return FakeElement(self, "number", (label,))

    def input(
        self,
        *,
        label: str,
        value: str,
        on_change: Callable[..., object] | None = None,
    ) -> FakeElement:
        """Record an input element."""
        self.inputs.append({"label": label, "value": value, "on_change": on_change})
        return FakeElement(self, "input", (label,))

    def switch(
        self,
        text: str,
        *,
        value: bool,
        on_change: Callable[..., object] | None = None,
    ) -> FakeElement:
        """Record a switch element."""
        self.switches.append({"text": text, "value": value, "on_change": on_change})
        return FakeElement(self, "switch", (text,))

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

    for module_name in UI_MODULE_NAMES:
        sys.modules.pop(module_name, None)

    yield ui

    for module_name in UI_MODULE_NAMES:
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
    assert fake_ui.images == [module.PAGE_IMAGE_STATIC_URL]
    assert "Example App" in fake_ui.labels
    assert "Started from tests." in fake_ui.labels
    assert "Application shell" in fake_ui.labels
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


def test_build_sub_page_routes_returns_registered_template_routes(
    fake_ui: FakeUi,
) -> None:
    """The sub-page route table binds all template pages."""
    module = importlib.import_module("desktop_app.ui.pages.routes")

    routes = module.build_sub_page_routes(
        application_name="Example App",
        startup_message="Started.",
    )

    assert set(routes) == {
        "/",
        "/components",
        "/diagnostics",
        "/logs",
        "/status",
        "/settings",
        "/{_:path}",
    }
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
    assert fake_ui.query_selectors == ["body"]
    assert fake_ui.links[:6] == [
        ("Home", "/"),
        ("Components", "/components"),
        ("Diagnostics", "/diagnostics"),
        ("Logs", "/logs"),
        ("Status", "/status"),
        ("Settings", "/settings"),
    ]
    assert fake_ui.sub_page_routes == expected_routes


def test_register_spa_routes_registers_root_and_catch_all_pages(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The SPA router registers both entry routes and builds the shell."""
    module = cast(Any, importlib.import_module("desktop_app.ui.router"))
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


def test_register_static_asset_routes_skips_when_nicegui_app_is_unavailable(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Static routes are skipped when only the UI fake is available."""
    module = cast(Any, importlib.import_module("desktop_app.ui.router"))

    module._static_asset_routes_registered = False
    monkeypatch.setitem(sys.modules, "nicegui", SimpleNamespace(ui=fake_ui))

    module._register_static_asset_routes()

    assert module._static_asset_routes_registered is False
    assert fake_ui.app.static_files == []
    assert fake_ui.app.get_routes == []


def test_register_static_asset_routes_registers_assets_and_favicon_once(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Static assets and favicon routes are registered once."""
    module = cast(Any, importlib.import_module("desktop_app.ui.router"))

    module._static_asset_routes_registered = False
    monkeypatch.setitem(
        sys.modules,
        "nicegui",
        SimpleNamespace(ui=fake_ui, app=fake_ui.app),
    )
    monkeypatch.setattr(module, "get_assets_directory_path", lambda: r"C:\app\assets")
    monkeypatch.setattr(module, "get_application_icon_path", lambda: r"C:\app\icon.ico")

    module._register_static_asset_routes()
    module._register_static_asset_routes()

    assert module._static_asset_routes_registered is True
    assert fake_ui.app.static_files == [("/assets", r"C:\app\assets")]
    assert fake_ui.app.get_routes == [("/favicon.ico", False)]
    assert len(fake_ui.app.get_callbacks) == 1


def test_registered_favicon_route_returns_file_response(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The registered favicon route returns a FileResponse for the app icon."""
    module = cast(Any, importlib.import_module("desktop_app.ui.router"))

    module._static_asset_routes_registered = False
    monkeypatch.setitem(
        sys.modules,
        "nicegui",
        SimpleNamespace(ui=fake_ui, app=fake_ui.app),
    )
    monkeypatch.setattr(module, "get_assets_directory_path", lambda: r"C:\app\assets")
    monkeypatch.setattr(module, "get_application_icon_path", lambda: r"C:\app\icon.ico")

    module._register_static_asset_routes()

    response = cast(Any, fake_ui.app.get_callbacks[0]())

    assert response.path == r"C:\app\icon.ico"


def test_build_components_page_renders_catalog(fake_ui: FakeUi) -> None:
    """The component catalog renders reusable examples."""
    module = importlib.import_module("desktop_app.ui.pages.components")

    module.build_components_page()

    assert get_app_state().ui_session.active_view == "components"
    assert "Component catalog" in fake_ui.labels
    assert "Status badges" in fake_ui.labels
    assert "Empty state" in fake_ui.labels


def test_build_diagnostics_page_renders_state_rows(fake_ui: FakeUi) -> None:
    """The diagnostics page renders current state details."""
    module = importlib.import_module("desktop_app.ui.pages.diagnostics")
    state = get_app_state()
    state.runtime.startup_source = "tests"
    state.runtime.port = 8765
    state.lifecycle.handlers_registered = True

    module.build_diagnostics_page()

    assert state.ui_session.active_view == "diagnostics"
    assert "Runtime diagnostics" in fake_ui.labels
    assert "tests" in fake_ui.labels
    assert "8765" in fake_ui.labels
    assert "Handlers registered" in fake_ui.labels


def test_build_logs_page_renders_log_content(
    fake_ui: FakeUi,
    tmp_path: Path,
) -> None:
    """The logs page displays the resolved log file tail."""
    module = importlib.import_module("desktop_app.ui.pages.logs")
    log_file = tmp_path / "app.log"
    log_file.write_text("first\nsecond\n", encoding="utf-8")
    state = get_app_state()
    state.log.effective_file_path = log_file

    module.build_logs_page()

    assert state.ui_session.active_view == "logs"
    assert "Runtime logs" in fake_ui.labels
    assert "Log file found" in fake_ui.labels
    assert "Limit: 120 lines" in fake_ui.labels
    assert fake_ui.codes == ["first\nsecond"]


def test_build_status_page_renders_current_status_and_history(
    fake_ui: FakeUi,
) -> None:
    """The status page renders the current status and recent history."""
    module = importlib.import_module("desktop_app.ui.pages.status")
    state = get_app_state()
    state.status.push("First message", "info")
    state.status.push("Second message", "success")

    module.build_status_page()

    assert state.ui_session.active_view == "status"
    assert "Application status" in fake_ui.labels
    assert "Second message" in fake_ui.labels
    assert "First message" in fake_ui.labels
    assert "Success" in fake_ui.labels


def test_build_settings_page_renders_controls(fake_ui: FakeUi) -> None:
    """The settings page renders reusable preference controls."""
    module = importlib.import_module("desktop_app.ui.pages.settings")
    state = get_app_state()
    state.settings.last_load_ok = True

    module.build_settings_page()

    assert state.ui_session.active_view == "settings"
    assert "Settings" in fake_ui.labels
    assert fake_ui.selects[0]["label"] == "Theme"
    assert fake_ui.numbers[0]["label"] == "Font scale"
    assert fake_ui.inputs[0]["label"] == "Accent color"
    assert fake_ui.switches[0]["text"] == "Dense mode"
    assert fake_ui.switches[1]["text"] == "Auto-save settings"
    assert "Settings file loaded" in fake_ui.labels


def test_page_helpers_render_without_optional_text(fake_ui: FakeUi) -> None:
    """Page helpers handle optional eyebrow and description text."""
    module = importlib.import_module("desktop_app.ui.components.page")

    module.build_page_header(
        title="Plain page",
        description="Description only.",
        theme="light",
    )
    module.build_section_header(
        title="Section without description",
        description=None,
        theme="light",
    )

    assert "Plain page" in fake_ui.labels
    assert "Description only." in fake_ui.labels
    assert "Section without description" in fake_ui.labels


def test_build_logs_page_renders_read_error(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The logs page renders recoverable log read errors."""
    module = importlib.import_module("desktop_app.ui.pages.logs")
    log_reader_module = importlib.import_module("desktop_app.application.log_reader")
    snapshot_type = log_reader_module.LogSnapshot

    monkeypatch.setattr(
        module,
        "read_log_snapshot",
        lambda *, state: snapshot_type(
            path=Path("logs/app.log"),
            exists=True,
            max_lines=120,
            lines=(),
            error="Could not read log file: permission denied",
        ),
    )

    module.build_logs_page()

    assert "Log file could not be read" in fake_ui.labels
    assert "Could not read log file: permission denied" in fake_ui.labels


def test_build_logs_page_renders_empty_state(
    fake_ui: FakeUi,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The logs page renders an empty state when no lines are available."""
    module = importlib.import_module("desktop_app.ui.pages.logs")
    log_reader_module = importlib.import_module("desktop_app.application.log_reader")
    snapshot_type = log_reader_module.LogSnapshot

    monkeypatch.setattr(
        module,
        "read_log_snapshot",
        lambda *, state: snapshot_type(
            path=None,
            exists=False,
            max_lines=120,
            lines=(),
        ),
    )

    module.build_logs_page()

    assert "Log file unavailable" in fake_ui.labels
    assert "Log file is not available." in fake_ui.labels
    assert "No log entries available" in fake_ui.labels


def test_build_status_page_renders_empty_states(fake_ui: FakeUi) -> None:
    """The status page renders empty states when no messages exist."""
    module = importlib.import_module("desktop_app.ui.pages.status")

    module.build_status_page()

    assert "No current status" in fake_ui.labels
    assert "No status history" in fake_ui.labels


def test_settings_event_value_helper_uses_default(fake_ui: FakeUi) -> None:
    """Settings event helper falls back when an event has no value."""
    module = importlib.import_module("desktop_app.ui.pages.settings")

    assert module._get_event_value(object(), "fallback") == "fallback"
    event = SimpleNamespace(value="custom")

    assert module._get_event_value(event, "fallback") == "custom"
