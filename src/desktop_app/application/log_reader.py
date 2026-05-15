# -----------------------------------------------------------------------------
# File: src/desktop_app/application/log_reader.py
# Purpose:
# Provide bounded runtime log reading for diagnostics pages.
# Behavior:
# Resolves the best log file path from AppState, reads only the latest lines with
# bounded memory, and returns metadata that the UI can render safely.
# Notes:
# Keep this module free of NiceGUI imports. Do not stream or watch log files from
# here; callers should explicitly request a snapshot when they need one.
# -----------------------------------------------------------------------------

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from desktop_app.core.state import AppState, get_app_state

DEFAULT_LOG_LINE_LIMIT: Final[int] = 120


@dataclass(frozen=True, slots=True)
class LogSnapshot:
    """Represent a bounded view of the current runtime log file.

    Attributes:
        path: Effective log path used for the read attempt.
        exists: Whether the path points to a regular file.
        max_lines: Maximum number of lines requested.
        lines: Latest log lines without trailing newline characters.
        error: Read error message, when a recoverable failure happened.
    """

    path: Path | None
    exists: bool
    max_lines: int
    lines: tuple[str, ...]
    error: str | None = None

    @property
    def has_lines(self) -> bool:
        """Return whether the snapshot contains log lines."""
        return bool(self.lines)

    @property
    def line_count(self) -> int:
        """Return the number of lines included in the snapshot."""
        return len(self.lines)


def resolve_runtime_log_path(state: AppState | None = None) -> Path | None:
    """Return the best available runtime log path.

    Args:
        state: Application state used as source. Uses the global state when omitted.

    Returns:
        Effective log path, configured log path, or None when unavailable.
    """
    current_state = state if state is not None else get_app_state()
    return (
        current_state.log.effective_file_path
        or current_state.paths.log_file_path
        or current_state.log.file_path
    )


def read_recent_log_lines(
    log_file_path: str | Path | None,
    *,
    max_lines: int = DEFAULT_LOG_LINE_LIMIT,
) -> tuple[str, ...]:
    """Read the latest lines from a log file using bounded memory.

    Args:
        log_file_path: Path to the log file.
        max_lines: Maximum number of lines to return.

    Returns:
        Latest log lines without trailing newline characters.
    """
    if log_file_path is None or max_lines <= 0:
        return ()

    path = Path(log_file_path)
    if not path.is_file():
        return ()

    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        return tuple(line.rstrip("\n") for line in deque(log_file, maxlen=max_lines))


def read_log_snapshot(
    *,
    state: AppState | None = None,
    max_lines: int = DEFAULT_LOG_LINE_LIMIT,
) -> LogSnapshot:
    """Read a bounded snapshot of the current runtime log.

    Args:
        state: Application state used as source. Uses the global state when omitted.
        max_lines: Maximum number of latest lines to include.

    Returns:
        Log snapshot with metadata and recoverable errors captured as text.
    """
    log_path = resolve_runtime_log_path(state)
    normalized_limit = max(0, max_lines)

    if log_path is None:
        return LogSnapshot(
            path=None,
            exists=False,
            max_lines=normalized_limit,
            lines=(),
        )

    path = Path(log_path)
    exists = path.is_file()

    if not exists or normalized_limit <= 0:
        return LogSnapshot(
            path=path,
            exists=exists,
            max_lines=normalized_limit,
            lines=(),
        )

    try:
        return LogSnapshot(
            path=path,
            exists=True,
            max_lines=normalized_limit,
            lines=read_recent_log_lines(path, max_lines=normalized_limit),
        )
    except OSError as exc:
        return LogSnapshot(
            path=path,
            exists=True,
            max_lines=normalized_limit,
            lines=(),
            error=f"Could not read log file: {exc}",
        )
