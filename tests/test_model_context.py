from __future__ import annotations

import pytest

from ctxkeeper.config import Settings
from ctxkeeper.model_context import (
    ModelContextWindowCache,
    active_context_window_overrides,
    enforce_context_window_in_payload,
    enforce_context_window_in_request_body,
    format_context_window_label,
    model_context_window_cache,
    parse_context_window_tokens,
    resolve_context_window,
    runtime_num_ctx_from_payload,
)


@pytest.fixture(autouse=True)
def clear_model_context_cache() -> None:
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    yield
    model_context_window_cache.clear()
    active_context_window_overrides.clear()


def test_discovers_context_window_from_ollama_model_info_metadata() -> None:
    payload = {
        "model": "gpt-oss:20b",
        "model_info": {
            "general.architecture": "llama",
            "llama.embedding_length": 8192,
            "llama.context_length": 131072,
            "llama.vocab_size": 200000,
        },
    }

    assert parse_context_window_tokens(payload) == 131072


def test_discovers_context_window_from_observed_ollama_architecture_keys() -> None:
    assert parse_context_window_tokens({"model_info": {"gptoss.context_length": 131072}}) == 131072
    assert parse_context_window_tokens({"model_info": {"llama.context_length": 32768}}) == 32768


def test_architecture_context_length_beats_generic_context_length() -> None:
    payload = {
        "model_info": {
            "context_length": 4096,
            "qwen2.context_length": 32768,
        }
    }

    assert parse_context_window_tokens(payload) == 32768


def test_generic_context_length_and_num_ctx_are_supported() -> None:
    assert parse_context_window_tokens({"context_length": 65536}) == 65536
    assert parse_context_window_tokens({"details": {"num_ctx": 32768}}) == 32768


@pytest.mark.parametrize(
    "payload",
    [
        {"model_info": {"llama.context_length": True}},
        {"model_info": {"llama.context_length": 0}},
        {"model_info": {"llama.context_length": -1}},
        {"model_info": {"llama.context_length": "131072"}},
        {"model_info": {"llama.embedding_length": 8192}},
        {"model_info": {"llama.vocab_size": 200000}},
        {"model_info": {"llama.parameter_count": 7_000_000_000}},
        {"model_info": {"llama.context_length": 99_000_000}},
    ],
)
def test_invalid_and_unrelated_metadata_values_are_ignored(payload: dict[str, object]) -> None:
    assert parse_context_window_tokens(payload) is None


def test_runtime_num_ctx_extraction_accepts_only_positive_integer_values() -> None:
    assert runtime_num_ctx_from_payload({"options": {"num_ctx": 65536}}) == 65536
    assert runtime_num_ctx_from_payload({"num_ctx": 32768}) == 32768
    assert runtime_num_ctx_from_payload({"options": {"num_ctx": True}}) is None
    assert runtime_num_ctx_from_payload({"options": {"num_ctx": 0}}) is None
    assert runtime_num_ctx_from_payload({"options": {"num_ctx": "65536"}}) is None


def test_context_window_resolution_priority_configured_detected_default() -> None:
    settings = Settings.model_validate(
        {
            "context": {"default_context_window_tokens": 32768},
            "models": {"gpt-oss:20b": {"context_window_tokens": 65536}},
        }
    )
    cache = ModelContextWindowCache()
    cache.store("gpt-oss:20b", 131072)
    cache.store("llama3.2:latest", 262144)

    ignored_runtime = resolve_context_window(settings, model_name="gpt-oss:20b", runtime_num_ctx=262144, cache=cache)
    configured = resolve_context_window(settings, model_name="gpt-oss:20b", cache=cache)
    detected = resolve_context_window(settings, model_name="llama3.2:latest", cache=cache)
    default = resolve_context_window(settings, model_name="unknown:latest", cache=cache)

    assert (ignored_runtime.tokens, ignored_runtime.source, ignored_runtime.source_label) == (
        65536,
        "configured",
        "Pre-defined",
    )
    assert (configured.tokens, configured.source, configured.source_label) == (65536, "configured", "Pre-defined")
    assert (detected.tokens, detected.source, detected.source_label) == (262144, "detected", "Discovered")
    assert (default.tokens, default.source, default.source_label) == (32768, "default", "Default")


def test_configured_model_lookup_tolerates_trivial_case_and_space_differences() -> None:
    settings = Settings.model_validate(
        {"models": {"Gpt-Oss:20B": {"context_window_tokens": 32768}}}
    )

    resolution = resolve_context_window(settings, model_name=" gpt-oss:20b ")

    assert resolution.tokens == 32768
    assert resolution.source == "configured"


def test_format_context_window_label_uses_compact_binary_units() -> None:
    assert format_context_window_label(16384) == "16K"
    assert format_context_window_label(32768) == "32K"
    assert format_context_window_label(131072) == "128K"
    assert format_context_window_label(262144) == "256K"
    assert format_context_window_label(1048576) == "1M"
    assert format_context_window_label(1000000) == "1,000,000"


def test_detected_cache_resolves_latest_alias_without_collapsing_other_tags() -> None:
    cache = ModelContextWindowCache()

    cache.store("llava", 32768)
    cache.store("llava:custom", 65536)

    assert cache.get("llava:latest") == 32768
    assert cache.get("llava") == 32768
    assert cache.get("llava:custom") == 65536


def test_discovery_attempts_use_backoff_and_can_retry_later() -> None:
    now = 100.0
    cache = ModelContextWindowCache(retry_after_seconds=10.0, clock=lambda: now)

    assert cache.should_attempt_discovery("llava") is True
    assert cache.should_attempt_discovery("llava:latest") is False

    now = 111.0
    assert cache.should_attempt_discovery("llava:latest") is True

    cache.store("llava:latest", 32768)
    now = 122.0
    assert cache.should_attempt_discovery("llava") is False


def test_active_context_window_store_tracks_resolved_generation_capacity() -> None:
    settings = Settings()
    default = resolve_context_window(settings, model_name="llava:latest")

    active_context_window_overrides.register("default-request", default, generation_sequence=7)

    latest = active_context_window_overrides.latest_for_model("LLAVA:LATEST")

    assert latest is not None
    assert latest.tokens == settings.context.default_context_window_tokens
    assert latest.source == "default"
    assert active_context_window_overrides.latest_for_generation_sequence(7) == latest

    active_context_window_overrides.remove("default-request")
    assert active_context_window_overrides.latest_for_model("llava:latest") is None


def test_enforce_context_window_in_payload_overwrites_client_num_ctx() -> None:
    payload = {
        "model": "qwen3.6:latest",
        "messages": [],
        "num_ctx": 16384,
        "options": {"temperature": 0.1, "num_ctx": 16384},
    }

    updated = enforce_context_window_in_payload(payload, 262144)

    assert updated["num_ctx"] == 262144
    assert updated["options"] == {"temperature": 0.1, "num_ctx": 262144}
    assert payload["options"]["num_ctx"] == 16384


def test_enforce_context_window_in_request_body_adds_options_num_ctx() -> None:
    body = b'{"model":"qwen3.6:latest","messages":[]}'

    updated = enforce_context_window_in_request_body(body, 262144)

    assert b'"options":{"num_ctx":262144}' in updated
