"""Test native window state package structure and packaging metadata."""

from __future__ import annotations

import tomllib
from pathlib import Path

NATIVE_WINDOW_STATE_PACKAGE_PATH = Path(
    "src/desktop_app/infrastructure/native_window_state"
)


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
    assert "pytest tests/infrastructure/test_native_window_state_package.py" in guide_text
