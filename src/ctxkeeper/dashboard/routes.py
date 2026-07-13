from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import time
from typing import Any

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..config import Settings
from ..context.compression_manager import ROLLING_SUMMARY_PREFIX
from ..context.context_meter import ContextMeter
from ..context.context_monitor import ContextMonitor
from ..context.conversation_store import Conversation, conversation_store
from ..diagnostics.metrics import metrics_store
from .insights import build_dashboard_insights
from .intelligence import DashboardMetrics, HealthAssessment, HealthEngine, HealthStatus
from .recommendations import build_recommendations
from .snapshots import ConversationSnapshotProvider
from .timeline import TimelineEvent
from .template import render_dashboard_html
from .trends import RollingTrends

_ACTIVE_MODEL_ENDPOINTS = {
    "/api/chat",
    "/api/generate",
    "/v1/chat/completions",
    "/v1/completions",
}
_MODEL_WARMUP_SUCCESSFUL_REQUEST_GRACE = 1
_PERSISTENT_LATENCY_SAMPLE_COUNT = 2


@dataclass(frozen=True)
class ModelWarmupState:
    """Detected model transition state derived from applicable request history."""

    active: bool
    model_name: str | None = None
    previous_model_name: str | None = None
    successful_requests: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "active": self.active,
            "model_name": self.model_name,
            "previous_model_name": self.previous_model_name,
            "successful_requests": self.successful_requests,
            "grace_successful_requests": _MODEL_WARMUP_SUCCESSFUL_REQUEST_GRACE,
        }


async def _check_ollama(settings: Settings) -> dict[str, object]:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.ollama.base_url.rstrip('/')}/api/version")
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        if response.status_code == 200:
            version = response.json().get("version", "unknown")
            return {"status": "online", "version": version, "latency_ms": latency_ms}
        return {"status": "warning", "version": None, "latency_ms": latency_ms, "detail": f"HTTP {response.status_code}"}
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {"status": "offline", "version": None, "latency_ms": latency_ms, "detail": str(exc)}


def _create_context_monitor(settings: Settings) -> ContextMonitor:
    return ContextMonitor(
        store=conversation_store,
        meter=_create_context_meter(settings),
    )


def _create_context_meter(settings: Settings) -> ContextMeter:
    return ContextMeter(
        context_window_tokens=settings.context.default_context_window_tokens,
        warning_threshold_percent=settings.context.warning_threshold_percent,
        compression_threshold_percent=settings.context.compression_threshold_percent,
    )


def _create_conversation_snapshot_provider(settings: Settings) -> ConversationSnapshotProvider:
    return ConversationSnapshotProvider(
        store=conversation_store,
        meter=_create_context_meter(settings),
    )


def _compression_history(conversations: list[Conversation]) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    for conversation in conversations:
        summaries = [
            message
            for message in conversation.messages
            if message.role == "system" and message.content.startswith(ROLLING_SUMMARY_PREFIX)
        ]
        if not summaries:
            continue
        latest = max(summaries, key=lambda message: message.timestamp)
        history.append(
            {
                "conversation_id": conversation.conversation_id,
                "compression_count": len(summaries),
                "last_compressed_at": latest.timestamp.isoformat(),
            }
        )
    return sorted(history, key=lambda item: str(item["last_compressed_at"]), reverse=True)


