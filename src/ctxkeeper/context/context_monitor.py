from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime

from .context_meter import ContextMeter, ContextStatus
from .conversation_store import Conversation, ConversationStore


@dataclass(frozen=True)
class MonitoredConversation:
    conversation_id: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    status: ContextStatus


@dataclass(frozen=True)
class ContextMonitoringStatistics:
    conversation_count: int
    message_count: int
    total_estimated_tokens: int
    warning_count: int
    compression_candidate_count: int
    average_usage_percent: float
    max_usage_percent: float


@dataclass(frozen=True)
class ContextMonitorScan:
    statistics: ContextMonitoringStatistics
    conversations: list[MonitoredConversation] = field(default_factory=list)
    warning_conversations: list[MonitoredConversation] = field(default_factory=list)
    compression_candidates: list[MonitoredConversation] = field(default_factory=list)


class ContextMonitor:
    def __init__(self, *, store: ConversationStore, meter: ContextMeter) -> None:
        self.store = store
        self.meter = meter
        self._last_scan = ContextMonitorScan(
            statistics=ContextMonitoringStatistics(
                conversation_count=0,
                message_count=0,
                total_estimated_tokens=0,
                warning_count=0,
                compression_candidate_count=0,
                average_usage_percent=0.0,
                max_usage_percent=0.0,
            )
        )

    def scan(self, conversations: Sequence[Conversation] | None = None) -> ContextMonitorScan:
        source_conversations = list(conversations) if conversations is not None else self.store.all()
        conversations = [
            self._monitor_conversation(conversation)
            for conversation in source_conversations
        ]
        warning_conversations = [
            conversation
            for conversation in conversations
            if conversation.status.warning_threshold_exceeded
        ]
        compression_candidates = [
            conversation
            for conversation in conversations
            if conversation.status.compression_threshold_exceeded
        ]
        statistics = ContextMonitoringStatistics(
            conversation_count=len(conversations),
            message_count=sum(conversation.message_count for conversation in conversations),
            total_estimated_tokens=sum(
                conversation.status.estimated_tokens
                for conversation in conversations
            ),
            warning_count=len(warning_conversations),
            compression_candidate_count=len(compression_candidates),
            average_usage_percent=_average_usage_percent(conversations),
            max_usage_percent=max(
                (conversation.status.usage_percent for conversation in conversations),
                default=0.0,
            ),
        )
        self._last_scan = ContextMonitorScan(
            statistics=statistics,
            conversations=conversations,
            warning_conversations=warning_conversations,
            compression_candidates=compression_candidates,
        )
        return self._last_scan

    def get_statistics(self) -> ContextMonitoringStatistics:
        return self._last_scan.statistics

    def get_warning_conversations(self) -> list[MonitoredConversation]:
        return list(self._last_scan.warning_conversations)

    def get_compression_candidates(self) -> list[MonitoredConversation]:
        return list(self._last_scan.compression_candidates)

    def _monitor_conversation(self, conversation: Conversation) -> MonitoredConversation:
        return MonitoredConversation(
            conversation_id=conversation.conversation_id,
            message_count=len(conversation.messages),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            status=self.meter.evaluate(conversation),
        )


def _average_usage_percent(conversations: list[MonitoredConversation]) -> float:
    if not conversations:
        return 0.0
    return round(
        sum(conversation.status.usage_percent for conversation in conversations) / len(conversations),
        2,
    )
