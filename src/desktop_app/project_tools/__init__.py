# -----------------------------------------------------------------------------
# File: src/desktop_app/project_tools/__init__.py
# Purpose:
# Expose maintenance helpers for template customization and release preparation.
# Behavior:
# Provides a small public API used by repository scripts and focused tests.
# Notes:
# These helpers are not part of the NiceGUI runtime path. They intentionally avoid
# UI imports and external command execution.
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Final

from desktop_app.project_tools.common import ChangedFile, ProjectToolError
from desktop_app.project_tools.release_automation import (
    ReleasePlan,
    build_release_plan,
    prepare_release,
)
from desktop_app.project_tools.template_customization import (
    TemplateIdentity,
    build_template_identity,
    customize_template,
)

__all__: Final[tuple[str, ...]] = (
    "ChangedFile",
    "ProjectToolError",
    "ReleasePlan",
    "TemplateIdentity",
    "build_release_plan",
    "build_template_identity",
    "customize_template",
    "prepare_release",
)
