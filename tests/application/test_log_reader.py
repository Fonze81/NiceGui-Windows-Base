# -----------------------------------------------------------------------------
# File: tests/application/test_log_reader.py
# Purpose:
# Validate bounded runtime log reading services.
# Behavior:
# Exercises path resolution, bounded tail reads, missing files, and snapshots.
# Notes:
# The log reader stays independent from NiceGUI so it can be tested directly.
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path

from desktop_app.application.log_reader import (
    read_log_snapshot,
    read_recent_log_lines,
    resolve_runtime_log_path,
)
from desktop_app.core.state import AppState


def test_resolve_runtime_log_path_prefers_effective_path(tmp_path: Path) -> None:
    """Effective log path has priority over fallback paths."""
    state = AppState()
    effective_path = tmp_path / "effective.log"
    state.log.effective_file_path = effective_path
    state.paths.log_file_path = tmp_path / "path.log"
    state.log.file_path = Path("logs") / "configured.log"

    assert resolve_runtime_log_path(state) == effective_path


def test_read_recent_log_lines_returns_bounded_tail(tmp_path: Path) -> None:
    """Only the requested number of latest lines is returned."""
    log_file = tmp_path / "app.log"
    log_file.write_text("one\ntwo\nthree\n", encoding="utf-8")

    assert read_recent_log_lines(log_file, max_lines=2) == ("two", "three")
    assert read_recent_log_lines(tmp_path / "missing.log") == ()
    assert read_recent_log_lines(log_file, max_lines=0) == ()
    assert read_recent_log_lines(None) == ()


def test_read_log_snapshot_returns_lines_and_metadata(tmp_path: Path) -> None:
    """Snapshot includes path, existence, limit, and line metadata."""
    log_file = tmp_path / "app.log"
    log_file.write_text("first\nsecond\n", encoding="utf-8")
    state = AppState()
    state.log.effective_file_path = log_file

    snapshot = read_log_snapshot(state=state, max_lines=10)

    assert snapshot.path == log_file
    assert snapshot.exists is True
    assert snapshot.max_lines == 10
    assert snapshot.lines == ("first", "second")
    assert snapshot.line_count == 2
    assert snapshot.has_lines is True
    assert snapshot.error is None


def test_read_log_snapshot_handles_missing_path(tmp_path: Path) -> None:
    """Missing files return an empty snapshot instead of failing."""
    state = AppState()
    state.log.effective_file_path = tmp_path / "missing.log"

    snapshot = read_log_snapshot(state=state, max_lines=-1)

    assert snapshot.path == tmp_path / "missing.log"
    assert snapshot.exists is False
    assert snapshot.max_lines == 0
    assert snapshot.lines == ()
    assert snapshot.has_lines is False
