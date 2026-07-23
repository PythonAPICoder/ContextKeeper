"""Isolated candidate Ollama connection testing for dashboard Settings."""

from __future__ import annotations

import asyncio
import logging
import socket
import ssl
import time
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

import httpx
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
)

from ..config import (
    Settings,
    normalize_ollama_base_url,
    validate_ollama_not_self_proxy,
    validate_ollama_timeout_seconds,
)

logger = logging.getLogger("ctxkeeper.dashboard.settings.connection")

ConnectionFailureCategory = Literal[
    "invalid_endpoint",
    "invalid_timeout",
    "invalid_request",
    "dns_resolution",
    "connection_refused",
    "timeout",
    "tls_error",
    "http_error",
    "malformed_response",
    "non_ollama_response",
    "missing_version",
    "invalid_version",
    "network_error",
]
ConnectionValidationDetail = list[dict[str, object]]

_MAX_INTERACTIVE_PROBE_TIMEOUT_SECONDS = 10.0
_MAX_VERSION_LENGTH = 128


class ConnectionTestCandidate(BaseModel):
    """Strict, normalized draft values used by one candidate probe."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_url: StrictStr
    timeout_seconds: StrictInt

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        return normalize_ollama_base_url(value)

    @field_validator("timeout_seconds")
    @classmethod
    def _validate_timeout_seconds(cls, value: int) -> int:
        return validate_ollama_timeout_seconds(value)


class ConnectionTestResult(BaseModel):
    """Safe structured response for the transient Settings candidate test."""

    model_config = ConfigDict(frozen=True)

    connected: bool
    tested_endpoint: str | None
    latency_ms: float | None = Field(ge=0)
    ollama_version: str | None
    failure_category: ConnectionFailureCategory | None
    message: str


class ConnectionTestValidationError(ValueError):
    """Client-safe request validation failure with field associations."""

    def __init__(
        self,
        *,
        result: ConnectionTestResult,
        detail: ConnectionValidationDetail,
    ) -> None:
        super().__init__(result.message)
        self.result = result
        self.detail = detail


def validate_connection_test_request(
    payload: object,
    settings: Settings,
) -> ConnectionTestCandidate:
    """Validate draft connection values without mutating canonical settings."""

    try:
        candidate = ConnectionTestCandidate.model_validate(payload)
    except ValidationError as exc:
        detail = _validation_error_detail(exc)
        category = _validation_failure_category(detail)
        result = _failure_result(
            endpoint=None,
            latency_ms=None,
            category=category,
            reason=(
                "AI Server Endpoint is invalid"
                if category == "invalid_endpoint"
                else "Request Timeout must be a positive whole number"
                if category == "invalid_timeout"
                else "the connection test request is invalid"
            ),
        )
        _log_failure(result)
        raise ConnectionTestValidationError(result=result, detail=detail) from exc

    try:
        validate_ollama_not_self_proxy(
            candidate.base_url,
            listener_host=settings.server.host,
            listener_port=settings.server.port,
        )
    except ValueError as exc:
        detail = [
            {
                "loc": ["body", "base_url"],
                "msg": str(exc),
                "type": "value_error",
            }
        ]
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=None,
            category="invalid_endpoint",
            reason="AI Server Endpoint points directly to ContextKeeper's own listener",
        )
        _log_failure(result)
        raise ConnectionTestValidationError(result=result, detail=detail) from exc
    return candidate


async def test_ollama_connection(
    candidate: ConnectionTestCandidate,
) -> ConnectionTestResult:
    """Perform exactly one bounded Ollama version probe with an isolated client."""

    version_url = f"{candidate.base_url}/api/version"
    probe_timeout = float(
        min(
            candidate.timeout_seconds,
            _MAX_INTERACTIVE_PROBE_TIMEOUT_SECONDS,
        )
    )
    started = time.perf_counter()
    try:
        async with asyncio.timeout(probe_timeout):
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(probe_timeout),
                trust_env=False,
                follow_redirects=False,
            ) as client:
                response = await client.get(
                    version_url,
                    headers={"Accept": "application/json"},
                )
    except Exception as exc:
        latency_ms = _elapsed_milliseconds(started)
        category, reason = _classify_request_failure(exc)
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category=category,
            reason=reason,
        )
        _log_failure(result)
        return result

    latency_ms = _elapsed_milliseconds(started)
    if not response.is_success:
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category="http_error",
            reason=f"Ollama returned HTTP {response.status_code}",
        )
        _log_failure(result)
        return result

    try:
        payload = response.json()
    except ValueError:
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category="malformed_response",
            reason="the server returned malformed JSON",
        )
        _log_failure(result)
        return result
    if not isinstance(payload, dict):
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category="non_ollama_response",
            reason="the server did not return an Ollama version object",
        )
        _log_failure(result)
        return result
    if "version" not in payload:
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category="missing_version",
            reason="the server response did not include an Ollama version",
        )
        _log_failure(result)
        return result

    raw_version = payload["version"]
    if (
        not isinstance(raw_version, str)
        or not raw_version.strip()
        or len(raw_version.strip()) > _MAX_VERSION_LENGTH
        or any(ord(character) < 32 or ord(character) == 127 for character in raw_version)
    ):
        result = _failure_result(
            endpoint=candidate.base_url,
            latency_ms=latency_ms,
            category="invalid_version",
            reason="the server returned an invalid Ollama version",
        )
        _log_failure(result)
        return result

    version = raw_version.strip()
    latency_text = _format_latency(latency_ms)
    return ConnectionTestResult(
        connected=True,
        tested_endpoint=candidate.base_url,
        latency_ms=latency_ms,
        ollama_version=version,
        failure_category=None,
        message=(
            f"Connection successful: Ollama {version} responded in {latency_text} ms. "
            "This test did not save or activate the endpoint. Save the configuration "
            "and restart ContextKeeper to use it unless a higher-priority override is active."
        ),
    )


def _validation_error_detail(exc: ValidationError) -> ConnectionValidationDetail:
    details: ConnectionValidationDetail = []
    for error in exc.errors():
        detail: dict[str, object] = {
            "loc": ["body", *error.get("loc", ())],
            "msg": str(error.get("msg", "Invalid connection test value.")),
            "type": str(error.get("type", "value_error")),
        }
        details.append(detail)
    return details


def _validation_failure_category(
    detail: ConnectionValidationDetail,
) -> ConnectionFailureCategory:
    locations = [
        item.get("loc")
        for item in detail
        if isinstance(item.get("loc"), list)
    ]
    if any("base_url" in location for location in locations):
        return "invalid_endpoint"
    if any("timeout_seconds" in location for location in locations):
        return "invalid_timeout"
    return "invalid_request"


def _classify_request_failure(
    exc: Exception,
) -> tuple[ConnectionFailureCategory, str]:
    chain = _exception_chain(exc)
    if any(
        isinstance(item, (httpx.TimeoutException, TimeoutError))
        for item in chain
    ):
        return "timeout", "the connection attempt timed out"
    if any(isinstance(item, ssl.SSLError) for item in chain):
        return "tls_error", "TLS or certificate verification failed"
    if any(isinstance(item, socket.gaierror) for item in chain):
        return "dns_resolution", "the server hostname could not be resolved"
    if any(isinstance(item, ConnectionRefusedError) for item in chain):
        return "connection_refused", "the server refused the connection"

    combined_message = " ".join(str(item).lower() for item in chain)
    if any(
        marker in combined_message
        for marker in (
            "name or service not known",
            "nodename nor servname",
            "getaddrinfo failed",
            "temporary failure in name resolution",
            "no such host",
        )
    ):
        return "dns_resolution", "the server hostname could not be resolved"
    if any(
        marker in combined_message
        for marker in ("certificate", "certificate_verify_failed", "ssl", "tls")
    ):
        return "tls_error", "TLS or certificate verification failed"
    if "refused" in combined_message:
        return "connection_refused", "the server refused the connection"
    return "network_error", "the server could not be reached"


def _exception_chain(exc: BaseException) -> list[BaseException]:
    chain: list[BaseException] = []
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or current.__context__
    return chain


def _failure_result(
    *,
    endpoint: str | None,
    latency_ms: float | None,
    category: ConnectionFailureCategory,
    reason: str,
) -> ConnectionTestResult:
    return ConnectionTestResult(
        connected=False,
        tested_endpoint=endpoint,
        latency_ms=latency_ms,
        ollama_version=None,
        failure_category=category,
        message=(
            f"Connection failed: {reason}. Runtime and saved configuration were not changed."
        ),
    )


def _elapsed_milliseconds(started: float) -> float:
    return round(max(0.0, (time.perf_counter() - started) * 1000.0), 2)


def _format_latency(latency_ms: float) -> str:
    return f"{latency_ms:.2f}".rstrip("0").rstrip(".")


def _log_failure(result: ConnectionTestResult) -> None:
    logger.warning(
        "Candidate Ollama connection test failed category=%s endpoint_origin=%s latency_ms=%s",
        result.failure_category,
        _safe_endpoint_origin(result.tested_endpoint),
        result.latency_ms,
    )


def _safe_endpoint_origin(endpoint: str | None) -> str:
    if endpoint is None:
        return "unavailable"
    parsed = urlsplit(endpoint)
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
