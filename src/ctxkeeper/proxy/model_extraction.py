from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RequestModelInfo:
    """Normalized model information from a proxy request body."""

    model: str | None
    field_path: str | None
    top_level_keys: tuple[str, ...]
    is_json_object: bool


def inspect_request_model(body: bytes) -> RequestModelInfo:
    """Extract model metadata from supported Ollama/OpenAI-compatible payloads.

    ContextKeeper currently supports the Ollama and OpenAI-compatible request
    shapes where the selected model is carried in the top-level ``model`` field,
    with ``name`` as a compatibility fallback for clients that use Ollama model
    naming terminology in request bodies.
    Prompt text and message contents are intentionally ignored.
    """

    data = _decode_json_object(body)
    if data is None:
        return RequestModelInfo(
            model=None,
            field_path=None,
            top_level_keys=(),
            is_json_object=False,
        )

    keys = tuple(sorted(str(key) for key in data.keys()))
    model = _normalized_model(data.get("model"))
    field_path = "model" if model else None
    if model is None:
        model = _normalized_model(data.get("name"))
        field_path = "name" if model else None
    return RequestModelInfo(
        model=model,
        field_path=field_path,
        top_level_keys=keys,
        is_json_object=True,
    )


def extract_request_model(body: bytes) -> str | None:
    """Return the normalized request model, if the request provides one."""

    return inspect_request_model(body).model


def _decode_json_object(body: bytes) -> dict[str, Any] | None:
    if not body:
        return None
    try:
        data: Any = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _normalized_model(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None
