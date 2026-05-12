# -----------------------------------------------------------------------------
# File: tests/infrastructure/test_native_window_state.py
# Purpose:
# Validate native window state capture, restoration, and persistence helpers.
# Behavior:
# Uses fake window objects and monkeypatched settings persistence so tests can
# exercise geometry handling without opening a real NiceGUI native window.
# Notes:
# These tests keep native integration behavior deterministic and avoid real file
# writes unless persistence is explicitly monkeypatched by a test.
# -----------------------------------------------------------------------------

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from desktop_app.core.state import AppState, reset_app_state


@dataclass(slots=True)
class FakeWindow:
    """Represent the subset of pywebview window API used by the app."""

    x: int = 10
    y: int = 20
    width: int = 1200
    height: int = 800
    moves: list[tuple[int, int]] = field(default_factory=list)
    resizes: list[tuple[int, int]] = field(default_factory=list)
    show_calls: int = 0
    maximize_calls: int = 0

    def move(self, x: int, y: int) -> None:
        """Record a native move request."""
        self.moves.append((x, y))
        self.x = x
        self.y = y

    def resize(self, width: int, height: int) -> None:
        """Record a native resize request."""
        self.resizes.append((width, height))
        self.width = width
        self.height = height

    def show(self) -> None:
        """Record a native show request."""
        self.show_calls += 1

    def maximize(self) -> None:
        """Record a native maximize request."""
        self.maximize_calls += 1


@pytest.fixture()
def native_window_state_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load native_window_state.py with a fake NiceGUI app object."""
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui_module = SimpleNamespace(app=SimpleNamespace(native=fake_native))

    reset_app_state()
    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)
    sys.modules.pop("desktop_app.infrastructure.native_window_state", None)

    module = importlib.import_module("desktop_app.infrastructure.native_window_state")

    yield module

    sys.modules.pop("desktop_app.infrastructure.native_window_state", None)
    reset_app_state()


def test_apply_initial_native_window_options_uses_persisted_geometry(
    native_window_state_module: ModuleType,
) -> None:
    """Native run options and window args receive persisted geometry."""
    state = AppState()
    state.window.x = 30
    state.window.y = 40
    state.window.width = 1440
    state.window.height = 900
    state.window.fullscreen = True
    options: dict[str, Any] = {}

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert options == {}
    assert native_window_state_module.app.native.window_args == {
        "width": 1440,
        "height": 900,
        "fullscreen": True,
        "x": 30,
        "y": 40,
    }


def test_apply_native_window_args_from_state_can_run_before_main(
    native_window_state_module: ModuleType,
) -> None:
    """Native window args can be prepared without building ui.run options."""
    state = AppState()
    state.window.x = 700
    state.window.y = 500
    state.window.width = 1366
    state.window.height = 768

    native_window_state_module.apply_native_window_args_from_state(state=state)

    assert native_window_state_module.app.native.window_args == {
        "width": 1366,
        "height": 768,
        "fullscreen": False,
        "x": 700,
        "y": 500,
    }


def test_apply_initial_native_window_options_omits_position_when_disabled(
    native_window_state_module: ModuleType,
) -> None:
    """Window position is not forced when persistence is disabled."""
    state = AppState()
    state.window.persist_state = False
    options: dict[str, Any] = {}

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert options == {}
    assert native_window_state_module.app.native.window_args == {
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }


def test_apply_initial_native_window_options_clears_stale_position_when_disabled(
    native_window_state_module: ModuleType,
) -> None:
    """Disabled persistence removes stale native position arguments."""
    state = AppState()
    state.window.persist_state = False
    options: dict[str, Any] = {}
    native_window_state_module.app.native.window_args.update(
        {"x": 500, "y": 600, "min_size": (400, 300)}
    )

    native_window_state_module.apply_initial_native_window_options(
        options,
        state=state,
    )

    assert native_window_state_module.app.native.window_args == {
        "min_size": (400, 300),
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }


def test_update_native_window_size_uses_resize_payload(
    native_window_state_module: ModuleType,
) -> None:
    """Resize event width and height payloads update AppState."""
    state = AppState()

    updated = native_window_state_module.update_native_window_size(
        1366,
        768,
        state=state,
    )

    assert updated is True
    assert state.window.width == 1366
    assert state.window.height == 768


def test_update_native_window_position_uses_move_payload(
    native_window_state_module: ModuleType,
) -> None:
    """Move event x and y payloads update AppState."""
    state = AppState()

    updated = native_window_state_module.update_native_window_position(
        44,
        88,
        state=state,
    )

    assert updated is True
    assert state.window.x == 44
    assert state.window.y == 88


def test_update_native_window_state_uses_event_window(
    native_window_state_module: ModuleType,
) -> None:
    """Window lifecycle event arguments update AppState geometry."""
    state = AppState()
    window = FakeWindow(x=55, y=66, width=1300, height=760)

    updated = native_window_state_module.update_native_window_state(window, state=state)

    assert updated is True
    assert state.window.x == 55
    assert state.window.y == 66
    assert state.window.width == 1300
    assert state.window.height == 760


def test_update_native_window_state_falls_back_to_main_window(
    native_window_state_module: ModuleType,
) -> None:
    """The current NiceGUI main window is used when event args are empty."""
    state = AppState()
    native_window_state_module.app.native.main_window = FakeWindow(
        x=70,
        y=80,
        width=1100,
        height=700,
    )

    updated = native_window_state_module.update_native_window_state(state=state)

    assert updated is True
    assert state.window.x == 70
    assert state.window.y == 80
    assert state.window.width == 1100
    assert state.window.height == 700


def test_update_native_window_state_ignores_invalid_or_small_values(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid geometry values do not overwrite safe defaults."""
    state = AppState()
    window = SimpleNamespace(x="bad", y=25, width=200, height=100)

    updated = native_window_state_module.update_native_window_state(window, state=state)

    assert updated is True
    assert state.window.x == 100
    assert state.window.y == 25
    assert state.window.width == 1024
    assert state.window.height == 720


