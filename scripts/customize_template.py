# -----------------------------------------------------------------------------
# File: scripts/customize_template.py
# Purpose:
# Customize public identity values for projects derived from this template.
# Behavior:
# Parses command-line arguments, loads the project maintenance API from src, and
# applies template customization changes or reports them in dry-run mode.
# Notes:
# This script intentionally keeps the internal desktop_app package name unchanged.
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from desktop_app.project_tools import (  # noqa: E402
    ProjectToolError,
    build_template_identity,
    customize_template,
)


def parse_args() -> argparse.Namespace:
    """Parse template customization arguments.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Customize public identity values for a derived project."
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Lowercase package/command slug, for example inventory-dashboard.",
    )
    parser.add_argument(
        "--display-name",
        required=True,
        help='Human-readable application name, for example "Inventory Dashboard".',
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Project metadata description.",
    )
    parser.add_argument(
        "--author-name",
        required=True,
        help="Contributor or organization name for metadata and Windows resources.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report files that would change without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    """Run template customization from command-line arguments.

    Returns:
        Process exit code.
    """
    args = parse_args()
    try:
        identity = build_template_identity(
            project_name=args.project_name,
            display_name=args.display_name,
            description=args.description,
            author_name=args.author_name,
        )
        changes = customize_template(PROJECT_ROOT, identity, dry_run=args.dry_run)
    except ProjectToolError as exc:
        print(f"Template customization failed: {exc}", file=sys.stderr)
        return 1

    changed_paths = [change.path.as_posix() for change in changes if change.changed]
    action = "Would update" if args.dry_run else "Updated"
    if changed_paths:
        print(f"{action} {len(changed_paths)} file(s):")
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("No template identity changes were required.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
