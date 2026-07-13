import pytest
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.context.conversation_store import conversation_store
from ctxkeeper.dashboard.routes import _latest_applicable_model, build_dashboard_status


@pytest.fixture(autouse=True)
def clear_conversation_store() -> None:
    conversation_store.clear()
    yield
    conversation_store.clear()


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
    assert "Request Trend" in response.text


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
    assert data["active_conversation"]["conversation_id"] == "dashboard-live"
    assert data["active_conversation"]["recent_messages"][0]["content"] == "hello"
    assert data["refresh_interval_ms"] == 1000


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


def test_dashboard_status_warns_when_latency_persists_after_model_warmup() -> None:
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

    assert status["intelligence"]["source"]["model_warmup"]["active"] is False
    assert health["status"] == "warning"
    assert "latency_warning" in health["reasons"]
    assert health["message"] == "Request latency is elevated."
    assert health["indicators"]["average_latency_ms"] == 2500.0
    assert "watch_latency" in {
        recommendation["code"]
        for recommendation in status["intelligence"]["recommendations"]
    }


def test_dashboard_status_preserves_request_load_warning_during_model_warmup() -> None:
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
