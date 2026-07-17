from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..config import Settings
from ..context.conversation_store import Conversation

_GENERATION_ENDPOINTS = {"/api/chat", "/api/generate"}
_PLACEHOLDER = "Not available"


@dataclass(frozen=True)
class ConversationInspectorIntelligence:
    status: str
    status_label: str
    severity: str
    explanation: str
    recommendation: str | None
    signals: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "status_label": self.status_label,
            "severity": self.severity,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "signals": self.signals,
        }


def classify_conversation_intelligence(
    *,
    conversation_available: bool,
    context_enabled: bool,
    compression_enabled: bool,
    usage_percent: float | None,
    estimated_tokens: int | None,
    context_window_tokens: int | None,
    warning_threshold_percent: int,
    compression_threshold_percent: int,
    compression_count: int,
    context_window_source_label: str | None = None,
) -> ConversationInspectorIntelligence:
    """Classify selected-conversation health using deterministic dashboard metadata."""

    base_signals = [
        _signal("Context tracking", "Enabled" if context_enabled else "Disabled"),
        _signal("Compression", "Enabled" if compression_enabled else "Disabled"),
        _signal("Compression events", str(max(0, compression_count))),
    ]

    if not conversation_available:
        return ConversationInspectorIntelligence(
            status="insufficient_data",
            status_label="Insufficient data",
            severity="unavailable",
            explanation="Conversation intelligence will appear when a conversation is available in the dashboard snapshot.",
            recommendation=None,
            signals=base_signals,
        )

    if not context_enabled:
        return ConversationInspectorIntelligence(
            status="insufficient_data",
            status_label="Insufficient data",
            severity="unavailable",
            explanation="Conversation intelligence requires context tracking to be enabled.",
            recommendation=None,
            signals=base_signals,
        )

    if usage_percent is None or estimated_tokens is None or context_window_tokens is None or context_window_tokens <= 0:
        return ConversationInspectorIntelligence(
            status="insufficient_data",
            status_label="Insufficient data",
            severity="unavailable",
            explanation="Context estimates are not available yet for this conversation.",
            recommendation=None,
            signals=[
                *base_signals,
                _signal("Context usage", _format_percent(usage_percent)),
                _signal("Model capacity", _format_tokens(context_window_tokens)),
            ],
        )

    remaining_tokens = max(0, int(context_window_tokens - estimated_tokens))
    signals = [
        _signal("Context usage", _format_percent(usage_percent)),
        _signal("Warning threshold", f"{warning_threshold_percent}%"),
        _signal("Compression threshold", f"{compression_threshold_percent}%"),
        _signal("Remaining headroom", _format_tokens(remaining_tokens)),
        _signal("Model capacity", _format_tokens(context_window_tokens)),
        _signal("Capacity source", _safe_text(context_window_source_label)),
        *base_signals,
    ]

    if usage_percent >= 100:
        return ConversationInspectorIntelligence(
            status="critical",
            status_label="Action required",
            severity="error",
            explanation="Based on estimated token usage, this conversation has exhausted or exceeded the known context capacity.",
            recommendation="Reduce context pressure or allow compression before continuing a long exchange.",
            signals=signals,
        )

    if usage_percent >= compression_threshold_percent:
        if not compression_enabled:
            return ConversationInspectorIntelligence(
                status="critical",
                status_label="Action required",
                severity="error",
                explanation=(
                    "Based on estimated token usage, this conversation is at or above the compression threshold "
                    "while compression is disabled."
                ),
                recommendation="Enable compression or reduce context before continuing the conversation.",
                signals=signals,
            )

        return ConversationInspectorIntelligence(
            status="compression_threshold",
            status_label="Compression threshold reached",
            severity="warning",
            explanation=(
                "Based on estimated token usage, this conversation is at or above the configured compression "
                "threshold. Compression is enabled and available."
            ),
            recommendation=None,
            signals=signals,
        )

    if usage_percent >= warning_threshold_percent:
        return ConversationInspectorIntelligence(
            status="warning",
            status_label="Warning",
            severity="warning",
            explanation="Based on estimated token usage, this conversation is approaching context pressure.",
            recommendation=None,
            signals=signals,
        )

    if compression_count > 0:
        return ConversationInspectorIntelligence(
            status="compression_present",
            status_label="Compression present",
            severity="info",
            explanation=(
                f"{compression_count} compression event{'s' if compression_count != 1 else ''} "
                "exist for this conversation; earlier active context has been condensed into a rolling summary."
            ),
            recommendation=None,
            signals=signals,
        )

    return ConversationInspectorIntelligence(
        status="healthy",
        status_label="Healthy",
        severity="success",
        explanation="Based on estimated token usage, available context headroom is healthy and no action is required.",
        recommendation=None,
        signals=signals,
    )


