from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: datetime = field(default_factory=_utc_now)


@dataclass
class Conversation:
    conversation_id: str
    messages: list[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)


class ConversationStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._conversations: dict[str, Conversation] = {}

    def create(self, conversation_id: str | None = None) -> Conversation:
        conversation_id = conversation_id or self._new_conversation_id()
        now = _utc_now()
        conversation = Conversation(
            conversation_id=conversation_id,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._conversations[conversation_id] = conversation
        return conversation

    def append_message(self, conversation_id: str, role: str, content: str) -> ConversationMessage:
        now = _utc_now()
        message = ConversationMessage(role=role, content=content, timestamp=now)
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                conversation = Conversation(
                    conversation_id=conversation_id,
                    created_at=now,
                    updated_at=now,
                )
                self._conversations[conversation_id] = conversation
            conversation.messages.append(message)
            conversation.updated_at = now
        return message

    def get(self, conversation_id: str) -> Conversation | None:
        with self._lock:
            return self._conversations.get(conversation_id)

    def delete(self, conversation_id: str) -> bool:
        with self._lock:
            return self._conversations.pop(conversation_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._conversations.clear()

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "conversation_count": len(self._conversations),
                "message_count": sum(
                    len(conversation.messages)
                    for conversation in self._conversations.values()
                ),
            }

    @staticmethod
    def _new_conversation_id() -> str:
        return f"ck_conv_{uuid4().hex}"