def _dashboard_intelligence(
    *,
    ollama_status: dict[str, object],
    context_usage_percent: float,
    request_metrics: dict[str, Any],
    recent_requests: list[dict[str, Any]],
    active_conversation: dict[str, Any],
    active_model: str | None,
    warmup_state: ModelWarmupState,
) -> dict[str, Any]:
    latency_values = [
        float(request["latency_ms"])
        for request in recent_requests
        if isinstance(request.get("latency_ms"), int | float)
    ]
    average_latency_ms = round(sum(latency_values) / len(latency_values), 2) if latency_values else 0.0
    recent_error_count = sum(
        1
        for request in recent_requests
        if isinstance(request.get("status_code"), int) and int(request["status_code"]) >= 400
    )
    metrics = DashboardMetrics(
        proxy_online=True,
        ollama_online=ollama_status.get("status") == "online",
        context_percent=context_usage_percent,
        average_latency_ms=_health_latency_ms(
            recent_requests=recent_requests,
            active_model=active_model,
        ),
        active_requests=len(recent_requests),
    )
    health = _apply_model_warmup_health(
        health=HealthEngine().evaluate_metrics(metrics),
        metrics=metrics,
        warmup_state=warmup_state,
    )
    trends = _request_trends(recent_requests)
    timeline_events = _timeline_events(recent_requests)
    conversation_risk = _conversation_risk(active_conversation)
    insights = [insight.to_dict() for insight in build_dashboard_insights(metrics, active_errors=recent_error_count)]
    if warmup_state.active:
        model_name = warmup_state.model_name or "selected model"
        insights.insert(
            1,
            {
                "code": "model_warming",
                "message": f"Model warming: Ollama is loading {model_name}.",
                "severity": "info",
            },
        )

    return {
        "health": {
            **health.to_dict(),
            "message": _health_message(health, warmup_state),
            "label": "Model warming" if health.reasons and health.reasons[0] == "model_warming" else None,
        },
        "insights": insights,
        "recommendations": [recommendation.to_dict() for recommendation in build_recommendations(metrics)],
        "trends": {
            "request_direction": trends.trend_direction(),
            "average_request_rate": trends.average_request_rate(),
            "average_latency_ms": trends.average_latency(),
        },
        "timeline": [event.to_dict() for event in timeline_events],
        "conversation_risk": conversation_risk,
        "source": {
            "recent_request_count": len(recent_requests),
            "total_errors": request_metrics.get("total_errors", 0),
            "health_latency_ms": metrics.average_latency_ms,
            "raw_average_latency_ms": average_latency_ms,
            "model_warmup": warmup_state.to_dict(),
        },
    }


def _request_trends(recent_requests: list[dict[str, Any]]) -> RollingTrends:
    trends = RollingTrends(max_samples=max(len(recent_requests), 2))
    for request in reversed(recent_requests):
        latency_ms = request.get("latency_ms")
        if not isinstance(latency_ms, int | float):
            continue
        trends.record_request(
            latency_ms=float(latency_ms),
            timestamp=_parse_timestamp(request.get("timestamp")),
        )
    return trends


def _timeline_events(recent_requests: list[dict[str, Any]]) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for request in recent_requests[:20]:
        timestamp = _parse_timestamp(request.get("timestamp"))
        if timestamp is None:
            continue
        endpoint = request.get("endpoint") or "unknown endpoint"
        status_code = request.get("status_code") or "unknown status"
        latency_ms = request.get("latency_ms")
        latency_text = f" in {latency_ms} ms" if isinstance(latency_ms, int | float) else ""
        events.append(TimelineEvent(message=f"{endpoint} returned {status_code}{latency_text}", timestamp=timestamp))
    return events


def _conversation_risk(active_conversation: dict[str, Any]) -> dict[str, Any]:
    context = active_conversation.get("context")
    if not isinstance(context, dict):
        return {
            "status": "none",
            "message": "No active conversation.",
            "indicators": [],
        }

    indicators: list[dict[str, str]] = []
    if context.get("compression_threshold_exceeded"):
        status = "critical"
        message = "Active conversation is at compression threshold."
        indicators.append({"code": "compression_threshold", "label": "Compression threshold reached", "severity": "critical"})
    elif context.get("warning_threshold_exceeded"):
        status = "warning"
        message = "Active conversation is approaching compression."
        indicators.append({"code": "warning_threshold", "label": "Context warning threshold reached", "severity": "warning"})
    else:
        status = "healthy"
        message = "Active conversation context is within normal range."
        indicators.append({"code": "context_available", "label": "Context within normal range", "severity": "positive"})

    if active_conversation.get("rolling_summary"):
        indicators.append({"code": "rolling_summary", "label": "Rolling summary available", "severity": "info"})

    return {
        "status": status,
        "message": message,
        "usage_percent": context.get("usage_percent", 0),
        "estimated_tokens": context.get("estimated_tokens", 0),
        "context_window_tokens": context.get("context_window_tokens", 0),
        "indicators": indicators,
    }


def _health_message(assessment: HealthAssessment, warmup_state: ModelWarmupState | None = None) -> str:
    if assessment.reasons and assessment.reasons[0] == "model_warming":
        model_name = warmup_state.model_name if warmup_state and warmup_state.model_name else "the selected model"
        return f"Ollama is loading {model_name}; the first response after switching models can be slower."

    reason_messages = {
        "nominal": "All monitored systems are operating normally.",
        "proxy_offline": "ContextKeeper proxy is offline.",
        "ollama_offline": "Ollama is unavailable.",
        "context_critical": "Context usage is at a critical level.",
        "latency_critical": "Request latency is critically high.",
        "request_load_critical": "Request load is critically high.",
        "context_warning": "Context usage is nearing compression.",
        "latency_warning": "Request latency is elevated.",
        "request_load_warning": "Request load is high.",
        "context_busy": "Context usage is elevated.",
        "latency_busy": "Request latency is above normal.",
        "active_requests": "Recent request activity detected.",
        "model_warming": "Ollama is loading the selected model.",
    }
    return reason_messages.get(assessment.reasons[0], "Dashboard health evaluated.")


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
    return value


