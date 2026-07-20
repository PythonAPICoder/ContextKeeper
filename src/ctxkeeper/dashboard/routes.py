from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import time
from threading import Lock
from typing import Any

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..config import Settings
from ..context.compression_manager import ROLLING_SUMMARY_PREFIX
from ..context.context_meter import ContextMeter
from ..context.context_monitor import ContextMonitor
from ..context.conversation_store import Conversation, conversation_store
from ..diagnostics.activity import activity_manager
from ..diagnostics.metrics import metrics_store
from ..model_context import ContextWindowResolution, active_context_window_overrides, resolve_context_window
from .config_persistence import (
    ConfigurationPersistenceError,
    ConfigurationPersistenceService,
)
from .insights import build_dashboard_insights
from .inspector import build_conversation_inspector_snapshot
from .intelligence import DashboardMetrics, HealthAssessment, HealthEngine, HealthStatus
from .recommendations import build_recommendations
from .settings_snapshot import (
    RuntimeSettingsUpdate,
    RuntimeSettingsUpdateError,
    build_dashboard_settings_snapshot,
    update_runtime_settings,
)
from .snapshots import ConversationSnapshotProvider
from .timeline import LIVE_CONVERSATION_TIMELINE_MAX_EVENTS, TimelineEvent, build_live_conversation_timeline
from .template import render_dashboard_html
from .trends import RollingTrends

logger = logging.getLogger("ctxkeeper.dashboard")

_ACTIVE_MODEL_ENDPOINTS = {
    "/api/chat",
    "/api/generate",
    "/v1/chat/completions",
    "/v1/completions",
}
_MODEL_WARMUP_SUCCESSFUL_REQUEST_GRACE = 1
_PERSISTENT_LATENCY_SAMPLE_COUNT = 2
_CONTEXT_HISTORY_MAX_SAMPLES = 30
_DASHBOARD_SELECTION_LOG_LOCK = Lock()
_LAST_DASHBOARD_SELECTION_SIGNATURE: tuple[object, ...] | None = None


class ContextHistoryStore:
    """Bounded in-memory context usage history for dashboard trend rendering."""

    def __init__(self, *, max_samples: int = _CONTEXT_HISTORY_MAX_SAMPLES) -> None:
        if max_samples < 2:
            raise ValueError("max_samples must be at least 2")
        self.max_samples = max_samples
        self._samples: dict[str, deque[dict[str, Any]]] = {}
        self._lock = Lock()

    def record(
        self,
        *,
        conversation_id: str,
        usage_percent: float,
        estimated_tokens: int,
        context_window_tokens: int,
    ) -> list[dict[str, Any]]:
        sample = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "usage_percent": round(usage_percent, 2),
            "estimated_tokens": estimated_tokens,
            "context_window_tokens": context_window_tokens,
        }
        with self._lock:
            samples = self._samples.setdefault(conversation_id, deque(maxlen=self.max_samples))
            samples.append(sample)
            return list(samples)

    def samples(self, conversation_id: str | None) -> list[dict[str, Any]]:
        if conversation_id is None:
            return []
        with self._lock:
            return list(self._samples.get(conversation_id, ()))

    def clear(self) -> None:
        with self._lock:
            self._samples.clear()


context_history_store = ContextHistoryStore()


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


