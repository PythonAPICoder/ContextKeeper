from __future__ import annotations

import asyncio
import time

import pytest

from ctxkeeper.dashboard.intelligence import DashboardMetrics, HealthEngine, HealthStatus
from ctxkeeper.diagnostics.activity import (
    ActivityState,
    OperationalActivityManager,
    is_generation_activity_request,
)
from ctxkeeper.proxy.routes import _track_streaming_response


def test_initial_activity_state_is_starting() -> None:
    manager = OperationalActivityManager()

    snapshot = manager.snapshot()

    assert snapshot.state is ActivityState.STARTING
    assert snapshot.to_dict()["state"] == "starting"


def test_ollama_unavailable_sets_connecting() -> None:
    manager = OperationalActivityManager()

    manager.observe_ollama_status("offline")

    assert manager.snapshot().state is ActivityState.CONNECTING


def test_ollama_available_before_completed_request_sets_ready() -> None:
    manager = OperationalActivityManager()

    manager.observe_ollama_status("online")

    snapshot = manager.snapshot()
    assert snapshot.state is ActivityState.READY
    assert snapshot.active_request_count == 0


def test_request_lifecycle_reaches_receiving_and_thinking() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")

    request_id = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")

    receiving = manager.snapshot()
    assert receiving.state is ActivityState.RECEIVING
    assert receiving.active_request_count == 1

    manager.mark_thinking(request_id)

    thinking = manager.snapshot()
    assert thinking.state is ActivityState.THINKING
    assert thinking.active_request_count == 1


def test_latest_model_updates_on_request_acceptance_and_persists_after_completion() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")
    first = manager.accept_request(method="POST", endpoint="/api/chat", model="qwen2.5:32b")
    manager.complete_request(first, ollama_available=True)

    second = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")

    active = manager.snapshot()
    assert active.active_model == "llava:latest"
    assert active.active_model_state == "known"
    assert active.latest_model == "llava:latest"
    assert active.to_dict()["active_model"] == "llava:latest"
    assert active.to_dict()["active_model_state"] == "known"
    assert active.to_dict()["latest_model"] == "llava:latest"

    manager.complete_request(second, ollama_available=True)

    idle = manager.snapshot()
    assert idle.state is ActivityState.IDLE
    assert idle.active_model is None
    assert idle.active_model_state == "none"
    assert idle.latest_model == "llava:latest"


def test_active_request_without_model_is_unknown_without_overwriting_latest_model() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")
    first = manager.accept_request(method="POST", endpoint="/api/chat", model="gpt-oss:20b")
    manager.complete_request(first, ollama_available=True)

    second = manager.accept_request(method="POST", endpoint="/api/chat", model=None)

    active = manager.snapshot()
    assert active.state is ActivityState.RECEIVING
    assert active.active_model is None
    assert active.active_model_state == "unknown"
    assert active.latest_model == "gpt-oss:20b"
    assert "unknown model" in active.details

    manager.complete_request(second, ollama_available=True)

    idle = manager.snapshot()
    assert idle.state is ActivityState.IDLE
    assert idle.active_model_state == "none"
    assert idle.latest_model == "gpt-oss:20b"


def test_streaming_begins_on_first_actual_streamed_chunk() -> None:
    async def source():
        yield b"first-token"
        yield b"second-token"

    async def run() -> None:
        manager = OperationalActivityManager()
        manager.observe_ollama_status("online")
        request_id = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")
        manager.mark_thinking(request_id)

        import ctxkeeper.proxy.routes as proxy_routes

        original_manager = proxy_routes.activity_manager
        proxy_routes.activity_manager = manager
        try:
            stream = _track_streaming_response(
                stream_iterator=source(),
                activity_request_id=request_id,
                started=time.perf_counter(),
                method="POST",
                endpoint="/api/chat",
                model="llava:latest",
                upstream_status_code=200,
                client_host="127.0.0.1",
            )
            chunk = await stream.__anext__()
            assert chunk == b"first-token"
            assert manager.snapshot().state is ActivityState.STREAMING
            await stream.aclose()
            assert manager.snapshot().state is ActivityState.IDLE
        finally:
            proxy_routes.activity_manager = original_manager

    asyncio.run(run())


