from __future__ import annotations

from datetime import timezone

from ctxkeeper.context import (
    CompressionManager,
    CompressionMetadata,
    CompressionPlanStatus,
    ConversationMessage,
)


def _message(content: str, role: str = "user") -> ConversationMessage:
    return ConversationMessage(role=role, content=content)


def test_select_messages_keeps_recent_messages_and_selects_older_for_compression() -> None:
    manager = CompressionManager(keep_recent_messages=2, max_summary_tokens=10)
    messages = [_message("one"), _message("two"), _message("three"), _message("four")]

    selection = manager.select_messages(messages)

    assert selection.compress_messages == messages[:2]
    assert selection.keep_messages == messages[2:]


def test_select_messages_keeps_all_when_not_enough_history() -> None:
    manager = CompressionManager(keep_recent_messages=3, max_summary_tokens=10)
    messages = [_message("one"), _message("two"), _message("three")]

    selection = manager.select_messages(messages)

    assert selection.compress_messages == []
    assert selection.keep_messages == messages


def test_create_plan_delegates_to_planner_without_compressing() -> None:
    manager = CompressionManager(keep_recent_messages=2, max_summary_tokens=10)
    messages = [_message("one"), _message("two"), _message("three")]

    plan = manager.create_plan(
        conversation_id="conv-1",
        messages=messages,
        estimated_tokens_before=100,
        compression_needed=True,
    )

    assert plan.status is CompressionPlanStatus.PLAN_READY
    assert plan.compress_messages == messages[:1]
    assert plan.keep_messages == messages[1:]


def test_create_summary_record_captures_summary_metadata() -> None:
    manager = CompressionManager()

    summary = manager.create_summary_record(
        conversation_id="conv-1",
        content="Summary text.",
        source_messages=[_message("old one"), _message("old two")],
        estimated_tokens=12,
    )

    assert summary.conversation_id == "conv-1"
    assert summary.content == "Summary text."
    assert summary.source_message_count == 2
    assert summary.estimated_tokens == 12
    assert summary.created_at.tzinfo is timezone.utc


def test_update_metadata_creates_initial_metadata() -> None:
    manager = CompressionManager()
    summary = manager.create_summary_record(
        conversation_id="conv-1",
        content="Summary text.",
        source_messages=[_message("old one"), _message("old two")],
        estimated_tokens=12,
    )

    metadata = manager.update_metadata(
        metadata=None,
        summary=summary,
        estimated_tokens_saved=50,
    )

    assert metadata == CompressionMetadata(
        conversation_id="conv-1",
        compression_count=1,
        total_messages_compressed=2,
        total_estimated_tokens_saved=50,
        last_compressed_at=summary.created_at,
        last_summary_tokens=12,
    )


def test_update_metadata_accumulates_existing_metadata() -> None:
    manager = CompressionManager()
    first_summary = manager.create_summary_record(
        conversation_id="conv-1",
        content="First summary.",
        source_messages=[_message("one"), _message("two")],
        estimated_tokens=10,
    )
    metadata = manager.update_metadata(
        metadata=None,
        summary=first_summary,
        estimated_tokens_saved=40,
    )
    second_summary = manager.create_summary_record(
        conversation_id="conv-1",
        content="Second summary.",
        source_messages=[_message("three")],
        estimated_tokens=8,
    )

    updated = manager.update_metadata(
        metadata=metadata,
        summary=second_summary,
        estimated_tokens_saved=20,
    )

    assert updated.conversation_id == "conv-1"
    assert updated.compression_count == 2
    assert updated.total_messages_compressed == 3
    assert updated.total_estimated_tokens_saved == 60
    assert updated.last_compressed_at == second_summary.created_at
    assert updated.last_summary_tokens == 8


def test_archive_plan_placeholder_preserves_full_history_without_encryption() -> None:
    manager = CompressionManager()
    messages = [_message("one"), _message("two"), _message("three")]

    archive_plan = manager.create_archive_plan("conv-1", messages)

    assert archive_plan.conversation_id == "conv-1"
    assert archive_plan.messages == messages
    assert archive_plan.encryption_enabled is False
    assert "not implemented" in archive_plan.reason
