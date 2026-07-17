"""Timeline helpers for dashboard activity feeds."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any

from ..context.compression_manager import ROLLING_SUMMARY_PREFIX
from ..context.conversation_store import Conversation, ConversationMessage


LIVE_CONVERSATION_TIMELINE_MAX_EVENTS = 40
_GENERATION_ENDPOINTS = frozenset(
    {
        "/api/chat",
        "/api/generate",
        "/v1/chat/completions",
        "/v1/completions",
    }
)
_EVENT_SORT_PRIORITY = {
    "conversation_started": 0,
    "model_selected": 10,
    "model_changed": 11,
    "request_received": 20,
    "request_completed": 30,
    "request_failed": 31,
    "context_warning": 40,
    "compression_completed": 50,
}


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


@dataclass(frozen=True)
class LiveConversationTimelineEvent:
    """A privacy-safe operational event for the active conversation timeline."""

    id: str
    timestamp: datetime
    type: str
    severity: str
    title: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return a stable serializable representation for dashboard polling."""

        timestamp = _ensure_timezone(self.timestamp)
        return {
            "id": self.id,
            "timestamp": timestamp.isoformat(),
            "time_label": _time_label(timestamp),
            "type": self.type,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
        }


def build_live_conversation_timeline(
    *,
    conversations: list[Conversation],
    active_conversation: dict[str, Any],
    recent_requests: list[dict[str, Any]],
    activity_snapshot: object | None = None,
    max_events: int = LIVE_CONVERSATION_TIMELINE_MAX_EVENTS,
) -> list[LiveConversationTimelineEvent]:
    """Build a bounded active-conversation timeline from existing dashboard state.

    The builder is intentionally deterministic and read-only. It does not append
    state to conversations, request metrics, or any separate timeline store.
    """

    if max_events <= 0:
        raise ValueError("max_events must be greater than 0")

    events: list[LiveConversationTimelineEvent] = []
    conversation = _active_conversation(conversations)
    conversation_id: str | None = None
    conversation_started_at: datetime | None = None
    if conversation is not None:
        conversation_id = conversation.conversation_id
        conversation_started_at = _ensure_timezone(conversation.created_at)
        events.append(
            LiveConversationTimelineEvent(
                id=_event_id("conversation_started", conversation.conversation_id, conversation.created_at.isoformat()),
                timestamp=conversation_started_at,
                type="conversation_started",
                severity="info",
                title="Conversation activity began",
                detail="ContextKeeper began tracking this conversation.",
            )
        )
        events.extend(_compression_completed_events(conversation))
        context_event = _context_warning_event(conversation, active_conversation)
        if context_event is not None:
            events.append(context_event)

    events.extend(
        _request_events(
            recent_requests,
            conversation_id=conversation_id,
            conversation_started_at=conversation_started_at,
        )
    )
    active_events = _active_activity_events(activity_snapshot)
    events.extend(active_events)

    return _bounded_chronological_events(events, max_events=max_events)


def _active_conversation(conversations: list[Conversation]) -> Conversation | None:
    if not conversations:
        return None
    return max(conversations, key=lambda conversation: conversation.updated_at)


