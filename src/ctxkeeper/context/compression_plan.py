from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence


class CompressionPlanStatus(Enum):
    NO_ACTION = "no_action"
    NOT_ENOUGH_HISTORY = "not_enough_history"
    PLAN_READY = "plan_ready"


@dataclass(frozen=True)
class CompressionPlan:
    conversation_id: str
    status: CompressionPlanStatus
    keep_messages: list[Any]
    compress_messages: list[Any]
    estimated_tokens_before: int
    estimated_tokens_after: int
    estimated_tokens_saved: int
    reason: str


class CompressionPlanner:
    def __init__(
        self,
        *,
        keep_recent_messages: int = 8,
        max_summary_tokens: int = 1200,
    ) -> None:
        if keep_recent_messages < 1:
            raise ValueError("keep_recent_messages must be greater than or equal to 1")
        if max_summary_tokens < 1:
            raise ValueError("max_summary_tokens must be greater than or equal to 1")

        self.keep_recent_messages = keep_recent_messages
        self.max_summary_tokens = max_summary_tokens

    def create_plan(
        self,
        conversation_id: str,
        messages: Sequence[Any],
        estimated_tokens_before: int,
        compression_needed: bool,
    ) -> CompressionPlan:
        if not compression_needed:
            return CompressionPlan(
                conversation_id=conversation_id,
                status=CompressionPlanStatus.NO_ACTION,
                keep_messages=list(messages),
                compress_messages=[],
                estimated_tokens_before=estimated_tokens_before,
                estimated_tokens_after=estimated_tokens_before,
                estimated_tokens_saved=0,
                reason="Compression threshold not exceeded.",
            )

        if len(messages) <= self.keep_recent_messages:
            return CompressionPlan(
                conversation_id=conversation_id,
                status=CompressionPlanStatus.NOT_ENOUGH_HISTORY,
                keep_messages=list(messages),
                compress_messages=[],
                estimated_tokens_before=estimated_tokens_before,
                estimated_tokens_after=estimated_tokens_before,
                estimated_tokens_saved=0,
                reason="Not enough history to preserve recent messages and compress older messages.",
            )

        compress_messages = list(messages[:-self.keep_recent_messages])
        keep_messages = list(messages[-self.keep_recent_messages:])
        estimated_tokens_after = self.max_summary_tokens + _estimate_messages_tokens(keep_messages)
        estimated_tokens_saved = estimated_tokens_before - estimated_tokens_after

        return CompressionPlan(
            conversation_id=conversation_id,
            status=CompressionPlanStatus.PLAN_READY,
            keep_messages=keep_messages,
            compress_messages=compress_messages,
            estimated_tokens_before=estimated_tokens_before,
            estimated_tokens_after=estimated_tokens_after,
            estimated_tokens_saved=estimated_tokens_saved,
            reason="Compression plan ready.",
        )


def _estimate_messages_tokens(messages: Sequence[Any]) -> int:
    return sum(_estimate_message_tokens(message) for message in messages)


def _estimate_message_tokens(message: Any) -> int:
    text = str(message)
    if not text:
        return 0
    return max(1, len(text) // 4)