def test_native_window_event_helpers_do_not_persist_settings(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Move and resize helpers update state without writing settings."""
    state = AppState()
    save_calls = 0

    def fail_if_saved(*_args: object, **_kwargs: object) -> bool:
        """Fail the test when event helpers unexpectedly write settings."""
        nonlocal save_calls
        save_calls += 1
        return False

    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        fail_if_saved,
    )

    size_updated = native_window_state_module.update_native_window_size(
        1280, 720, state=state
    )
    position_updated = native_window_state_module.update_native_window_position(
        300, 250, state=state
    )

    assert size_updated is True
    assert position_updated is True
    assert state.window.width == 1280
    assert state.window.height == 720
    assert state.window.x == 300
    assert state.window.y == 250
    assert state.window.last_saved_at is None
    assert save_calls == 0


def test_persist_native_window_state_on_exit_skips_when_disabled(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disabled persistence does not write settings on exit."""
    state = AppState()
    state.window.persist_state = False
    save_calls = 0

    def fail_if_saved(*_args: object, **_kwargs: object) -> bool:
        """Fail the test when persistence unexpectedly writes settings."""
        nonlocal save_calls
        save_calls += 1
        return False

    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        fail_if_saved,
    )

    result = native_window_state_module.persist_native_window_state_on_exit(
        FakeWindow(),
        state=state,
    )

    assert result is True
    assert save_calls == 0
    assert state.window.last_saved_at is None


