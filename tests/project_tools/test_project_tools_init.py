# -----------------------------------------------------------------------------
# File: tests/project_tools/test_project_tools_init.py
# Purpose:
# Validate the project tools package public API.
# Behavior:
# Ensures repository scripts can rely on stable exported helper names.
# Notes:
# This test does not execute file mutations.
# -----------------------------------------------------------------------------

from __future__ import annotations

import desktop_app.project_tools as project_tools


def test_project_tools_public_api_exports_supported_symbols() -> None:
    """The project tools package exposes only supported public helpers."""
    assert project_tools.__all__ == (
        "ChangedFile",
        "ProjectToolError",
        "ReleasePlan",
        "TemplateIdentity",
        "build_release_plan",
        "build_template_identity",
        "customize_template",
        "prepare_release",
    )
