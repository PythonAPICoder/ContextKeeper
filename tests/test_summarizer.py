from __future__ import annotations

import json

import httpx
import pytest

from ctxkeeper.context import OllamaSummarizer


def test_prompt_generation_preserves_roles_and_content_ordering() -> None:
    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
    )
    messages = [
        {"role": "user", "content": "First request."},
        {"role": "assistant", "content": "First answer."},
        {"role": "user", "content": "Second request."},
    ]

    prompt = summarizer.build_prompt(messages)

    first = prompt.index("1. user: First request.")
    second = prompt.index("2. assistant: First answer.")
    third = prompt.index("3. user: Second request.")
    assert first < second < third


@pytest.mark.anyio
async def test_empty_messages_return_none() -> None:
    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    assert await summarizer.summarize([]) is None


@pytest.mark.anyio
async def test_successful_ollama_response_returns_summary_text() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "Summary text."}},
        )

    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
        transport=httpx.MockTransport(handler),
    )

    summary = await summarizer.summarize([{"role": "user", "content": "Hello"}])

    assert summary == "Summary text."
    assert requests[0].url == "http://ollama.test:11434/api/chat"
    payload = json.loads(requests[0].content.decode("utf-8"))
    assert payload["model"] == "gpt-oss:20b"
    assert payload["stream"] is False
    assert payload["options"]["num_predict"] == 100


@pytest.mark.anyio
async def test_malformed_ollama_response_returns_none() -> None:
    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"done": True})),
    )

    assert await summarizer.summarize([{"role": "user", "content": "Hello"}]) is None


@pytest.mark.anyio
async def test_http_failure_returns_none() -> None:
    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    assert await summarizer.summarize([{"role": "user", "content": "Hello"}]) is None


@pytest.mark.anyio
async def test_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    summarizer = OllamaSummarizer(
        base_url="http://ollama.test:11434",
        model="gpt-oss:20b",
        timeout_seconds=30,
        max_summary_tokens=100,
        transport=httpx.MockTransport(handler),
    )

    assert await summarizer.summarize([{"role": "user", "content": "Hello"}]) is None
