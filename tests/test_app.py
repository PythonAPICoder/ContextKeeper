import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.context.conversation_store import conversation_store
from ctxkeeper.dashboard.intelligence import HealthEngine
from ctxkeeper.dashboard.routes import _latest_applicable_model, build_dashboard_status
from ctxkeeper.diagnostics.activity import activity_manager, is_generation_activity_request
from ctxkeeper.model_context import active_context_window_overrides, model_context_window_cache


@pytest.fixture(autouse=True)
def clear_conversation_store() -> None:
    activity_manager.reset()
    conversation_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    yield
    conversation_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    activity_manager.reset()


def _timeline_metrics_snapshot(recent_requests: list[dict[str, object]] | None = None) -> dict[str, object]:
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


def _timeline_status(
    *,
    recent_requests: list[dict[str, object]] | None = None,
    settings: Settings | None = None,
) -> dict[str, object]:
    return build_dashboard_status(
        settings=settings or Settings(),
        metrics_snapshot=_timeline_metrics_snapshot(recent_requests),
        ollama_status={"status": "online", "version": "test", "latency_ms": 1.0},
    )


def test_health_endpoint() -> None:
    app = create_app(Settings())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_dashboard_endpoint() -> None:
    app = create_app(Settings())
    client = TestClient(app)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "ContextKeeper Dashboard" in response.text
    assert "Ollama Status" in response.text
    assert "ContextKeeper Status" in response.text
    assert "Context Usage" in response.text
    assert "Request Statistics" in response.text
    assert "Compression History" in response.text
    assert "Live Activity" in response.text
    assert "Active Conversation" in response.text
    assert "System Health" in response.text
    assert "Insights" in response.text
    assert "Recommendations" in response.text
    assert "Activity Timeline" in response.text
    assert "Live Conversation Timeline" in response.text
    assert "Waiting for conversation activity" in response.text
    assert "Request Trend" in response.text
    assert "requestTrafficSvg" in response.text
    assert "renderRequestTraffic" in response.text
    assert "REQUEST_TRAFFIC_BUCKETS = 24" in response.text
    assert "REQUEST_TRAFFIC_WINDOW_MS = 60000" in response.text
    assert "Live request traffic over the last minute" in response.text
    assert "Waiting for request traffic" in response.text
    assert "Current Activity" in response.text
    assert "liveConversationTimelineList" in response.text
    assert "renderLiveConversationTimeline" in response.text
    assert "currentActivityStatus" in response.text
    assert "refreshOperationalActivity" in response.text
    assert "activity-streaming" in response.text
    assert "@media (prefers-reduced-motion: reduce)" in response.text
    assert response.text.count("setInterval(") == 1
    assert "ops-activity-summary" in response.text
    assert "No model observed yet" in response.text
    assert "No active model yet" not in response.text


def test_dashboard_conversation_inspector_foundation_contract() -> None:
    app = create_app(Settings())
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    html = response.text
    assert 'id="conversationInspectorDrawer"' in html
    assert 'role="complementary"' in html
    assert 'aria-labelledby="conversationInspectorTitle"' in html
    assert "Conversation Inspector" in html
    assert 'id="conversationInspectorClose"' in html
    assert 'aria-label="Close Conversation Inspector"' in html
    assert "Loading conversation details…" in html
    assert "Conversation details unavailable" in html
    assert "selectedConversationId:null" in html
    assert "inspectorOpen:false" in html
    assert "inspectorLoading:false" in html
    assert "inspectorError:null" in html
    assert "data-inspector-conversation-id" in html
    assert "aria-pressed" in html
    assert "is-selected" in html
    assert ".conversation-inspector-state[hidden],.conversation-inspector-section[hidden] { display:none; }" in html
    assert "showConversationInspectorPanel('loading')" in html
    assert "showConversationInspectorPanel('unavailable')" in html
    assert "showConversationInspectorPanel('metadata')" in html
    assert "handleTimelineInspectorSelection" in html
    assert "openConversationInspector" in html
    assert "closeConversationInspector" in html
    assert "updateConversationInspectorFromDashboardData(data)" in html
    assert "event.key === 'Escape'" in html
    assert "conversation-inspector-live-region" in html
    assert ".conversation-inspector-drawer" in html
    assert ".conversation-inspector-backdrop" in html
    assert ".conversation-inspector-drawer,.conversation-inspector-backdrop,.conversation-inspector-close" in html