def _request_events(
    recent_requests: list[dict[str, Any]],
    *,
    conversation_id: str | None,
    conversation_started_at: datetime | None,
) -> list[LiveConversationTimelineEvent]:
    events: list[LiveConversationTimelineEvent] = []
    chronological_requests = _chronological_generation_requests(recent_requests)
    previous_model: str | None = None

    for request in chronological_requests:
        timestamp = _parse_timestamp(request.get("timestamp"))
        if timestamp is None:
            continue
        request_conversation_id = _string_or_none(request.get("conversation_id"))
        if conversation_id is not None and request_conversation_id is not None and request_conversation_id != conversation_id:
            continue
        if request_conversation_id is None and conversation_started_at is not None and timestamp < conversation_started_at:
            continue

        model = _string_or_none(request.get("model"))
        if model is not None:
            request_key = _request_key(request)
            if previous_model is None:
                events.append(
                    LiveConversationTimelineEvent(
                        id=_event_id("model_selected", request_key, model),
                        timestamp=timestamp,
                        type="model_selected",
                        severity="info",
                        title="Model observed",
                        detail=model,
                    )
                )
            elif model != previous_model:
                events.append(
                    LiveConversationTimelineEvent(
                        id=_event_id("model_changed", request_key, previous_model, model),
                        timestamp=timestamp,
                        type="model_changed",
                        severity="info",
                        title="Model changed",
                        detail=f"{previous_model} -> {model}",
                    )
                )
            previous_model = model

        status_code = _int_or_none(request.get("status_code"))
        if status_code is None:
            continue
        failed = status_code >= 400
        event_type = "request_failed" if failed else "request_completed"
        events.append(
            LiveConversationTimelineEvent(
                id=_event_id(event_type, _request_key(request), status_code),
                timestamp=timestamp,
                type=event_type,
                severity="error" if failed else "success",
                title="Request failed" if failed else "Request completed",
                detail=_request_detail(request, status_code=status_code),
            )
        )

    return events


def _active_activity_events(activity_snapshot: object | None) -> list[LiveConversationTimelineEvent]:
    if activity_snapshot is None:
        return []
    active_count = _int_or_none(getattr(activity_snapshot, "active_request_count", None)) or 0
    if active_count <= 0:
        return []

    timestamp = _parse_timestamp(getattr(activity_snapshot, "active_accepted_at", None))
    if timestamp is None:
        timestamp = _parse_timestamp(getattr(activity_snapshot, "updated_at", None))
    if timestamp is None:
        return []

    request_id = _string_or_none(getattr(activity_snapshot, "active_request_id", None))
    endpoint = _string_or_none(getattr(activity_snapshot, "active_endpoint", None))
    model = _string_or_none(getattr(activity_snapshot, "active_model", None))
    generation_sequence = _int_or_none(getattr(activity_snapshot, "active_generation_sequence", None))
    key = request_id or str(generation_sequence or timestamp.isoformat())
    detail = _join_detail(endpoint, model)
    events = [
        LiveConversationTimelineEvent(
            id=_event_id("request_received", key, endpoint, model),
            timestamp=timestamp,
            type="request_received",
            severity="info",
            title="Request received",
            detail=detail,
        )
    ]
    if model is not None:
        events.append(
            LiveConversationTimelineEvent(
                id=_event_id("model_selected", "active", key, model),
                timestamp=timestamp,
                type="model_selected",
                severity="info",
                title="Model observed",
                detail=model,
            )
        )
    return events


def _compression_completed_events(conversation: Conversation) -> list[LiveConversationTimelineEvent]:
    summaries = [
        message
        for message in conversation.messages
        if _is_rolling_summary(message)
    ]
    events: list[LiveConversationTimelineEvent] = []
    for index, message in enumerate(sorted(summaries, key=lambda item: item.timestamp), start=1):
        timestamp = _ensure_timezone(message.timestamp)
        events.append(
            LiveConversationTimelineEvent(
                id=_event_id("compression_completed", conversation.conversation_id, timestamp.isoformat(), index),
                timestamp=timestamp,
                type="compression_completed",
                severity="success",
                title="Compression completed",
                detail=f"Rolling summary {index} recorded.",
            )
        )
    return events


def _context_warning_event(
    conversation: Conversation,
    active_conversation: dict[str, Any],
) -> LiveConversationTimelineEvent | None:
    context = active_conversation.get("context")
    if not isinstance(context, dict):
        return None
    compression_threshold = bool(context.get("compression_threshold_exceeded"))
    warning_threshold = bool(context.get("warning_threshold_exceeded"))
    if not compression_threshold and not warning_threshold:
        return None

    usage_percent = _number_or_none(context.get("usage_percent"))
    estimated_tokens = _int_or_none(context.get("estimated_tokens"))
    context_window_tokens = _int_or_none(context.get("context_window_tokens"))
    title = "Compression threshold reached" if compression_threshold else "Context warning threshold reached"
    threshold_type = "compression" if compression_threshold else "warning"
    return LiveConversationTimelineEvent(
        id=_event_id(
            "context_warning",
            conversation.conversation_id,
            threshold_type,
            usage_percent,
            estimated_tokens,
            context_window_tokens,
        ),
        timestamp=_ensure_timezone(conversation.updated_at),
        type="context_warning",
        severity="warning",
        title=title,
        detail=_context_detail(
            usage_percent=usage_percent,
            estimated_tokens=estimated_tokens,
            context_window_tokens=context_window_tokens,
        ),
    )


