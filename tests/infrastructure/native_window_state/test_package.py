"""Test native window state package structure and packaging metadata."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

NATIVE_WINDOW_STATE_PACKAGE_PATH = Path(
    "src/desktop_app/infrastructure/native_window_state"
)
NATIVE_WINDOW_STATE_TEST_PATH = Path("tests/infrastructure/native_window_state")


def test_native_window_state_is_a_package() -> None:
    """Ensure native window state internals are organized as a package."""
    expected_files = {
        "__init__.py",
        "arguments.py",
        "assignment.py",
        "bridge.py",
        "defaults.py",
        "events.py",
        "geometry.py",
        "models.py",
        "persistence.py",
        "README.md",
        "service.py",
    }

    assert NATIVE_WINDOW_STATE_PACKAGE_PATH.is_dir()
    assert not Path("src/desktop_app/infrastructure/native_window_state.py").exists()
    assert expected_files.issubset(
        {path.name for path in NATIVE_WINDOW_STATE_PACKAGE_PATH.iterdir()}
    )


def test_native_window_state_tests_follow_package_layout() -> None:
    """Ensure native window tests mirror the source package structure."""
    expected_test_files = {
        "conftest.py",
        "test_arguments.py",
        "test_events.py",
        "test_geometry.py",
        "test_package.py",
        "test_persistence.py",
        "test_service.py",
    }

    assert NATIVE_WINDOW_STATE_TEST_PATH.is_dir()
    assert not Path("tests/infrastructure/test_native_window_state.py").exists()
    assert not Path("tests/infrastructure/test_native_window_state_package.py").exists()
    assert expected_test_files.issubset(
        {path.name for path in NATIVE_WINDOW_STATE_TEST_PATH.iterdir()}
    )


def test_native_window_state_package_guide_is_bundled_as_package_data() -> None:
    """Ensure the package-local native window guide is included in builds."""
    pyproject_data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject_data["tool"]["setuptools"]["package-data"]

    assert "infrastructure/native_window_state/*.md" in package_data["desktop_app"]
    assert (NATIVE_WINDOW_STATE_PACKAGE_PATH / "README.md").is_file()


def test_native_window_persistence_guide_lives_inside_package() -> None:
    """Ensure detailed native window documentation stays package-local."""
    package_guide = NATIVE_WINDOW_STATE_PACKAGE_PATH / "README.md"
    guide_text = package_guide.read_text(encoding="utf-8")

    assert not Path("docs/native_window_persistence.md").exists()
    assert "## 🖥️ Multi-monitor safety" in guide_text
    assert "## 💾 Save behavior" in guide_text
    assert "pytest tests/infrastructure/native_window_state" in guide_text


def test_native_window_state_package_exports_only_public_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure old single-module compatibility helpers are not package API."""
    fake_native = SimpleNamespace(main_window=None, window_args={})
    fake_nicegui_module = SimpleNamespace(app=SimpleNamespace(native=fake_native))

    for module_name in tuple(sys.modules):
        if module_name == "desktop_app.infrastructure.native_window_state" or (
            module_name.startswith("desktop_app.infrastructure.native_window_state.")
        ):
            sys.modules.pop(module_name, None)

    monkeypatch.setitem(sys.modules, "nicegui", fake_nicegui_module)

    import desktop_app.infrastructure.native_window_state as native_window_state

    assert native_window_state.__all__ == [
        "apply_initial_native_window_options",
        "apply_native_window_args_from_state",
        "normalize_persisted_window_geometry",
        "persist_native_window_state_on_exit",
        "refresh_native_window_state_from_proxy",
        "update_native_window_position",
        "update_native_window_size",
        "update_native_window_state",
    ]

    removed_compatibility_names = (
        "_clamp_axis_position",
        "_coerce_optional_int",
        "_get_native_window_args",
        "_get_windows_monitor_work_areas",
        "_request_native_window_pair",
        "_save_native_window_group",
        "MonitorWorkArea",
        "app",
    )

    for name in removed_compatibility_names:
        assert not hasattr(native_window_state, name)
