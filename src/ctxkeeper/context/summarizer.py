from __future__ import annotations

import logging
from typing import Any, Protocol, Sequence

import httpx


logger = logging.getLogger("ctxkeeper.context.summarizer")


class BaseSummarizer(Protocol):
    async def summarize(self, messages: Sequence[dict[str, str]]) -> str | None:
        """Return a summary for chat messages, or None when summarization fails."""


class OllamaSummarizer:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: int,
        max_summary_tokens: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if max_summary_tokens < 1:
            raise ValueError("max_summary_tokens must be greater than or equal to 1")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        self.max_summary_tokens = max_summary_tokens
        self._transport = transport

    async def summarize(self, messages: Sequence[dict[str, str]]) -> str | None:
        if not messages:
            return None

        prompt = self.build_prompt(messages)
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You summarize prior chat history for context retention. "
                        "Preserve important facts, decisions, constraints, and unresolved tasks. "
                        "Do not invent details."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "options": {"num_predict": self.max_summary_tokens},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self._transport) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning(
                "Ollama summarization request failed model=%s message_count=%s error=%s",
                self.model,
                len(messages),
                exc.__class__.__name__,
            )
            return None

        return self._summary_from_response(response)

    @staticmethod
    def build_prompt(messages: Sequence[dict[str, str]]) -> str:
        lines = [
            "Summarize the following conversation messages for future context.",
            "Keep the summary concise and factual.",
            "",
            "Messages:",
        ]
        for index, message in enumerate(messages, start=1):
            role = str(message.get("role", "unknown"))
            content = str(message.get("content", ""))
            lines.append(f"{index}. {role}: {content}")
        return "\n".join(lines)

    def _summary_from_response(self, response: httpx.Response) -> str | None:
        try:
            data: Any = response.json()
        except ValueError:
            logger.warning("Ollama summarization returned non-JSON response model=%s", self.model)
            return None

        if not isinstance(data, dict):
            logger.warning("Ollama summarization returned malformed response model=%s", self.model)
            return None

        message = data.get("message")
        if not isinstance(message, dict):
            logger.warning("Ollama summarization response missing message object model=%s", self.model)
            return None

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            logger.warning("Ollama summarization response missing summary text model=%s", self.model)
            return None

        return content.strip()
