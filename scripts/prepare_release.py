# -----------------------------------------------------------------------------
# File: scripts/prepare_release.py
# Purpose:
# Prepare release metadata consistently across project files.
# Behavior:
# Parses a semantic version, updates release-managed files through the project
# maintenance API, and prints the files changed or planned in dry-run mode.
# Notes:
# This script does not run tests, Git, PyInstaller, or publishing commands.
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
    build_release_plan,
    prepare_release,
)


def parse_args() -> argparse.Namespace:
    """Parse release preparation arguments.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Prepare project metadata for a release."
    )
    parser.add_argument(
        "version",
        help="Release version in MAJOR.MINOR.PATCH format, for example 0.10.0.",
    )
    parser.add_argument(
        "--date",
        dest="release_date",
        help="Release date in YYYY-MM-DD format. Defaults to today's date.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report files that would change without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    """Run release preparation from command-line arguments.

    Returns:
        Process exit code.
    """
    args = parse_args()
    try:
        plan = build_release_plan(args.version, release_date=args.release_date)
        changes = prepare_release(PROJECT_ROOT, plan, dry_run=args.dry_run)
    except ProjectToolError as exc:
        print(f"Release preparation failed: {exc}", file=sys.stderr)
        return 1

    changed_paths = [change.path.as_posix() for change in changes if change.changed]
    action = "Would update" if args.dry_run else "Updated"
    if changed_paths:
        print(f"{action} {len(changed_paths)} file(s):")
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("No release metadata changes were required.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
