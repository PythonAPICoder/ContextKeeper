from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from itertools import count
from typing import Any, Protocol

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from .ollama_client import OllamaClient
from .model_extraction import inspect_request_model
from ..config import Settings
from ..context.conversation_store import conversation_store
from ..diagnostics.activity import activity_manager, is_generation_activity_request
from ..diagnostics.metrics import metrics_store
from ..model_context import (
    ContextWindowResolution,
    active_context_window_overrides,
    configured_context_window_tokens,
    enforce_context_window_in_request_body,
    model_context_window_cache,
    normalize_model_name,
    resolve_context_window,
    runtime_num_ctx_from_request_body,
)

logger = logging.getLogger("ctxkeeper.proxy")
_DISCOVERY_TASKS: dict[str, asyncio.Task[int | None]] = {}
_FIRST_CALL_DISCOVERY_TIMEOUT_SECONDS = 5.0
_GENERATION_SEQUENCE = count(1)


class _ConversationIdentity(Protocol):
    conversation_id: str


try:
    from ..diagnostics.conversation_identity import conversation_identity_registry
except ImportError:
    conversation_identity_registry = None


def _decode_json_object(body: bytes) -> dict[str, Any] | None:
    if not body:
        return None
    import json

    try:
        data: Any = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _wants_stream(body: bytes) -> bool:
    return b'"stream":false' not in body.replace(b" ", b"").lower()


def _conversation_id_for_chat(
    *,
    request: Request,
    model: str | None,
    wants_stream: bool,
) -> str | None:
    if request.url.path != "/api/chat" or request.method.upper() != "POST":
        return None

    if conversation_identity_registry is not None:
        identity: _ConversationIdentity | None = conversation_identity_registry.observe_request(
            method=request.method,
            endpoint=request.url.path,
            model=model,
            stream=wants_stream,
            client_host=request.client.host if request.client else None,
            client_user_agent=request.headers.get("user-agent"),
        )
        if identity is not None:
            return identity.conversation_id

    conversation = conversation_store.create()
    return conversation.conversation_id


def _record_incoming_chat_messages(conversation_id: str | None, body: bytes) -> None:
    if conversation_id is None:
        return

    data = _decode_json_object(body)
    if data is None:
        return

    messages = data.get("messages")
    if not isinstance(messages, list):
        return

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        if isinstance(role, str) and isinstance(content, str):
            conversation_store.append_message(conversation_id, role, content)


def _record_chat_assistant_response(conversation_id: str | None, response_body: bytes) -> None:
    if conversation_id is None:
        return

    data = _decode_json_object(response_body)
    if data is None:
        return

    message = data.get("message")
    if not isinstance(message, dict):
        return

    content = message.get("content")
    if isinstance(content, str):
        conversation_store.append_message(conversation_id, "assistant", content)


def _num_ctx_diagnostics(body: bytes) -> tuple[bool, int | None]:
    data = _decode_json_object(body)
    if data is None:
        return False, None
    options = data.get("options")
    if isinstance(options, dict) and "num_ctx" in options:
        return True, runtime_num_ctx_from_request_body(body)
    if "num_ctx" in data:
        return True, runtime_num_ctx_from_request_body(body)
    return False, None