def _is_applicable_model_request(request: object) -> bool:
    if not isinstance(request, dict):
        return False
    endpoint = request.get("endpoint")
    model = request.get("model")
    return endpoint in _ACTIVE_MODEL_ENDPOINTS and isinstance(model, str) and bool(model)


def _applicable_model_requests(recent_requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [request for request in recent_requests if _is_applicable_model_request(request)]


def _is_successful_request(request: dict[str, Any]) -> bool:
    status_code = request.get("status_code")
    return isinstance(status_code, int) and 200 <= status_code < 400


def _detect_model_warmup(recent_requests: list[dict[str, Any]]) -> ModelWarmupState:
    applicable_requests = _applicable_model_requests(recent_requests)
    if not applicable_requests:
        return ModelWarmupState(active=False)

    current_model = applicable_requests[0]["model"]
    successful_requests = 0
    previous_model: str | None = None
    for request in applicable_requests:
        model = request["model"]
        if model == current_model:
            if _is_successful_request(request):
                successful_requests += 1
            continue
        previous_model = model
        break

    if previous_model is None:
        return ModelWarmupState(
            active=False,
            model_name=current_model,
            successful_requests=successful_requests,
        )

    active = _is_successful_request(applicable_requests[0]) and successful_requests <= _MODEL_WARMUP_SUCCESSFUL_REQUEST_GRACE
    return ModelWarmupState(
        active=active,
        model_name=current_model,
        previous_model_name=previous_model,
        successful_requests=successful_requests,
    )


def _current_model_latency_values(
    recent_requests: list[dict[str, Any]],
    active_model: str | None,
) -> list[float]:
    if not active_model:
        return []

    values: list[float] = []
    for request in _applicable_model_requests(recent_requests):
        if request.get("model") != active_model:
            if values:
                break
            continue
        latency_ms = request.get("latency_ms")
        if isinstance(latency_ms, int | float):
            values.append(float(latency_ms))
    return values


def _persistent_latency_for_health(latency_values: list[float]) -> float:
    if len(latency_values) < _PERSISTENT_LATENCY_SAMPLE_COUNT:
        return 0.0

    critical_values = [
        value
        for value in latency_values
        if value >= HealthEngine.CRITICAL_LATENCY_MS
    ]
    if len(critical_values) >= _PERSISTENT_LATENCY_SAMPLE_COUNT:
        return round(sum(critical_values) / len(critical_values), 2)

    warning_values = [
        value
        for value in latency_values
        if value >= HealthEngine.WARNING_LATENCY_MS
    ]
    if len(warning_values) >= _PERSISTENT_LATENCY_SAMPLE_COUNT:
        return round(sum(warning_values) / len(warning_values), 2)

    busy_values = [
        value
        for value in latency_values
        if value >= HealthEngine.BUSY_LATENCY_MS
    ]
    if len(busy_values) >= _PERSISTENT_LATENCY_SAMPLE_COUNT:
        return round(sum(busy_values) / len(busy_values), 2)

    return 0.0


def _health_latency_ms(
    *,
    recent_requests: list[dict[str, Any]],
    active_model: str | None,
) -> float:
    current_model_values = _current_model_latency_values(recent_requests, active_model)
    if current_model_values:
        return _persistent_latency_for_health(current_model_values)

    fallback_values = [
        float(request["latency_ms"])
        for request in recent_requests
        if isinstance(request.get("latency_ms"), int | float)
    ]
    return _persistent_latency_for_health(fallback_values)


def _apply_model_warmup_health(
    *,
    health: HealthAssessment,
    metrics: DashboardMetrics,
    warmup_state: ModelWarmupState,
) -> HealthAssessment:
    if not warmup_state.active:
        return health
    if health.status not in {HealthStatus.HEALTHY, HealthStatus.BUSY}:
        return health
    return HealthAssessment(
        status=HealthStatus.BUSY,
        reasons=["model_warming", *[reason for reason in health.reasons if reason != "nominal"]],
        indicators=metrics.to_dict(),
    )


def _latest_applicable_model(request_metrics: dict[str, Any]) -> str | None:
    recent_requests = request_metrics.get("recent_requests", [])
    if isinstance(recent_requests, list):
        for request in _applicable_model_requests(recent_requests):
            model = request.get("model")
            if isinstance(model, str):
                return model

    last_endpoint = request_metrics.get("last_endpoint")
    last_model = request_metrics.get("last_model")
    if last_endpoint in _ACTIVE_MODEL_ENDPOINTS and isinstance(last_model, str) and last_model:
        return last_model
    return None


def build_dashboard_status(
    *,
    settings: Settings,
    metrics_snapshot: dict[str, Any],
    ollama_status: dict[str, object],
) -> dict[str, Any]:
    request_metrics = metrics_snapshot["requests"]
    recent_requests = list(request_metrics.get("recent_requests", []))
    active_model = _latest_applicable_model(request_metrics)
    warmup_state = _detect_model_warmup(recent_requests)
    context_scan = _create_context_monitor(settings).scan()
    compression_history = _compression_history(conversation_store.all())
    context_stats = context_scan.statistics
    active_conversation = _create_conversation_snapshot_provider(settings).active_snapshot(
        model_name=active_model
    )
    active_conversation_data = active_conversation.to_dict()

    return {
        "contextkeeper": {
            "status": "running",
            "app": settings.app.name,
        },
        "ollama": ollama_status,
        "requests": {
            "total_count": request_metrics.get("total_requests", 0),
            "recent_count": len(recent_requests),
            "latest": recent_requests[:10],
            "total_errors": request_metrics.get("total_errors", 0),
            "last_endpoint": request_metrics.get("last_endpoint"),
            "last_model": active_model,
            "last_observed_model": request_metrics.get("last_model"),
            "last_latency_ms": request_metrics.get("last_latency_ms"),
            "last_status_code": request_metrics.get("last_status_code"),
            "model_transition": warmup_state.to_dict(),
        },
        "context": {
            "usage_percent": context_stats.max_usage_percent,
            "average_usage_percent": context_stats.average_usage_percent,
            "conversation_count": context_stats.conversation_count,
            "message_count": context_stats.message_count,
            "estimated_tokens": context_stats.total_estimated_tokens,
            "warning_count": context_stats.warning_count,
            "compression_candidate_count": context_stats.compression_candidate_count,
        },
        "compression": {
            "count": sum(item["compression_count"] for item in compression_history),
            "history": compression_history[:10],
        },
        "active_conversation": active_conversation_data,
        "intelligence": _dashboard_intelligence(
            ollama_status=ollama_status,
            context_usage_percent=context_stats.max_usage_percent,
            request_metrics=request_metrics,
            recent_requests=recent_requests,
            active_conversation=active_conversation_data,
            active_model=active_model,
            warmup_state=warmup_state,
        ),
        "system": metrics_snapshot["system"],
        "refresh_interval_ms": settings.dashboard.refresh_interval_ms or 1000,
    }


def create_dashboard_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health(request: Request) -> dict[str, object]:
        snapshot = metrics_store.snapshot()
        requests = snapshot["requests"]
        recent = requests.get("recent_requests", [])
        client_count = len({r.get("client_host") for r in recent if r.get("client_host")})
        last_model = _latest_applicable_model(requests)
        warmup_state = _detect_model_warmup(list(recent) if isinstance(recent, list) else [])
        ollama_status = await _check_ollama(settings)
        client_status = "online" if client_count > 0 else "waiting"
        model_status = "busy" if warmup_state.active else "active" if last_model else "waiting"
        return {
            "app": settings.app.name,
            "status": "running",
            "proxy_url": str(request.base_url).rstrip("/"),
            "ollama_base_url": settings.ollama.base_url,
            "connections": {
                "client": {"status": client_status, "count": client_count},
                "proxy": {"status": "online", "listen": f"{settings.server.host}:{settings.server.port}"},
                "ollama": ollama_status,
                "model": {"status": model_status, "name": last_model},
            },
        }

    @router.get("/metrics")
    async def metrics() -> dict[str, object]:
        return metrics_store.snapshot()

    @router.get("/dashboard/data")
    async def dashboard_data() -> dict[str, Any]:
        return build_dashboard_status(
            settings=settings,
            metrics_snapshot=metrics_store.snapshot(),
            ollama_status=await _check_ollama(settings),
        )

    @router.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        return render_dashboard_html(settings)
    return router
