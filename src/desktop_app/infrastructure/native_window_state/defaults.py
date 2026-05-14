# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/defaults.py
# Purpose:
# Store default values used by the native window state package.
# Behavior:
# Defines geometry limits, visibility thresholds, and known native attribute
# names shared by startup, event, and monitor helpers.
# Notes:
# Keep these constants package-local so native window state behavior can evolve
# without depending on unrelated application constants.
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Final

MIN_WINDOW_WIDTH: Final[int] = 400
MIN_WINDOW_HEIGHT: Final[int] = 300
MAX_START_POSITION_RATIO: Final[float] = 0.90
MIN_VISIBLE_EDGE_RATIO: Final[float] = 0.10

X_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("x", "left")
Y_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("y", "top")
WIDTH_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("width", "inner_width")
HEIGHT_ATTRIBUTE_NAMES: Final[tuple[str, ...]] = ("height", "inner_height")