def _log_generation_observation(
    *,
    event: str,
    generation_sequence: int | None,
    endpoint: str,
    method: str,
    model: str | None,
    model_field: str | None = None,
    top_level_keys: tuple[str, ...] = (),
    num_ctx_present: bool | None = None,
    num_ctx_value: int | None = None,
    request_id: str | None = None,
    context_resolution: ContextWindowResolution | None = None,
    metric_event: dict[str, Any] | None = None,
    status_code: int | None = None,
    stream: bool | None = None,
    detail: str | None = None,
) -> None:
    if event == "start":
        logger.info(
            "B4.8_DIAG event=start gen_seq=%s endpoint=%s method=%s model=%s model_field_present=%s model_field=%s top_level_keys=%s num_ctx_present=%s num_ctx=%s stream=%s",
            generation_sequence,
            endpoint,
            method,
            model,
            model_field is not None,
            model_field,
            ",".join(top_level_keys),
            num_ctx_present,
            num_ctx_value,
            stream,
        )
        return
    if event in {"override_register", "override_cleanup"}:
        logger.info(
            "B4.8_DIAG event=%s gen_seq=%s request_id=%s model=%s context_source=%s context_tokens=%s",
            event,
            generation_sequence,
            request_id,
            model,
            context_resolution.source if context_resolution else None,
            context_resolution.tokens if context_resolution else None,
        )
        return
    if event == "metric_record":
        logger.info(
            "B4.8_DIAG event=metric_record gen_seq=%s metric_seq=%s metric_timestamp=%s endpoint=%s method=%s model=%s status=%s context_source=%s context_tokens=%s",
            generation_sequence,
            metric_event.get("sequence") if metric_event else None,
            metric_event.get("timestamp") if metric_event else None,
            endpoint,
            method,
            model,
            status_code,
            context_resolution.source if context_resolution else None,
            context_resolution.tokens if context_resolution else None,
        )
        return
    logger.info(
        "B4.8_DIAG event=%s gen_seq=%s endpoint=%s method=%s model=%s status=%s detail=%s",
        event,
        generation_sequence,
        endpoint,
        method,
        model,
        status_code,
        detail,
    )


def _record_show_metadata(model: str | None, response_body: bytes) -> None:
    payload = _decode_json_object(response_body)
    if payload is None:
        return
    tokens = model_context_window_cache.store_from_show_payload(model, payload)
    if tokens is not None:
        logger.debug("Discovered model context window model=%s tokens=%s source=/api/show", model, tokens)


def _discard_discovery_task(cache_key: str, completed: asyncio.Task[int | None]) -> None:
    if _DISCOVERY_TASKS.get(cache_key) is completed:
        _DISCOVERY_TASKS.pop(cache_key, None)


async def _ensure_model_context_discovered(
    *,
    ollama: OllamaClient,
    settings: Settings,
    model: str | None,
) -> int | None:
    if not model:
        return None
    if configured_context_window_tokens(settings, model) is not None:
        return None

    cached = model_context_window_cache.get(model)
    if cached is not None:
        return cached

    key = normalize_model_name(model)
    if key is None:
        return None

    task = _DISCOVERY_TASKS.get(key)
    if task is None:
        if not model_context_window_cache.should_attempt_discovery(model):
            return model_context_window_cache.get(model)
        task = asyncio.create_task(_discover_model_context_window(ollama, model))
        _DISCOVERY_TASKS[key] = task
        task.add_done_callback(lambda completed, cache_key=key: _discard_discovery_task(cache_key, completed))

    timeout_seconds = min(_FIRST_CALL_DISCOVERY_TIMEOUT_SECONDS, float(settings.ollama.timeout_seconds))
    try:
        return await asyncio.wait_for(asyncio.shield(task), timeout=timeout_seconds)
    except TimeoutError:
        logger.debug("Model context first-call discovery timed out model=%s timeout_seconds=%s", model, timeout_seconds)
        return model_context_window_cache.get(model)


async def _discover_model_context_window(ollama: OllamaClient, model: str | None) -> int | None:
    if not model:
        return None
    body = json.dumps({"model": model, "name": model}).encode("utf-8")
    try:
        response = await ollama.request(
            method="POST",
            path="/api/show",
            headers={"content-type": "application/json"},
            body=body,
            query="",
    )
    except Exception as exc:
        logger.debug("Model context discovery failed model=%s error=%s", model, exc)
        return None

    if response.status_code < 200 or response.status_code >= 300:
        logger.debug("Model context discovery returned HTTP %s model=%s", response.status_code, model)
        return None
    before = model_context_window_cache.get(model)
    _record_show_metadata(model, response.content)
    after = model_context_window_cache.get(model)
    if before is None and after is None:
        logger.debug("Model context discovery found no usable context window model=%s", model)
    return after


