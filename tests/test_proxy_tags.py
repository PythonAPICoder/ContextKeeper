from __future__ import annotations

import json
import logging
import asyncio
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import ClassVar

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ctxkeeper.config import Settings
from ctxkeeper.context import conversation_store
from ctxkeeper.dashboard.routes import build_dashboard_status
from ctxkeeper.diagnostics.activity import activity_manager
from ctxkeeper.model_context import active_context_window_overrides, model_context_window_cache
from ctxkeeper.proxy import routes
from ctxkeeper.proxy.model_extraction import extract_request_model, inspect_request_model


class FakeOllamaClient:
    instances: ClassVar[list["FakeOllamaClient"]] = []
    requests: ClassVar[list[dict[str, object]]] = []
    show_context_windows: ClassVar[dict[str, int | None]] = {
        "gpt-oss:20b": 131072,
        "llava:latest": 32768,
        "qwen2.5:32b": 32768,
        "qwen3.6:latest": 262144,
    }

    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.instances.append(self)

    async def request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        query: str,
    ) -> httpx.Response:
        self.requests.append(
            {
                "method": method,
                "path": path,
                "headers": headers,
                "body": body,
                "query": query,
            }
        )
        request_payload = _json_body(body)
        requested_model = request_payload.get("model") or request_payload.get("name")
        if path == "/api/chat":
            return httpx.Response(
                status_code=200,
                json={
                    "model": requested_model or "unknown",
                    "message": {
                        "role": "assistant",
                        "content": "Hello from Ollama.",
                    },
                    "done": True,
                },
                headers={"content-type": "application/json"},
            )
        if path == "/api/show":
            model = requested_model if isinstance(requested_model, str) else "llava:latest"
            context_window = self.show_context_windows.get(model, 32768)
            model_info = (
                {
                    "general.architecture": "llama",
                    "llama.context_length": context_window,
                }
                if context_window is not None
                else {"general.architecture": "llama", "llama.embedding_length": 8192}
            )
            return httpx.Response(
                status_code=200,
                json={
                    "model": model,
                    "model_info": model_info,
                },
                headers={"content-type": "application/json"},
            )
        return httpx.Response(
            status_code=200,
            json={
                "models": [
                    {
                        "name": "gpt-oss:20b",
                        "model": "gpt-oss:20b",
                        "modified_at": "2026-07-03T12:00:00Z",
                        "size": 123,
                    }
                ]
            },
            headers={"content-type": "application/json"},
        )

    async def stream(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        query: str,
    ) -> tuple[int, dict[str, str], AsyncIterator[bytes]]:
        self.requests.append(
            {
                "method": method,
                "path": path,
                "headers": headers,
                "body": body,
                "query": query,
                "stream": True,
            }
        )

        async def iterator() -> AsyncIterator[bytes]:
            yield b'{"message":{"content":"hello"},"done":false}\n'
            yield b'{"done":true}\n'

        return 200, {"content-type": "application/x-ndjson"}, iterator()


def _json_body(body: bytes | object) -> dict[str, object]:
    if not isinstance(body, bytes):
        return {}
    try:
        parsed = json.loads(body.decode("utf-8"))
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _upstream_requests_for(path: str) -> list[dict[str, object]]:
    return [request for request in FakeOllamaClient.requests if request.get("path") == path]


def _last_upstream_json(path: str) -> dict[str, object]:
    requests = _upstream_requests_for(path)
    assert requests
    return _json_body(requests[-1].get("body"))


def _detail_texts(instrument: dict[str, object]) -> list[str]:
    lines = instrument.get("detail_lines")
    assert isinstance(lines, list)
    return [str(line.get("text")) for line in lines if isinstance(line, dict)]


class FakeConversationIdentityRegistry:
    def observe_request(self, **_: object) -> SimpleNamespace:
        return SimpleNamespace(conversation_id="ck_conv_proxy_test")


class FailingOllamaClient(FakeOllamaClient):
    async def request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        query: str,
    ) -> httpx.Response:
        raise RuntimeError("upstream failed")


