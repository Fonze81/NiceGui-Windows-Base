# -----------------------------------------------------------------------------
# File: tests/application/test_status.py
# Purpose:
# Validate status history snapshot generation.
# Behavior:
# Exercises bounded reverse chronological status formatting without NiceGUI.
# Notes:
# Status history is intentionally in-memory runtime state.
# -----------------------------------------------------------------------------

from __future__ import annotations

from desktop_app.application.status import build_status_history_snapshot
from desktop_app.core.state import AppState


def test_build_status_history_snapshot_returns_newest_first() -> None:
    """Recent status messages are returned newest first."""
    state = AppState()
    state.status.push("First", "info")
    state.status.push("Second", "success")
    state.status.push("Third", "warning")

    snapshot = build_status_history_snapshot(state, limit=2)

    assert [item.text for item in snapshot] == ["Third", "Second"]
    assert [item.level for item in snapshot] == ["warning", "success"]
    assert all(item.created_at_text for item in snapshot)


def test_build_status_history_snapshot_handles_empty_or_disabled_history() -> None:
    """Empty and disabled limits return an empty snapshot."""
    state = AppState()

    assert build_status_history_snapshot(state) == ()
    state.status.push("Stored", "info")
    assert build_status_history_snapshot(state, limit=0) == ()
