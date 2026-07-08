"""In-memory activity timeline for dashboard intelligence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class TimelineEvent:
    """A timestamped dashboard activity event."""

    message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation of the event."""
        return {
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class EventTimeline:
    """Simple in-memory event timeline for dashboard activity feeds."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Create an event timeline with an optional timestamp provider."""
        self._clock = clock or _utc_now
        self._events: list[TimelineEvent] = []

    def add_event(self, message: str) -> TimelineEvent:
        """Add an event to the timeline and return the stored event."""
        if not message.strip():
            raise ValueError("message must not be empty")

        event = TimelineEvent(
            message=message,
            timestamp=_ensure_timezone(self._clock()),
        )
        self._events.append(event)
        return event

    def recent_events(self, limit: int = 20) -> list[TimelineEvent]:
        """Return the most recent events in newest-first order."""
        if limit <= 0:
            raise ValueError("limit must be greater than 0")
        return list(reversed(self._events[-limit:]))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