def test_request_completion_passes_through_finalizing_and_returns_idle() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")
    request_id = manager.accept_request(method="POST", endpoint="/api/generate", model="llava:latest")
    manager.mark_thinking(request_id)

    manager.mark_finalizing(request_id)

    finalizing = manager.snapshot()
    assert finalizing.state is ActivityState.FINALIZING

    manager.complete_request(request_id, ollama_available=True)

    idle = manager.snapshot()
    assert idle.state is ActivityState.IDLE
    assert idle.active_request_count == 0


def test_sequential_requests_do_not_leave_stale_activity() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")

    first = manager.accept_request(method="POST", endpoint="/api/chat", model="qwen2.5:32b")
    manager.mark_thinking(first)
    manager.mark_finalizing(first)
    manager.complete_request(first, ollama_available=True)

    second = manager.accept_request(method="POST", endpoint="/api/generate", model="llava:latest")
    manager.mark_thinking(second)
    manager.mark_streaming(second)
    manager.mark_finalizing(second)
    manager.complete_request(second, ollama_available=True)

    snapshot = manager.snapshot()
    assert snapshot.state is ActivityState.IDLE
    assert snapshot.active_request_count == 0


def test_overlapping_requests_do_not_return_to_idle_early() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")
    streaming = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")
    thinking = manager.accept_request(method="POST", endpoint="/api/generate", model="qwen2.5:32b")
    manager.mark_streaming(streaming)
    manager.mark_thinking(thinking)

    assert manager.snapshot().state is ActivityState.STREAMING

    manager.mark_finalizing(streaming)
    manager.complete_request(streaming, ollama_available=True)

    still_active = manager.snapshot()
    assert still_active.state is ActivityState.THINKING
    assert still_active.active_request_count == 1

    manager.mark_finalizing(thinking)
    manager.complete_request(thinking, ollama_available=True)

    assert manager.snapshot().state is ActivityState.IDLE


def test_error_cleanup_returns_to_non_stale_connecting_state() -> None:
    manager = OperationalActivityManager()
    manager.observe_ollama_status("online")
    request_id = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")
    manager.mark_thinking(request_id)
    manager.mark_finalizing(request_id)

    manager.complete_request(request_id, ollama_available=False)

    snapshot = manager.snapshot()
    assert snapshot.state is ActivityState.CONNECTING
    assert snapshot.active_request_count == 0


def test_cancellation_cleanup_returns_to_valid_non_stale_state() -> None:
    async def source():
        raise asyncio.CancelledError
        yield b"unreachable"

    async def run() -> None:
        manager = OperationalActivityManager()
        manager.observe_ollama_status("online")
        request_id = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")
        manager.mark_thinking(request_id)

        import ctxkeeper.proxy.routes as proxy_routes

        original_manager = proxy_routes.activity_manager
        proxy_routes.activity_manager = manager
        try:
            stream = _track_streaming_response(
                stream_iterator=source(),
                activity_request_id=request_id,
                started=time.perf_counter(),
                method="POST",
                endpoint="/api/chat",
                model="llava:latest",
                upstream_status_code=200,
                client_host="127.0.0.1",
            )
            with pytest.raises(asyncio.CancelledError):
                await stream.__anext__()
            snapshot = manager.snapshot()
            assert snapshot.state is ActivityState.IDLE
            assert snapshot.active_request_count == 0
        finally:
            proxy_routes.activity_manager = original_manager

    asyncio.run(run())


def test_metadata_requests_are_not_generation_activity() -> None:
    assert is_generation_activity_request("POST", "/api/show") is False
    assert is_generation_activity_request("GET", "/api/tags") is False
    assert is_generation_activity_request("POST", "/api/chat") is True
    assert is_generation_activity_request("POST", "/v1/chat/completions") is True


def test_health_engine_remains_independent_from_activity_state() -> None:
    manager = OperationalActivityManager()
    request_id = manager.accept_request(method="POST", endpoint="/api/chat", model="llava:latest")
    manager.mark_streaming(request_id)

    assessment = HealthEngine().evaluate_metrics(
        DashboardMetrics(
            proxy_online=True,
            ollama_online=True,
            context_percent=0.0,
            average_latency_ms=0.0,
            active_requests=0,
        )
    )

    assert manager.snapshot().state is ActivityState.STREAMING
    assert assessment.status is HealthStatus.HEALTHY
