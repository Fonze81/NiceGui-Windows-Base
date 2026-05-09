# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/asset_paths.py
# Purpose:
# Resolve application asset file paths.
# Behavior:
# Uses runtime information to build the correct asset path during normal Python
# execution and inside the PyInstaller packaged executable.
# Notes:
# NiceGUI accepts file paths as strings for components such as ui.image and for
# the application favicon, so this module returns string paths.
# -----------------------------------------------------------------------------

from pathlib import Path, PurePosixPath, PureWindowsPath

from desktop_app.constants import (
    APP_ICON_FILENAME,
    LOCAL_ASSETS_DIR,
    PACKAGED_ASSETS_DIR,
)
from desktop_app.core.runtime import get_runtime_root, is_frozen_executable
from desktop_app.infrastructure.logger import logger_get_logger

logger = logger_get_logger(__name__)


def _normalize_asset_filename(asset_filename: str) -> Path:
    """Return a safe relative asset filename path.

    Args:
        asset_filename: Asset filename stored in the application assets directory.

    Returns:
        Safe relative path for the requested asset file.

    Raises:
        ValueError: If the filename is empty, absolute, drive-based, rooted, or
            leaves the asset directory.
    """
    normalized_filename = asset_filename.strip()

    if not normalized_filename:
        msg = "Asset filename must not be empty."
        raise ValueError(msg)

    asset_filename_path = Path(normalized_filename)
    posix_filename_path = PurePosixPath(normalized_filename)
    windows_filename_path = PureWindowsPath(normalized_filename)

    is_unsafe_path = (
        asset_filename_path.is_absolute()
        or posix_filename_path.is_absolute()
        or windows_filename_path.is_absolute()
        or bool(posix_filename_path.root)
        or bool(windows_filename_path.root)
        or bool(windows_filename_path.drive)
        or ".." in asset_filename_path.parts
        or ".." in posix_filename_path.parts
        or ".." in windows_filename_path.parts
    )

    if is_unsafe_path:
        msg = (
            f"Asset filename must be relative to the assets directory: {asset_filename}"
        )
        raise ValueError(msg)

    return asset_filename_path


def resolve_asset_path(asset_filename: str) -> str:
    """Return the absolute path for an application asset.

    Args:
        asset_filename: Asset filename stored in the application assets directory.

    Returns:
        Absolute path to the requested asset file as a string.

    Raises:
        ValueError: If the filename is empty, absolute, drive-based, rooted, or
            leaves the asset directory.
    """
    safe_asset_filename = _normalize_asset_filename(asset_filename)
    runtime_root = get_runtime_root(module_file=__file__)
    assets_dir = PACKAGED_ASSETS_DIR if is_frozen_executable() else LOCAL_ASSETS_DIR
    asset_path = runtime_root / assets_dir / safe_asset_filename

    logger.debug("Asset path resolved for %s: %s", safe_asset_filename, asset_path)

    if not asset_path.exists():
        logger.warning("Asset file is missing and may not render: %s", asset_path)

    return str(asset_path)


def get_application_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file as a string.
    """
    icon_path = resolve_asset_path(APP_ICON_FILENAME)
    logger.debug("Application icon resolved: %s", icon_path)
    return icon_path
