from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, Sequence

from ..diagnostics.metrics import estimate_text_tokens
from .compression_plan import CompressionPlan, CompressionPlanner
from .context_meter import ContextMeter
from .conversation_store import Conversation, ConversationMessage
from .summarizer import BaseSummarizer


ROLLING_SUMMARY_PREFIX = "[ContextKeeper rolling summary]\n"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SummaryRecord:
    conversation_id: str
    content: str
    source_message_count: int
    estimated_tokens: int
    created_at: datetime


@dataclass(frozen=True)
class CompressionMetadata:
    conversation_id: str
    compression_count: int
    total_messages_compressed: int
    total_estimated_tokens_saved: int
    last_compressed_at: datetime | None = None
    last_summary_tokens: int = 0


@dataclass(frozen=True)
class CompressionSelection:
    keep_messages: list[ConversationMessage]
    compress_messages: list[ConversationMessage]


@dataclass(frozen=True)
class ArchivePlan:
    conversation_id: str
    messages: list[ConversationMessage]
    encryption_enabled: bool
    reason: str


class HistoryArchive(Protocol):
    def create_archive_plan(self, conversation_id: str, messages: Sequence[ConversationMessage]) -> ArchivePlan:
        """Create a future archive plan without persisting or encrypting data yet."""


class LocalHistoryArchivePlaceholder:
    def create_archive_plan(self, conversation_id: str, messages: Sequence[ConversationMessage]) -> ArchivePlan:
        return ArchivePlan(
            conversation_id=conversation_id,
            messages=list(messages),
            encryption_enabled=False,
            reason="Archive placeholder only; persistence and encryption are not implemented yet.",
        )


class CompressionManager:
    def __init__(
        self,
        *,
        keep_recent_messages: int = 8,
        max_summary_tokens: int = 1200,
        enabled: bool = True,
        meter: ContextMeter | None = None,
        summarizer: BaseSummarizer | None = None,
        archive: HistoryArchive | None = None,
    ) -> None:
        self.planner = CompressionPlanner(
            keep_recent_messages=keep_recent_messages,
            max_summary_tokens=max_summary_tokens,
        )
        self.enabled = enabled
        self.meter = meter
        self.summarizer = summarizer
        self.archive = archive or LocalHistoryArchivePlaceholder()
        self.metadata_by_conversation_id: dict[str, CompressionMetadata] = {}

    @property
    def keep_recent_messages(self) -> int:
        return self.planner.keep_recent_messages

    @property
    def max_summary_tokens(self) -> int:
        return self.planner.max_summary_tokens

    async def compress_if_needed(
        self,
        conversation: Conversation,
        *,
        meter: ContextMeter | None = None,
        summarizer: BaseSummarizer | None = None,
    ) -> Conversation:
        if not self.enabled or not conversation.messages:
            return conversation

        meter = meter or self.meter
        summarizer = summarizer or self.summarizer
        if meter is None:
            raise ValueError("ContextMeter is required when compression is enabled")

        status = meter.evaluate(conversation)
        if not status.compression_threshold_exceeded:
            return conversation
        if summarizer is None:
            raise ValueError("BaseSummarizer is required when compression is enabled")

        existing_summary = conversation.messages[0] if _is_rolling_summary(conversation.messages[0]) else None
        active_messages = conversation.messages[1:] if existing_summary else conversation.messages
        if len(active_messages) <= self.keep_recent_messages:
            return conversation

        selection = self.select_messages(active_messages)
        messages_to_summarize = list(selection.compress_messages)
        if existing_summary is not None:
            messages_to_summarize.insert(0, existing_summary)

        summary_text = await summarizer.summarize(_messages_to_chat_dicts(messages_to_summarize))
        if summary_text is None:
            return conversation

        summary_message = ConversationMessage(
            role="system",
            content=f"{ROLLING_SUMMARY_PREFIX}{summary_text}",
        )
        summary_record = self.create_summary_record(
            conversation_id=conversation.conversation_id,
            content=summary_message.content,
            source_messages=messages_to_summarize,
            estimated_tokens=estimate_text_tokens(summary_message.content),
        )
        estimated_after = meter.evaluate([summary_message, *selection.keep_messages]).estimated_tokens
        metadata = self.metadata_by_conversation_id.get(conversation.conversation_id)
        self.metadata_by_conversation_id[conversation.conversation_id] = self.update_metadata(
            metadata=metadata,
            summary=summary_record,
            estimated_tokens_saved=status.estimated_tokens - estimated_after,
        )

        conversation.messages = [summary_message, *selection.keep_messages]
        conversation.updated_at = summary_message.timestamp
        return conversation

    def select_messages(self, messages: Sequence[ConversationMessage]) -> CompressionSelection:
        if len(messages) <= self.keep_recent_messages:
            return CompressionSelection(
                keep_messages=list(messages),
                compress_messages=[],
            )
        return CompressionSelection(
            keep_messages=list(messages[-self.keep_recent_messages:]),
            compress_messages=list(messages[:-self.keep_recent_messages]),
        )

    def create_plan(
        self,
        *,
        conversation_id: str,
        messages: Sequence[ConversationMessage],
        estimated_tokens_before: int,
        compression_needed: bool,
    ) -> CompressionPlan:
        return self.planner.create_plan(
            conversation_id=conversation_id,
            messages=messages,
            estimated_tokens_before=estimated_tokens_before,
            compression_needed=compression_needed,
        )

    def create_summary_record(
        self,
        *,
        conversation_id: str,
        content: str,
        source_messages: Sequence[ConversationMessage],
        estimated_tokens: int,
    ) -> SummaryRecord:
        return SummaryRecord(
            conversation_id=conversation_id,
            content=content,
            source_message_count=len(source_messages),
            estimated_tokens=estimated_tokens,
            created_at=_utc_now(),
        )

    def update_metadata(
        self,
        *,
        metadata: CompressionMetadata | None,
        summary: SummaryRecord,
        estimated_tokens_saved: int,
    ) -> CompressionMetadata:
        if metadata is None:
            return CompressionMetadata(
                conversation_id=summary.conversation_id,
                compression_count=1,
                total_messages_compressed=summary.source_message_count,
                total_estimated_tokens_saved=estimated_tokens_saved,
                last_compressed_at=summary.created_at,
                last_summary_tokens=summary.estimated_tokens,
            )

        return CompressionMetadata(
            conversation_id=metadata.conversation_id,
            compression_count=metadata.compression_count + 1,
            total_messages_compressed=metadata.total_messages_compressed + summary.source_message_count,
            total_estimated_tokens_saved=metadata.total_estimated_tokens_saved + estimated_tokens_saved,
            last_compressed_at=summary.created_at,
            last_summary_tokens=summary.estimated_tokens,
        )

    def create_archive_plan(self, conversation_id: str, messages: Sequence[ConversationMessage]) -> ArchivePlan:
        return self.archive.create_archive_plan(conversation_id, messages)


def _is_rolling_summary(message: ConversationMessage) -> bool:
    return message.role == "system" and message.content.startswith(ROLLING_SUMMARY_PREFIX)


def _messages_to_chat_dicts(messages: Sequence[ConversationMessage]) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": message.content}
        for message in messages
    ]
