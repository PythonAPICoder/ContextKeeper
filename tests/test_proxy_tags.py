from __future__ import annotations

import logging
from typing import ClassVar

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ctxkeeper.config import Settings
from ctxkeeper.proxy import routes


class FakeOllamaClient:
    instances: ClassVar[list["FakeOllamaClient"]] = []
    requests: ClassVar[list[dict[str, object]]] = []

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
