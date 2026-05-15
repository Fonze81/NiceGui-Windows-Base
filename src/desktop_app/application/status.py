# -----------------------------------------------------------------------------
# File: src/desktop_app/application/status.py
# Purpose:
# Build status history snapshots for UI diagnostics.
# Behavior:
# Converts AppState status messages into immutable records with formatted times
# and bounded history ordering.
# Notes:
# Keep this module independent from NiceGUI so status rendering remains testable.
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from desktop_app.core.state import AppState, StatusLevel, StatusMessage

DEFAULT_STATUS_HISTORY_LIMIT: Final[int] = 20


@dataclass(frozen=True, slots=True)
class StatusHistoryItem:
    """Represent one rendered status history entry.

    Attributes:
        text: User-facing status message.
        level: Message level.
        created_at: Original message timestamp.
        created_at_text: Formatted timestamp for the UI.
    """

    text: str
    level: StatusLevel
    created_at: datetime
    created_at_text: str


def build_status_history_snapshot(
    state: AppState,
    *,
    limit: int = DEFAULT_STATUS_HISTORY_LIMIT,
) -> tuple[StatusHistoryItem, ...]:
    """Build recent status history in reverse chronological order.

    Args:
        state: Application state used as source.
        limit: Maximum number of recent messages to return.

    Returns:
        Recent status messages with newest items first.
    """
    if limit <= 0:
        return ()

    recent_messages = state.status.history[-limit:]
    return tuple(
        _build_status_history_item(message) for message in reversed(recent_messages)
    )


def _build_status_history_item(message: StatusMessage) -> StatusHistoryItem:
    """Build a display item from one status message.

    Args:
        message: Status message stored in AppState.

    Returns:
        Display-ready status history item.
    """
    return StatusHistoryItem(
        text=message.text,
        level=message.level,
        created_at=message.created_at,
        created_at_text=message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )
