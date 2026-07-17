from datetime import datetime, timezone

import pytest

from ctxkeeper.config import Settings
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.context.conversation_store import conversation_store
from ctxkeeper.dashboard.inspector import classify_conversation_intelligence
from ctxkeeper.dashboard.routes import build_dashboard_status
from ctxkeeper.diagnostics.activity import activity_manager
from ctxkeeper.model_context import active_context_window_overrides, model_context_window_cache


@pytest.fixture(autouse=True)
def clear_dashboard_inspector_state() -> None:
    activity_manager.reset()
    conversation_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    yield
    conversation_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    activity_manager.reset()


def _classify(
    *,
    usage_percent: float | None,
    context_enabled: bool = True,
    compression_enabled: bool = True,
    compression_count: int = 0,
    conversation_available: bool = True,
) -> dict[str, object]:
    estimated_tokens = None if usage_percent is None else int(usage_percent * 10)
    return classify_conversation_intelligence(
        conversation_available=conversation_available,
        context_enabled=context_enabled,
        compression_enabled=compression_enabled,
        usage_percent=usage_percent,
        estimated_tokens=estimated_tokens,
        context_window_tokens=1000 if estimated_tokens is not None else None,
        warning_threshold_percent=70,
        compression_threshold_percent=90,
        compression_count=compression_count,
        context_window_source_label="Default",
    ).to_dict()


def _metrics_snapshot(recent_requests: list[dict[str, object]] | None = None) -> dict[str, object]:
    requests = list(recent_requests or [])
    latest = requests[0] if requests else {}
    return {
        "requests": {
            "total_requests": len(requests),
            "total_errors": sum(
                1
                for request in requests
                if isinstance(request.get("status_code"), int) and int(request["status_code"]) >= 400
            ),
            "last_sequence": latest.get("sequence", len(requests) if requests else 0),
            "last_generation_sequence": latest.get("generation_sequence"),
            "last_endpoint": latest.get("endpoint"),
            "last_model": latest.get("model"),
            "last_latency_ms": latest.get("latency_ms"),
            "last_status_code": latest.get("status_code"),
            "recent_requests": requests,
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }


def test_conversation_inspector_payload_maps_available_conversation_metadata() -> None:
    conversation = conversation_store.create("inspect-overview")
    conversation.created_at = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    conversation_store.append_message("inspect-overview", "user", "hello")
    conversation_store.append_message("inspect-overview", "assistant", "response")
    conversation.updated_at = datetime(2026, 7, 15, 12, 0, 5, tzinfo=timezone.utc)
    recent_requests = [
        {
            "sequence": 1,
            "generation_sequence": 1,
            "timestamp": "2026-07-15T12:00:05+00:00",
            "endpoint": "/api/chat",
            "model": "<model&name>",
            "client_host": "qa-client.local",
            "status_code": 200,
            "latency_ms": 125.0,
            "conversation_id": "inspect-overview",
        }
    ]

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=_metrics_snapshot(recent_requests),
        ollama_status={"status": "online", "version": "test", "latency_ms": 1.0},
    )

    inspector = status["conversation_inspector"]
    overview = inspector["overview"]
    assert inspector["conversation_id"] == "inspect-overview"
    assert overview["conversation_id"] == "inspect-overview"
    assert overview["state"] == "completed"
    assert overview["model"] == "<model&name>"
    assert overview["client_source"] == "qa-client.local"
    assert overview["endpoint"] == "/api/chat"
    assert overview["request_type"] == "Chat"
    assert overview["message_count"] == 2
    assert overview["request_count"] == 1
    assert overview["estimated_tokens"] is not None
    assert overview["context_window_tokens"] is not None
    assert overview["context_usage_percent"] is not None
    assert overview["compression_count"] == 0
    assert overview["last_activity_at"] == "2026-07-15T12:00:05+00:00"
    assert overview["duration_ms"] == 5000


def test_conversation_inspector_payload_reports_missing_values_safely() -> None:
    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=_metrics_snapshot(),
        ollama_status={"status": "online", "version": "test", "latency_ms": 1.0},
    )

    inspector = status["conversation_inspector"]
    assert inspector["conversation_id"] is None
    assert inspector["overview"]["conversation_id"] is None
    assert inspector["overview"]["state"] == "unavailable"
    assert inspector["intelligence"]["status"] == "insufficient_data"


def test_conversation_inspector_healthy_classification_below_warning() -> None:
    intelligence = _classify(usage_percent=20)

    assert intelligence["status"] == "healthy"
    assert intelligence["severity"] == "success"
    assert "healthy" in intelligence["explanation"]


def test_conversation_inspector_just_below_warning_threshold_is_healthy() -> None:
    assert _classify(usage_percent=69.99)["status"] == "healthy"


def test_conversation_inspector_exact_warning_threshold_is_warning() -> None:
    intelligence = _classify(usage_percent=70)

    assert intelligence["status"] == "warning"
    assert intelligence["severity"] == "warning"


def test_conversation_inspector_just_below_compression_threshold_remains_warning() -> None:
    assert _classify(usage_percent=89.99)["status"] == "warning"


def test_conversation_inspector_exact_compression_threshold_uses_compression_state() -> None:
    intelligence = _classify(usage_percent=90)

    assert intelligence["status"] == "compression_threshold"
    assert intelligence["status_label"] == "Compression threshold reached"


def test_conversation_inspector_above_compression_threshold_uses_compression_state() -> None:
    assert _classify(usage_percent=95)["status"] == "compression_threshold"


def test_conversation_inspector_compression_history_is_supporting_state() -> None:
    intelligence = _classify(usage_percent=45, compression_count=2)

    assert intelligence["status"] == "compression_present"
    assert "2 compression events" in intelligence["explanation"]
    assert any(signal["label"] == "Compression events" and signal["value"] == "2" for signal in intelligence["signals"])


def test_conversation_inspector_context_disabled_is_insufficient_data() -> None:
    intelligence = _classify(usage_percent=20, context_enabled=False)

    assert intelligence["status"] == "insufficient_data"
    assert intelligence["severity"] == "unavailable"
    assert "context tracking" in intelligence["explanation"].lower()


def test_conversation_inspector_compression_disabled_at_threshold_requires_action() -> None:
    intelligence = _classify(usage_percent=90, compression_enabled=False)

    assert intelligence["status"] == "critical"
    assert intelligence["severity"] == "error"
    assert intelligence["recommendation"]


def test_conversation_inspector_no_conversation_is_insufficient_data() -> None:
    intelligence = _classify(usage_percent=None, conversation_available=False)

    assert intelligence["status"] == "insufficient_data"
    assert intelligence["severity"] == "unavailable"


def test_conversation_inspector_context_capacity_exhausted_is_critical() -> None:
    intelligence = _classify(usage_percent=100)

    assert intelligence["status"] == "critical"
    assert intelligence["status_label"] == "Action required"


def test_conversation_inspector_confirmed_compression_count_from_history_without_summary_leakage() -> None:
    conversation = conversation_store.create("inspect-compression")
    conversation_store.append_message("inspect-compression", "user", "PRIVATE_PROMPT")
    conversation_store.append_message("inspect-compression", "system", f"{ROLLING_SUMMARY_PREFIX}PRIVATE_SUMMARY")

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=_metrics_snapshot(),
        ollama_status={"status": "online", "version": "test", "latency_ms": 1.0},
    )
    serialized = str(status["conversation_inspector"])

    assert status["conversation_inspector"]["overview"]["compression_count"] == 1
    assert "PRIVATE_PROMPT" not in serialized
    assert "PRIVATE_SUMMARY" not in serialized
