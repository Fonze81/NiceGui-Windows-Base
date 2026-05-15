# -----------------------------------------------------------------------------
# File: tests/infrastructure/test_asset_paths.py
# Purpose:
# Validate application asset path resolution.
# Behavior:
# Uses temporary directories and monkeypatching to simulate normal and packaged
# runtime modes without depending on real project assets or PyInstaller.
# Notes:
# These tests cover path building, missing-file warnings, icon lookup, and
# validation for unsafe asset filenames.
# -----------------------------------------------------------------------------

from pathlib import Path
from unittest.mock import Mock

import pytest

from desktop_app.constants import APP_ICON_FILENAME
from desktop_app.infrastructure import asset_paths


def test_resolve_asset_path_returns_local_asset_path_when_not_frozen(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resolve assets from the local assets directory in normal execution."""
    logger_mock = Mock()
    asset_file = tmp_path / "assets" / "page_image.png"
    asset_file.parent.mkdir()
    asset_file.touch()

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(asset_paths, "get_runtime_root", Mock(return_value=tmp_path))
    monkeypatch.setattr(asset_paths, "is_frozen_executable", Mock(return_value=False))

    resolved_path = asset_paths.resolve_asset_path("page_image.png")

    assert resolved_path == str(asset_file)
    logger_mock.debug.assert_called_once_with(
        "Asset path resolved for %s: %s",
        Path("page_image.png"),
        asset_file,
    )
    logger_mock.warning.assert_not_called()


def test_resolve_asset_path_returns_packaged_asset_path_when_frozen(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resolve assets from the bundled package directory in frozen execution."""
    logger_mock = Mock()
    asset_file = tmp_path / "desktop_app" / "assets" / "page_image.png"
    asset_file.parent.mkdir(parents=True)
    asset_file.touch()

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(asset_paths, "get_runtime_root", Mock(return_value=tmp_path))
    monkeypatch.setattr(asset_paths, "is_frozen_executable", Mock(return_value=True))

    resolved_path = asset_paths.resolve_asset_path("page_image.png")

    assert resolved_path == str(asset_file)
    logger_mock.debug.assert_called_once_with(
        "Asset path resolved for %s: %s",
        Path("page_image.png"),
        asset_file,
    )
    logger_mock.warning.assert_not_called()


def test_resolve_asset_path_logs_warning_when_asset_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Log a warning when the resolved asset path does not exist."""
    logger_mock = Mock()
    expected_path = tmp_path / "assets" / "missing.png"

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(asset_paths, "get_runtime_root", Mock(return_value=tmp_path))
    monkeypatch.setattr(asset_paths, "is_frozen_executable", Mock(return_value=False))

    resolved_path = asset_paths.resolve_asset_path("missing.png")

    assert resolved_path == str(expected_path)
    logger_mock.warning.assert_called_once_with(
        "Asset file is missing and may not render: %s",
        expected_path,
    )


def test_get_assets_directory_path_returns_local_assets_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resolve the local assets directory in normal execution."""
    logger_mock = Mock()
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(asset_paths, "get_runtime_root", Mock(return_value=tmp_path))
    monkeypatch.setattr(asset_paths, "is_frozen_executable", Mock(return_value=False))

    resolved_path = asset_paths.get_assets_directory_path()

    assert resolved_path == str(assets_dir)
    logger_mock.debug.assert_called_once_with(
        "Assets directory resolved: %s",
        assets_dir,
    )
    logger_mock.warning.assert_not_called()


def test_get_assets_directory_path_returns_packaged_directory_and_warns_when_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resolve the packaged assets directory and warn when it is missing."""
    logger_mock = Mock()
    assets_dir = tmp_path / "desktop_app" / "assets"

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(asset_paths, "get_runtime_root", Mock(return_value=tmp_path))
    monkeypatch.setattr(asset_paths, "is_frozen_executable", Mock(return_value=True))

    resolved_path = asset_paths.get_assets_directory_path()

    assert resolved_path == str(assets_dir)
    logger_mock.debug.assert_called_once_with(
        "Assets directory resolved: %s",
        assets_dir,
    )
    logger_mock.warning.assert_called_once_with(
        "Assets directory is missing and may not render: %s",
        assets_dir,
    )


def test_build_static_asset_url_returns_stable_asset_url() -> None:
    """Build a stable URL under the registered static assets route."""
    static_url = asset_paths.build_static_asset_url("page_image.png")

    assert static_url == "/assets/page_image.png"


def test_build_static_asset_url_supports_nested_relative_asset_paths() -> None:
    """Build a stable URL for nested assets using POSIX URL separators."""
    static_url = asset_paths.build_static_asset_url("icons/page_image.png")

    assert static_url == "/assets/icons/page_image.png"


def test_get_application_icon_path_resolves_configured_icon_filename(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve the application icon through the generic asset resolver."""
    logger_mock = Mock()
    resolve_asset_path_mock = Mock(return_value="resolved/icon/path.ico")

    monkeypatch.setattr(asset_paths, "logger", logger_mock)
    monkeypatch.setattr(
        asset_paths,
        "resolve_asset_path",
        resolve_asset_path_mock,
    )

    icon_path = asset_paths.get_application_icon_path()

    assert icon_path == "resolved/icon/path.ico"
    resolve_asset_path_mock.assert_called_once_with(APP_ICON_FILENAME)
    logger_mock.debug.assert_called_once_with(
        "Application icon resolved: %s",
        "resolved/icon/path.ico",
    )


@pytest.mark.parametrize(
    "asset_filename",
    [
        "",
        "   ",
        "/tmp/file.png",
        "../secret.txt",
        "icons/../secret.txt",
        r"..\secret.txt",
        r"C:\temp\file.png",
        "C:file.png",
    ],
)
def test_resolve_asset_path_rejects_invalid_asset_filenames(
    asset_filename: str,
) -> None:
    """Reject filenames that are empty, absolute, or outside the assets folder."""
    with pytest.raises(ValueError, match="Asset filename"):
        asset_paths.resolve_asset_path(asset_filename)
