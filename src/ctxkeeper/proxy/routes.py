from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from typing import Any, Protocol

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from .ollama_client import OllamaClient
from .model_extraction import inspect_request_model
from ..config import Settings
from ..context.conversation_store import conversation_store
from ..diagnostics.activity import activity_manager, is_generation_activity_request
from ..diagnostics.metrics import metrics_store

logger = logging.getLogger("ctxkeeper.proxy")


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


def create_proxy_router(settings: Settings) -> APIRouter:
    router = APIRouter()
    ollama = OllamaClient(settings.ollama.base_url, settings.ollama.timeout_seconds)

    async def proxy_request(request: Request) -> Response:
        started = time.perf_counter()
        full_path = request.url.path
        body = await request.body()
        model_info = inspect_request_model(body)
        model = model_info.model
        client_host = request.client.host if request.client else None
        is_stream_candidate = full_path in {"/api/chat", "/api/generate"}
        wants_stream = _wants_stream(body)
        activity_request_id: str | None = None
        conversation_id: str | None = None

        try:
            if is_generation_activity_request(request.method, full_path):
                activity_request_id = activity_manager.accept_request(
                    method=request.method,
                    endpoint=full_path,
                    model=model,
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
                    body=body,
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
                body=body,
                query=request.url.query,
            )
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
            try:
                latency_ms = (time.perf_counter() - started) * 1000
                metrics_store.record_request(
                    method=request.method,
                    endpoint=full_path,
                    model=model,
                    status_code=upstream.status_code,
                    latency_ms=latency_ms,
                    client_host=client_host,
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
        except asyncio.CancelledError:
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
                activity_manager.complete_request(activity_request_id)
            raise
        except Exception as exc:
            if activity_request_id is not None:
                activity_manager.mark_finalizing(activity_request_id)
            latency_ms = (time.perf_counter() - started) * 1000
            metrics_store.record_request(
                method=request.method,
                endpoint=full_path,
                model=model,
                status_code=502,
                latency_ms=latency_ms,
                client_host=client_host,
            )
            logger.exception("Proxy failure for %s %s", request.method, full_path)
            if activity_request_id is not None:
                activity_manager.complete_request(activity_request_id, ollama_available=False)
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
            metrics_store.record_request(
                method=method,
                endpoint=endpoint,
                model=model,
                status_code=completion_status_code,
                latency_ms=latency_ms,
                client_host=client_host,
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
