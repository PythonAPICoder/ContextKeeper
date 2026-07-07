import pytest
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.context.conversation_store import conversation_store
from ctxkeeper.dashboard.routes import build_dashboard_status


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
    assert data["active_conversation"]["conversation_id"] == "dashboard-live"
    assert data["active_conversation"]["recent_messages"][0]["content"] == "hello"
    assert data["refresh_interval_ms"] == 1000


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
                {"endpoint": "/api/chat", "status_code": 200},
                {"endpoint": "/api/tags", "status_code": 200},
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