@dataclass(frozen=True)
class ActiveGenerationState:
    """Coherent active/completed generation request selected for dashboard state."""

    model_name: str | None
    endpoint: str | None
    request_sequence: int | None
    generation_sequence: int | None
    context_window_resolution: ContextWindowResolution
    status: str
    observed_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        context_window_state = _context_window_state_for_model(
            self.context_window_resolution,
            active_model=self.model_name,
        )
        waiting_for_model = context_window_state == "waiting"
        return {
            "model_name": self.model_name,
            "endpoint": self.endpoint,
            "request_sequence": self.request_sequence,
            "generation_sequence": self.generation_sequence,
            "context_window_tokens": None if waiting_for_model else self.context_window_resolution.tokens,
            "context_window_source": None if waiting_for_model else self.context_window_resolution.source,
            "context_window_source_label": None if waiting_for_model else self.context_window_resolution.source_label,
            "context_window_label": None if waiting_for_model else self.context_window_resolution.label,
            "context_window_state": context_window_state,
            "status": self.status,
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


def _create_context_monitor(settings: Settings, *, context_window_tokens: int | None = None) -> ContextMonitor:
    return ContextMonitor(
        store=conversation_store,
        meter=_create_context_meter(settings, context_window_tokens=context_window_tokens),
    )


def _create_context_meter(
    settings: Settings,
    *,
    model_name: str | None = None,
    context_window_tokens: int | None = None,
) -> ContextMeter:
    resolved_context_window_tokens = context_window_tokens
    if resolved_context_window_tokens is None:
        resolved_context_window_tokens = _context_window_resolution_for_model(settings, model_name).tokens
    return ContextMeter(
        context_window_tokens=resolved_context_window_tokens,
        warning_threshold_percent=settings.context.warning_threshold_percent,
        compression_threshold_percent=settings.context.compression_threshold_percent,
    )


def _create_conversation_snapshot_provider(
    settings: Settings,
    *,
    model_name: str | None = None,
    context_window_tokens: int | None = None,
) -> ConversationSnapshotProvider:
    return ConversationSnapshotProvider(
        store=conversation_store,
        meter=_create_context_meter(settings, model_name=model_name, context_window_tokens=context_window_tokens),
    )


def _context_window_resolution_for_model(
    settings: Settings,
    model_name: str | None,
) -> ContextWindowResolution:
    return resolve_context_window(
        settings,
        model_name=model_name,
    )


def _context_window_tokens_for_model(settings: Settings, model_name: str | None) -> tuple[int, str]:
    resolution = _context_window_resolution_for_model(settings, model_name)
    return resolution.tokens, resolution.source


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


def _conversation_by_id(conversations: list[Conversation], conversation_id: str | None) -> Conversation | None:
    if conversation_id is None:
        return None
    return next((conversation for conversation in conversations if conversation.conversation_id == conversation_id), None)


def _dashboard_intelligence(
    *,
    ollama_status: dict[str, object],
    context_usage_percent: float,
    request_metrics: dict[str, Any],
    recent_requests: list[dict[str, Any]],
    active_conversation: dict[str, Any],
    active_model: str | None,
    warmup_state: ModelWarmupState,
    active_request_count: int,
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
        active_requests=active_request_count,
    )
    health = _apply_recent_error_health(
        health=HealthEngine().evaluate_metrics(metrics),
        metrics=metrics,
        recent_error_count=recent_error_count,
    )
    health = _apply_model_warmup_health(
        health=health,
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
            "active_request_count": active_request_count,
            "health_latency_ms": metrics.average_latency_ms,
            "raw_average_latency_ms": average_latency_ms,
            "latency_health_basis": "explicit_service_latency_only",
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


def _build_instrument_panel(
    *,
    settings: Settings,
    system_metrics: dict[str, Any],
    active_conversation: dict[str, Any],
    compression_history: list[dict[str, Any]],
    active_model: str | None,
    context_window_resolution: ContextWindowResolution,
) -> dict[str, Any]:
    context_usage = _context_usage_instrument(
        settings=settings,
        active_conversation=active_conversation,
        active_model=active_model,
        context_window_resolution=context_window_resolution,
    )
    return {
        "cpu": _cpu_instrument(system_metrics),
        "gpu": _gpu_instrument(system_metrics),
        "memory": _memory_instrument(system_metrics),
        "context_usage": context_usage,
        "context_trend": _context_trend_instrument(settings=settings, context_usage=context_usage),
        "compression_status": _compression_status_instrument(
            settings=settings,
            active_conversation=active_conversation,
            compression_history=compression_history,
            context_usage=context_usage,
        ),
    }


def _instrument_detail_line(
    text: str | None,
    *,
    fallback: str,
    title: str | None = None,
    **extra: str | None,
) -> dict[str, str]:
    display = _string_or_none(text) or fallback
    full_title = _string_or_none(title) or display
    line = {"text": display, "title": full_title}
    for key, value in extra.items():
        normalized = _string_or_none(value)
        if normalized is not None:
            line[key] = normalized
    return line


def _instrument_detail_lines(*lines: dict[str, str]) -> list[dict[str, str]]:
    normalized = list(lines[:3])
    while len(normalized) < 3:
        normalized.append(_instrument_detail_line(None, fallback="Not reported"))
    return normalized


def _context_window_source_line(
    resolution: ContextWindowResolution,
    *,
    active_model: str | None,
) -> str:
    if active_model:
        return f"{active_model} • {resolution.source_label}"
    return f"{resolution.source_label} context window"


def _context_window_source_detail_line(
    resolution: ContextWindowResolution,
    *,
    active_model: str | None,
    fallback: str,
) -> dict[str, str]:
    text = _context_window_source_line(resolution, active_model=active_model)
    if active_model:
        return _instrument_detail_line(
            text,
            fallback=fallback,
            title=text,
            kind="model_source",
            model_name=active_model,
            source_label=resolution.source_label,
        )
    return _instrument_detail_line(text, fallback=fallback, title=text)


def _context_window_state_for_model(
    resolution: ContextWindowResolution,
    *,
    active_model: str | None,
) -> str:
    if not active_model:
        return "waiting"
    if resolution.source == "configured":
        return "pre-defined"
    if resolution.source == "detected":
        return "discovered"
    return "default"


def _cpu_instrument(system_metrics: dict[str, Any]) -> dict[str, Any]:
    cpu = system_metrics.get("cpu")
    detail = cpu if isinstance(cpu, dict) else {}
    usage_percent = _number_or_none(detail.get("usage_percent", system_metrics.get("cpu_percent")))
    available = bool(detail.get("available", usage_percent is not None)) and usage_percent is not None
    name = _string_or_none(detail.get("name"))
    thread_count = _int_or_none(detail.get("thread_count"))
    if thread_count is None:
        thread_count = _int_or_none(detail.get("logical_processor_count"))
    temperature_c = _number_or_none(detail.get("temperature_c"))
    status = _string_or_none(detail.get("status")) or _resource_status(usage_percent)
    status_label = _string_or_none(detail.get("status_label")) or _resource_status_label(usage_percent)
    if not available:
        message = "CPU utilization telemetry is unavailable."
    elif name and thread_count is not None:
        message = f"{name} · {_format_thread_count(thread_count)}"
    elif name:
        message = name
    elif thread_count is not None:
        message = _format_thread_count(thread_count)
    else:
        message = "Processor details unavailable."
    return {
        "available": available,
        "usage_percent": usage_percent,
        "status": status if available else "unavailable",
        "status_label": status_label if available else "Unavailable",
        "name": name,
        "logical_processor_count": thread_count,
        "thread_count": thread_count,
        "temperature_c": temperature_c,
        "message": message,
        "detail_lines": _instrument_detail_lines(
            _instrument_detail_line(name, fallback="CPU identity unavailable", title=name),
            _instrument_detail_line(_format_thread_count(thread_count), fallback="Thread count unavailable"),
            _instrument_detail_line(_format_temperature(temperature_c), fallback="Temperature unavailable"),
        ),
    }


def _memory_instrument(system_metrics: dict[str, Any]) -> dict[str, Any]:
    memory = system_metrics.get("memory")
    detail = memory if isinstance(memory, dict) else {}
    usage_percent = _number_or_none(detail.get("usage_percent", system_metrics.get("ram_percent")))
    used_gb = _number_or_none(detail.get("used_gb", system_metrics.get("ram_used_gb")))
    total_gb = _number_or_none(detail.get("total_gb", system_metrics.get("ram_total_gb")))
    available = bool(detail.get("available", usage_percent is not None)) and usage_percent is not None
    status = _string_or_none(detail.get("status")) or _resource_status(usage_percent)
    status_label = _string_or_none(detail.get("status_label")) or _resource_status_label(usage_percent)
    if not available:
        message = "System memory telemetry is unavailable."
    elif used_gb is not None and total_gb is not None:
        message = f"{_format_number(used_gb)} / {_format_number(total_gb)} GB used"
    else:
        message = "Memory utilization available; capacity detail unavailable."
    return {
        "available": available,
        "usage_percent": usage_percent,
        "used_gb": used_gb,
        "total_gb": total_gb,
        "status": status if available else "unavailable",
        "status_label": status_label if available else "Unavailable",
        "message": message,
        "detail_lines": _instrument_detail_lines(
            _instrument_detail_line(
                f"{_format_number(used_gb)} GB used" if used_gb is not None else None,
                fallback="Used memory unavailable",
            ),
            _instrument_detail_line(
                f"{_format_number(total_gb)} GB total" if total_gb is not None else None,
                fallback="Total memory unavailable",
            ),
            _instrument_detail_line(status_label if available else "Memory status unavailable", fallback="Memory status unavailable"),
        ),
    }


def _gpu_instrument(system_metrics: dict[str, Any]) -> dict[str, Any]:
    gpu_detail = system_metrics.get("gpu_detail")
    legacy_gpu = system_metrics.get("gpu")
    if isinstance(gpu_detail, dict):
        detail = gpu_detail
    elif isinstance(legacy_gpu, dict):
        detail = {
            "available": True,
            "telemetry_status": "available",
            "status": _resource_status(_number_or_none(legacy_gpu.get("gpu_percent"))),
            "status_label": _resource_status_label(_number_or_none(legacy_gpu.get("gpu_percent"))),
            "name": legacy_gpu.get("name"),
            "usage_percent": legacy_gpu.get("gpu_percent"),
            "vram_used_gb": legacy_gpu.get("vram_used_gb"),
            "vram_total_gb": legacy_gpu.get("vram_total_gb"),
            "temperature_c": legacy_gpu.get("temperature_c"),
            "message": "GPU telemetry is available.",
        }
    else:
        detail = {
            "available": False,
            "telemetry_status": "unavailable",
            "status": "unavailable",
            "status_label": "Unavailable",
            "message": "GPU telemetry is unavailable.",
        }

    usage_percent = _number_or_none(detail.get("usage_percent"))
    vram_used_gb = _number_or_none(detail.get("vram_used_gb"))
    vram_total_gb = _number_or_none(detail.get("vram_total_gb"))
    temperature_c = _number_or_none(detail.get("temperature_c"))
    available = bool(detail.get("available"))
    telemetry_status = _string_or_none(detail.get("telemetry_status")) or ("available" if available else "unavailable")
    status = _string_or_none(detail.get("status")) or _resource_status(usage_percent)
    status_label = _string_or_none(detail.get("status_label")) or _resource_status_label(usage_percent)
    name = _string_or_none(detail.get("name"))
    vram_line = _gpu_vram_line(vram_used_gb=vram_used_gb, vram_total_gb=vram_total_gb)
    if not available:
        message = _string_or_none(detail.get("message")) or "GPU telemetry is unavailable."
    else:
        detail_parts = [name or "GPU"]
        if vram_line is not None:
            detail_parts.append(vram_line)
        if temperature_c is not None:
            detail_parts.append(_format_temperature(temperature_c))
        message = " · ".join(detail_parts)
    return {
        "available": available,
        "telemetry_status": telemetry_status,
        "usage_percent": usage_percent,
        "status": status if available else telemetry_status,
        "status_label": status_label if available else status_label,
        "name": name,
        "vram_used_gb": vram_used_gb,
        "vram_total_gb": vram_total_gb,
        "temperature_c": temperature_c,
        "message": message,
        "detail_lines": _instrument_detail_lines(
            _instrument_detail_line(
                name,
                fallback="GPU unavailable" if not available else "GPU identity unavailable",
                title=name,
            ),
            _instrument_detail_line(vram_line, fallback="VRAM unavailable"),
            _instrument_detail_line(_format_temperature(temperature_c), fallback="Temperature unavailable"),
        ),
    }


def _context_usage_instrument(
    *,
    settings: Settings,
    active_conversation: dict[str, Any],
    active_model: str | None,
    context_window_resolution: ContextWindowResolution,
) -> dict[str, Any]:
    warning_threshold = settings.context.warning_threshold_percent
    compression_threshold = settings.context.compression_threshold_percent
    context_window_tokens = context_window_resolution.tokens
    context_window_source = context_window_resolution.source
    context_window_state = _context_window_state_for_model(
        context_window_resolution,
        active_model=active_model,
    )
    waiting_for_model = settings.context.enabled and context_window_state == "waiting"
    context_window_source_label = None if waiting_for_model else context_window_resolution.source_label
    context_window_label = None if waiting_for_model else context_window_resolution.label
    header_badge = "--" if waiting_for_model else context_window_resolution.label
    header_badge_title = (
        "Waiting for first conversational model"
        if waiting_for_model
        else (
            f"Effective context window: {context_window_tokens:,} tokens "
            f"({context_window_resolution.source_label})"
        )
    )
    base = {
        "warning_threshold_percent": warning_threshold,
        "compression_threshold_percent": compression_threshold,
        "context_window_state": context_window_state,
        "context_window_source": None if waiting_for_model else context_window_source,
        "context_window_source_label": context_window_source_label,
        "context_window_label": context_window_label,
        "header_badge": header_badge,
        "header_badge_title": header_badge_title,
        "active_model": active_model,
    }
    if not settings.context.enabled:
        return {
            **base,
            "state": "disabled",
            "status": "disabled",
            "status_label": "Off",
            "conversation_id": active_conversation.get("conversation_id"),
            "usage_percent": None,
            "estimated_tokens": None,
            "context_window_tokens": context_window_tokens,
            "message": "Context Tracking OFF",
            "detail_lines": _instrument_detail_lines(
                _instrument_detail_line("Context Tracking OFF", fallback="Context Tracking OFF"),
                _context_window_source_detail_line(
                    context_window_resolution,
                    active_model=None,
                    fallback="Context window unavailable",
                ),
                _instrument_detail_line(
                    _format_thresholds(warning_threshold, compression_threshold),
                    fallback="Thresholds unavailable",
                ),
            ),
        }

    context = active_conversation.get("context")
    if not isinstance(context, dict):
        return {
            **base,
            "state": "no_active_conversation",
            "status": "waiting",
            "status_label": "Waiting",
            "conversation_id": None,
            "usage_percent": 0.0,
            "estimated_tokens": None,
            "context_window_tokens": None if waiting_for_model else context_window_tokens,
            "message": "No active conversation",
            "detail_lines": _instrument_detail_lines(
                _instrument_detail_line("No active conversation", fallback="No active conversation"),
                _instrument_detail_line("Waiting for model...", fallback="Waiting for model...")
                if waiting_for_model
                else _context_window_source_detail_line(
                    context_window_resolution,
                    active_model=active_model,
                    fallback="Context window unavailable",
                ),
                _instrument_detail_line(
                    _format_thresholds(warning_threshold, compression_threshold),
                    fallback="Thresholds unavailable",
                ),
            ),
        }

    usage_percent = _number_or_none(context.get("usage_percent"))
    estimated_tokens = _int_or_none(context.get("estimated_tokens"))
    active_context_window_tokens = _int_or_none(context.get("context_window_tokens")) or context_window_tokens
    if active_context_window_tokens <= 0:
        return {
            **base,
            "state": "unknown_model_context_size",
            "status": "unavailable",
            "status_label": "Unknown",
            "conversation_id": active_conversation.get("conversation_id"),
            "usage_percent": usage_percent,
            "estimated_tokens": estimated_tokens,
            "context_window_tokens": None,
            "message": "Model context-window size is unknown.",
            "detail_lines": _instrument_detail_lines(
                _instrument_detail_line(
                    f"{estimated_tokens:,} estimated tokens" if estimated_tokens is not None else None,
                    fallback="Token estimate unavailable",
                ),
                _context_window_source_detail_line(
                    context_window_resolution,
                    active_model=active_model,
                    fallback="Context window unknown",
                ),
                _instrument_detail_line(
                    _format_thresholds(warning_threshold, compression_threshold),
                    fallback="Thresholds unavailable",
                ),
            ),
        }

    status = _context_status(usage_percent, warning_threshold, compression_threshold)
    status_label = {
        "healthy": "Healthy",
        "moderate": "Moderate",
        "warning": "Warning",
        "critical": "Critical",
        "unavailable": "Unavailable",
    }[status]
    if context_window_source == "configured":
        window_message = "pre-defined model context window"
    elif context_window_source == "detected":
        window_message = "discovered model context window"
    elif active_model:
        window_message = "default context window; model-specific size unavailable"
    else:
        window_message = "default context window; active model unknown"
    token_message = (
        f"{estimated_tokens:,} / {active_context_window_tokens:,} estimated tokens"
        if estimated_tokens is not None
        else f"{active_context_window_tokens:,} token context window"
    )
    return {
        **base,
        "state": "active",
        "status": status,
        "status_label": status_label,
        "conversation_id": active_conversation.get("conversation_id"),
        "usage_percent": usage_percent,
        "estimated_tokens": estimated_tokens,
        "context_window_tokens": active_context_window_tokens,
        "message": f"{token_message} · {window_message}",
        "detail_lines": _instrument_detail_lines(
            _instrument_detail_line(
                _format_context_tokens(estimated_tokens, active_context_window_tokens),
                fallback="Token estimate unavailable",
            ),
            _context_window_source_detail_line(
                context_window_resolution,
                active_model=active_model,
                fallback="Active model unknown",
            ),
            _instrument_detail_line(
                _format_thresholds(warning_threshold, compression_threshold),
                fallback="Thresholds unavailable",
            ),
        ),
    }


def _context_trend_instrument(*, settings: Settings, context_usage: dict[str, Any]) -> dict[str, Any]:
    thresholds = {
        "warning_threshold_percent": settings.context.warning_threshold_percent,
        "compression_threshold_percent": settings.context.compression_threshold_percent,
        "context_window_tokens": context_usage.get("context_window_tokens"),
        "context_window_source": context_usage.get("context_window_source"),
        "context_window_source_label": context_usage.get("context_window_source_label"),
        "context_window_label": context_usage.get("context_window_label"),
        "context_window_state": context_usage.get("context_window_state"),
    }
    if context_usage.get("state") == "disabled":
        return {
            **thresholds,
            "state": "disabled",
            "current_usage_percent": None,
            "samples": [],
            "message": "Context tracking is disabled.",
            "estimate_label": "Estimate unavailable",
        }
    conversation_id = _string_or_none(context_usage.get("conversation_id"))
    usage_percent = _number_or_none(context_usage.get("usage_percent"))
    estimated_tokens = _int_or_none(context_usage.get("estimated_tokens"))
    context_window_tokens = _int_or_none(context_usage.get("context_window_tokens"))
    if conversation_id is None or usage_percent is None or estimated_tokens is None or context_window_tokens is None:
        return {
            **thresholds,
            "state": "empty",
            "status": "waiting",
            "status_label": "Waiting",
            "current_usage_percent": usage_percent,
            "samples": [],
            "message": "Awaiting context history.",
            "estimate_label": "Estimate unavailable",
        }

    samples = context_history_store.record(
        conversation_id=conversation_id,
        usage_percent=usage_percent,
        estimated_tokens=estimated_tokens,
        context_window_tokens=context_window_tokens,
    )
    state = "ready" if len(samples) >= 2 else "collecting"
    return {
        **thresholds,
        "state": state,
        "status": state,
        "status_label": "Ready" if state == "ready" else "Collecting",
        "current_usage_percent": usage_percent,
        "samples": samples,
        "message": "Context trend ready." if state == "ready" else "Awaiting context history.",
        "estimate_label": "Estimate unavailable",
    }


def _compression_status_instrument(
    *,
    settings: Settings,
    active_conversation: dict[str, Any],
    compression_history: list[dict[str, Any]],
    context_usage: dict[str, Any],
) -> dict[str, Any]:
    threshold = settings.context.compression_threshold_percent
    event_count = sum(_int_or_none(item.get("compression_count")) or 0 for item in compression_history)
    active_conversation_id = _string_or_none(active_conversation.get("conversation_id"))
    active_history = next(
        (item for item in compression_history if item.get("conversation_id") == active_conversation_id),
        None,
    )
    usage_percent = _number_or_none(context_usage.get("usage_percent"))
    proximity_percent = None
    if usage_percent is not None and threshold > 0:
        proximity_percent = round(min(100.0, (usage_percent / threshold) * 100), 2)

    if not settings.compression.enabled:
        state = "disabled"
        label = "Off"
        message = "Compression OFF"
    elif not settings.context.enabled:
        state = "unavailable"
        label = "Unavailable"
        message = "Compression requires context tracking to be enabled."
    elif context_usage.get("state") in {"no_active_conversation", "empty"}:
        state = "ready"
        label = "Ready"
        message = "Waiting for context threshold"
    elif context_usage.get("status") == "critical":
        state = "approaching"
        label = "Approaching"
        message = "Active context is at or beyond the configured compression threshold."
    elif context_usage.get("status") == "warning":
        state = "approaching"
        label = "Approaching"
        message = "Active context is approaching the configured compression threshold."
    elif active_history is not None:
        state = "completed"
        label = "Completed"
        message = "A compression summary exists for the active conversation."
    else:
        state = "available"
        label = "Available"
        message = "Compression is enabled and ready if context reaches threshold."

    return {
        "state": state,
        "status": state,
        "status_label": label,
        "threshold_percent": threshold,
        "event_count": event_count,
        "active_conversation_event_count": _int_or_none(active_history.get("compression_count")) if active_history else 0,
        "proximity_percent": proximity_percent,
        "context_window_tokens": context_usage.get("context_window_tokens"),
        "context_window_source": context_usage.get("context_window_source"),
        "context_window_source_label": context_usage.get("context_window_source_label"),
        "context_window_label": context_usage.get("context_window_label"),
        "context_window_state": context_usage.get("context_window_state"),
        "message": message,
        "detail_lines": _compression_detail_lines(
            state=state,
            message=message,
            threshold=threshold,
            event_count=event_count,
        ),
    }


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


def _resource_status(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if value >= 90:
        return "critical"
    if value >= 75:
        return "warning"
    if value >= 55:
        return "moderate"
    return "healthy"


def _resource_status_label(value: float | None) -> str:
    return {
        "healthy": "Healthy",
        "moderate": "Moderate",
        "warning": "Warning",
        "critical": "Critical",
        "unavailable": "Unavailable",
    }[_resource_status(value)]


def _context_status(usage_percent: float | None, warning_threshold: int, compression_threshold: int) -> str:
    if usage_percent is None:
        return "unavailable"
    if usage_percent >= compression_threshold:
        return "critical"
    if usage_percent >= warning_threshold:
        return "warning"
    moderate_threshold = max(1.0, warning_threshold * 0.65)
    if usage_percent >= moderate_threshold:
        return "moderate"
    return "healthy"


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


def _format_thread_count(value: int | None) -> str | None:
    if value is None:
        return None
    return f"{value} thread{'s' if value != 1 else ''}"


def _format_temperature(value: float | None) -> str | None:
    if value is None:
        return None
    return f"{_format_number(value)} °C"


def _gpu_vram_line(*, vram_used_gb: float | None, vram_total_gb: float | None) -> str | None:
    if vram_used_gb is not None and vram_total_gb is not None:
        return f"{_format_number(vram_used_gb)} / {_format_number(vram_total_gb)} GB VRAM"
    if vram_total_gb is not None:
        return f"{_format_number(vram_total_gb)} GB VRAM"
    if vram_used_gb is not None:
        return f"{_format_number(vram_used_gb)} GB VRAM used"
    return None


def _format_context_window(tokens: int | None) -> str | None:
    if tokens is None or tokens <= 0:
        return None
    return f"{tokens:,} token window"


def _format_context_tokens(estimated_tokens: int | None, context_window_tokens: int | None) -> str | None:
    if estimated_tokens is not None and context_window_tokens is not None and context_window_tokens > 0:
        return f"{estimated_tokens:,} / {context_window_tokens:,} tokens"
    if estimated_tokens is not None:
        return f"{estimated_tokens:,} estimated tokens"
    return _format_context_window(context_window_tokens)


def _format_thresholds(warning_threshold: int, compression_threshold: int) -> str:
    return f"Warn {warning_threshold}% • Compress {compression_threshold}%"


def _compression_detail_lines(*, state: str, message: str, threshold: int, event_count: int) -> list[dict[str, str]]:
    event_line = f"{event_count} compression event{'s' if event_count != 1 else ''}"
    if state == "disabled":
        return _instrument_detail_lines(
            _instrument_detail_line("Compression OFF", fallback="Compression OFF"),
            _instrument_detail_line(f"Threshold {threshold}%", fallback="Threshold unavailable"),
            _instrument_detail_line(event_line, fallback="Compression events unavailable"),
        )
    return _instrument_detail_lines(
        _instrument_detail_line(f"Threshold {threshold}%", fallback="Threshold unavailable"),
        _instrument_detail_line(event_line, fallback="Compression events unavailable"),
        _instrument_detail_line(message, fallback="Compression status unavailable", title=message),
    )


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
        "active_requests": "Active generation request in progress.",
        "model_warming": "Ollama is loading the selected model.",
        "recent_request_errors": "Recent request errors detected.",
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
    applicable_requests = [request for request in recent_requests if _is_applicable_model_request(request)]
    if not applicable_requests:
        return applicable_requests

    oldest = datetime.min.replace(tzinfo=timezone.utc)
    return [
        request
        for _, request in sorted(
            enumerate(applicable_requests),
            key=lambda item: (
                _request_generation_sequence(item[1]) or -1,
                _request_sequence(item[1]) or -1,
                _parse_timestamp(item[1].get("timestamp")) or oldest,
                -item[0],
            ),
            reverse=True,
        )
    ]


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
    service_latency_fields = (
        "service_latency_ms",
        "time_to_first_token_ms",
        "first_token_latency_ms",
    )
    latency_values: list[float] = []
    for request in _applicable_model_requests(recent_requests):
        if active_model and request.get("model") != active_model:
            if latency_values:
                break
            continue
        for field in service_latency_fields:
            latency_ms = request.get(field)
            if isinstance(latency_ms, int | float):
                latency_values.append(float(latency_ms))
                break
    return _persistent_latency_for_health(latency_values)


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


def _apply_recent_error_health(
    *,
    health: HealthAssessment,
    metrics: DashboardMetrics,
    recent_error_count: int,
) -> HealthAssessment:
    if recent_error_count <= 0:
        return health
    if health.status in {HealthStatus.CRITICAL, HealthStatus.WARNING}:
        return health
    return HealthAssessment(
        status=HealthStatus.WARNING,
        reasons=["recent_request_errors", *[reason for reason in health.reasons if reason != "nominal"]],
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


def _request_sequence(request: dict[str, Any] | None) -> int | None:
    if not isinstance(request, dict):
        return None
    return _int_or_none(request.get("sequence"))


def _request_generation_sequence(request: dict[str, Any] | None) -> int | None:
    if not isinstance(request, dict):
        return None
    return _int_or_none(request.get("generation_sequence"))


def _latest_applicable_generation_request(request_metrics: dict[str, Any]) -> dict[str, Any] | None:
    recent_requests = request_metrics.get("recent_requests", [])
    if isinstance(recent_requests, list):
        applicable = _applicable_model_requests(recent_requests)
        if applicable:
            return applicable[0]

    last_endpoint = request_metrics.get("last_endpoint")
    last_model = request_metrics.get("last_model")
    if last_endpoint in _ACTIVE_MODEL_ENDPOINTS and isinstance(last_model, str) and last_model:
        return {
            "endpoint": last_endpoint,
            "model": last_model,
            "sequence": _int_or_none(request_metrics.get("last_sequence")),
            "generation_sequence": _int_or_none(request_metrics.get("last_generation_sequence")),
        }
    return None


def _active_generation_state(
    *,
    settings: Settings,
    request_metrics: dict[str, Any],
    recent_requests: list[dict[str, Any]],
    activity_snapshot: object | None,
) -> ActiveGenerationState:
    active_candidate: ActiveGenerationState | None = None
    active_request_count = getattr(activity_snapshot, "active_request_count", 0)
    if isinstance(active_request_count, int) and active_request_count > 0:
        active_model = getattr(activity_snapshot, "active_model", None)
        model_name = active_model if isinstance(active_model, str) and active_model else None
        active_generation_sequence = _int_or_none(getattr(activity_snapshot, "active_generation_sequence", None))
        active_override = active_context_window_overrides.latest_for_generation_sequence(active_generation_sequence)
        if active_override is None:
            active_override = active_context_window_overrides.latest_for_model(model_name)
        resolution = active_override or _context_window_resolution_for_model(settings, model_name)
        endpoint = getattr(activity_snapshot, "active_endpoint", None)
        observed_at = getattr(activity_snapshot, "updated_at", None)
        active_candidate = ActiveGenerationState(
            model_name=model_name,
            endpoint=endpoint if isinstance(endpoint, str) and endpoint else None,
            request_sequence=None,
            generation_sequence=active_generation_sequence,
            context_window_resolution=resolution,
            status="active" if model_name else "active_unknown",
            observed_at=observed_at if isinstance(observed_at, datetime) else None,
        )

    completed_candidate: ActiveGenerationState | None = None
    latest_request = _latest_applicable_generation_request(request_metrics)
    if latest_request is not None:
        model_name = _string_or_none(latest_request.get("model"))
        resolution = _context_window_resolution_for_model(settings, model_name)
        completed_candidate = ActiveGenerationState(
            model_name=model_name,
            endpoint=_string_or_none(latest_request.get("endpoint")),
            request_sequence=_request_sequence(latest_request),
            generation_sequence=_request_generation_sequence(latest_request),
            context_window_resolution=resolution,
            status="completed",
            observed_at=_parse_timestamp(latest_request.get("timestamp")),
        )

    selected = _select_generation_state(active_candidate, completed_candidate)
    if selected is not None:
        rejected = completed_candidate if selected is active_candidate else active_candidate
        if rejected is not None:
            _log_dashboard_candidate_rejection(rejected, selected)
        return selected

    latest_activity_model = getattr(activity_snapshot, "latest_model", None)
    model_name = latest_activity_model if isinstance(latest_activity_model, str) and latest_activity_model else None
    resolution = _context_window_resolution_for_model(settings, model_name)
    return ActiveGenerationState(
        model_name=model_name,
        endpoint=None,
        request_sequence=None,
        generation_sequence=None,
        context_window_resolution=resolution,
        status="activity_history" if model_name else "none",
    )


def _select_generation_state(
    active: ActiveGenerationState | None,
    completed: ActiveGenerationState | None,
) -> ActiveGenerationState | None:
    if active is None:
        return completed
    if completed is None:
        return active

    active_generation_sequence = active.generation_sequence
    completed_generation_sequence = completed.generation_sequence
    if active_generation_sequence is not None and completed_generation_sequence is not None:
        return active if active_generation_sequence >= completed_generation_sequence else completed

    if active_generation_sequence is not None:
        return active
    if completed_generation_sequence is not None:
        return completed

    return active


def _state_age_seconds(state: ActiveGenerationState) -> float | None:
    if state.observed_at is None:
        return None
    return max(0.0, round((datetime.now(timezone.utc) - state.observed_at).total_seconds(), 2))


def _log_dashboard_candidate_rejection(
    rejected: ActiveGenerationState,
    selected: ActiveGenerationState,
) -> None:
    rejected_key = rejected.generation_sequence if rejected.generation_sequence is not None else rejected.request_sequence
    selected_key = selected.generation_sequence if selected.generation_sequence is not None else selected.request_sequence
    reason = "older_generation_sequence"
    if rejected.generation_sequence is None or selected.generation_sequence is None:
        reason = "legacy_unsequenced_candidate"
    logger.info(
        "B4.8_DIAG event=dashboard_candidate_rejected candidate_model=%s candidate_gen_seq=%s selected_model=%s selected_gen_seq=%s rejection_reason=%s candidate_status=%s selected_status=%s candidate_age_seconds=%s selected_age_seconds=%s candidate_key=%s selected_key=%s",
        rejected.model_name,
        rejected.generation_sequence,
        selected.model_name,
        selected.generation_sequence,
        reason,
        rejected.status,
        selected.status,
        _state_age_seconds(rejected),
        _state_age_seconds(selected),
        rejected_key,
        selected_key,
    )


def _log_dashboard_selection(state: ActiveGenerationState) -> None:
    global _LAST_DASHBOARD_SELECTION_SIGNATURE
    context_window_state = _context_window_state_for_model(
        state.context_window_resolution,
        active_model=state.model_name,
    )
    waiting_for_model = context_window_state == "waiting"
    signature = (
        state.generation_sequence,
        state.request_sequence,
        state.endpoint,
        state.model_name,
        context_window_state,
        None if waiting_for_model else state.context_window_resolution.source,
        None if waiting_for_model else state.context_window_resolution.tokens,
        state.status,
    )
    with _DASHBOARD_SELECTION_LOG_LOCK:
        if signature == _LAST_DASHBOARD_SELECTION_SIGNATURE:
            return
        _LAST_DASHBOARD_SELECTION_SIGNATURE = signature
    logger.info(
        "B4.8_DIAG event=dashboard_selection gen_seq=%s request_seq=%s endpoint=%s model=%s status=%s context_state=%s context_source=%s context_tokens=%s context_label=%s",
        state.generation_sequence,
        state.request_sequence,
        state.endpoint,
        state.model_name,
        state.status,
        context_window_state,
        None if waiting_for_model else state.context_window_resolution.source,
        None if waiting_for_model else state.context_window_resolution.tokens,
        None if waiting_for_model else state.context_window_resolution.label,
    )


def _latest_observed_model(
    request_metrics: dict[str, Any],
    activity_snapshot: object | None = None,
) -> str | None:
    active_request_count = getattr(activity_snapshot, "active_request_count", 0)
    if isinstance(active_request_count, int) and active_request_count > 0:
        active_model = getattr(activity_snapshot, "active_model", None)
        return active_model if isinstance(active_model, str) and active_model else None

    latest_metrics_model = _latest_applicable_model(request_metrics)
    if latest_metrics_model:
        return latest_metrics_model

    latest_activity_model = getattr(activity_snapshot, "latest_model", None)
    if isinstance(latest_activity_model, str) and latest_activity_model:
        return latest_activity_model
    return None


def _dashboard_model_state(activity_snapshot: object | None, model: str | None) -> str:
    active_request_count = getattr(activity_snapshot, "active_request_count", 0)
    if isinstance(active_request_count, int) and active_request_count > 0:
        return "active_known" if model else "active_unknown"
    return "observed" if model else "none"


def _dashboard_model_label(model: str | None, model_state: str) -> str:
    if model:
        return model
    if model_state == "active_unknown":
        return "Unknown model"
    return "No model observed yet"


def build_dashboard_status(
    *,
    settings: Settings,
    metrics_snapshot: dict[str, Any],
    ollama_status: dict[str, object],
) -> dict[str, Any]:
    activity_manager.observe_ollama_status(ollama_status.get("status"))
    activity_snapshot = activity_manager.snapshot()
    request_metrics = metrics_snapshot["requests"]
    recent_requests = list(request_metrics.get("recent_requests", []))
    active_generation = _active_generation_state(
        settings=settings,
        request_metrics=request_metrics,
        recent_requests=recent_requests,
        activity_snapshot=activity_snapshot,
    )
    _log_dashboard_selection(active_generation)
    active_model = active_generation.model_name
    model_state = _dashboard_model_state(activity_snapshot, active_model)
    model_label = _dashboard_model_label(active_model, model_state)
    warmup_state = _detect_model_warmup(recent_requests)
    context_window_resolution = active_generation.context_window_resolution
    context_window_state = _context_window_state_for_model(context_window_resolution, active_model=active_model)
    conversations = conversation_store.all()
    context_scan = _create_context_monitor(
        settings,
        context_window_tokens=context_window_resolution.tokens,
    ).scan(conversations)
    compression_history = _compression_history(conversations)
    context_stats = context_scan.statistics
    active_conversation = _create_conversation_snapshot_provider(
        settings,
        model_name=active_model,
        context_window_tokens=context_window_resolution.tokens,
    ).active_snapshot(model_name=active_model, conversations=conversations)
    active_conversation_data = active_conversation.to_dict()
    if isinstance(active_conversation_data.get("context"), dict):
        active_conversation_data["context"]["context_window_state"] = context_window_state
        if context_window_state == "waiting":
            active_conversation_data["context"]["context_window_tokens"] = None
            active_conversation_data["context"]["context_window_source"] = None
            active_conversation_data["context"]["context_window_source_label"] = None
            active_conversation_data["context"]["context_window_label"] = None
        else:
            active_conversation_data["context"]["context_window_source"] = context_window_resolution.source
            active_conversation_data["context"]["context_window_source_label"] = context_window_resolution.source_label
            active_conversation_data["context"]["context_window_label"] = context_window_resolution.label
    system_metrics = metrics_snapshot["system"]
    live_timeline_events = build_live_conversation_timeline(
        conversations=conversations,
        active_conversation=active_conversation_data,
        recent_requests=recent_requests,
        activity_snapshot=activity_snapshot,
    )
    active_conversation_record = _conversation_by_id(
        conversations,
        _string_or_none(active_conversation_data.get("conversation_id")),
    )
    conversation_inspector = build_conversation_inspector_snapshot(
        settings=settings,
        conversation=active_conversation_record,
        active_conversation=active_conversation_data,
        recent_requests=recent_requests,
        compression_history=compression_history,
        active_request_count=activity_snapshot.active_request_count,
    )

    return {
        "contextkeeper": {
            "status": "running",
            "app": settings.app.name,
        },
        "ollama": ollama_status,
        "activity": activity_snapshot.to_dict(),
        "requests": {
            "total_count": request_metrics.get("total_requests", 0),
            "recent_count": len(recent_requests),
            "latest": recent_requests[:10],
            "total_errors": request_metrics.get("total_errors", 0),
            "last_endpoint": request_metrics.get("last_endpoint"),
            "last_model": active_model,
            "model_state": model_state,
            "model_label": model_label,
            "last_observed_model": request_metrics.get("last_model"),
            "last_latency_ms": request_metrics.get("last_latency_ms"),
            "last_status_code": request_metrics.get("last_status_code"),
            "model_transition": warmup_state.to_dict(),
            "active_generation": active_generation.to_dict(),
        },
        "context": {
            "usage_percent": context_stats.max_usage_percent,
            "average_usage_percent": context_stats.average_usage_percent,
            "conversation_count": context_stats.conversation_count,
            "message_count": context_stats.message_count,
            "estimated_tokens": context_stats.total_estimated_tokens,
            "warning_count": context_stats.warning_count,
            "compression_candidate_count": context_stats.compression_candidate_count,
            "context_window_tokens": None if context_window_state == "waiting" else context_window_resolution.tokens,
            "context_window_source": None if context_window_state == "waiting" else context_window_resolution.source,
            "context_window_source_label": None if context_window_state == "waiting" else context_window_resolution.source_label,
            "context_window_label": None if context_window_state == "waiting" else context_window_resolution.label,
            "context_window_state": context_window_state,
        },
        "compression": {
            "count": sum(item["compression_count"] for item in compression_history),
            "history": compression_history[:10],
        },
        "active_conversation": active_conversation_data,
        "conversation_timeline": {
            "events": [event.to_dict() for event in live_timeline_events],
            "max_events": LIVE_CONVERSATION_TIMELINE_MAX_EVENTS,
            "conversation_id": active_conversation_data.get("conversation_id"),
        },
        "conversation_inspector": conversation_inspector,
        "intelligence": _dashboard_intelligence(
            ollama_status=ollama_status,
            context_usage_percent=context_stats.max_usage_percent,
            request_metrics=request_metrics,
            recent_requests=recent_requests,
            active_conversation=active_conversation_data,
            active_model=active_model,
            warmup_state=warmup_state,
            active_request_count=activity_snapshot.active_request_count,
        ),
        "system": system_metrics,
        "instrument_panel": _build_instrument_panel(
            settings=settings,
            system_metrics=system_metrics,
            active_conversation=active_conversation_data,
            compression_history=compression_history,
            active_model=active_model,
            context_window_resolution=context_window_resolution,
        ),
        "refresh_interval_ms": settings.dashboard.refresh_interval_ms or 1000,
    }


def create_dashboard_router(
    settings: Settings,
    *,
    configuration_persistence: ConfigurationPersistenceService | None = None,
) -> APIRouter:
    router = APIRouter()
    persistence = configuration_persistence or ConfigurationPersistenceService()

    def persisted_settings_for_snapshot() -> Settings:
        try:
            return persistence.read_persisted_settings()
        except ConfigurationPersistenceError as exc:
            logger.warning(
                "Configuration settings read failed code=%s status_code=%s",
                exc.code,
                exc.status_code,
            )
            raise HTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
            ) from exc

    @router.get("/health")
    async def health(request: Request) -> dict[str, object]:
        snapshot = metrics_store.snapshot()
        requests = snapshot["requests"]
        recent = requests.get("recent_requests", [])
        client_count = len({r.get("client_host") for r in recent if r.get("client_host")})
        warmup_state = _detect_model_warmup(list(recent) if isinstance(recent, list) else [])
        ollama_status = await _check_ollama(settings)
        activity_manager.observe_ollama_status(ollama_status.get("status"))
        activity_snapshot = activity_manager.snapshot()
        active_generation = _active_generation_state(
            settings=settings,
            request_metrics=requests,
            recent_requests=list(recent) if isinstance(recent, list) else [],
            activity_snapshot=activity_snapshot,
        )
        last_model = active_generation.model_name
        model_state = _dashboard_model_state(activity_snapshot, last_model)
        model_label = _dashboard_model_label(last_model, model_state)
        client_status = "online" if client_count > 0 else "waiting"
        if model_state == "active_unknown":
            model_status = "unknown"
        else:
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
                "model": {"status": model_status, "name": last_model, "label": model_label},
            },
            "activity": activity_snapshot.to_dict(),
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

    @router.get("/api/dashboard/settings")
    def dashboard_settings() -> dict[str, object]:
        persisted_settings = persisted_settings_for_snapshot()
        return build_dashboard_settings_snapshot(settings, persisted_settings).to_dict()

    @router.patch("/api/dashboard/settings")
    def update_dashboard_settings(payload: RuntimeSettingsUpdate) -> dict[str, object]:
        try:
            persisted_settings = persisted_settings_for_snapshot()
            return update_runtime_settings(
                settings,
                payload,
                persisted_settings=persisted_settings,
            ).to_dict()
        except RuntimeSettingsUpdateError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    @router.put("/api/dashboard/settings/config")
    def persist_dashboard_settings(
        payload: dict[str, object] = Body(...),
    ) -> dict[str, object]:
        try:
            result = persistence.persist(payload)
        except ConfigurationPersistenceError as exc:
            logger.warning(
                "Configuration persistence failed code=%s status_code=%s",
                exc.code,
                exc.status_code,
            )
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
        except Exception as exc:
            logger.exception("Unexpected configuration persistence failure")
            raise HTTPException(
                status_code=500,
                detail="The configuration could not be saved safely.",
            ) from exc

        logger.info(
            "Configuration persistence succeeded setting_count=%s configuration_created=%s",
            len(result.persisted_setting_ids),
            result.configuration_created,
        )
        snapshot = build_dashboard_settings_snapshot(
            settings,
            result.persisted_settings,
        )
        return {
            "status": "saved",
            "persisted_setting_ids": list(result.persisted_setting_ids),
            "configuration_created": result.configuration_created,
            "settings": snapshot.to_dict(),
        }

    @router.api_route(
        "/api/dashboard/settings/config",
        methods=["GET", "POST", "PATCH", "DELETE", "HEAD", "OPTIONS"],
        include_in_schema=False,
    )
    async def dashboard_configuration_persistence_method_not_allowed() -> None:
        raise HTTPException(
            status_code=405,
            detail="Method Not Allowed",
            headers={"Allow": "PUT"},
        )

    @router.api_route("/api/dashboard/settings", methods=["POST", "PUT", "DELETE"])
    async def dashboard_settings_read_only() -> None:
        raise HTTPException(status_code=405, detail="Use PATCH to update runtime settings.")

    @router.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        return render_dashboard_html(settings)
    return router
