"""Tests for the desktop_app.core package public API."""

from importlib import import_module
from typing import cast


def test_core_package_exports_no_public_symbols() -> None:
    """Ensure the core package does not expose an unstable public API."""
    module = import_module("desktop_app.core")

    public_exports = cast("list[str]", module.__all__)

    assert public_exports == []
    assert all(isinstance(export_name, str) for export_name in public_exports)