def test_persist_native_window_state_on_exit_saves_window_group(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Enabled persistence captures geometry and saves only the window group."""
    state = AppState()
    calls: list[tuple[str, AppState]] = []

    def save_group(group: str, *, state: AppState) -> bool:
        """Capture the requested settings group."""
        calls.append((group, state))
        return True

    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        save_group,
    )

    result = native_window_state_module.persist_native_window_state_on_exit(
        FakeWindow(x=15, y=25, width=1500, height=900),
        state=state,
    )

    assert result is True
    assert calls == [("window", state)]
    assert state.window.x == 15
    assert state.window.y == 25
    assert state.window.width == 1500
    assert state.window.height == 900
    assert state.window.last_saved_at is not None


def test_update_native_window_size_uses_nicegui_native_event_arguments(
    native_window_state_module: ModuleType,
) -> None:
    """NiceGUI NativeEventArguments resize payload updates AppState."""
    state = AppState()
    event_args = SimpleNamespace(args={"width": 1555, "height": 944})

    updated = native_window_state_module.update_native_window_size(
        event_args,
        state=state,
    )

    assert updated is True
    assert state.window.width == 1555
    assert state.window.height == 944


def test_update_native_window_position_uses_nicegui_native_event_arguments(
    native_window_state_module: ModuleType,
) -> None:
    """NiceGUI NativeEventArguments move payload updates AppState."""
    state = AppState()
    event_args = SimpleNamespace(args={"x": 321, "y": 654})

    updated = native_window_state_module.update_native_window_position(
        event_args,
        state=state,
    )

    assert updated is True
    assert state.window.x == 321
    assert state.window.y == 654


def test_normalize_persisted_window_geometry_clamps_position_after_monitor_change(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted coordinates beyond the current screen are clamped."""
    state = AppState()
    state.window.x = 1400
    state.window.y = 900
    state.window.width = 500
    state.window.height = 400
    save_calls: list[tuple[str, AppState]] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append((group, state)) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.y == 720
    assert state.window.width == 500
    assert state.window.height == 400
    assert state.window.last_saved_at is not None
    assert save_calls == [("window", state)]


def test_normalize_persisted_window_geometry_recovers_window_hidden_left_or_top(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted coordinates that hide the window before the screen are fixed."""
    state = AppState()
    state.window.x = -800
    state.window.y = -600
    state.window.width = 500
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 0
    assert state.window.y == 0
    assert save_calls == ["window"]


def test_apply_native_window_args_resets_geometry_when_persistence_is_disabled(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Disabled persistence clears stale saved geometry and uses defaults."""
    state = AppState()
    state.window.persist_state = False
    state.window.x = 1600
    state.window.y = 900
    state.window.width = 300
    state.window.height = 200
    state.window.maximized = True
    state.window.fullscreen = True
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    native_window_state_module.apply_native_window_args_from_state(state=state)

    assert state.window.x == 100
    assert state.window.y == 100
    assert state.window.width == 1024
    assert state.window.height == 720
    assert state.window.maximized is False
    assert state.window.fullscreen is False
    assert state.window.persist_state is False
    assert state.window.last_saved_at is not None
    assert native_window_state_module.app.native.window_args == {
        "width": 1024,
        "height": 720,
        "fullscreen": False,
    }
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_keeps_valid_secondary_monitor_position(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valid coordinates on a secondary monitor are not clamped to primary."""
    state = AppState()
    state.window.x = 2100
    state.window.y = 120
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.MonitorWorkArea(0, 0, 1920, 1040),
            native_window_state_module.MonitorWorkArea(1920, 0, 3840, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is False
    assert state.window.x == 2100
    assert state.window.y == 120
    assert save_calls == []


def test_normalize_persisted_window_geometry_clamps_against_selected_monitor(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Out-of-range coordinates are clamped inside the nearest monitor."""
    state = AppState()
    state.window.x = 3900
    state.window.y = 1200
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.MonitorWorkArea(0, 0, 1920, 1040),
            native_window_state_module.MonitorWorkArea(1920, 0, 3840, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 3648
    assert state.window.y == 936
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_supports_negative_monitor_coordinates(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordinates on a left-side monitor remain valid when visible there."""
    state = AppState()
    state.window.x = -1700
    state.window.y = 100
    state.window.width = 600
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (
            native_window_state_module.MonitorWorkArea(-1920, 0, 0, 1040),
            native_window_state_module.MonitorWorkArea(0, 0, 1920, 1040),
        ),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is False
    assert state.window.x == -1700
    assert state.window.y == 100
    assert save_calls == []


def test_normalize_persisted_window_geometry_limits_start_position_after_90_percent(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordinates after 90 percent of a work area are limited without resizing."""
    state = AppState()
    state.window.x = 800
    state.window.y = 767
    state.window.width = 400
    state.window.height = 400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 800
    assert state.window.y == 720
    assert state.window.width == 400
    assert state.window.height == 400
    assert save_calls == ["window"]


def test_normalize_persisted_window_geometry_synchronizes_native_args(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrected geometry is applied to current native args immediately."""
    state = AppState()
    state.window.x = 800
    state.window.y = 767
    state.window.width = 400
    state.window.height = 400

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda _group, *, state: True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert native_window_state_module.app.native.window_args == {
        "width": 400,
        "height": 400,
        "fullscreen": False,
        "x": 800,
        "y": 720,
    }


def test_normalize_persisted_window_geometry_preserves_oversized_window_dimensions(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Monitor visibility correction does not reduce saved width or height."""
    state = AppState()
    state.window.x = 1400
    state.window.y = 900
    state.window.width = 2500
    state.window.height = 1400
    save_calls: list[str] = []

    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda group, *, state: save_calls.append(group) or True,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.y == 720
    assert state.window.width == 2500
    assert state.window.height == 1400
    assert save_calls == ["window"]


class AssignableCallable:
    """Wrap a callable while allowing ctypes-style attributes."""

    def __init__(self, implementation: Any) -> None:
        """Store the wrapped implementation."""
        self._implementation = implementation

    def __call__(self, *args: object) -> object:
        """Delegate the call to the wrapped implementation."""
        return self._implementation(*args)


class AsyncNativeWindowProxy:
    """Expose async NiceGUI native window geometry methods for tests."""

    def __init__(
        self,
        *,
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Store geometry values returned by async methods."""
        self._position = position
        self._size = size

    async def get_position(self) -> tuple[int, int] | None:
        """Return the configured native window position."""
        return self._position

    async def get_size(self) -> tuple[int, int] | None:
        """Return the configured native window size."""
        return self._size


class BrokenNativeWindowProxy:
    """Expose a native window method that raises during geometry refresh."""

    def get_position(self) -> tuple[int, int]:
        """Raise to simulate a failing native proxy call."""
        raise RuntimeError("native proxy failed")


def _install_fake_win32_monitor_api(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    *,
    work_areas: dict[int, tuple[int, int, int, int]] | None = None,
    enum_result: int = 1,
    enum_raises: bool = False,
) -> None:
    """Install a fake Win32 monitor API on the module's ctypes object."""
    selected_work_areas = work_areas or {1: (0, 0, 1000, 800)}

    def winfunctype_factory(*_args: object) -> Any:
        """Return a callback adapter matching ctypes.WINFUNCTYPE."""
        return lambda callback: callback

    def get_monitor_info(monitor_handle: int, monitor_info_pointer: object) -> int:
        """Populate monitor information for one fake monitor handle."""
        if monitor_handle not in selected_work_areas:
            return 0

        monitor_info = monitor_info_pointer._obj
        left, top, right, bottom = selected_work_areas[monitor_handle]
        monitor_info.rcWork.left = left
        monitor_info.rcWork.top = top
        monitor_info.rcWork.right = right
        monitor_info.rcWork.bottom = bottom
        return 1

    def enum_display_monitors(
        _hdc: object,
        _clip_rect: object,
        callback: Any,
        _data: object,
    ) -> int:
        """Invoke the callback for all configured fake monitor handles."""
        if enum_raises:
            raise OSError("monitor enumeration failed")

        for monitor_handle in selected_work_areas:
            callback(monitor_handle, 0, None, 0)
        return enum_result

    fake_user32 = SimpleNamespace(
        GetMonitorInfoW=AssignableCallable(get_monitor_info),
        EnumDisplayMonitors=AssignableCallable(enum_display_monitors),
    )
    fake_windll = SimpleNamespace(user32=fake_user32)

    monkeypatch.setattr(
        native_window_state_module.ctypes,
        "WINFUNCTYPE",
        winfunctype_factory,
        raising=False,
    )
    monkeypatch.setattr(
        native_window_state_module.ctypes,
        "windll",
        fake_windll,
        raising=False,
    )


def test_update_native_window_state_returns_false_without_window(
    native_window_state_module: ModuleType,
) -> None:
    """State refresh reports no update when no native window is available."""
    state = AppState()

    updated = native_window_state_module.update_native_window_state(
        object(),
        state=state,
    )

    assert updated is False


def test_persist_native_window_state_on_exit_reports_save_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failed native window persistence is reported as False."""
    state = AppState()
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda _group, *, state: False,
    )

    saved = native_window_state_module.persist_native_window_state_on_exit(
        FakeWindow(),
        state=state,
    )

    assert saved is False
    assert state.window.last_saved_at is not None


def test_normalize_persisted_window_geometry_reports_save_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Normalization still reports changed in memory when save fails."""
    state = AppState()
    state.window.x = 1200
    monkeypatch.setattr(
        native_window_state_module,
        "_get_windows_monitor_work_areas",
        lambda: (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),),
    )
    monkeypatch.setattr(
        native_window_state_module,
        "save_settings_group",
        lambda _group, *, state: False,
    )

    changed = native_window_state_module.normalize_persisted_window_geometry(
        state=state,
    )

    assert changed is True
    assert state.window.x == 900
    assert state.window.last_saved_at is not None


def test_clamp_axis_position_ignores_invalid_available_size(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid monitor axis sizes leave the persisted coordinate unchanged."""
    assert (
        native_window_state_module._clamp_axis_position(
            position=42,
            size=100,
            available_start=0,
            available_size=0,
        )
        == 42
    )


def test_get_native_window_args_creates_missing_dict(
    native_window_state_module: ModuleType,
) -> None:
    """Native window args are initialized when NiceGUI exposes no dictionary."""
    native_window_state_module.app.native.window_args = None

    window_args = native_window_state_module._get_native_window_args()

    assert window_args == {}
    assert native_window_state_module.app.native.window_args is window_args


def test_extract_pair_by_keys_skips_invalid_payload_before_valid_payload(
    native_window_state_module: ModuleType,
) -> None:
    """NativeEventArguments extraction continues until it finds a valid pair."""
    first = SimpleNamespace(args={"width": "bad", "height": 500})
    second = SimpleNamespace(args={"width": "640", "height": 480.5})

    assert native_window_state_module._extract_pair_by_keys(
        (first, second),
        "width",
        "height",
    ) == (640, 480)


def test_extract_pair_uses_nested_args_pair(
    native_window_state_module: ModuleType,
) -> None:
    """Pair extraction supports event objects whose args value is a pair."""
    event_args = SimpleNamespace(args=(111, 222))

    assert native_window_state_module._extract_pair((event_args,)) == (111, 222)


@pytest.mark.parametrize("raw_value", [True, None, "", "abc"])
def test_coerce_optional_int_rejects_invalid_values(
    native_window_state_module: ModuleType,
    raw_value: object,
) -> None:
    """Invalid geometry scalars are rejected instead of coerced."""
    assert native_window_state_module._coerce_optional_int(raw_value) is None


def test_coerce_pair_rejects_wrong_lengths(
    native_window_state_module: ModuleType,
) -> None:
    """Geometry pair coercion rejects one-item and three-item iterables."""
    assert native_window_state_module._coerce_pair((1,)) is None
    assert native_window_state_module._coerce_pair((1, 2, 3)) is None


def test_read_int_attribute_logs_ignored_invalid_attribute(
    native_window_state_module: ModuleType,
) -> None:
    """Invalid native window attributes are skipped until a valid one is found."""
    value = SimpleNamespace(x="bad", left="25")

    assert native_window_state_module._read_int_attribute(value, ("x", "left")) == 25


def test_refresh_native_window_state_from_proxy_returns_false_without_window(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh is skipped safely when no native main window exists."""
    import asyncio

    state = AppState()
    native_window_state_module.app.native.main_window = None

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is False


def test_refresh_native_window_state_from_proxy_updates_complete_geometry(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh updates position and size returned by async methods."""
    import asyncio

    state = AppState()
    native_window_state_module.app.native.main_window = AsyncNativeWindowProxy(
        position=(333, 444),
        size=(1280, 720),
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 333
    assert state.window.y == 444
    assert state.window.width == 1280
    assert state.window.height == 720


def test_refresh_native_window_state_from_proxy_ignores_small_size(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh ignores width and height below supported minimums."""
    import asyncio

    state = AppState()
    native_window_state_module.app.native.main_window = AsyncNativeWindowProxy(
        position=(100, 100),
        size=(100, 100),
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is False
    assert state.window.width == 1024
    assert state.window.height == 720


def test_request_native_window_pair_returns_none_when_method_is_missing(
    native_window_state_module: ModuleType,
) -> None:
    """Missing proxy methods are reported as unavailable geometry."""
    import asyncio

    result = asyncio.run(
        native_window_state_module._request_native_window_pair(object(), "missing")
    )

    assert result is None


def test_request_native_window_pair_returns_none_when_method_fails(
    native_window_state_module: ModuleType,
) -> None:
    """Failing native proxy methods do not raise into lifecycle handlers."""
    import asyncio

    result = asyncio.run(
        native_window_state_module._request_native_window_pair(
            BrokenNativeWindowProxy(),
            "get_position",
        )
    )

    assert result is None


def test_get_windows_monitor_work_areas_reads_win32_work_areas(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Windows monitor enumeration returns valid work areas."""
    _install_fake_win32_monitor_api(
        native_window_state_module,
        monkeypatch,
        work_areas={1: (0, 0, 1000, 800), 2: (1920, 0, 3840, 1040)},
    )

    work_areas = native_window_state_module._get_windows_monitor_work_areas()

    assert work_areas == (
        native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),
        native_window_state_module.MonitorWorkArea(1920, 0, 3840, 1040),
    )


def test_get_windows_monitor_work_areas_skips_monitor_info_failures(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Monitor handles without work area data are ignored."""
    _install_fake_win32_monitor_api(
        native_window_state_module,
        monkeypatch,
        work_areas={1: (0, 0, 1000, 800), 2: (0, 0, 0, 0)},
    )

    work_areas = native_window_state_module._get_windows_monitor_work_areas()

    assert work_areas == (native_window_state_module.MonitorWorkArea(0, 0, 1000, 800),)


def test_get_windows_monitor_work_areas_returns_empty_on_enum_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed Win32 enumeration result is treated as unavailable monitors."""
    _install_fake_win32_monitor_api(
        native_window_state_module,
        monkeypatch,
        enum_result=0,
    )

    assert native_window_state_module._get_windows_monitor_work_areas() == ()


def test_get_windows_monitor_work_areas_returns_empty_on_enum_exception(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Win32 monitor API exceptions do not break application startup."""
    _install_fake_win32_monitor_api(
        native_window_state_module,
        monkeypatch,
        enum_raises=True,
    )

    assert native_window_state_module._get_windows_monitor_work_areas() == ()


class PartialAsyncNativeWindowProxy:
    """Expose optional async geometry values for branch-specific refresh tests."""

    def __init__(
        self,
        *,
        position: tuple[int, int] | None,
        size: tuple[int, int] | None,
    ) -> None:
        """Store optional geometry values."""
        self._position = position
        self._size = size

    async def get_position(self) -> tuple[int, int] | None:
        """Return the configured optional position."""
        return self._position

    async def get_size(self) -> tuple[int, int] | None:
        """Return the configured optional size."""
        return self._size


class SyncNativeWindowProxy:
    """Expose synchronous geometry methods accepted by the proxy helper."""

    def get_size(self) -> tuple[int, int]:
        """Return a synchronous native window size pair."""
        return 1440, 900


def test_refresh_native_window_state_from_proxy_updates_size_without_position(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh can update size when position is unavailable."""
    import asyncio

    state = AppState()
    native_window_state_module.app.native.main_window = PartialAsyncNativeWindowProxy(
        position=None,
        size=(1440, 900),
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 100
    assert state.window.y == 100
    assert state.window.width == 1440
    assert state.window.height == 900


def test_refresh_native_window_state_from_proxy_updates_position_without_size(
    native_window_state_module: ModuleType,
) -> None:
    """Proxy refresh can update position when size is unavailable."""
    import asyncio

    state = AppState()
    native_window_state_module.app.native.main_window = PartialAsyncNativeWindowProxy(
        position=(333, 444),
        size=None,
    )

    updated = asyncio.run(
        native_window_state_module.refresh_native_window_state_from_proxy(state=state)
    )

    assert updated is True
    assert state.window.x == 333
    assert state.window.y == 444
    assert state.window.width == 1024
    assert state.window.height == 720


def test_request_native_window_pair_accepts_synchronous_method_result(
    native_window_state_module: ModuleType,
) -> None:
    """Native proxy geometry methods may return a pair without awaiting."""
    import asyncio

    result = asyncio.run(
        native_window_state_module._request_native_window_pair(
            SyncNativeWindowProxy(),
            "get_size",
        )
    )

    assert result == (1440, 900)


def test_get_windows_monitor_work_areas_keeps_valid_monitors_after_info_failure(
    native_window_state_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A monitor info failure does not prevent later valid monitors from loading."""

    def winfunctype_factory(*_args: object) -> Any:
        """Return a callback adapter matching ctypes.WINFUNCTYPE."""
        return lambda callback: callback

    def get_monitor_info(monitor_handle: int, monitor_info_pointer: object) -> int:
        """Fail the first fake monitor and populate the second one."""
        if monitor_handle == 1:
            return 0

        monitor_info = monitor_info_pointer._obj
        monitor_info.rcWork.left = 10
        monitor_info.rcWork.top = 20
        monitor_info.rcWork.right = 1010
        monitor_info.rcWork.bottom = 820
        return 1

    def enum_display_monitors(
        _hdc: object,
        _clip_rect: object,
        callback: Any,
        _data: object,
    ) -> int:
        """Enumerate one failing monitor and one valid monitor."""
        callback(1, 0, None, 0)
        callback(2, 0, None, 0)
        return 1

    fake_user32 = SimpleNamespace(
        GetMonitorInfoW=AssignableCallable(get_monitor_info),
        EnumDisplayMonitors=AssignableCallable(enum_display_monitors),
    )

    monkeypatch.setattr(
        native_window_state_module.ctypes,
        "WINFUNCTYPE",
        winfunctype_factory,
        raising=False,
    )
    monkeypatch.setattr(
        native_window_state_module.ctypes,
        "windll",
        SimpleNamespace(user32=fake_user32),
        raising=False,
    )

    assert native_window_state_module._get_windows_monitor_work_areas() == (
        native_window_state_module.MonitorWorkArea(10, 20, 1010, 820),
    )
