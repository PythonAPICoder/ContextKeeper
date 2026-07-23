from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterator
from pathlib import Path
import socket
import ssl
from typing import ClassVar

import httpx
import pytest
import yaml
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.dashboard import connection_test
from ctxkeeper.diagnostics.activity import activity_manager
from ctxkeeper.diagnostics.metrics import metrics_store
from ctxkeeper.model_context import model_context_window_cache
from ctxkeeper.proxy import routes as proxy_routes


CONNECTION_TEST_ENDPOINT = "/api/dashboard/settings/connection/test"
CONNECTION_RESPONSE_KEYS = {
    "connected",
    "tested_endpoint",
    "latency_ms",
    "ollama_version",
    "failure_category",
    "message",
}


class RecordingAsyncClient:
    """Small async-client test double with explicit resource tracking."""

    instances: ClassVar[list["RecordingAsyncClient"]] = []
    handler: ClassVar[Callable[[httpx.Request], httpx.Response]]

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs
        self.requests: list[httpx.Request] = []
        self.closed = False
        self.instances.append(self)

    async def __aenter__(self) -> "RecordingAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        self.closed = True

    async def get(self, url: str, **kwargs: object) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        request = httpx.Request(method, url, **kwargs)
        self.requests.append(request)
        response = type(self).handler(request)
        if response.request is None:
            response.request = request
        return response


class TrackingProxyClient:
    """Proxy-client double used only to prove the active instance is retained."""

    instances: ClassVar[list["TrackingProxyClient"]] = []

    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.instances.append(self)