class RecordingActivityManager:
    def __init__(self) -> None:
        self.events: list[tuple[object, ...]] = []

    def accept_request(
        self,
        *,
        method: str,
        endpoint: str,
        model: str | None,
        generation_sequence: int | None = None,
    ) -> str:
        self.events.append(("accept", method, endpoint, model, generation_sequence))
        return "activity-1"

    def mark_thinking(self, request_id: str) -> None:
        self.events.append(("thinking", request_id))

    def mark_streaming(self, request_id: str) -> None:
        self.events.append(("streaming", request_id))

    def mark_finalizing(self, request_id: str) -> None:
        self.events.append(("finalizing", request_id))

    def complete_request(self, request_id: str, *, ollama_available: bool | None = None) -> None:
        self.events.append(("complete", request_id, ollama_available))


class RecordingMetricsStore:
    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []
        self.sequence = 0

    def record_request(self, **kwargs: object) -> dict[str, object]:
        self.sequence += 1
        kwargs.setdefault("sequence", self.sequence)
        kwargs.setdefault("timestamp", f"2026-07-15T12:00:{self.sequence:02d}+00:00")
        self.requests.append(kwargs)
        return dict(kwargs)


@pytest.fixture(autouse=True)
def clear_model_context_cache() -> None:
    activity_manager.reset()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    routes._DISCOVERY_TASKS.clear()
    FakeOllamaClient.show_context_windows = {
        "gpt-oss:20b": 131072,
        "llava:latest": 32768,
        "qwen2.5:32b": 32768,
        "qwen3.6:latest": 262144,
    }
    yield
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    routes._DISCOVERY_TASKS.clear()
    activity_manager.reset()


@pytest.mark.parametrize(
    ("endpoint", "body"),
    [
        ("/api/chat", b'{"model":"llava:latest","messages":[],"stream":false}'),
        ("/api/generate", b'{"model":"llava:latest","prompt":"hello","stream":false}'),
        ("/v1/chat/completions", b'{"model":"llava:latest","messages":[],"stream":false}'),
        ("/v1/completions", b'{"model":"llava:latest","prompt":"hello","stream":false}'),
    ],
)
def test_request_model_extraction_supports_compatible_generation_payloads(endpoint: str, body: bytes) -> None:
    info = inspect_request_model(body)

    assert endpoint
    assert extract_request_model(body) == "llava:latest"
    assert info.model == "llava:latest"
    assert info.field_path == "model"
    assert "model" in info.top_level_keys


def test_request_model_extraction_missing_model_returns_unknown() -> None:
    info = inspect_request_model(b'{"messages":[],"stream":true}')

    assert info.model is None
    assert info.field_path is None
    assert info.is_json_object is True
    assert info.top_level_keys == ("messages", "stream")


def test_request_model_extraction_supports_name_fallback() -> None:
    info = inspect_request_model(b'{"name":"qwen2.5:32b","messages":[],"stream":false}')

    assert info.model == "qwen2.5:32b"
    assert info.field_path == "name"
    assert "name" in info.top_level_keys


def test_api_tags_passthrough_uses_configured_ollama_url(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="ctxkeeper.proxy"):
        response = client.get("/api/tags?verbose=true")

    assert response.status_code == 200
    assert response.json() == {
        "models": [
            {
                "name": "gpt-oss:20b",
                "model": "gpt-oss:20b",
                "modified_at": "2026-07-03T12:00:00Z",
                "size": 123,
            }
        ]
    }
    assert response.headers["content-type"].startswith("application/json")
    assert FakeOllamaClient.instances[0].base_url == "http://ollama.test:11434"
    assert FakeOllamaClient.requests[0]["method"] == "GET"
    assert FakeOllamaClient.requests[0]["path"] == "/api/tags"
    assert FakeOllamaClient.requests[0]["query"] == "verbose=true"
    assert FakeOllamaClient.requests[0]["body"] == b""

    log_text = caplog.text
    assert "GET /api/tags" in log_text
    assert "status=200" in log_text
    assert "latency_ms=" in log_text
    assert "gpt-oss prompt" not in log_text


