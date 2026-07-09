from __future__ import annotations

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
from .intelligence import DashboardMetrics, HealthAssessment, HealthEngine
from .recommendations import build_recommendations
from .snapshots import ConversationSnapshotProvider
from .timeline import TimelineEvent
from .template import render_dashboard_html
from .trends import RollingTrends


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
        average_latency_ms=average_latency_ms,
        active_requests=len(recent_requests),
    )
    health = HealthEngine().evaluate_metrics(metrics)
    trends = _request_trends(recent_requests)
    timeline_events = _timeline_events(recent_requests)
    conversation_risk = _conversation_risk(active_conversation)

    return {
        "health": {
            **health.to_dict(),
            "message": _health_message(health),
        },
        "insights": [insight.to_dict() for insight in build_dashboard_insights(metrics, active_errors=recent_error_count)],
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


def _health_message(assessment: HealthAssessment) -> str:
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


def build_dashboard_status(
    *,
    settings: Settings,
    metrics_snapshot: dict[str, Any],
    ollama_status: dict[str, object],
) -> dict[str, Any]:
    request_metrics = metrics_snapshot["requests"]
    recent_requests = list(request_metrics.get("recent_requests", []))
    context_scan = _create_context_monitor(settings).scan()
    compression_history = _compression_history(conversation_store.all())
    context_stats = context_scan.statistics
    active_conversation = _create_conversation_snapshot_provider(settings).active_snapshot(
        model_name=request_metrics.get("last_model")
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
            "last_model": request_metrics.get("last_model"),
            "last_latency_ms": request_metrics.get("last_latency_ms"),
            "last_status_code": request_metrics.get("last_status_code"),
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
        last_model = requests.get("last_model")
        ollama_status = await _check_ollama(settings)
        client_status = "online" if client_count > 0 else "waiting"
        model_status = "active" if last_model else "waiting"
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