def _request_context_window_resolution(settings: Settings, model: str | None) -> ContextWindowResolution:
    return resolve_context_window(
        settings,
        model_name=model,
    )


def _register_active_context_window_override(
    request_id: str | None,
    resolution: ContextWindowResolution,
    *,
    generation_sequence: int | None = None,
) -> None:
    active_context_window_overrides.register(
        request_id,
        resolution,
        generation_sequence=generation_sequence,
    )


def create_proxy_router(settings: Settings) -> APIRouter:
    router = APIRouter()
    ollama = OllamaClient(settings.ollama.base_url, settings.ollama.timeout_seconds)

    async def proxy_request(request: Request) -> Response:
        started = time.perf_counter()
        full_path = request.url.path
        body = await request.body()
        model_info = inspect_request_model(body)
        model = model_info.model
        num_ctx_present, num_ctx_value = _num_ctx_diagnostics(body)
        client_host = request.client.host if request.client else None
        is_generation_request = is_generation_activity_request(request.method, full_path)
        is_stream_candidate = full_path in {"/api/chat", "/api/generate"}
        wants_stream = _wants_stream(body)
        generation_sequence: int | None = (
            next(_GENERATION_SEQUENCE)
            if is_generation_request
            else None
        )
        if is_generation_request:
            await _ensure_model_context_discovered(
                ollama=ollama,
                settings=settings,
                model=model,
            )
        context_resolution = _request_context_window_resolution(settings, model)
        outgoing_body = (
            enforce_context_window_in_request_body(body, context_resolution.tokens)
            if is_generation_request
            else body
        )
        activity_request_id: str | None = None
        conversation_id: str | None = None

        try:
            if is_generation_request:
                _log_generation_observation(
                    event="start",
                    generation_sequence=generation_sequence,
                    endpoint=full_path,
                    method=request.method,
                    model=model,
                    model_field=model_info.field_path,
                    top_level_keys=model_info.top_level_keys,
                    num_ctx_present=num_ctx_present,
                    num_ctx_value=num_ctx_value,
                    stream=wants_stream,
                )
                activity_request_id = activity_manager.accept_request(
                    method=request.method,
                    endpoint=full_path,
                    model=model,
                    generation_sequence=generation_sequence,
                )
                _register_active_context_window_override(
                    activity_request_id,
                    context_resolution,
                    generation_sequence=generation_sequence,
                )
                _log_generation_observation(
                    event="override_register",
                    generation_sequence=generation_sequence,
                    endpoint=full_path,
                    method=request.method,
                    model=model,
                    request_id=activity_request_id,
                    context_resolution=context_resolution,
                )
                logger.debug(
                    "Accepted generation request request_id=%s endpoint=%s model=%s model_field=%s top_level_keys=%s stream=%s",
                    activity_request_id,
                    full_path,
                    model,
                    model_info.field_path,
                    ",".join(model_info.top_level_keys),
                    wants_stream,
                )

            conversation_id = _conversation_id_for_chat(
                request=request,
                model=model,
                wants_stream=wants_stream,
            )
            _record_incoming_chat_messages(conversation_id, body)

            if activity_request_id is not None:
                activity_manager.mark_thinking(activity_request_id)

            if is_stream_candidate and wants_stream:
                status_code, headers, stream_iterator = await ollama.stream(
                    method=request.method,
                    path=full_path,
                    headers=dict(request.headers),
                    body=outgoing_body,
                    query=request.url.query,
                )

                monitored_stream = _track_streaming_response(
                    stream_iterator=stream_iterator,
                    activity_request_id=activity_request_id,
                    started=started,
                    method=request.method,
                    endpoint=full_path,
                    model=model,
                    upstream_status_code=status_code,
                    client_host=client_host,
                    context_resolution=context_resolution,
                    generation_sequence=generation_sequence,
                    conversation_id=conversation_id,
                )
                # TODO: Capture streaming assistant responses only after adding a
                # transparent stream tee that preserves chunk timing and errors.
                return StreamingResponse(
                    monitored_stream,
                    status_code=status_code,
                    media_type=headers.get("content-type", "application/x-ndjson"),
                )

            upstream = await ollama.request(
                method=request.method,
                path=full_path,
                headers=dict(request.headers),
                body=outgoing_body,
                query=request.url.query,
            )
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
            try:
                latency_ms = (time.perf_counter() - started) * 1000
                if full_path == "/api/show" and request.method.upper() == "POST":
                    _record_show_metadata(model, upstream.content)
                metric_event = metrics_store.record_request(
                    method=request.method,
                    endpoint=full_path,
                    model=model,
                    status_code=upstream.status_code,
                    latency_ms=latency_ms,
                    client_host=client_host,
                    context_window_tokens=context_resolution.tokens
                    if is_generation_request
                    else None,
                    context_window_source=context_resolution.source
                    if is_generation_request
                    else None,
                    context_window_source_label=context_resolution.source_label
                    if is_generation_request
                    else None,
                    generation_sequence=generation_sequence
                    if is_generation_request
                    else None,
                    conversation_id=conversation_id,
                )
                if is_generation_request:
                    _log_generation_observation(
                        event="metric_record",
                        generation_sequence=generation_sequence,
                        endpoint=full_path,
                        method=request.method,
                        model=model,
                        context_resolution=context_resolution,
                        metric_event=metric_event if isinstance(metric_event, dict) else None,
                        status_code=upstream.status_code,
                    )
                if full_path == "/api/chat" and request.method.upper() == "POST":
                    _record_chat_assistant_response(conversation_id, upstream.content)
                logger.info(
                    "%s %s model=%s status=%s latency_ms=%.2f client=%s stream=false",
                    request.method,
                    full_path,
                    model,
                    upstream.status_code,
                    latency_ms,
                    client_host,
                )
                return Response(
                    content=upstream.content,
                    status_code=upstream.status_code,
                    media_type=upstream.headers.get("content-type"),
                )
            finally:
                if activity_request_id is not None:
                    activity_manager.complete_request(activity_request_id, ollama_available=True)
                    active_context_window_overrides.remove(activity_request_id)
                    _log_generation_observation(
                        event="override_cleanup",
                        generation_sequence=generation_sequence,
                        endpoint=full_path,
                        method=request.method,
                        model=model,
                        request_id=activity_request_id,
                        context_resolution=context_resolution,
                    )
        except asyncio.CancelledError:
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
                activity_manager.complete_request(activity_request_id)
                active_context_window_overrides.remove(activity_request_id)
                _log_generation_observation(
                    event="override_cleanup",
                    generation_sequence=generation_sequence,
                    endpoint=full_path,
                    method=request.method,
                    model=model,
                    request_id=activity_request_id,
                    context_resolution=context_resolution,
                )
            _log_generation_observation(
                event="cancel",
                generation_sequence=generation_sequence,
                endpoint=full_path,
                method=request.method,
                model=model,
                detail="request_cancelled",
            )
            raise
        except Exception as exc:
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
            latency_ms = (time.perf_counter() - started) * 1000
            metric_event = metrics_store.record_request(
                method=request.method,
                endpoint=full_path,
                model=model,
                status_code=502,
                latency_ms=latency_ms,
                client_host=client_host,
                context_window_tokens=context_resolution.tokens
                if is_generation_request
                else None,
                context_window_source=context_resolution.source
                if is_generation_request
                else None,
                context_window_source_label=context_resolution.source_label
                if is_generation_request
                else None,
                generation_sequence=generation_sequence
                if is_generation_request
                else None,
                conversation_id=conversation_id,
            )
            if is_generation_request:
                _log_generation_observation(
                    event="metric_record",
                    generation_sequence=generation_sequence,
                    endpoint=full_path,
                    method=request.method,
                    model=model,
                    context_resolution=context_resolution,
                    metric_event=metric_event if isinstance(metric_event, dict) else None,
                    status_code=502,
                )
            logger.exception("Proxy failure for %s %s", request.method, full_path)
            if activity_request_id is not None:
                activity_manager.complete_request(activity_request_id, ollama_available=False)
                active_context_window_overrides.remove(activity_request_id)
                _log_generation_observation(
                    event="override_cleanup",
                    generation_sequence=generation_sequence,
                    endpoint=full_path,
                    method=request.method,
                    model=model,
                    request_id=activity_request_id,
                    context_resolution=context_resolution,
                )
            _log_generation_observation(
                event="failure",
                generation_sequence=generation_sequence,
                endpoint=full_path,
                method=request.method,
                model=model,
                status_code=502,
                detail=type(exc).__name__,
            )
            return JSONResponse(
                status_code=502,
                content={
                    "error": "ContextKeeper could not reach Ollama or proxy the request.",
                    "detail": str(exc),
                    "ollama_base_url": settings.ollama.base_url,
                },
            )

    @router.get("/api/tags")
    async def api_tags(request: Request) -> Response:
        return await proxy_request(request)

    @router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def proxy(request: Request, path: str) -> Response:
        return await proxy_request(request)

    return router