def test_api_chat_updates_conversation_store_while_enforcing_context_option(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conversation_store.clear()
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "conversation_identity_registry", FakeConversationIdentityRegistry())
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)
    body = (
        b'{"model":"gpt-oss:20b","messages":['
        b'{"role":"system","content":"Use short answers."},'
        b'{"role":"user","content":"Say hello."}'
        b'],"stream":false}'
    )

    response = client.post(
        "/api/chat",
        content=body,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["message"]["content"] == "Hello from Ollama."
    outbound_chat = _last_upstream_json("/api/chat")
    assert outbound_chat["messages"][1]["content"] == "Say hello."
    assert outbound_chat["options"] == {"num_ctx": 131072}
    assert conversation_store.stats() == {
        "conversation_count": 1,
        "message_count": 3,
    }
    conversation = conversation_store.get("ck_conv_proxy_test")
    assert conversation is not None
    assert [message.role for message in conversation.messages] == [
        "system",
        "user",
        "assistant",
    ]
    assert [message.content for message in conversation.messages] == [
        "Use short answers.",
        "Say hello.",
        "Hello from Ollama.",
    ]
    conversation_store.clear()


def test_generation_request_signals_operational_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    activity = RecordingActivityManager()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "activity_manager", activity)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/generate",
        content=b'{"model":"llava:latest","prompt":"hello","stream":false}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert activity.events[0][:4] == ("accept", "POST", "/api/generate", "llava:latest")
    assert isinstance(activity.events[0][4], int)
    assert activity.events[1:] == [
        ("thinking", "activity-1"),
        ("finalizing", "activity-1"),
        ("complete", "activity-1", True),
    ]


@pytest.mark.parametrize(
    ("endpoint", "body"),
    [
        ("/api/chat", b'{"model":"llava:latest","messages":[],"stream":false}'),
        ("/api/generate", b'{"model":"llava:latest","prompt":"hello","stream":false}'),
        ("/v1/chat/completions", b'{"model":"llava:latest","messages":[],"stream":false}'),
        ("/v1/completions", b'{"model":"llava:latest","prompt":"hello","stream":false}'),
    ],
)
def test_proxy_uses_central_model_extraction_for_activity_and_metrics(
    endpoint: str,
    body: bytes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    activity = RecordingActivityManager()
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "activity_manager", activity)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        endpoint,
        content=body,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert activity.events[0][:4] == ("accept", "POST", endpoint, "llava:latest")
    assert isinstance(activity.events[0][4], int)
    assert metrics.requests[0]["endpoint"] == endpoint
    assert metrics.requests[0]["model"] == "llava:latest"
    assert metrics.requests[0]["context_window_source"] == "detected"
    assert metrics.requests[0]["context_window_tokens"] == 32768
    assert isinstance(metrics.requests[0]["generation_sequence"], int)
    assert _last_upstream_json(endpoint)["options"]["num_ctx"] == 32768


def test_public_proxy_route_records_model_switch_with_name_fallback_and_openai_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    metrics = RecordingMetricsStore()
    activity = RecordingActivityManager()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    monkeypatch.setattr(routes, "activity_manager", activity)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    first = client.post(
        "/api/chat",
        content=b'{"model":"gpt-oss:20b","messages":[],"stream":false,"options":{"num_ctx":16384}}',
        headers={"content-type": "application/json"},
    )
    second = client.post(
        "/v1/chat/completions",
        content=b'{"name":"qwen2.5:32b","messages":[],"stream":false}',
        headers={"content-type": "application/json"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert [request["model"] for request in metrics.requests] == ["gpt-oss:20b", "qwen2.5:32b"]
    assert metrics.requests[0]["context_window_source"] == "detected"
    assert metrics.requests[0]["context_window_tokens"] == 131072
    assert metrics.requests[1]["context_window_source"] == "detected"
    assert metrics.requests[1]["context_window_tokens"] == 32768
    assert _upstream_requests_for("/api/show")
    assert _upstream_requests_for("/api/chat")
    assert _upstream_requests_for("/v1/chat/completions")
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 131072
    assert _last_upstream_json("/v1/chat/completions")["options"]["num_ctx"] == 32768
    assert activity.events[0][:4] == ("accept", "POST", "/api/chat", "gpt-oss:20b")
    assert activity.events[4][:4] == ("accept", "POST", "/v1/chat/completions", "qwen2.5:32b")
    assert metrics.requests[0]["generation_sequence"] < metrics.requests[1]["generation_sequence"]


def test_route_level_qwen_generation_beats_stale_active_gpt_in_dashboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="gpt-oss:20b",
        generation_sequence=0,
    )

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "model": "qwen2.5:32b",
            "messages": [{"role": "user", "content": "hello"}],
            "tools": [{"type": "function", "function": {"name": "noop", "parameters": {"type": "object"}}}],
            "stream": False,
            "options": {"num_ctx": 16384},
        },
    )

    assert response.status_code == 200
    qwen_metric = metrics.requests[-1]
    assert qwen_metric["model"] == "qwen2.5:32b"
    assert qwen_metric["context_window_source"] == "detected"
    assert qwen_metric["context_window_tokens"] == 32768
    assert isinstance(qwen_metric["generation_sequence"], int)
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 32768

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot={
            "requests": {
                "total_requests": len(metrics.requests),
                "total_errors": 0,
                "last_sequence": qwen_metric["sequence"],
                "last_generation_sequence": qwen_metric["generation_sequence"],
                "last_endpoint": qwen_metric["endpoint"],
                "last_model": qwen_metric["model"],
                "last_latency_ms": qwen_metric["latency_ms"],
                "last_status_code": qwen_metric["status_code"],
                "recent_requests": list(reversed(metrics.requests)),
            },
            "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
        },
        ollama_status={"status": "online"},
    )

    assert status["activity"]["active_model"] == "gpt-oss:20b"
    assert status["requests"]["last_model"] == "qwen2.5:32b"
    assert status["requests"]["active_generation"]["generation_sequence"] == qwen_metric["generation_sequence"]
    assert status["requests"]["active_generation"]["context_window_source"] == "detected"


