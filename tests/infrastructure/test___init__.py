# -----------------------------------------------------------------------------
# File: tests/infrastructure/test___init__.py
# Purpose:
# Validate the infrastructure package initialization contract.
# Behavior:
# Imports the infrastructure package and verifies that it intentionally exposes
# no aggregated public API.
# Notes:
# Keep this test small because the package initializer must remain lightweight
# and free of infrastructure side effects.
# -----------------------------------------------------------------------------

from __future__ import annotations

import desktop_app.infrastructure as infrastructure


def test_infrastructure_package_exports_no_public_symbols() -> None:
    """Ensure the infrastructure package keeps an empty public API."""
    assert infrastructure.__all__ == ()


def test_infrastructure_package_has_clear_docstring() -> None:
    """Ensure the package documents its architectural purpose."""
    assert infrastructure.__doc__ is not None
    assert "Infrastructure integrations" in infrastructure.__doc__
    assert "no aggregated public API" in infrastructure.__doc__