async def _track_streaming_response(
    *,
    stream_iterator: AsyncIterator[bytes],
    activity_request_id: str | None,
    started: float,
    method: str,
    endpoint: str,
    model: str | None,
    upstream_status_code: int,
    client_host: str | None,
    context_resolution: ContextWindowResolution | None = None,
    generation_sequence: int | None = None,
    conversation_id: str | None = None,
) -> AsyncIterator[bytes]:
    first_chunk_seen = False
    completion_status_code = upstream_status_code
    try:
        async for chunk in stream_iterator:
            if chunk and activity_request_id is not None and not first_chunk_seen:
                activity_manager.mark_streaming(activity_request_id)
                first_chunk_seen = True
            yield chunk
    except asyncio.CancelledError:
        completion_status_code = 499
        raise
    except Exception:
        completion_status_code = 502
        logger.exception("Streaming proxy failure for %s %s", method, endpoint)
        raise
    finally:
        if activity_request_id is not None:
            activity_manager.mark_finalizing(activity_request_id)
        try:
            latency_ms = (time.perf_counter() - started) * 1000
            metric_event = metrics_store.record_request(
                method=method,
                endpoint=endpoint,
                model=model,
                status_code=completion_status_code,
                latency_ms=latency_ms,
                client_host=client_host,
                context_window_tokens=context_resolution.tokens if context_resolution is not None else None,
                context_window_source=context_resolution.source if context_resolution is not None else None,
                context_window_source_label=context_resolution.source_label if context_resolution is not None else None,
                generation_sequence=generation_sequence,
                conversation_id=conversation_id,
            )
            _log_generation_observation(
                event="metric_record",
                generation_sequence=generation_sequence,
                endpoint=endpoint,
                method=method,
                model=model,
                context_resolution=context_resolution,
                metric_event=metric_event if isinstance(metric_event, dict) else None,
                status_code=completion_status_code,
            )
            logger.info(
                "%s %s model=%s status=%s latency_ms=%.2f client=%s stream=true",
                method,
                endpoint,
                model,
                completion_status_code,
                latency_ms,
                client_host,
            )
        finally:
            if activity_request_id is not None:
                activity_manager.complete_request(activity_request_id, ollama_available=True)
                active_context_window_overrides.remove(activity_request_id)
                _log_generation_observation(
                    event="override_cleanup",
                    generation_sequence=generation_sequence,
                    endpoint=endpoint,
                    method=method,
                    model=model,
                    request_id=activity_request_id,
                    context_resolution=context_resolution,
                )
