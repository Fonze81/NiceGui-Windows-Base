# -----------------------------------------------------------------------------
# File: tests/infrastructure/settings/test_paths.py
# Purpose:
# Validate path resolution rules used by the settings subsystem.
# Behavior:
# Uses pytest monkeypatching to simulate environment variables, PyInstaller
# runtime markers, executable paths, and bundled template candidates.
# Notes:
# Tests avoid writing outside tmp_path and keep runtime state isolated.
# -----------------------------------------------------------------------------

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from desktop_app.infrastructure.settings import paths


def _return_false() -> bool:
    """Return False for monkeypatched runtime checks."""
    return False


def _return_true() -> bool:
    """Return True for monkeypatched runtime checks."""
    return True


@pytest.fixture(autouse=True)
def clear_settings_root_environment(monkeypatch: MonkeyPatch) -> None:
    """Clear the settings root environment variable before each test."""
    monkeypatch.delenv(paths.APP_ROOT_ENV_VAR, raising=False)


def test_resolve_settings_root_uses_configured_environment_root(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Use the configured settings root when the environment variable exists."""
    configured_root = tmp_path / "configured-settings-root"

    monkeypatch.setenv(paths.APP_ROOT_ENV_VAR, str(configured_root))
    monkeypatch.setattr(paths, "is_frozen_executable", _return_false)

    assert paths.resolve_settings_root() == configured_root.resolve()


def test_resolve_settings_root_uses_executable_parent_when_frozen(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Use the executable directory during PyInstaller execution."""
    executable_path = tmp_path / "dist" / "nicegui-windows-base.exe"

    monkeypatch.setattr(paths, "is_frozen_executable", _return_true)
    monkeypatch.setattr(sys, "executable", str(executable_path))

    assert paths.resolve_settings_root() == executable_path.resolve().parent


def test_resolve_settings_root_uses_current_working_directory(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Use the current working directory during normal Python execution."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(paths, "is_frozen_executable", _return_false)

    assert paths.resolve_settings_root() == tmp_path.resolve()


def test_resolve_settings_file_path_appends_settings_file_name(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Append the settings file name to the resolved settings root."""
    monkeypatch.setattr(paths, "resolve_settings_root", lambda: tmp_path)

    assert paths.resolve_settings_file_path() == tmp_path / paths.SETTINGS_FILE_NAME


def test_resolve_default_settings_path_keeps_compatibility(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Keep the previous public function name compatible."""
    expected_path = tmp_path / paths.SETTINGS_FILE_NAME

    monkeypatch.setattr(paths, "resolve_settings_file_path", lambda: expected_path)

    assert paths.resolve_default_settings_path() == expected_path


def test_resolve_pyinstaller_temp_dir_returns_none_when_marker_is_absent(
    monkeypatch: MonkeyPatch,
) -> None:
    """Return None when PyInstaller did not define the extraction marker."""
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    assert paths.resolve_pyinstaller_temp_dir() is None
    assert paths.get_pyinstaller_temp_dir() is None


def test_resolve_pyinstaller_temp_dir_returns_resolved_path(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return the resolved PyInstaller extraction directory."""
    pyinstaller_temp_dir = tmp_path / "pyinstaller-temp"

    monkeypatch.setattr(sys, "_MEIPASS", str(pyinstaller_temp_dir), raising=False)

    assert paths.resolve_pyinstaller_temp_dir() == pyinstaller_temp_dir.resolve()
    assert paths.get_pyinstaller_temp_dir() == pyinstaller_temp_dir.resolve()


def test_resolve_bundled_settings_candidate_paths_includes_pyinstaller_paths(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Include PyInstaller and development candidates when temp dir exists."""
    pyinstaller_temp_dir = tmp_path / "pyinstaller-temp"
    working_dir = tmp_path / "working-dir"
    package_root = Path(paths.__file__).resolve().parents[2]

    working_dir.mkdir()

    monkeypatch.chdir(working_dir)
    monkeypatch.setattr(
        paths,
        "resolve_pyinstaller_temp_dir",
        lambda: pyinstaller_temp_dir,
    )

    expected_candidate_paths = [
        pyinstaller_temp_dir / "desktop_app" / paths.SETTINGS_FILE_NAME,
        pyinstaller_temp_dir / paths.SETTINGS_FILE_NAME,
        package_root / paths.SETTINGS_FILE_NAME,
        working_dir / paths.SETTINGS_FILE_NAME,
    ]

    assert paths.resolve_bundled_settings_candidate_paths() == expected_candidate_paths
    assert paths.get_bundled_settings_candidate_paths() == expected_candidate_paths


def test_resolve_bundled_settings_candidate_paths_without_pyinstaller_paths(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return only development candidates when PyInstaller temp dir is absent."""
    package_root = Path(paths.__file__).resolve().parents[2]

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(paths, "resolve_pyinstaller_temp_dir", lambda: None)

    expected_candidate_paths = [
        package_root / paths.SETTINGS_FILE_NAME,
        tmp_path / paths.SETTINGS_FILE_NAME,
    ]

    assert paths.resolve_bundled_settings_candidate_paths() == expected_candidate_paths


def test_read_bundled_settings_template_text_returns_first_existing_file(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Read the first existing candidate file and ignore later candidates."""
    missing_template_path = tmp_path / "missing-settings.toml"
    first_template_path = tmp_path / "first-settings.toml"
    second_template_path = tmp_path / "second-settings.toml"

    first_template_path.write_text("app.name = 'First'\n", encoding="utf-8")
    second_template_path.write_text("app.name = 'Second'\n", encoding="utf-8")

    monkeypatch.setattr(
        paths,
        "resolve_bundled_settings_candidate_paths",
        lambda: [
            missing_template_path,
            first_template_path,
            second_template_path,
        ],
    )

    assert paths.read_bundled_settings_template_text() == "app.name = 'First'\n"


def test_read_bundled_settings_template_text_skips_directories(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Skip candidate directories and continue searching for a valid file."""
    directory_candidate_path = tmp_path / "settings-directory"
    file_candidate_path = tmp_path / "settings.toml"

    directory_candidate_path.mkdir()
    file_candidate_path.write_text("app.name = 'Fallback'\n", encoding="utf-8")

    monkeypatch.setattr(
        paths,
        "resolve_bundled_settings_candidate_paths",
        lambda: [
            directory_candidate_path,
            file_candidate_path,
        ],
    )

    assert paths.read_bundled_settings_template_text() == "app.name = 'Fallback'\n"


def test_read_bundled_settings_template_text_returns_none_without_file(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return None when no bundled settings candidate file exists."""
    missing_template_path = tmp_path / "missing-settings.toml"

    monkeypatch.setattr(
        paths,
        "resolve_bundled_settings_candidate_paths",
        lambda: [missing_template_path],
    )

    assert paths.read_bundled_settings_template_text() is None


def test_read_bundled_settings_text_keeps_compatibility(
    monkeypatch: MonkeyPatch,
) -> None:
    """Keep the previous bundled settings reader name compatible."""
    monkeypatch.setattr(
        paths,
        "read_bundled_settings_template_text",
        lambda: "app.name = 'Compatible'\n",
    )

    assert paths.read_bundled_settings_text() == "app.name = 'Compatible'\n"
