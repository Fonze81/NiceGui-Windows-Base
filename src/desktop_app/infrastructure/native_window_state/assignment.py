# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/native_window_state/assignment.py
# Purpose:
# Provide small assignment helpers for native window state updates.
# Behavior:
# Updates mutable objects only when a value actually changes so callers can
# report whether state was modified.
# Notes:
# This module has no application or NiceGUI dependency.
# -----------------------------------------------------------------------------

from __future__ import annotations


def _assign_if_different(target: object, attribute_name: str, value: object) -> bool:
    """Assign an attribute only when its value changes.

    Args:
        target: Mutable object that owns the attribute.
        attribute_name: Name of the attribute to update.
        value: New value to assign.

    Returns:
        True when assignment changed the previous value.
    """
    if getattr(target, attribute_name) == value:
        return False

    setattr(target, attribute_name, value)
    return True
