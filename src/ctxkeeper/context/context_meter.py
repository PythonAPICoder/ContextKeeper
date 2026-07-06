from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from ..diagnostics.metrics import estimate_text_tokens
from .conversation_store import Conversation, ConversationMessage


class _MessageLike(Protocol):
    role: str
    content: str


@dataclass(frozen=True)
class ContextStatus:
    estimated_tokens: int
    context_window_tokens: int
    usage_percent: float
    warning_threshold_exceeded: bool
    compression_threshold_exceeded: bool


class ContextMeter:
    def __init__(
        self,
        *,
        context_window_tokens: int,
        warning_threshold_percent: int,
        compression_threshold_percent: int,
    ) -> None:
        if context_window_tokens <= 0:
            raise ValueError("context_window_tokens must be greater than 0")
        if not 0 <= warning_threshold_percent <= 100:
            raise ValueError("warning_threshold_percent must be between 0 and 100")
        if not 0 <= compression_threshold_percent <= 100:
            raise ValueError("compression_threshold_percent must be between 0 and 100")
        if warning_threshold_percent > compression_threshold_percent:
            raise ValueError("warning_threshold_percent must be less than or equal to compression_threshold_percent")

        self.context_window_tokens = context_window_tokens
        self.warning_threshold_percent = warning_threshold_percent
        self.compression_threshold_percent = compression_threshold_percent

    def evaluate(
        self,
        conversation_or_messages: Conversation | Iterable[ConversationMessage],
    ) -> ContextStatus:
        messages = _messages_from(conversation_or_messages)
        estimated_tokens = sum(_estimate_message_tokens(message) for message in messages)
        usage_percent = round((estimated_tokens / self.context_window_tokens) * 100, 2)

        return ContextStatus(
            estimated_tokens=estimated_tokens,
            context_window_tokens=self.context_window_tokens,
            usage_percent=usage_percent,
            warning_threshold_exceeded=usage_percent >= self.warning_threshold_percent,
            compression_threshold_exceeded=usage_percent >= self.compression_threshold_percent,
        )


def _messages_from(conversation_or_messages: Conversation | Iterable[ConversationMessage]) -> list[ConversationMessage]:
    if isinstance(conversation_or_messages, Conversation):
        return list(conversation_or_messages.messages)
    return list(conversation_or_messages)


def _estimate_message_tokens(message: _MessageLike) -> int:
    return estimate_text_tokens(message.role) + estimate_text_tokens(message.content)
