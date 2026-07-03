from __future__ import annotations

import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from .ollama_client import OllamaClient
from ..config import Settings
from ..diagnostics.metrics import metrics_store

logger = logging.getLogger("ctxkeeper.proxy")


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


def create_proxy_router(settings: Settings) -> APIRouter:
    router = APIRouter()
    ollama = OllamaClient(settings.ollama.base_url, settings.ollama.timeout_seconds)

    @router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def proxy(request: Request, path: str) -> Response:
        started = time.perf_counter()
        full_path = request.url.path
        body = await request.body()
        model = _extract_model(body)
        client_host = request.client.host if request.client else None

        try:
            is_stream_candidate = full_path in {"/api/chat", "/api/generate"}
            wants_stream = b'"stream":false' not in body.replace(b" ", b"").lower()

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

    return router
