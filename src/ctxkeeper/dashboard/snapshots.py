from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from ..context.compression_manager import ROLLING_SUMMARY_PREFIX
from ..context.context_meter import ContextMeter, ContextStatus
from ..context.conversation_store import Conversation, ConversationMessage, ConversationStore


@dataclass(frozen=True)
class ConversationMessageSnapshot:
    role: str
    content: str
    timestamp: str

    @classmethod
    def from_message(cls, message: ConversationMessage) -> ConversationMessageSnapshot:
        return cls(
            role=message.role,
            content=message.content,
            timestamp=message.timestamp.isoformat(),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class ConversationContextSnapshot:
    estimated_tokens: int
    context_window_tokens: int
    usage_percent: float
    warning_threshold_exceeded: bool
    compression_threshold_exceeded: bool

    @classmethod
    def from_status(cls, status: ContextStatus) -> ConversationContextSnapshot:
        return cls(
            estimated_tokens=status.estimated_tokens,
            context_window_tokens=status.context_window_tokens,
            usage_percent=status.usage_percent,
            warning_threshold_exceeded=status.warning_threshold_exceeded,
            compression_threshold_exceeded=status.compression_threshold_exceeded,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "estimated_tokens": self.estimated_tokens,
            "context_window_tokens": self.context_window_tokens,
            "usage_percent": self.usage_percent,
            "warning_threshold_exceeded": self.warning_threshold_exceeded,
            "compression_threshold_exceeded": self.compression_threshold_exceeded,
        }


@dataclass(frozen=True)
class ConversationSnapshot:
    conversation_id: str | None
    model_name: str | None
    rolling_summary: str | None
    recent_messages: list[ConversationMessageSnapshot]
    context: ConversationContextSnapshot | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "model_name": self.model_name,
            "rolling_summary": self.rolling_summary,
            "recent_messages": [message.to_dict() for message in self.recent_messages],
            "context": self.context.to_dict() if self.context is not None else None,
        }


class ConversationSnapshotProvider:
    def __init__(
        self,
        *,
        store: ConversationStore,
        meter: ContextMeter,
        recent_message_limit: int = 8,
    ) -> None:
        if recent_message_limit <= 0:
            raise ValueError("recent_message_limit must be greater than 0")
        self.store = store
        self.meter = meter
        self.recent_message_limit = recent_message_limit

    def active_snapshot(
        self,
        *,
        model_name: str | None,
        conversations: Sequence[Conversation] | None = None,
    ) -> ConversationSnapshot:
        conversation = self._active_conversation(conversations)
        if conversation is None:
            return ConversationSnapshot(
                conversation_id=None,
                model_name=model_name,
                rolling_summary=None,
                recent_messages=[],
                context=None,
            )

        rolling_summary = _latest_rolling_summary(conversation)
        recent_messages = [
            ConversationMessageSnapshot.from_message(message)
            for message in _recent_visible_messages(conversation, self.recent_message_limit)
        ]
        context = ConversationContextSnapshot.from_status(self.meter.evaluate(conversation))
        return ConversationSnapshot(
            conversation_id=conversation.conversation_id,
            model_name=model_name,
            rolling_summary=rolling_summary,
            recent_messages=recent_messages,
            context=context,
        )

    def _active_conversation(self, conversations: Sequence[Conversation] | None = None) -> Conversation | None:
        available_conversations = list(conversations) if conversations is not None else self.store.all()
        if not available_conversations:
            return None
        return max(available_conversations, key=lambda conversation: conversation.updated_at)


def _latest_rolling_summary(conversation: Conversation) -> str | None:
    summaries = [
        message
        for message in conversation.messages
        if message.role == "system" and message.content.startswith(ROLLING_SUMMARY_PREFIX)
    ]
    if not summaries:
        return None
    latest = max(summaries, key=lambda message: message.timestamp)
    return latest.content.removeprefix(ROLLING_SUMMARY_PREFIX)


def _recent_visible_messages(
    conversation: Conversation,
    limit: int,
) -> list[ConversationMessage]:
    visible_messages = [
        message
        for message in conversation.messages
        if not (message.role == "system" and message.content.startswith(ROLLING_SUMMARY_PREFIX))
    ]
    return visible_messages[-limit:]