def _chronological_generation_requests(recent_requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    generation_requests = [
        request
        for request in recent_requests
        if isinstance(request, dict) and request.get("endpoint") in _GENERATION_ENDPOINTS
    ]
    oldest = datetime.min.replace(tzinfo=timezone.utc)
    return sorted(
        generation_requests,
        key=lambda request: (
            _parse_timestamp(request.get("timestamp")) or oldest,
            _int_or_none(request.get("generation_sequence")) or -1,
            _int_or_none(request.get("sequence")) or -1,
        ),
    )


def _bounded_chronological_events(
    events: list[LiveConversationTimelineEvent],
    *,
    max_events: int,
) -> list[LiveConversationTimelineEvent]:
    unique: dict[str, LiveConversationTimelineEvent] = {}
    for event in events:
        unique.setdefault(event.id, event)

    ordered = sorted(
        unique.values(),
        key=lambda event: (
            _ensure_timezone(event.timestamp),
            _EVENT_SORT_PRIORITY.get(event.type, 100),
            event.id,
        ),
    )
    return ordered[-max_events:]


def _request_key(request: dict[str, Any]) -> str:
    sequence = _int_or_none(request.get("sequence"))
    if sequence is not None:
        return f"sequence:{sequence}"
    generation_sequence = _int_or_none(request.get("generation_sequence"))
    if generation_sequence is not None:
        return f"generation:{generation_sequence}"
    return _stable_fragment(
        request.get("timestamp"),
        request.get("method"),
        request.get("endpoint"),
        request.get("model"),
        request.get("status_code"),
        request.get("latency_ms"),
    )


def _request_detail(request: dict[str, Any], *, status_code: int) -> str:
    return _join_detail(
        _latency_detail(request.get("latency_ms")),
        f"HTTP {status_code}",
        _string_or_none(request.get("endpoint")),
        _string_or_none(request.get("model")),
    )


def _context_detail(
    *,
    usage_percent: float | None,
    estimated_tokens: int | None,
    context_window_tokens: int | None,
) -> str:
    usage = f"{_format_number(usage_percent)}% context used" if usage_percent is not None else None
    tokens = (
        f"{estimated_tokens:,} / {context_window_tokens:,} estimated tokens"
        if estimated_tokens is not None and context_window_tokens is not None
        else f"{estimated_tokens:,} estimated tokens"
        if estimated_tokens is not None
        else None
    )
    return _join_detail(usage, tokens)


def _latency_detail(value: object) -> str | None:
    latency_ms = _number_or_none(value)
    if latency_ms is None:
        return None
    if latency_ms >= 1000:
        return f"{_format_number(round(latency_ms / 1000, 2))} s"
    return f"{_format_number(latency_ms)} ms"


def _join_detail(*parts: str | None) -> str:
    return " • ".join(part for part in parts if part)


def _event_id(event_type: str, *parts: object) -> str:
    return f"{event_type}-{_stable_fragment(event_type, *parts)}"


def _stable_fragment(*parts: object) -> str:
    stable = "|".join("" if part is None else str(part) for part in parts)
    return sha1(stable.encode("utf-8")).hexdigest()[:12]


def _parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return _ensure_timezone(value)
    if not isinstance(value, str):
        return None
    try:
        return _ensure_timezone(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError:
        return None


def _time_label(timestamp: datetime) -> str:
    return timestamp.astimezone().strftime("%H:%M:%S")


def _is_rolling_summary(message: ConversationMessage) -> bool:
    return message.role == "system" and message.content.startswith(ROLLING_SUMMARY_PREFIX)


def _int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _number_or_none(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, 2)


def _string_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)