@pytest.fixture(autouse=True)
def _isolate_connection_test(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    monkeypatch.chdir(tmp_path)
    model_context_window_cache.clear()
    RecordingAsyncClient.instances = []
    RecordingAsyncClient.handler = lambda request: httpx.Response(
        200,
        json={"version": "0.0.0-test"},
        request=request,
    )
    TrackingProxyClient.instances = []
    yield
    model_context_window_cache.clear()


def _write_config(path: Path, data: dict[str, object]) -> bytes:
    serialized = yaml.safe_dump(data, sort_keys=False)
    path.write_text(serialized, encoding="utf-8")
    return path.read_bytes()


def _client(
    *,
    settings: Settings | None = None,
    config_path: str | Path = "contextkeeper.yaml",
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[TestClient, object | None]:
    monkeypatch.setattr(connection_test.httpx, "AsyncClient", RecordingAsyncClient)
    app = create_app(settings or Settings(), config_path=config_path)
    return TestClient(app), app


def _post_candidate(
    client: TestClient,
    *,
    base_url: object = "http://candidate-ollama.internal:11434",
    timeout_seconds: object = 120,
) -> httpx.Response:
    return client.post(
        CONNECTION_TEST_ENDPOINT,
        json={
            "base_url": base_url,
            "timeout_seconds": timeout_seconds,
        },
    )


def _timeout_value(client: RecordingAsyncClient, field: str) -> float:
    timeout = client.kwargs["timeout"]
    if isinstance(timeout, (int, float)):
        return float(timeout)
    value = getattr(timeout, field)
    assert isinstance(value, (int, float))
    return float(value)


def _connect_error(
    request: httpx.Request,
    cause: BaseException,
) -> httpx.ConnectError:
    try:
        raise cause
    except BaseException as error:
        try:
            raise httpx.ConnectError("connection failed", request=request) from error
        except httpx.ConnectError as wrapped:
            return wrapped


def test_connection_test_success_uses_normalized_draft_and_returns_version_latency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"version": "0.5.7"}, request=request)

    RecordingAsyncClient.handler = handler
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(
        client,
        base_url="https://candidate-ollama.internal/ollama///",
        timeout_seconds=120,
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == CONNECTION_RESPONSE_KEYS
    assert data["connected"] is True
    assert data["tested_endpoint"] == (
        "https://candidate-ollama.internal/ollama"
    )
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0
    assert data["ollama_version"] == "0.5.7"
    assert data["failure_category"] is None
    assert "Connection successful" in data["message"]
    assert "0.5.7" in data["message"]
    assert "restart ContextKeeper" in data["message"]
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert str(requests[0].url) == (
        "https://candidate-ollama.internal/ollama/api/version"
    )


@pytest.mark.parametrize(
    ("draft_timeout", "expected_probe_timeout"),
    [
        (1, 1.0),
        (3, 3.0),
        (10, 10.0),
        (120, 10.0),
        (2**31, 10.0),
        (10**309, 10.0),
    ],
)
def test_connection_test_uses_bounded_draft_timeout_for_all_http_phases(
    monkeypatch: pytest.MonkeyPatch,
    draft_timeout: int,
    expected_probe_timeout: float,
) -> None:
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(client, timeout_seconds=draft_timeout)

    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert len(RecordingAsyncClient.instances) == 1
    temporary = RecordingAsyncClient.instances[0]
    for field in ("connect", "read", "write", "pool"):
        assert _timeout_value(temporary, field) == expected_probe_timeout
    assert temporary.kwargs["trust_env"] is False
    assert temporary.kwargs["follow_redirects"] is False
    assert temporary.kwargs.get("verify", True) is not False


def test_connection_test_enforces_absolute_wall_clock_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class SlowAsyncClient(RecordingAsyncClient):
        async def get(self, url: str, **kwargs: object) -> httpx.Response:
            request = httpx.Request("GET", url, **kwargs)
            self.requests.append(request)
            await asyncio.Event().wait()
            raise AssertionError("The absolute probe deadline did not cancel the request.")

    monkeypatch.setattr(connection_test, "_MAX_INTERACTIVE_PROBE_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(connection_test.httpx, "AsyncClient", SlowAsyncClient)
    client = TestClient(create_app(Settings()))

    response = _post_candidate(client, timeout_seconds=120)

    assert response.status_code == 200
    assert response.json()["connected"] is False
    assert response.json()["failure_category"] == "timeout"
    assert len(SlowAsyncClient.instances) == 1
    assert SlowAsyncClient.instances[0].closed is True
    assert len(SlowAsyncClient.instances[0].requests) == 1


@pytest.mark.parametrize(
    ("base_url", "timeout_seconds", "category", "location"),
    [
        ("", 120, "invalid_endpoint", ["body", "base_url"]),
        ("ollama.internal:11434", 120, "invalid_endpoint", ["body", "base_url"]),
        ("ftp://ollama.internal:11434", 120, "invalid_endpoint", ["body", "base_url"]),
        (
            "http://user:secret@ollama.internal:11434",
            120,
            "invalid_endpoint",
            ["body", "base_url"],
        ),
        (
            "http://ollama.internal:11434?query=yes",
            120,
            "invalid_endpoint",
            ["body", "base_url"],
        ),
        (
            "http://ollama.internal:11434#fragment",
            120,
            "invalid_endpoint",
            ["body", "base_url"],
        ),
        ("http://ollama.internal:99999", 120, "invalid_endpoint", ["body", "base_url"]),
        ("http://localhost:11500", 120, "invalid_endpoint", ["body", "base_url"]),
        ("http://127.0.0.2:11500", 120, "invalid_endpoint", ["body", "base_url"]),
        (
            "http://[::ffff:127.0.0.1]:11500/api",
            120,
            "invalid_endpoint",
            ["body", "base_url"],
        ),
        (
            "http://[::ffff:127.0.0.2%251]:11500/v1",
            120,
            "invalid_endpoint",
            ["body", "base_url"],
        ),
        ("http://ollama.internal:11434", 0, "invalid_timeout", ["body", "timeout_seconds"]),
        ("http://ollama.internal:11434", -1, "invalid_timeout", ["body", "timeout_seconds"]),
        ("http://ollama.internal:11434", True, "invalid_timeout", ["body", "timeout_seconds"]),
        ("http://ollama.internal:11434", 3.0, "invalid_timeout", ["body", "timeout_seconds"]),
        ("http://ollama.internal:11434", "3", "invalid_timeout", ["body", "timeout_seconds"]),
    ],
)
def test_connection_test_invalid_candidate_returns_structured_422_without_probe(
    monkeypatch: pytest.MonkeyPatch,
    base_url: object,
    timeout_seconds: object,
    category: str,
    location: list[str],
) -> None:
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(
        client,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )

    assert response.status_code == 422
    data = response.json()
    assert CONNECTION_RESPONSE_KEYS.issubset(data)
    assert data["connected"] is False
    if base_url in {
        "http://localhost:11500",
        "http://127.0.0.2:11500",
        "http://[::ffff:127.0.0.1]:11500/api",
        "http://[::ffff:127.0.0.2%251]:11500/v1",
    }:
        assert data["tested_endpoint"] == base_url
    else:
        assert data["tested_endpoint"] is None
    assert data["latency_ms"] is None
    assert data["ollama_version"] is None
    assert data["failure_category"] == category
    assert "detail" in data
    assert any(detail["loc"] == location for detail in data["detail"])
    assert RecordingAsyncClient.instances == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"base_url": "http://ollama.internal:11434"},
        {"timeout_seconds": 120},
        {"base_url": None, "timeout_seconds": 120},
        {"base_url": 123, "timeout_seconds": 120},
        [],
    ],
)
def test_connection_test_malformed_request_returns_structured_422(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    client, _ = _client(monkeypatch=monkeypatch)

    response = client.post(CONNECTION_TEST_ENDPOINT, json=payload)

    assert response.status_code == 422
    data = response.json()
    assert CONNECTION_RESPONSE_KEYS.issubset(data)
    assert data["connected"] is False
    assert data["latency_ms"] is None
    assert data["ollama_version"] is None
    assert data["failure_category"] in {
        "invalid_endpoint",
        "invalid_timeout",
        "invalid_request",
    }
    assert isinstance(data.get("detail"), list)
    assert RecordingAsyncClient.instances == []


def test_connection_test_malformed_json_returns_structured_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _client(monkeypatch=monkeypatch)

    response = client.post(
        CONNECTION_TEST_ENDPOINT,
        content="{not-json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    data = response.json()
    assert CONNECTION_RESPONSE_KEYS.issubset(data)
    assert data["connected"] is False
    assert data["failure_category"] == "invalid_request"
    assert isinstance(data.get("detail"), list)
    assert RecordingAsyncClient.instances == []


@pytest.mark.parametrize(
    ("handler", "category"),
    [
        (
            lambda request: (_ for _ in ()).throw(
                _connect_error(
                    request,
                    socket.gaierror(socket.EAI_NONAME, "name not known"),
                )
            ),
            "dns_resolution",
        ),
        (
            lambda request: (_ for _ in ()).throw(
                _connect_error(request, ConnectionRefusedError("refused"))
            ),
            "connection_refused",
        ),
        (
            lambda request: (_ for _ in ()).throw(
                httpx.ReadTimeout("timed out", request=request)
            ),
            "timeout",
        ),
        (
            lambda request: (_ for _ in ()).throw(
                _connect_error(
                    request,
                    ssl.SSLCertVerificationError("certificate verify failed"),
                )
            ),
            "tls_error",
        ),
        (
            lambda request: httpx.Response(
                503,
                json={"error": "unavailable"},
                request=request,
            ),
            "http_error",
        ),
        (
            lambda request: httpx.Response(
                200,
                content=b"{not-json",
                headers={"content-type": "application/json"},
                request=request,
            ),
            "malformed_response",
        ),
        (
            lambda request: httpx.Response(
                200,
                json=["not", "an", "ollama", "object"],
                request=request,
            ),
            "non_ollama_response",
        ),
        (
            lambda request: httpx.Response(
                200,
                json={"status": "ok"},
                request=request,
            ),
            "missing_version",
        ),
        (
            lambda request: httpx.Response(
                200,
                json={"version": ""},
                request=request,
            ),
            "invalid_version",
        ),
        (
            lambda request: (_ for _ in ()).throw(
                httpx.ConnectError("other network failure", request=request)
            ),
            "network_error",
        ),
    ],
)
def test_connection_test_categorizes_probe_failures_without_internal_details(
    monkeypatch: pytest.MonkeyPatch,
    handler: Callable[[httpx.Request], httpx.Response],
    category: str,
) -> None:
    RecordingAsyncClient.handler = handler
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(
        client,
        base_url="https://candidate-ollama.internal/ollama/",
        timeout_seconds=120,
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == CONNECTION_RESPONSE_KEYS
    assert data["connected"] is False
    assert data["tested_endpoint"] == (
        "https://candidate-ollama.internal/ollama"
    )
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0
    assert data["ollama_version"] is None
    assert data["failure_category"] == category
    assert "Connection failed" in data["message"]
    assert "Runtime and saved configuration were not changed" in data["message"]
    assert "Traceback" not in response.text
    assert "certificate verify failed" not in response.text
    assert "other network failure" not in response.text
    assert len(RecordingAsyncClient.instances) == 1
    assert len(RecordingAsyncClient.instances[0].requests) == 1
    assert RecordingAsyncClient.instances[0].closed is True


@pytest.mark.parametrize(
    ("payload", "category"),
    [
        ({}, "missing_version"),
        ({"version": None}, "invalid_version"),
        ({"version": 0}, "invalid_version"),
        ({"version": True}, "invalid_version"),
        ({"version": []}, "invalid_version"),
        ({"version": {}}, "invalid_version"),
        ({"version": "   "}, "invalid_version"),
    ],
)
def test_connection_test_rejects_missing_or_invalid_version_payload(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    category: str,
) -> None:
    RecordingAsyncClient.handler = lambda request: httpx.Response(
        200,
        json=payload,
        request=request,
    )
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(client)

    assert response.status_code == 200
    assert response.json()["connected"] is False
    assert response.json()["failure_category"] == category


@pytest.mark.parametrize("success", [True, False])
def test_connection_test_closes_temporary_client_on_success_and_failure(
    monkeypatch: pytest.MonkeyPatch,
    success: bool,
) -> None:
    if not success:
        RecordingAsyncClient.handler = lambda request: (_ for _ in ()).throw(
            httpx.ReadTimeout("timed out", request=request)
        )
    client, _ = _client(monkeypatch=monkeypatch)

    response = _post_candidate(client)

    assert response.status_code == 200
    assert response.json()["connected"] is success
    assert len(RecordingAsyncClient.instances) == 1
    assert RecordingAsyncClient.instances[0].closed is True


@pytest.mark.parametrize("success", [True, False])
def test_connection_test_preserves_runtime_yaml_active_client_and_health_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    success: bool,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_config(
        config_path,
        {
            "server": {"host": "127.0.0.1", "port": 11600},
            "ollama": {
                "base_url": "http://active-ollama.internal:11434",
                "timeout_seconds": 120,
            },
            "custom_future_category": {"preserve": True},
        },
    )
    runtime = Settings(
        server={"host": "127.0.0.1", "port": 11600},
        ollama={
            "base_url": "http://active-ollama.internal:11434",
            "timeout_seconds": 120,
        },
    )
    monkeypatch.setattr(proxy_routes, "OllamaClient", TrackingProxyClient)
    monkeypatch.setattr(connection_test.httpx, "AsyncClient", RecordingAsyncClient)
    if not success:
        RecordingAsyncClient.handler = lambda request: (_ for _ in ()).throw(
            httpx.ConnectError("network failure", request=request)
        )
    app = create_app(runtime, config_path=config_path)
    client = TestClient(app)
    assert len(TrackingProxyClient.instances) == 1
    active_client = TrackingProxyClient.instances[0]
    runtime_before = runtime.model_dump()
    health_before = activity_manager.snapshot().to_dict()
    request_metrics_before = metrics_store.snapshot()["requests"]
    model_context_window_cache.store("preserved-model:latest", 32768)

    response = _post_candidate(
        client,
        base_url="http://candidate-ollama.internal:11434",
        timeout_seconds=30,
    )

    assert response.status_code == 200
    assert response.json()["connected"] is success
    assert app.state.settings is runtime
    assert runtime.model_dump() == runtime_before
    assert config_path.read_bytes() == original
    assert len(TrackingProxyClient.instances) == 1
    assert TrackingProxyClient.instances[0] is active_client
    assert activity_manager.snapshot().to_dict() == health_before
    assert metrics_store.snapshot()["requests"] == request_metrics_before
    assert model_context_window_cache.get("preserved-model:latest") == 32768


def test_connection_test_unsupported_methods_are_not_proxied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _client(monkeypatch=monkeypatch)

    for method in ("GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
        response = client.request(method, CONNECTION_TEST_ENDPOINT, json={})
        assert response.status_code == 405
        assert response.headers["allow"] == "POST"

    assert RecordingAsyncClient.instances == []


def test_connection_configuration_put_does_not_replace_active_proxy_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_config(
        config_path,
        {
            "ollama": {
                "base_url": "http://active-ollama.internal:11434",
                "timeout_seconds": 120,
            }
        },
    )
    runtime = Settings(
        ollama={
            "base_url": "http://active-ollama.internal:11434",
            "timeout_seconds": 120,
        }
    )
    monkeypatch.setattr(proxy_routes, "OllamaClient", TrackingProxyClient)
    app = create_app(runtime, config_path=config_path)
    client = TestClient(app)
    assert len(TrackingProxyClient.instances) == 1
    active_client = TrackingProxyClient.instances[0]

    response = client.put(
        "/api/dashboard/settings/config",
        json={
            "ollama": {
                "base_url": "http://unreachable-candidate.internal:11434",
                "timeout_seconds": 45,
            }
        },
    )

    assert response.status_code == 200
    assert app.state.settings is runtime
    assert runtime.ollama.base_url == "http://active-ollama.internal:11434"
    assert runtime.ollama.timeout_seconds == 120
    assert len(TrackingProxyClient.instances) == 1
    assert TrackingProxyClient.instances[0] is active_client
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["ollama"] == {
        "base_url": "http://unreachable-candidate.internal:11434",
        "timeout_seconds": 45,
    }