def test_dashboard_connection_flow_animation_contract() -> None:
    app = create_app(Settings())
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    html = response.text
    assert 'id="connections" class="card flow-panel ops-panel traffic-idle" data-traffic-state="idle" data-active-requests="0"' in html
    assert 'id="flowNote"' in html
    assert "Topology idle; connected paths show availability." in html
    for node in ("client", "proxy", "ollama", "model"):
        assert f'data-flow-node="{node}"' in html
    for link in ("client-proxy", "proxy-ollama", "ollama-model"):
        assert f'data-flow-link="{link}"' in html
        assert f'data-flow-segment="{link}"' in html

    assert "TOPOLOGY_OUTBOUND_DURATION_MS = 1300" in html
    assert "TOPOLOGY_INBOUND_DURATION_MS = 1200" in html
    assert "TOPOLOGY_FLOW_CLASSES = ['traffic-idle','traffic-outbound','traffic-processing','traffic-inbound']" in html
    assert "function updateTopologyTraffic(activity)" in html
    assert "current.active_request_count" in html
    assert "panel.dataset.activeEndpoint = current.active_endpoint || ''" in html
    assert "panel.dataset.activeGenerationSequence = current.active_generation_sequence ?? ''" in html
    assert "panel.dataset.activeRequestId = current.active_request_id || ''" in html
    assert "setTopologyTrafficState(panel, 'outbound')" in html
    assert "setTopologyTrafficState(panel, 'processing')" in html
    assert "setTopologyTrafficState(panel, 'inbound')" in html
    assert "setTopologyTrafficState(panel, 'idle')" in html
    assert "scheduleTopologySettle(panel, TOPOLOGY_OUTBOUND_DURATION_MS)" in html
    assert "scheduleTopologySettle(panel, TOPOLOGY_INBOUND_DURATION_MS)" in html
    assert "triggerTopologyPulse" not in html

    assert '<circle id="flowPacketHalo" class="flow-svg-packet-halo" r="10" cx="0" cy="0"></circle>' in html
    assert '<circle id="flowPacket" class="flow-svg-packet" r="6.5" cx="0" cy="0"></circle>' in html
    assert ".flow-svg-packet,.flow-svg-packet-halo" in html
    assert ".flow-panel.traffic-outbound .flow-svg-packet" in html
    assert ".flow-panel.traffic-outbound .flow-svg-packet-halo" in html
    assert ".flow-panel.traffic-inbound .flow-svg-packet" in html
    assert ".flow-panel.traffic-inbound .flow-svg-packet-halo" in html
    assert ".flow-svg-packet,.flow-svg-packet-halo,.flow-stage::after" in html
    assert ".flow-panel.traffic-processing [data-flow-segment=\"ollama-model\"]" in html
    assert "flowPacketOutbound" in html
    assert "flowPacketInbound" in html
    assert "@media (prefers-reduced-motion: reduce)" in html
    assert ".flow-panel.traffic-outbound .flow-svg-packet" in html
    assert ".flow-panel.traffic-inbound .flow-svg-packet" in html
    assert ".flow-panel.traffic-processing [data-flow-link=\"ollama-model\"]::after" in html

    animation_block = html[
        html.index(".flow-panel.traffic-outbound"):
        html.index("@keyframes flowPacketOutbound")
    ]
    for layout_property in ("grid-template", "min-height:", "height:", "width:", "padding:", "margin:"):
        assert layout_property not in animation_block

    assert "requestTrafficSvg" in html
    assert "renderRequestTraffic" in html
    assert is_generation_activity_request("POST", "/api/chat") is True
    assert is_generation_activity_request("POST", "/api/generate") is True
    assert is_generation_activity_request("POST", "/api/show") is False
    assert is_generation_activity_request("GET", "/api/tags") is False


def test_dashboard_data_endpoint(monkeypatch) -> None:
    async def fake_check_ollama(settings: Settings) -> dict[str, object]:
        return {"status": "online", "version": "test", "latency_ms": 1.0}

    monkeypatch.setattr("ctxkeeper.dashboard.routes._check_ollama", fake_check_ollama)
    conversation_store.append_message("dashboard-live", "user", "hello")
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard/data")

    assert response.status_code == 200
    data = response.json()
    assert data["contextkeeper"]["status"] == "running"
    assert data["ollama"]["status"] == "online"
    assert data["activity"]["state"] == "ready"
    assert data["activity"]["active_request_count"] == 0
    assert "updated_at" in data["activity"]
    assert "total_count" in data["requests"]
    assert "recent_count" in data["requests"]
    assert "latest" in data["requests"]
    assert "usage_percent" in data["context"]
    assert "count" in data["compression"]
    assert data["intelligence"]["health"]["status"] in {"healthy", "busy", "warning", "critical", "offline"}
    assert "message" in data["intelligence"]["health"]
    assert "insights" in data["intelligence"]
    assert "recommendations" in data["intelligence"]
    assert "request_direction" in data["intelligence"]["trends"]
    assert "average_request_rate" in data["intelligence"]["trends"]
    assert "average_latency_ms" in data["intelligence"]["trends"]
    assert "timeline" in data["intelligence"]
    assert "conversation_risk" in data["intelligence"]
    assert "conversation_timeline" in data
    assert "events" in data["conversation_timeline"]
    assert data["conversation_timeline"]["conversation_id"] == "dashboard-live"
    assert data["active_conversation"]["conversation_id"] == "dashboard-live"
    assert data["active_conversation"]["recent_messages"][0]["content"] == "hello"
    assert data["refresh_interval_ms"] == 1000


def test_dashboard_status_reuses_single_conversation_snapshot(monkeypatch) -> None:
    conversation_store.append_message("dashboard-foundation", "user", "hello")
    original_all = conversation_store.all
    calls = 0

    def counted_all() -> list[object]:
        nonlocal calls
        calls += 1
        return original_all()

    monkeypatch.setattr(conversation_store, "all", counted_all)
    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot={
            "requests": {
                "total_requests": 0,
                "total_errors": 0,
                "last_sequence": 0,
                "last_generation_sequence": None,
                "last_endpoint": None,
                "last_model": None,
                "last_latency_ms": None,
                "last_status_code": None,
                "recent_requests": [],
            },
            "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
        },
        ollama_status={"status": "online", "version": "test", "latency_ms": 1.0},
    )

    assert calls == 1
    assert status["context"]["conversation_count"] == 1
    assert status["active_conversation"]["conversation_id"] == "dashboard-foundation"


def test_dashboard_data_exposes_activity_independently_from_health() -> None:
    activity_manager.reset()
    request_id = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="llava:latest",
    )
    activity_manager.mark_streaming(request_id)
    metrics_snapshot = {
        "requests": {
            "total_requests": 0,
            "total_errors": 0,
            "last_endpoint": None,
            "last_model": None,
            "last_latency_ms": None,
            "last_status_code": None,
            "recent_requests": [],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "offline"},
    )

    assert status["intelligence"]["health"]["status"] == "critical"
    assert status["activity"]["state"] == "streaming"
    assert status["activity"]["label"] == "Streaming Response"
    assert status["activity"]["active_request_count"] == 1