def build_conversation_inspector_snapshot(
    *,
    settings: Settings,
    conversation: Conversation | None,
    active_conversation: dict[str, Any],
    recent_requests: list[dict[str, Any]],
    compression_history: list[dict[str, Any]],
    active_request_count: int = 0,
) -> dict[str, object]:
    """Build the inspector view model from the existing dashboard snapshot inputs."""

    if conversation is None:
        intelligence = classify_conversation_intelligence(
            conversation_available=False,
            context_enabled=settings.context.enabled,
            compression_enabled=settings.compression.enabled,
            usage_percent=None,
            estimated_tokens=None,
            context_window_tokens=None,
            warning_threshold_percent=settings.context.warning_threshold_percent,
            compression_threshold_percent=settings.context.compression_threshold_percent,
            compression_count=0,
        )
        return {
            "conversation_id": None,
            "overview": _empty_overview(),
            "intelligence": intelligence.to_dict(),
        }

    conversation_id = conversation.conversation_id
    context = active_conversation.get("context") if isinstance(active_conversation, dict) else None
    context = context if isinstance(context, dict) else {}
    latest_request = _latest_conversation_request(
        recent_requests,
        conversation_id=conversation_id,
        conversation_started_at=conversation.created_at,
    )
    compression_count = _compression_count(compression_history, conversation_id)
    state = _conversation_state(
        active_request_count=active_request_count,
        latest_request=latest_request,
        conversation_id=conversation_id,
    )
    usage_percent = _number_or_none(context.get("usage_percent"))
    estimated_tokens = _int_or_none(context.get("estimated_tokens"))
    context_window_tokens = _int_or_none(context.get("context_window_tokens"))
    context_source_label = _string_or_none(context.get("context_window_source_label"))
    request_count = _request_count(
        recent_requests,
        conversation_id=conversation_id,
        conversation_started_at=conversation.created_at,
    )
    duration_ms = max(0, int((_ensure_timezone(conversation.updated_at) - _ensure_timezone(conversation.created_at)).total_seconds() * 1000))
    overview = {
        "conversation_id": conversation_id,
        "state": state,
        "state_label": _state_label(state),
        "model": _string_or_none(active_conversation.get("model_name")) or _string_or_none(latest_request.get("model")),
        "client_source": _string_or_none(latest_request.get("client_host")) or _string_or_none(latest_request.get("client")),
        "endpoint": _string_or_none(latest_request.get("endpoint")),
        "request_type": _request_type(latest_request),
        "message_count": len(conversation.messages),
        "request_count": request_count,
        "estimated_tokens": estimated_tokens,
        "context_window_tokens": context_window_tokens,
        "context_window_source_label": context_source_label,
        "context_usage_percent": usage_percent,
        "compression_count": compression_count,
        "started_at": _ensure_timezone(conversation.created_at).isoformat(),
        "last_activity_at": _ensure_timezone(conversation.updated_at).isoformat(),
        "duration_ms": duration_ms,
    }
    intelligence = classify_conversation_intelligence(
        conversation_available=True,
        context_enabled=settings.context.enabled,
        compression_enabled=settings.compression.enabled,
        usage_percent=usage_percent,
        estimated_tokens=estimated_tokens,
        context_window_tokens=context_window_tokens,
        warning_threshold_percent=settings.context.warning_threshold_percent,
        compression_threshold_percent=settings.context.compression_threshold_percent,
        compression_count=compression_count,
        context_window_source_label=context_source_label,
    )
    return {
        "conversation_id": conversation_id,
        "overview": overview,
        "intelligence": intelligence.to_dict(),
    }


