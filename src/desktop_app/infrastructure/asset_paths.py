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

import logging

from desktop_app.constants import (
    APP_ICON_FILENAME,
    LOCAL_ASSETS_DIR,
    PACKAGED_ASSETS_DIR,
)
from desktop_app.core.runtime import get_runtime_root, is_frozen_executable

logger = logging.getLogger(__name__)


def resolve_asset_path(filename: str) -> str:
    """Return the absolute path for an application asset.

    Args:
        filename: Asset filename stored in the application assets directory.

    Returns:
        Absolute path to the requested asset file as a string.
    """
    runtime_root = get_runtime_root(module_file=__file__)

    if is_frozen_executable():
        asset_path = runtime_root / PACKAGED_ASSETS_DIR / filename
    else:
        asset_path = runtime_root / LOCAL_ASSETS_DIR / filename

    logger.debug("Resolved asset path for %s: %s", filename, asset_path)

    if not asset_path.exists():
        logger.warning("Asset file was not found: %s", asset_path)

    return str(asset_path)


def get_application_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file as a string.
    """
    icon_path = resolve_asset_path(APP_ICON_FILENAME)
    logger.debug("Application icon path resolved: %s", icon_path)
    return icon_path