def test_completed_request_history_does_not_count_as_active_health_load() -> None:
    completed_request_id = activity_manager.accept_request(
        method="POST",
        endpoint="/api/generate",
        model="llama3.2:latest",
    )
    activity_manager.mark_finalizing(completed_request_id)
    activity_manager.complete_request(completed_request_id, ollama_available=True)
    recent_requests = [
        {
            "timestamp": f"2026-07-12T10:{minute:02d}:00+00:00",
            "endpoint": "/api/generate",
            "model": "llama3.2:latest",
            "status_code": 200,
            "latency_ms": 6_000.0,
        }
        for minute in range(55)
    ]
    metrics_snapshot = {
        "requests": {
            "total_requests": 55,
            "total_errors": 0,
            "last_endpoint": "/api/generate",
            "last_model": "llama3.2:latest",
            "last_latency_ms": 6_000.0,
            "last_status_code": 200,
            "recent_requests": recent_requests,
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]
    recommendation_codes = {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }

    assert status["activity"]["state"] == "idle"
    assert status["activity"]["active_request_count"] == 0
    assert health["status"] == "healthy"
    assert health["indicators"]["active_requests"] == 0
    assert health["indicators"]["average_latency_ms"] == 0.0
    assert status["intelligence"]["source"]["active_request_count"] == 0
    assert status["intelligence"]["source"]["health_latency_ms"] == 0.0
    assert status["intelligence"]["source"]["raw_average_latency_ms"] == 6000.0
    assert status["requests"]["last_latency_ms"] == 6_000.0
    assert status["intelligence"]["trends"]["average_latency_ms"] == 6000.0
    assert "request_load_warning" not in health["reasons"]
    assert "latency_critical" not in health["reasons"]
    assert "monitor_load" not in recommendation_codes
    assert "ollama_overloaded" not in recommendation_codes


def test_genuine_active_concurrency_still_warns_about_request_load() -> None:
    for index in range(HealthEngine.WARNING_ACTIVE_REQUESTS):
        activity_manager.accept_request(
            method="POST",
            endpoint="/api/chat",
            model=f"model-{index}",
        )
    metrics_snapshot = {
        "requests": {
            "total_requests": 0,
            "total_errors": 0,
            "last_endpoint": None,
            "last_model": None,
            "last_latency_ms": None,
            "last_status_code": None,
            "recent_requests": [],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]
    recommendation_codes = {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }

    assert status["activity"]["active_request_count"] == HealthEngine.WARNING_ACTIVE_REQUESTS
    assert health["status"] == "warning"
    assert "request_load_warning" in health["reasons"]
    assert "monitor_load" in recommendation_codes


def test_recent_request_errors_still_warn_without_duration_health_signal() -> None:
    metrics_snapshot = {
        "requests": {
            "total_requests": 1,
            "total_errors": 1,
            "last_endpoint": "/api/generate",
            "last_model": "llama3.2:latest",
            "last_latency_ms": 20.0,
            "last_status_code": 502,
            "recent_requests": [
                {
                    "timestamp": "2026-07-12T10:00:00+00:00",
                    "endpoint": "/api/generate",
                    "model": "llama3.2:latest",
                    "status_code": 502,
                    "latency_ms": 20.0,
                }
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]

    assert status["activity"]["active_request_count"] == 0
    assert health["status"] == "warning"
    assert health["reasons"][0] == "recent_request_errors"
    assert health["message"] == "Recent request errors detected."


def test_health_endpoint_reports_latest_applicable_request_model(monkeypatch) -> None:
    async def fake_check_ollama(settings: Settings) -> dict[str, object]:
        return {"status": "online", "version": "test", "latency_ms": 1.0}

    class FakeMetricsStore:
        def snapshot(self) -> dict[str, object]:
            return {
                "requests": {
                    "last_endpoint": "/api/show",
                    "last_model": "qwen2.5:32b",
                    "recent_requests": [
                        {
                            "endpoint": "/api/show",
                            "model": "qwen2.5:32b",
                            "client_host": "127.0.0.1",
                        },
                        {
                            "endpoint": "/api/chat",
                            "model": "llava:latest",
                            "client_host": "127.0.0.1",
                        },
                    ],
                }
            }

    monkeypatch.setattr("ctxkeeper.dashboard.routes._check_ollama", fake_check_ollama)
    monkeypatch.setattr("ctxkeeper.dashboard.routes.metrics_store", FakeMetricsStore())
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["connections"]["model"] == {
        "status": "active",
        "name": "llava:latest",
        "label": "llava:latest",
    }


def test_build_dashboard_status_includes_context_and_compression_history() -> None:
    conversation = conversation_store.create("dashboard-test")
    conversation_store.append_message("dashboard-test", "user", "hello")
    conversation_store.append_message(
        "dashboard-test",
        "system",
        f"{ROLLING_SUMMARY_PREFIX}older conversation summary",
    )
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_endpoint": "/api/chat",
            "last_model": "test-model",
            "last_latency_ms": 12.5,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-08T12:01:00+00:00",
                    "endpoint": "/api/chat",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
                {
                    "timestamp": "2026-07-08T12:00:00+00:00",
                    "endpoint": "/api/tags",
                    "status_code": 200,
                    "latency_ms": 50.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "offline"},
    )

    assert conversation.conversation_id == "dashboard-test"
    assert status["requests"]["total_count"] == 2
    assert status["requests"]["recent_count"] == 2
    assert status["context"]["conversation_count"] == 1
    assert status["context"]["message_count"] == 2
    assert status["context"]["usage_percent"] > 0
    assert status["compression"]["count"] == 1
    assert status["compression"]["history"][0]["conversation_id"] == "dashboard-test"
    assert status["active_conversation"]["conversation_id"] == "dashboard-test"
    assert status["active_conversation"]["model_name"] == "test-model"
    assert status["active_conversation"]["rolling_summary"] == "older conversation summary"
    assert status["active_conversation"]["context"]["usage_percent"] > 0
    assert status["intelligence"]["health"]["status"] == "critical"
    assert status["intelligence"]["health"]["message"] == "Ollama is unavailable."
    assert status["intelligence"]["trends"]["average_latency_ms"] == 75.0
    assert status["intelligence"]["trends"]["average_request_rate"] == 2.0
    assert status["intelligence"]["timeline"][0]["message"] == "/api/chat returned 200 in 100.0 ms"
    assert status["intelligence"]["conversation_risk"]["status"] == "healthy"


def test_live_conversation_timeline_empty_state() -> None:
    status = _timeline_status()

    timeline = status["conversation_timeline"]

    assert timeline["events"] == []
    assert timeline["conversation_id"] is None
    assert timeline["max_events"] == 40


def test_live_conversation_timeline_payload_structure_ordering_and_stable_ids() -> None:
    conversation = conversation_store.create("timeline-structure")
    conversation.created_at = datetime(2026, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    conversation.updated_at = datetime(2026, 7, 15, 12, 0, 3, tzinfo=timezone.utc)
    recent_requests = [
        {
            "sequence": 2,
            "generation_sequence": 2,
            "timestamp": "2026-07-15T12:00:02+00:00",
            "endpoint": "/api/chat",
            "model": "qwen2.5:32b",
            "status_code": 502,
            "latency_ms": 25.5,
        },
        {
            "sequence": 1,
            "generation_sequence": 1,
            "timestamp": "2026-07-15T12:00:01+00:00",
            "endpoint": "/api/chat",
            "model": "gpt-oss:20b",
            "status_code": 200,
            "latency_ms": 2400.0,
        },
    ]

    first = _timeline_status(recent_requests=recent_requests)["conversation_timeline"]["events"]
    second = _timeline_status(recent_requests=recent_requests)["conversation_timeline"]["events"]

    assert first
    assert [event["id"] for event in first] == [event["id"] for event in second]
    assert [event["timestamp"] for event in first] == sorted(event["timestamp"] for event in first)
    for event in first:
        assert set(event) == {"id", "timestamp", "time_label", "type", "severity", "title", "detail"}
        assert event["id"]
        assert event["timestamp"]
        assert event["time_label"]
        assert event["severity"] in {"info", "success", "warning", "error"}

    assert any(event["type"] == "conversation_started" for event in first)
    assert any(event["type"] == "model_selected" and event["detail"] == "gpt-oss:20b" for event in first)
    assert any(event["type"] == "model_changed" and event["detail"] == "gpt-oss:20b -> qwen2.5:32b" for event in first)
    assert any(event["type"] == "request_completed" and "2.4 s" in event["detail"] for event in first)
    assert any(event["type"] == "request_failed" and "HTTP 502" in event["detail"] for event in first)


def test_live_conversation_timeline_is_bounded_to_recent_events() -> None:
    base = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    chronological_requests = [
        {
            "sequence": index + 1,
            "generation_sequence": index + 1,
            "timestamp": (base + timedelta(seconds=index)).isoformat(),
            "endpoint": "/api/chat",
            "model": "gpt-oss:20b",
            "status_code": 200,
            "latency_ms": 10.0,
        }
        for index in range(60)
    ]

    timeline = _timeline_status(recent_requests=list(reversed(chronological_requests)))["conversation_timeline"]
    events = timeline["events"]

    assert len(events) == timeline["max_events"] == 40
    assert [event["timestamp"] for event in events] == sorted(event["timestamp"] for event in events)
    assert events[0]["type"] == "request_completed"


def test_live_conversation_timeline_handles_incomplete_legacy_data_safely() -> None:
    conversation = conversation_store.create("timeline-legacy")
    conversation.created_at = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    conversation.updated_at = conversation.created_at
    recent_requests = [
        {"endpoint": "/api/chat", "timestamp": "not-a-timestamp", "status_code": 200},
        {"timestamp": "2026-07-15T12:00:01+00:00", "status_code": None, "model": "missing-endpoint"},
        {"endpoint": "/api/tags", "timestamp": "2026-07-15T12:00:02+00:00", "status_code": 200},
    ]

    events = _timeline_status(recent_requests=recent_requests)["conversation_timeline"]["events"]

    assert [event["type"] for event in events] == ["conversation_started"]


def test_live_conversation_timeline_prefers_request_conversation_identity_when_available() -> None:
    conversation = conversation_store.create("timeline-active")
    conversation.created_at = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    conversation.updated_at = datetime(2026, 7, 15, 12, 0, 3, tzinfo=timezone.utc)
    recent_requests = [
        {
            "sequence": 2,
            "generation_sequence": 2,
            "timestamp": "2026-07-15T12:00:02+00:00",
            "endpoint": "/api/chat",
            "model": "other-model",
            "status_code": 200,
            "latency_ms": 20.0,
            "conversation_id": "timeline-other",
        },
        {
            "sequence": 1,
            "generation_sequence": 1,
            "timestamp": "2026-07-15T12:00:01+00:00",
            "endpoint": "/api/chat",
            "model": "active-model",
            "status_code": 200,
            "latency_ms": 10.0,
            "conversation_id": "timeline-active",
        },
    ]

    events = _timeline_status(recent_requests=recent_requests)["conversation_timeline"]["events"]
    serialized = json.dumps(events)

    assert "active-model" in serialized
    assert "other-model" not in serialized


def test_live_conversation_timeline_represents_active_request_received() -> None:
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="llava:latest",
        request_id="active-timeline-request",
        generation_sequence=7,
    )

    events = _timeline_status()["conversation_timeline"]["events"]

    assert any(event["type"] == "request_received" and "/api/chat" in event["detail"] for event in events)
    assert any(event["type"] == "model_selected" and event["detail"] == "llava:latest" for event in events)


def test_live_conversation_timeline_represents_context_warning() -> None:
    conversation_store.append_message("timeline-context-warning", "user", "a" * 96)
    conversation = conversation_store.get("timeline-context-warning")
    assert conversation is not None
    conversation.created_at = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    conversation.updated_at = datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
    settings = Settings.model_validate(
        {
            "context": {
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 10,
                "compression_threshold_percent": 90,
            }
        }
    )
    recent_requests = [
        {
            "sequence": 1,
            "generation_sequence": 1,
            "timestamp": "2026-07-15T12:00:00+00:00",
            "endpoint": "/api/chat",
            "model": "gpt-oss:20b",
            "status_code": 200,
            "latency_ms": 10.0,
        }
    ]

    events = _timeline_status(settings=settings, recent_requests=recent_requests)["conversation_timeline"]["events"]

    assert any(
        event["type"] == "context_warning"
        and event["title"] == "Context warning threshold reached"
        and "context used" in event["detail"]
        for event in events
    )


def test_live_conversation_timeline_represents_confirmed_compression_without_summary_leakage() -> None:
    prompt_secret = "PRIVATE_PROMPT_TIMELINE_SECRET"
    response_secret = "PRIVATE_RESPONSE_TIMELINE_SECRET"
    summary_secret = "PRIVATE_SUMMARY_TIMELINE_SECRET"
    conversation = conversation_store.create("timeline-compression")
    conversation.created_at = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    user_message = conversation_store.append_message("timeline-compression", "user", prompt_secret)
    assistant_message = conversation_store.append_message("timeline-compression", "assistant", response_secret)
    summary_message = conversation_store.append_message(
        "timeline-compression",
        "system",
        f"{ROLLING_SUMMARY_PREFIX}{summary_secret}",
    )
    user_message.timestamp = datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
    assistant_message.timestamp = datetime(2026, 7, 15, 12, 0, 2, tzinfo=timezone.utc)
    summary_message.timestamp = datetime(2026, 7, 15, 12, 0, 3, tzinfo=timezone.utc)
    conversation.updated_at = summary_message.timestamp

    events = _timeline_status()["conversation_timeline"]["events"]
    serialized = json.dumps(events)

    assert any(event["type"] == "compression_completed" for event in events)
    assert "Rolling summary 1 recorded." in serialized
    assert prompt_secret not in serialized
    assert response_secret not in serialized
    assert summary_secret not in serialized


def test_dashboard_status_uses_latest_applicable_request_model() -> None:
    conversation_store.create("dashboard-model-test")
    metrics_snapshot = {
        "requests": {
            "total_requests": 3,
            "total_errors": 0,
            "last_endpoint": "/api/show",
            "last_model": "qwen2.5:32b",
            "last_latency_ms": 12.5,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:01:02+00:00",
                    "endpoint": "/api/show",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 40.0,
                },
                {
                    "timestamp": "2026-07-11T18:01:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
                {
                    "timestamp": "2026-07-11T18:01:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 80.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["requests"]["last_model"] == "llava:latest"
    assert status["requests"]["last_observed_model"] == "qwen2.5:32b"
    assert status["active_conversation"]["model_name"] == "llava:latest"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/chat",
        "/api/generate",
        "/v1/chat/completions",
        "/v1/completions",
    ],
)
def test_dashboard_active_model_updates_during_active_generation_request(endpoint: str) -> None:
    activity_manager.accept_request(
        method="POST",
        endpoint=endpoint,
        model="llava:latest",
    )
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_endpoint": "/api/show",
            "last_model": "qwen2.5:32b",
            "last_latency_ms": 12.5,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:01:02+00:00",
                    "endpoint": "/api/show",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 40.0,
                },
                {
                    "timestamp": "2026-07-11T18:01:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["requests"]["last_model"] == "llava:latest"
    assert status["requests"]["model_state"] == "active_known"
    assert status["requests"]["model_label"] == "llava:latest"
    assert status["activity"]["active_model"] == "llava:latest"
    assert status["activity"]["active_model_state"] == "known"
    assert status["activity"]["latest_model"] == "llava:latest"
    assert status["active_conversation"]["model_name"] == "llava:latest"


def test_active_request_without_model_does_not_reuse_previous_model(monkeypatch) -> None:
    async def fake_check_ollama(settings: Settings) -> dict[str, object]:
        return {"status": "online", "version": "test", "latency_ms": 1.0}

    class FakeMetricsStore:
        def snapshot(self) -> dict[str, object]:
            return {
                "requests": {
                    "total_requests": 1,
                    "total_errors": 0,
                    "last_endpoint": "/api/chat",
                    "last_model": "gpt-oss:20b",
                    "last_latency_ms": 100.0,
                    "last_status_code": 200,
                    "recent_requests": [
                        {
                            "timestamp": "2026-07-11T18:01:00+00:00",
                            "endpoint": "/api/chat",
                            "model": "gpt-oss:20b",
                            "status_code": 200,
                            "latency_ms": 100.0,
                            "client_host": "127.0.0.1",
                        },
                    ],
                },
                "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
            }

    first = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
    )
    activity_manager.complete_request(first, ollama_available=True)
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model=None,
    )
    metrics_snapshot = FakeMetricsStore().snapshot()

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["active_request_count"] == 1
    assert status["activity"]["active_model"] is None
    assert status["activity"]["active_model_state"] == "unknown"
    assert status["activity"]["latest_model"] == "gpt-oss:20b"
    assert status["requests"]["last_model"] is None
    assert status["requests"]["model_state"] == "active_unknown"
    assert status["requests"]["model_label"] == "Unknown model"
    assert status["requests"]["last_observed_model"] == "gpt-oss:20b"
    assert status["active_conversation"]["model_name"] is None

    monkeypatch.setattr("ctxkeeper.dashboard.routes._check_ollama", fake_check_ollama)
    monkeypatch.setattr("ctxkeeper.dashboard.routes.metrics_store", FakeMetricsStore())
    app = create_app(Settings())
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model=None,
    )
    client = TestClient(app)

    health = client.get("/health").json()

    assert health["connections"]["model"] == {
        "status": "unknown",
        "name": None,
        "label": "Unknown model",
    }


def test_completed_model_switch_persists_over_later_metadata_requests() -> None:
    first = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="qwen2.5:32b",
    )
    activity_manager.complete_request(first, ollama_available=True)
    second = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="llava:latest",
    )
    activity_manager.complete_request(second, ollama_available=True)
    metrics_snapshot = {
        "requests": {
            "total_requests": 4,
            "total_errors": 0,
            "last_endpoint": "/api/show",
            "last_model": "qwen2.5:32b",
            "last_latency_ms": 40.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:01:03+00:00",
                    "endpoint": "/api/show",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 40.0,
                },
                {
                    "timestamp": "2026-07-11T18:01:02+00:00",
                    "endpoint": "/api/chat",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 90.0,
                },
                {
                    "timestamp": "2026-07-11T18:01:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["state"] == "idle"
    assert status["activity"]["active_request_count"] == 0
    assert status["requests"]["last_model"] == "llava:latest"
    assert status["requests"]["last_observed_model"] == "qwen2.5:32b"


def test_completed_generation_metrics_take_priority_over_stale_activity_latest_model() -> None:
    first = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
    )
    activity_manager.complete_request(first, ollama_available=True)
    metrics_snapshot = {
        "requests": {
            "total_requests": 3,
            "total_errors": 0,
            "last_endpoint": "/api/show",
            "last_model": "gpt-oss:20b",
            "last_latency_ms": 40.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-15T12:02:00+00:00",
                    "endpoint": "/api/show",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "latency_ms": 40.0,
                },
                {
                    "timestamp": "2026-07-15T12:01:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 90.0,
                },
                {
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["latest_model"] == "gpt-oss:20b"
    assert status["requests"]["last_model"] == "llava:latest"
    assert status["active_conversation"]["model_name"] == "llava:latest"


def test_completed_generate_request_can_update_dashboard_active_model() -> None:
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_endpoint": "/api/generate",
            "last_model": "llava:latest",
            "last_latency_ms": 90.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-15T12:01:00+00:00",
                    "endpoint": "/api/generate",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 90.0,
                },
                {
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "latency_ms": 100.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["requests"]["last_model"] == "llava:latest"
    assert status["active_conversation"]["model_name"] == "llava:latest"


def test_latest_applicable_model_uses_newest_timestamp_not_list_position() -> None:
    metrics = {
        "last_endpoint": "/api/chat",
        "last_model": "qwen2.5:32b",
        "recent_requests": [
            {
                "timestamp": "2026-07-11T18:01:00+00:00",
                "endpoint": "/api/chat",
                "model": "qwen2.5:32b",
            },
            {
                "timestamp": "2026-07-11T18:01:01+00:00",
                "endpoint": "/api/chat",
                "model": "llava:latest",
            },
        ],
    }

    assert _latest_applicable_model(metrics) == "llava:latest"


def test_latest_applicable_model_uses_sequence_when_timestamps_tie() -> None:
    metrics = {
        "last_endpoint": "/api/chat",
        "last_model": "gpt-oss:20b",
        "recent_requests": [
            {
                "sequence": 10,
                "timestamp": "2026-07-15T12:00:00+00:00",
                "endpoint": "/api/chat",
                "model": "gpt-oss:20b",
            },
            {
                "sequence": 11,
                "timestamp": "2026-07-15T12:00:00+00:00",
                "endpoint": "/api/chat",
                "model": "qwen2.5:32b",
            },
        ],
    }

    assert _latest_applicable_model(metrics) == "qwen2.5:32b"


def test_dashboard_active_generation_state_keeps_model_and_authoritative_context_from_same_request() -> None:
    conversation_store.append_message("coherent-state", "user", "hello")
    model_context_window_cache.store("qwen2.5:32b", 32768)
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_sequence": 2,
            "last_endpoint": "/api/chat",
            "last_model": "qwen2.5:32b",
            "last_latency_ms": 90.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "sequence": 2,
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "detected",
                    "context_window_source_label": "Discovered",
                },
                {
                    "sequence": 1,
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "default",
                    "context_window_source_label": "Default",
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    active_generation = status["requests"]["active_generation"]
    assert active_generation["request_sequence"] == 2
    assert active_generation["model_name"] == "qwen2.5:32b"
    assert active_generation["context_window_tokens"] == 32768
    assert active_generation["context_window_source"] == "detected"
    assert status["instrument_panel"]["context_usage"]["active_model"] == "qwen2.5:32b"
    assert status["instrument_panel"]["context_usage"]["context_window_tokens"] == 32768


def test_newer_completed_qwen_beats_older_still_active_gpt_request() -> None:
    model_context_window_cache.store("qwen2.5:32b", 32768)
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
        generation_sequence=1,
    )
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_sequence": 2,
            "last_generation_sequence": 2,
            "last_endpoint": "/api/chat",
            "last_model": "qwen2.5:32b",
            "last_latency_ms": 90.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "sequence": 2,
                    "generation_sequence": 2,
                    "timestamp": "2026-07-15T12:00:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "detected",
                    "context_window_source_label": "Discovered",
                },
                {
                    "sequence": 1,
                    "generation_sequence": 1,
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "default",
                    "context_window_source_label": "Default",
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["active_model"] == "gpt-oss:20b"
    active_generation = status["requests"]["active_generation"]
    assert active_generation["generation_sequence"] == 2
    assert active_generation["model_name"] == "qwen2.5:32b"
    assert active_generation["context_window_source"] == "detected"
    assert active_generation["context_window_tokens"] == 32768
    assert status["requests"]["last_model"] == "qwen2.5:32b"
    assert status["instrument_panel"]["context_usage"]["active_model"] == "qwen2.5:32b"
    assert status["instrument_panel"]["context_usage"]["header_badge"] == "32K"
    assert "qwen2.5:32b • Discovered" in status["instrument_panel"]["context_usage"]["detail_lines"][1]["text"]


def test_immediate_qwen_switch_same_conversation_does_not_wait_for_idle_expiration() -> None:
    conversation_store.append_message("shared-thread", "user", "gpt prompt")
    conversation_store.append_message("shared-thread", "assistant", "gpt response")
    conversation_store.append_message("shared-thread", "user", "qwen prompt")
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
        generation_sequence=1,
    )
    metrics_snapshot = {
        "requests": {
            "total_requests": 3,
            "total_errors": 0,
            "last_sequence": 3,
            "last_generation_sequence": 2,
            "last_endpoint": "/api/show",
            "last_model": "gpt-oss:20b",
            "last_latency_ms": 22.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "sequence": 3,
                    "timestamp": "2026-07-15T12:00:02+00:00",
                    "endpoint": "/api/show",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                },
                {
                    "sequence": 2,
                    "generation_sequence": 2,
                    "timestamp": "2026-07-15T12:00:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "default",
                    "context_window_source_label": "Default",
                },
                {
                    "sequence": 1,
                    "generation_sequence": 1,
                    "timestamp": "2026-07-15T12:00:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "gpt-oss:20b",
                    "status_code": 200,
                    "context_window_tokens": 32768,
                    "context_window_source": "default",
                    "context_window_source_label": "Default",
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["active_model"] == "gpt-oss:20b"
    assert status["requests"]["active_generation"]["generation_sequence"] == 2
    assert status["requests"]["last_model"] == "qwen2.5:32b"
    assert status["active_conversation"]["model_name"] == "qwen2.5:32b"


def test_exact_b48_qa_sequence_uses_newest_generation_without_five_minute_expiration() -> None:
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
        generation_sequence=1,
    )
    base_requests = [
        {
            "sequence": 1,
            "generation_sequence": 1,
            "timestamp": "2026-07-15T12:00:00+00:00",
            "endpoint": "/api/chat",
            "model": "gpt-oss:20b",
            "status_code": 200,
            "context_window_tokens": 32768,
            "context_window_source": "default",
            "context_window_source_label": "Default",
        },
        {
            "sequence": 2,
            "generation_sequence": 2,
            "timestamp": "2026-07-15T12:00:01+00:00",
            "endpoint": "/api/chat",
            "model": "qwen2.5:32b",
            "status_code": 200,
            "context_window_tokens": 32768,
            "context_window_source": "default",
            "context_window_source_label": "Default",
        },
        {
            "sequence": 3,
            "generation_sequence": 3,
            "timestamp": "2026-07-15T12:00:02+00:00",
            "endpoint": "/api/chat",
            "model": "llava:latest",
            "status_code": 200,
            "context_window_tokens": 32768,
            "context_window_source": "default",
            "context_window_source_label": "Default",
        },
        {
            "sequence": 4,
            "generation_sequence": 4,
            "timestamp": "2026-07-15T12:05:02+00:00",
            "endpoint": "/api/chat",
            "model": "qwen2.5:32b",
            "status_code": 200,
            "context_window_tokens": 32768,
            "context_window_source": "default",
            "context_window_source_label": "Default",
        },
    ]

    def status_for(requests: list[dict[str, object]]) -> dict[str, object]:
        latest = requests[-1]
        return build_dashboard_status(
            settings=Settings(),
            metrics_snapshot={
                "requests": {
                    "total_requests": len(requests),
                    "total_errors": 0,
                    "last_sequence": latest["sequence"],
                    "last_generation_sequence": latest["generation_sequence"],
                    "last_endpoint": latest["endpoint"],
                    "last_model": latest["model"],
                    "last_latency_ms": 90.0,
                    "last_status_code": 200,
                    "recent_requests": list(reversed(requests)),
                },
                "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
            },
            ollama_status={"status": "online"},
        )

    immediate_qwen = status_for(base_requests[:2])
    other_model = status_for(base_requests[:3])
    later_qwen = status_for(base_requests)

    assert immediate_qwen["requests"]["last_model"] == "qwen2.5:32b"
    assert immediate_qwen["requests"]["active_generation"]["generation_sequence"] == 2
    assert other_model["requests"]["last_model"] == "llava:latest"
    assert other_model["requests"]["active_generation"]["generation_sequence"] == 3
    assert later_qwen["requests"]["last_model"] == "qwen2.5:32b"
    assert later_qwen["requests"]["active_generation"]["generation_sequence"] == 4


def test_generation_sequence_orders_models_when_metric_sequence_namespace_would_mislead() -> None:
    metrics = {
        "last_endpoint": "/api/chat",
        "last_model": "qwen2.5:32b",
        "recent_requests": [
            {
                "sequence": 100,
                "generation_sequence": 1,
                "timestamp": "2026-07-15T12:00:00+00:00",
                "endpoint": "/api/chat",
                "model": "gpt-oss:20b",
            },
            {
                "sequence": 2,
                "generation_sequence": 2,
                "timestamp": "2026-07-15T12:00:00+00:00",
                "endpoint": "/api/chat",
                "model": "qwen2.5:32b",
            },
        ],
    }

    assert _latest_applicable_model(metrics) == "qwen2.5:32b"


def test_health_and_dashboard_data_use_same_active_generation_model(monkeypatch) -> None:
    async def fake_check_ollama(settings: Settings) -> dict[str, object]:
        return {"status": "online", "version": "test", "latency_ms": 1.0}

    class FakeMetricsStore:
        def snapshot(self) -> dict[str, object]:
            return {
                "requests": {
                    "total_requests": 2,
                    "total_errors": 0,
                    "last_endpoint": "/api/show",
                    "last_model": "qwen2.5:32b",
                    "last_latency_ms": 40.0,
                    "last_status_code": 200,
                    "recent_requests": [
                        {
                            "timestamp": "2026-07-11T18:01:02+00:00",
                            "endpoint": "/api/show",
                            "model": "qwen2.5:32b",
                            "status_code": 200,
                            "latency_ms": 40.0,
                            "client_host": "127.0.0.1",
                        },
                        {
                            "timestamp": "2026-07-11T18:01:01+00:00",
                            "endpoint": "/api/chat",
                            "model": "qwen2.5:32b",
                            "status_code": 200,
                            "latency_ms": 100.0,
                            "client_host": "127.0.0.1",
                        },
                    ],
                },
                "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
            }

    monkeypatch.setattr("ctxkeeper.dashboard.routes._check_ollama", fake_check_ollama)
    monkeypatch.setattr("ctxkeeper.dashboard.routes.metrics_store", FakeMetricsStore())
    app = create_app(Settings())
    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="llava:latest",
    )
    client = TestClient(app)

    health = client.get("/health").json()
    dashboard = client.get("/dashboard/data").json()

    assert health["connections"]["model"]["name"] == "llava:latest"
    assert health["activity"]["latest_model"] == "llava:latest"
    assert dashboard["requests"]["last_model"] == "llava:latest"
    assert dashboard["activity"]["latest_model"] == "llava:latest"
    assert dashboard["active_conversation"]["model_name"] == "llava:latest"


def test_dashboard_status_reports_model_warming_for_single_slow_request_after_model_switch() -> None:
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_endpoint": "/api/generate",
            "last_model": "llava:latest",
            "last_latency_ms": 4200.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:02:01+00:00",
                    "endpoint": "/api/generate",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 4200.0,
                },
                {
                    "timestamp": "2026-07-11T18:02:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 120.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]
    recommendation_messages = [
        recommendation["message"]
        for recommendation in status["intelligence"]["recommendations"]
    ]

    assert status["requests"]["last_model"] == "llava:latest"
    assert status["requests"]["last_latency_ms"] == 4200.0
    assert health["status"] == "busy"
    assert health["label"] == "Model warming"
    assert health["reasons"][0] == "model_warming"
    assert health["message"] == "Ollama is loading llava:latest; the first response after switching models can be slower."
    assert health["indicators"]["average_latency_ms"] == 0.0
    assert status["intelligence"]["trends"]["average_latency_ms"] == 2160.0
    assert status["intelligence"]["source"]["model_warmup"]["active"] is True
    assert "watch_latency" not in {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }
    assert all("reduce concurrent load" not in message for message in recommendation_messages)


def test_dashboard_status_treats_successful_generation_duration_as_telemetry() -> None:
    metrics_snapshot = {
        "requests": {
            "total_requests": 3,
            "total_errors": 0,
            "last_endpoint": "/api/chat",
            "last_model": "llava:latest",
            "last_latency_ms": 2600.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:03:02+00:00",
                    "endpoint": "/api/chat",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 2600.0,
                },
                {
                    "timestamp": "2026-07-11T18:03:01+00:00",
                    "endpoint": "/api/chat",
                    "model": "llava:latest",
                    "status_code": 200,
                    "latency_ms": 2400.0,
                },
                {
                    "timestamp": "2026-07-11T18:03:00+00:00",
                    "endpoint": "/api/chat",
                    "model": "qwen2.5:32b",
                    "status_code": 200,
                    "latency_ms": 120.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]
    recommendation_codes = {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }

    assert status["intelligence"]["source"]["model_warmup"]["active"] is False
    assert health["status"] == "healthy"
    assert health["message"] == "All monitored systems are operating normally."
    assert health["indicators"]["average_latency_ms"] == 0.0
    assert status["intelligence"]["source"]["health_latency_ms"] == 0.0
    assert status["intelligence"]["source"]["raw_average_latency_ms"] == pytest.approx(1706.67)
    assert status["intelligence"]["trends"]["average_latency_ms"] == pytest.approx(1706.67)
    assert "watch_latency" not in recommendation_codes
    assert "ollama_overloaded" not in recommendation_codes


def test_dashboard_status_uses_explicit_service_latency_for_health_when_available() -> None:
    metrics_snapshot = {
        "requests": {
            "total_requests": 2,
            "total_errors": 0,
            "last_endpoint": "/api/generate",
            "last_model": "llama3.2:latest",
            "last_latency_ms": 6_000.0,
            "last_status_code": 200,
            "recent_requests": [
                {
                    "timestamp": "2026-07-11T18:05:01+00:00",
                    "endpoint": "/api/generate",
                    "model": "llama3.2:latest",
                    "status_code": 200,
                    "latency_ms": 6_000.0,
                    "service_latency_ms": 2_600.0,
                },
                {
                    "timestamp": "2026-07-11T18:05:00+00:00",
                    "endpoint": "/api/generate",
                    "model": "llama3.2:latest",
                    "status_code": 200,
                    "latency_ms": 5_500.0,
                    "service_latency_ms": 2_400.0,
                },
            ],
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]
    recommendation_codes = {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }

    assert health["status"] == "warning"
    assert "latency_warning" in health["reasons"]
    assert health["indicators"]["average_latency_ms"] == 2500.0
    assert status["intelligence"]["source"]["health_latency_ms"] == 2500.0
    assert status["intelligence"]["source"]["raw_average_latency_ms"] == 5750.0
    assert "watch_latency" in recommendation_codes


def test_dashboard_status_preserves_request_load_warning_during_model_warmup() -> None:
    for index in range(HealthEngine.WARNING_ACTIVE_REQUESTS):
        activity_manager.accept_request(
            method="POST",
            endpoint="/api/generate",
            model=f"llava-active-{index}",
        )
    recent_requests = [
        {
            "timestamp": "2026-07-11T18:04:49+00:00",
            "endpoint": "/api/generate",
            "model": "llava:latest",
            "status_code": 200,
            "latency_ms": 4200.0,
        }
    ]
    recent_requests.extend(
        {
            "timestamp": f"2026-07-11T18:04:{second:02d}+00:00",
            "endpoint": "/api/chat",
            "model": "qwen2.5:32b",
            "status_code": 200,
            "latency_ms": 120.0,
        }
        for second in range(49)
    )
    metrics_snapshot = {
        "requests": {
            "total_requests": 50,
            "total_errors": 0,
            "last_endpoint": "/api/generate",
            "last_model": "llava:latest",
            "last_latency_ms": 4200.0,
            "last_status_code": 200,
            "recent_requests": recent_requests,
        },
        "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
    }

    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    health = status["intelligence"]["health"]

    assert status["intelligence"]["source"]["model_warmup"]["active"] is True
    assert status["intelligence"]["source"]["active_request_count"] == HealthEngine.WARNING_ACTIVE_REQUESTS
    assert health["status"] == "warning"
    assert "request_load_warning" in health["reasons"]
    assert health["message"] == "Request load is high."
    assert "monitor_load" in {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }


def test_latest_applicable_model_ignores_model_metadata_requests() -> None:
    metrics = {
        "last_endpoint": "/api/show",
        "last_model": "qwen2.5:32b",
        "recent_requests": [
            {"endpoint": "/api/show", "model": "qwen2.5:32b"},
            {"endpoint": "/api/tags", "model": None},
        ],
    }

    assert _latest_applicable_model(metrics) is None


def test_latest_applicable_model_supports_openai_compatible_chat_endpoint() -> None:
    metrics = {
        "last_endpoint": "/v1/chat/completions",
        "last_model": "llava:latest",
        "recent_requests": [],
    }

    assert _latest_applicable_model(metrics) == "llava:latest"
