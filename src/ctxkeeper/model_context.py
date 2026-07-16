from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import time
from threading import RLock
from typing import Any, Callable, Literal

from .config import Settings


ContextWindowSource = Literal["configured", "detected", "default"]

_MAX_CONTEXT_WINDOW_TOKENS = 16_777_216
_SOURCE_LABELS: dict[ContextWindowSource, str] = {
    "configured": "Pre-defined",
    "detected": "Discovered",
    "default": "Default",
}
_ARCHITECTURE_CONTEXT_SUFFIX = ".context_length"
_GENERIC_CONTEXT_KEYS = {
    "context_length": 80,
    "num_ctx": 70,
    "context_window_tokens": 60,
}

logger = logging.getLogger("ctxkeeper.model_context")


@dataclass(frozen=True)
class ContextWindowResolution:
    tokens: int
    source: ContextWindowSource
    source_label: str
    label: str
    model_name: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "tokens": self.tokens,
            "source": self.source,
            "source_label": self.source_label,
            "label": self.label,
            "model_name": self.model_name,
        }


class ModelContextWindowCache:
    """Small process-local cache of discovered model context windows."""

    def __init__(
        self,
        *,
        max_models: int = 128,
        retry_after_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_models <= 0:
            raise ValueError("max_models must be greater than 0")
        if retry_after_seconds < 0:
            raise ValueError("retry_after_seconds must be greater than or equal to 0")
        self.max_models = max_models
        self.retry_after_seconds = retry_after_seconds
        self._clock = clock
        self._windows: dict[str, int] = {}
        self._attempted_at: dict[str, float] = {}
        self._lock = RLock()

    def get(self, model_name: str | None) -> int | None:
        keys = _model_cache_keys(model_name)
        with self._lock:
            for key in keys:
                value = self._windows.get(key)
                if value is not None:
                    return value
            return None

    def store(self, model_name: str | None, context_window_tokens: object) -> int | None:
        keys = _model_cache_keys(model_name)
        tokens = _positive_int(context_window_tokens)
        if not keys or tokens is None:
            return None

        with self._lock:
            for key in keys:
                if key not in self._windows:
                    self._evict_if_needed_locked()
                self._windows[key] = tokens
                self._attempted_at.pop(key, None)
            return tokens

    def store_from_show_payload(self, model_name: str | None, payload: Mapping[str, Any]) -> int | None:
        tokens = parse_context_window_tokens(payload)
        target_model = model_name or model_name_from_metadata(payload)
        return self.store(target_model, tokens)

    def should_attempt_discovery(self, model_name: str | None) -> bool:
        keys = _model_cache_keys(model_name)
        if not keys:
            return False
        now = self._clock()
        with self._lock:
            if any(key in self._windows for key in keys):
                return False
            last_attempt = max(
                (self._attempted_at[key] for key in keys if key in self._attempted_at),
                default=None,
            )
            if last_attempt is not None and now - last_attempt < self.retry_after_seconds:
                return False
            for key in keys:
                self._attempted_at[key] = now
            return True

    def clear(self) -> None:
        with self._lock:
            self._windows.clear()
            self._attempted_at.clear()

    def _evict_if_needed_locked(self) -> None:
        if len(self._windows) < self.max_models:
            return
        oldest = next(iter(self._windows))
        self._windows.pop(oldest, None)


class ActiveContextWindowOverrideStore:
    """Tracks resolved context windows for currently active requests."""

    def __init__(self) -> None:
        self._overrides: dict[str, tuple[datetime, ContextWindowResolution, int | None]] = {}
        self._lock = RLock()

    def register(
        self,
        request_id: str | None,
        resolution: ContextWindowResolution,
        *,
        generation_sequence: int | None = None,
    ) -> None:
        if not request_id:
            return
        with self._lock:
            self._overrides[request_id] = (datetime.now(timezone.utc), resolution, generation_sequence)

    def remove(self, request_id: str | None) -> None:
        if not request_id:
            return
        with self._lock:
            self._overrides.pop(request_id, None)

    def latest_for_model(self, model_name: str | None) -> ContextWindowResolution | None:
        normalized_model = normalize_model_name(model_name)
        if normalized_model is None:
            return None
        with self._lock:
            candidates = [
                (recorded_at, resolution)
                for recorded_at, resolution, _ in self._overrides.values()
                if normalize_model_name(resolution.model_name) == normalized_model
            ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]

    def latest_for_generation_sequence(self, generation_sequence: int | None) -> ContextWindowResolution | None:
        if generation_sequence is None:
            return None
        with self._lock:
            candidates = [
                (recorded_at, resolution)
                for recorded_at, resolution, recorded_generation_sequence in self._overrides.values()
                if recorded_generation_sequence == generation_sequence
            ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]

    def clear(self) -> None:
        with self._lock:
            self._overrides.clear()


model_context_window_cache = ModelContextWindowCache()
active_context_window_overrides = ActiveContextWindowOverrideStore()


def normalize_model_name(model_name: object) -> str | None:
    if not isinstance(model_name, str):
        return None
    normalized = model_name.strip()
    return normalized.casefold() if normalized else None


def _model_cache_keys(model_name: str | None) -> tuple[str, ...]:
    normalized = normalize_model_name(model_name)
    if normalized is None:
        return ()

    keys = [normalized]
    last_segment = normalized.rsplit("/", 1)[-1]
    if ":" not in last_segment:
        keys.append(f"{normalized}:latest")
    elif normalized.endswith(":latest"):
        keys.append(normalized[: -len(":latest")])
    return tuple(dict.fromkeys(keys))


def parse_context_window_tokens(metadata: Mapping[str, Any]) -> int | None:
    """Parse an Ollama-compatible model metadata payload for context capacity."""

    candidates: list[tuple[int, int, str]] = []
    for path, value in _walk_metadata(metadata):
        tokens = _positive_int(value)
        if tokens is None:
            continue

        key = _normalized_key(path[-1])
        score = _context_key_score(key)
        if score is None:
            continue

        if any(part == "model_info" for part in (_normalized_key(item) for item in path[:-1])):
            score += 5
        candidates.append((score, tokens, ".".join(path)))

    if not candidates:
        return None

    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    return candidates[0][1]


def model_name_from_metadata(metadata: Mapping[str, Any]) -> str | None:
    for key in ("model", "name"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    details = metadata.get("details")
    if isinstance(details, Mapping):
        value = details.get("model")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def runtime_num_ctx_from_request_body(body: bytes) -> int | None:
    data = _decode_json_object(body)
    if data is None:
        return None
    return runtime_num_ctx_from_payload(data)


def runtime_num_ctx_from_payload(payload: Mapping[str, Any]) -> int | None:
    options = payload.get("options")
    if isinstance(options, Mapping):
        tokens = _positive_int(options.get("num_ctx"))
        if tokens is not None:
            return tokens
    return _positive_int(payload.get("num_ctx"))


def resolve_context_window(
    settings: Settings,
    *,
    model_name: str | None,
    runtime_num_ctx: object = None,
    cache: ModelContextWindowCache = model_context_window_cache,
) -> ContextWindowResolution:
    # Client-supplied num_ctx is intentionally ignored for effective capacity.
    # It remains available through runtime_num_ctx_from_payload/body for safe
    # diagnostics, but ContextKeeper's authoritative priority is:
    # configured override -> detected model capability -> global default.
    _ = runtime_num_ctx

    configured_tokens = configured_context_window_tokens(settings, model_name)
    if configured_tokens is not None:
        return _resolution(configured_tokens, "configured", model_name)

    detected_tokens = cache.get(model_name)
    if detected_tokens is not None:
        return _resolution(detected_tokens, "detected", model_name)

    return _resolution(settings.context.default_context_window_tokens, "default", model_name)


def configured_context_window_tokens(settings: Settings, model_name: str | None) -> int | None:
    if not model_name:
        return None

    exact_config = settings.models.get(model_name)
    exact_tokens = _configured_tokens_from_mapping(exact_config)
    if exact_tokens is not None:
        return exact_tokens

    normalized = normalize_model_name(model_name)
    if normalized is None:
        return None
    for configured_name, model_config in settings.models.items():
        if normalize_model_name(configured_name) != normalized:
            continue
        tokens = _configured_tokens_from_mapping(model_config)
        if tokens is not None:
            return tokens
    return None


def format_context_window_label(tokens: int | None) -> str | None:
    if tokens is None or tokens <= 0:
        return None
    if tokens % (1024 * 1024) == 0:
        return f"{tokens // (1024 * 1024)}M"
    if tokens % 1024 == 0:
        return f"{tokens // 1024}K"
    return f"{tokens:,}"


def _resolution(tokens: int, source: ContextWindowSource, model_name: str | None) -> ContextWindowResolution:
    return ContextWindowResolution(
        tokens=tokens,
        source=source,
        source_label=_SOURCE_LABELS[source],
        label=format_context_window_label(tokens) or f"{tokens:,}",
        model_name=model_name,
    )


def enforce_context_window_in_payload(payload: Mapping[str, Any], context_window_tokens: int) -> dict[str, Any]:
    """Return a JSON-compatible request payload with authoritative num_ctx set."""

    tokens = _positive_int(context_window_tokens)
    if tokens is None:
        raise ValueError("context_window_tokens must be a positive integer")

    updated = dict(payload)
    options = updated.get("options")
    if isinstance(options, Mapping):
        updated_options = dict(options)
    else:
        updated_options = {}
    updated_options["num_ctx"] = tokens
    updated["options"] = updated_options
    if "num_ctx" in updated:
        updated["num_ctx"] = tokens
    return updated


def enforce_context_window_in_request_body(body: bytes, context_window_tokens: int) -> bytes:
    """Return an outgoing request body with options.num_ctx overwritten when possible."""

    data = _decode_json_object(body)
    if data is None:
        return body
    updated = enforce_context_window_in_payload(data, context_window_tokens)
    return json.dumps(updated, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _configured_tokens_from_mapping(model_config: object) -> int | None:
    if not isinstance(model_config, Mapping):
        return None
    return _positive_int(model_config.get("context_window_tokens"))


def _context_key_score(key: str) -> int | None:
    if key.endswith(_ARCHITECTURE_CONTEXT_SUFFIX) and key != "context_length":
        return 100
    return _GENERIC_CONTEXT_KEYS.get(key)


def _walk_metadata(value: object, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], object]]:
    results: list[tuple[tuple[str, ...], object]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            next_path = (*path, str(key))
            results.append((next_path, child))
            results.extend(_walk_metadata(child, next_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            results.extend(_walk_metadata(child, (*path, str(index))))
    return results


def _normalized_key(key: str) -> str:
    return key.strip().casefold().replace("-", "_")


def _positive_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value <= 0 or value > _MAX_CONTEXT_WINDOW_TOKENS:
        return None
    return value


def _decode_json_object(body: bytes) -> dict[str, Any] | None:
    if not body:
        return None
    try:
        data: Any = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None