def test_proxy_does_not_assign_previous_model_when_generation_request_has_no_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    activity = RecordingActivityManager()
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "activity_manager", activity)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        content=b'{"messages":[],"stream":false}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert activity.events[0][:4] == ("accept", "POST", "/api/chat", None)
    assert isinstance(activity.events[0][4], int)
    assert metrics.requests[0]["endpoint"] == "/api/chat"
    assert metrics.requests[0]["model"] is None
    assert metrics.requests[0]["context_window_source"] == "default"
    assert metrics.requests[0]["context_window_tokens"] == 32768
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 32768


def test_metadata_request_does_not_signal_operational_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    activity = RecordingActivityManager()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "activity_manager", activity)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/show",
        content=b'{"model":"llava:latest"}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert activity.events == []


def test_api_show_passthrough_caches_detected_context_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/show",
        content=b'{"model":"llava:latest"}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "model": "llava:latest",
        "model_info": {
            "general.architecture": "llama",
            "llama.context_length": 32768,
        },
    }
    assert FakeOllamaClient.requests[0]["path"] == "/api/show"
    assert model_context_window_cache.get("llava:latest") == 32768


def test_generation_metrics_record_configured_override_priority_over_client_num_ctx(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(
        ollama={"base_url": "http://ollama.test:11434"},
        models={"llava:latest": {"context_window_tokens": 65536}},
    )

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        content=b'{"model":"llava:latest","messages":[],"stream":false,"options":{"num_ctx":16384}}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert metrics.requests[0]["context_window_tokens"] == 65536
    assert metrics.requests[0]["context_window_source"] == "configured"
    assert metrics.requests[0]["context_window_source_label"] == "Pre-defined"
    assert not _upstream_requests_for("/api/show")
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 65536
    assert active_context_window_overrides.latest_for_model("llava:latest") is None


def test_first_generation_request_detects_and_forwards_model_context_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        content=b'{"model":"qwen3.6:latest","messages":[],"stream":false,"options":{"num_ctx":16384}}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert [request["path"] for request in FakeOllamaClient.requests] == ["/api/show", "/api/chat"]
    assert metrics.requests[0]["context_window_tokens"] == 262144
    assert metrics.requests[0]["context_window_source"] == "detected"
    assert metrics.requests[0]["context_window_source_label"] == "Discovered"
    assert model_context_window_cache.get("qwen3.6:latest") == 262144
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 262144

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot={
            "requests": {
                "total_requests": 1,
                "total_errors": 0,
                "last_sequence": metrics.requests[0]["sequence"],
                "last_generation_sequence": metrics.requests[0]["generation_sequence"],
                "last_endpoint": metrics.requests[0]["endpoint"],
                "last_model": metrics.requests[0]["model"],
                "last_latency_ms": metrics.requests[0]["latency_ms"],
                "last_status_code": metrics.requests[0]["status_code"],
                "recent_requests": list(reversed(metrics.requests)),
            },
            "system": {"cpu_percent": 0, "ram_percent": 0, "gpu": None},
        },
        ollama_status={"status": "online"},
    )

    assert status["instrument_panel"]["context_usage"]["context_window_tokens"] == 262144
    assert status["instrument_panel"]["context_usage"]["context_window_source"] == "detected"
    assert status["instrument_panel"]["context_usage"]["header_badge"] == "256K"
    assert _detail_texts(status["instrument_panel"]["context_usage"])[1] == "qwen3.6:latest • Discovered"


