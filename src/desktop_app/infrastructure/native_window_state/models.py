# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/models.py
# Purpose:
# Define lightweight native window state data models.
# Behavior:
# Provides immutable value objects used by monitor detection and geometry
# normalization helpers.
# Notes:
# Models in this module intentionally avoid NiceGUI and application-state
# dependencies.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MonitorWorkArea:
    """Represent a Windows monitor work area in virtual-screen coordinates."""

    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        """Return the work-area width."""
        return self.right - self.left

    @property
    def height(self) -> int:
        """Return the work-area height."""
        return self.bottom - self.top
