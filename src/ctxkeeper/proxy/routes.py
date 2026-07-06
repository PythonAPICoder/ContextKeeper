from __future__ import annotations

import json
import logging
import time
from typing import Any, Protocol

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from .ollama_client import OllamaClient
from ..config import Settings
from ..context.conversation_store import conversation_store
from ..diagnostics.metrics import metrics_store

logger = logging.getLogger("ctxkeeper.proxy")


class _ConversationIdentity(Protocol):
    conversation_id: str


try:
    from ..diagnostics.conversation_identity import conversation_identity_registry
except ImportError:
    conversation_identity_registry = None


def _extract_model(body: bytes) -> str | None:
    if not body:
        return None
    try:
        data: Any = json.loads(body.decode("utf-8"))
        if isinstance(data, dict):
            model = data.get("model")
            return str(model) if model else None
    except Exception:
        return None
    return None


def _decode_json_object(body: bytes) -> dict[str, Any] | None:
    if not body:
        return None
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
        model = _extract_model(body)
        client_host = request.client.host if request.client else None
        is_stream_candidate = full_path in {"/api/chat", "/api/generate"}
        wants_stream = _wants_stream(body)
        conversation_id = _conversation_id_for_chat(
            request=request,
            model=model,
            wants_stream=wants_stream,
        )
        _record_incoming_chat_messages(conversation_id, body)

        try:
            if is_stream_candidate and wants_stream:
                status_code, headers, stream_iterator = await ollama.stream(
                    method=request.method,
                    path=full_path,
                    headers=dict(request.headers),
                    body=body,
                    query=request.url.query,
                )
                latency_ms = (time.perf_counter() - started) * 1000
                metrics_store.record_request(
                    method=request.method,
                    endpoint=full_path,
                    model=model,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    client_host=client_host,
                )
                logger.info(
                    "%s %s model=%s status=%s latency_ms=%.2f client=%s stream=true",
                    request.method,
                    full_path,
                    model,
                    status_code,
                    latency_ms,
                    client_host,
                )
                # TODO: Capture streaming assistant responses only after adding a
                # transparent stream tee that preserves chunk timing and errors.
                return StreamingResponse(
                    stream_iterator,
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
        except Exception as exc:
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