def _empty_overview() -> dict[str, object]:
    return {
        "conversation_id": None,
        "state": "unavailable",
        "state_label": "Unavailable",
        "model": None,
        "client_source": None,
        "endpoint": None,
        "request_type": None,
        "message_count": None,
        "request_count": None,
        "estimated_tokens": None,
        "context_window_tokens": None,
        "context_window_source_label": None,
        "context_usage_percent": None,
        "compression_count": 0,
        "started_at": None,
        "last_activity_at": None,
        "duration_ms": None,
    }


def _latest_conversation_request(
    recent_requests: list[dict[str, Any]],
    *,
    conversation_id: str,
    conversation_started_at: datetime,
) -> dict[str, Any]:
    for request in recent_requests:
        if not isinstance(request, dict):
            continue
        if request.get("endpoint") not in _GENERATION_ENDPOINTS:
            continue
        request_conversation_id = _string_or_none(request.get("conversation_id"))
        if request_conversation_id is not None and request_conversation_id != conversation_id:
            continue
        if request_conversation_id is None:
            timestamp = _parse_timestamp(request.get("timestamp"))
            if timestamp is not None and timestamp < _ensure_timezone(conversation_started_at):
                continue
        return request
    return {}


def _request_count(
    recent_requests: list[dict[str, Any]],
    *,
    conversation_id: str,
    conversation_started_at: datetime,
) -> int:
    count = 0
    started_at = _ensure_timezone(conversation_started_at)
    for request in recent_requests:
        if not isinstance(request, dict):
            continue
        if request.get("endpoint") not in _GENERATION_ENDPOINTS:
            continue
        request_conversation_id = _string_or_none(request.get("conversation_id"))
        if request_conversation_id is not None:
            if request_conversation_id == conversation_id:
                count += 1
            continue
        timestamp = _parse_timestamp(request.get("timestamp"))
        if timestamp is None or timestamp >= started_at:
            count += 1
    return count


def _conversation_state(*, active_request_count: int, latest_request: dict[str, Any], conversation_id: str) -> str:
    if active_request_count > 0:
        latest_conversation_id = _string_or_none(latest_request.get("conversation_id"))
        if latest_conversation_id is None or latest_conversation_id == conversation_id:
            return "active"
    status_code = _int_or_none(latest_request.get("status_code"))
    if status_code is not None and status_code >= 400:
        return "failed"
    if status_code is not None:
        return "completed"
    return "idle"


def _state_label(state: str) -> str:
    return {
        "active": "Active",
        "completed": "Completed",
        "failed": "Failed",
        "idle": "Idle",
        "unavailable": "Unavailable",
    }.get(state, "Unavailable")


def _request_type(request: dict[str, Any]) -> str | None:
    endpoint = _string_or_none(request.get("endpoint"))
    if endpoint == "/api/chat":
        return "Chat"
    if endpoint == "/api/generate":
        return "Generate"
    return None


def _compression_count(compression_history: list[dict[str, Any]], conversation_id: str) -> int:
    for item in compression_history:
        if item.get("conversation_id") == conversation_id:
            return _int_or_none(item.get("compression_count")) or 0
    return 0


def _signal(label: str, value: str) -> dict[str, str]:
    return {"label": label, "value": value}


def _format_percent(value: float | None) -> str:
    if value is None:
        return _PLACEHOLDER
    return f"{value:g}%"


def _format_tokens(value: int | None) -> str:
    if value is None:
        return _PLACEHOLDER
    return f"{value:,} tokens"


def _safe_text(value: str | None) -> str:
    if value is None or not value.strip():
        return _PLACEHOLDER
    return value.strip()


def _number_or_none(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, 2)


def _int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return _ensure_timezone(value)
    if not isinstance(value, str):
        return None
    try:
        return _ensure_timezone(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError:
        return None


def _ensure_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
