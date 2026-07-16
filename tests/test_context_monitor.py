from __future__ import annotations

from ctxkeeper.context import (
    ContextMeter,
    ContextMonitor,
    ContextMonitoringStatistics,
    ContextMonitorScan,
    ConversationStore,
    MonitoredConversation,
)


def _monitor(store: ConversationStore) -> ContextMonitor:
    return ContextMonitor(
        store=store,
        meter=ContextMeter(
            context_window_tokens=50,
            warning_threshold_percent=50,
            compression_threshold_percent=80,
        ),
    )


def test_empty_store_scan_returns_zero_statistics() -> None:
    monitor = _monitor(ConversationStore())

    scan = monitor.scan()

    assert isinstance(scan, ContextMonitorScan)
    assert scan.statistics == ContextMonitoringStatistics(
        conversation_count=0,
        message_count=0,
        total_estimated_tokens=0,
        warning_count=0,
        compression_candidate_count=0,
        average_usage_percent=0.0,
        max_usage_percent=0.0,
    )
    assert scan.conversations == []
    assert monitor.get_warning_conversations() == []
    assert monitor.get_compression_candidates() == []


def test_scan_reports_all_conversation_statistics() -> None:
    store = ConversationStore()
    store.append_message("small", "user", "hello")
    store.append_message("warning", "user", "a" * 96)
    store.append_message("compression", "user", "a" * 156)
    monitor = _monitor(store)

    scan = monitor.scan()

    assert scan.statistics.conversation_count == 3
    assert scan.statistics.message_count == 3
    assert scan.statistics.total_estimated_tokens == 68
    assert scan.statistics.warning_count == 2
    assert scan.statistics.compression_candidate_count == 1
    assert scan.statistics.average_usage_percent == 45.33
    assert scan.statistics.max_usage_percent == 80.0
    assert [conversation.conversation_id for conversation in scan.conversations] == [
        "small",
        "warning",
        "compression",
    ]


def test_scan_can_reuse_supplied_conversation_snapshot() -> None:
    store = ConversationStore()
    store.append_message("included", "user", "hello")
    store.append_message("excluded", "user", "a" * 156)
    included = store.get("included")
    assert included is not None
    monitor = _monitor(store)

    scan = monitor.scan([included])

    assert scan.statistics.conversation_count == 1
    assert scan.statistics.message_count == 1
    assert scan.statistics.compression_candidate_count == 0
    assert [conversation.conversation_id for conversation in scan.conversations] == ["included"]


def test_warning_conversations_include_warning_and_compression_states() -> None:
    store = ConversationStore()
    store.append_message("below", "user", "hello")
    store.append_message("warning", "user", "a" * 96)
    store.append_message("compression", "user", "a" * 156)
    monitor = _monitor(store)

    monitor.scan()
    warning_conversations = monitor.get_warning_conversations()

    assert all(isinstance(conversation, MonitoredConversation) for conversation in warning_conversations)
    assert [conversation.conversation_id for conversation in warning_conversations] == [
        "warning",
        "compression",
    ]
    assert [conversation.status.usage_percent for conversation in warning_conversations] == [
        50.0,
        80.0,
    ]


def test_compression_candidates_include_only_compression_state() -> None:
    store = ConversationStore()
    store.append_message("warning", "user", "a" * 96)
    store.append_message("compression", "user", "a" * 156)
    monitor = _monitor(store)

    monitor.scan()
    compression_candidates = monitor.get_compression_candidates()

    assert [conversation.conversation_id for conversation in compression_candidates] == [
        "compression",
    ]
    assert compression_candidates[0].status.compression_threshold_exceeded is True


def test_getters_return_last_scan_until_rescanned() -> None:
    store = ConversationStore()
    monitor = _monitor(store)
    monitor.scan()

    store.append_message("warning", "user", "a" * 96)

    assert monitor.get_statistics().conversation_count == 0
    monitor.scan()
    assert monitor.get_statistics().conversation_count == 1
    assert monitor.get_warning_conversations()[0].conversation_id == "warning"


def test_scan_does_not_mutate_conversations() -> None:
    store = ConversationStore()
    first = store.append_message("conv-1", "user", "hello")
    conversation = store.get("conv-1")
    assert conversation is not None
    created_at = conversation.created_at
    updated_at = conversation.updated_at
    messages = list(conversation.messages)
    monitor = _monitor(store)

    monitor.scan()

    assert conversation.created_at == created_at
    assert conversation.updated_at == updated_at
    assert conversation.messages == messages == [first]