def test_generation_request_falls_back_to_32k_and_forwards_default_when_metadata_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    FakeOllamaClient.show_context_windows = {"unknown-large:latest": None}
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/generate",
        content=b'{"model":"unknown-large:latest","prompt":"hello","stream":false,"options":{"num_ctx":16384}}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 200
    assert [request["path"] for request in FakeOllamaClient.requests] == ["/api/show", "/api/generate"]
    assert metrics.requests[0]["context_window_tokens"] == 32768
    assert metrics.requests[0]["context_window_source"] == "default"
    assert metrics.requests[0]["context_window_source_label"] == "Default"
    assert _last_upstream_json("/api/generate")["options"]["num_ctx"] == 32768


def test_concurrent_first_call_discovery_is_shared(monkeypatch: pytest.MonkeyPatch) -> None:
    class CountingShowClient(FakeOllamaClient):
        request_count = 0

        async def request(self, **kwargs: object) -> httpx.Response:  # type: ignore[override]
            if kwargs.get("path") == "/api/show":
                type(self).request_count += 1
                await asyncio.sleep(0.01)
            return await super().request(**kwargs)  # type: ignore[arg-type]

    async def run() -> None:
        client = CountingShowClient("http://ollama.test:11434", 120)
        results = await asyncio.gather(
            routes._ensure_model_context_discovered(ollama=client, settings=Settings(), model="qwen3.6:latest"),
            routes._ensure_model_context_discovered(ollama=client, settings=Settings(), model="qwen3.6:latest"),
        )

        assert results == [262144, 262144]

    asyncio.run(run())

    assert CountingShowClient.request_count == 1
    assert model_context_window_cache.get("qwen3.6:latest") == 262144


def test_generation_failure_cleans_active_context_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FailingOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        content=b'{"model":"gpt-oss:20b","messages":[],"stream":false,"options":{"num_ctx":16384}}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 502
    assert metrics.requests[0]["status_code"] == 502
    assert metrics.requests[0]["context_window_source"] == "default"
    assert metrics.requests[0]["context_window_tokens"] == 32768
    assert active_context_window_overrides.latest_for_model("gpt-oss:20b") is None


def test_streaming_completion_records_latest_model_in_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeOllamaClient.instances = []
    FakeOllamaClient.requests = []
    metrics = RecordingMetricsStore()
    monkeypatch.setattr(routes, "OllamaClient", FakeOllamaClient)
    monkeypatch.setattr(routes, "metrics_store", metrics)
    settings = Settings(ollama={"base_url": "http://ollama.test:11434"})

    app = FastAPI()
    app.include_router(routes.create_proxy_router(settings))
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/chat",
        content=b'{"model":"llava:latest","messages":[],"stream":true}',
        headers={"content-type": "application/json"},
    ) as response:
        body = b"".join(response.iter_bytes())

    assert response.status_code == 200
    assert b'"done":true' in body
    assert metrics.requests[-1]["endpoint"] == "/api/chat"
    assert metrics.requests[-1]["model"] == "llava:latest"
    assert metrics.requests[-1]["status_code"] == 200
    assert isinstance(metrics.requests[-1]["generation_sequence"], int)
    assert metrics.requests[-1]["context_window_source"] == "detected"
    assert metrics.requests[-1]["context_window_tokens"] == 32768
    assert _last_upstream_json("/api/chat")["options"]["num_ctx"] == 32768
