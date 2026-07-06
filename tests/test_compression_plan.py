from __future__ import annotations

from dataclasses import dataclass

import pytest

from ctxkeeper.context import CompressionPlanner, CompressionPlanStatus


@dataclass(frozen=True)
class MessageObject:
    role: str
    content: str


def test_no_action_when_compression_not_needed() -> None:
    planner = CompressionPlanner(keep_recent_messages=2, max_summary_tokens=10)
    messages = ["one", "two", "three"]

    plan = planner.create_plan(
        conversation_id="conv-1",
        messages=messages,
        estimated_tokens_before=100,
        compression_needed=False,
    )

    assert plan.conversation_id == "conv-1"
    assert plan.status is CompressionPlanStatus.NO_ACTION
    assert plan.keep_messages == messages
    assert plan.compress_messages == []
    assert plan.estimated_tokens_before == 100
    assert plan.estimated_tokens_after == 100
    assert plan.estimated_tokens_saved == 0
    assert plan.reason


def test_not_enough_history_when_messages_are_within_keep_limit() -> None:
    planner = CompressionPlanner(keep_recent_messages=3, max_summary_tokens=10)
    messages = ["one", "two", "three"]

    plan = planner.create_plan(
        conversation_id="conv-1",
        messages=messages,
        estimated_tokens_before=100,
        compression_needed=True,
    )

    assert plan.status is CompressionPlanStatus.NOT_ENOUGH_HISTORY
    assert plan.keep_messages == messages
    assert plan.compress_messages == []
    assert plan.estimated_tokens_after == 100
    assert plan.estimated_tokens_saved == 0
    assert plan.reason


def test_plan_ready_splits_compress_and_keep_messages() -> None:
    planner = CompressionPlanner(keep_recent_messages=2, max_summary_tokens=10)
    messages = ["one", "two", "three", "four", "five"]

    plan = planner.create_plan(
        conversation_id="conv-1",
        messages=messages,
        estimated_tokens_before=100,
        compression_needed=True,
    )

    assert plan.status is CompressionPlanStatus.PLAN_READY
    assert plan.compress_messages == ["one", "two", "three"]
    assert plan.keep_messages == ["four", "five"]
    assert plan.reason


def test_estimated_token_savings_is_calculated_for_kept_messages() -> None:
    planner = CompressionPlanner(keep_recent_messages=2, max_summary_tokens=10)
    messages = [
        {"role": "system", "content": "old"},
        MessageObject(role="user", content="old"),
        "a" * 8,
        "b" * 12,
    ]

    plan = planner.create_plan(
        conversation_id="conv-1",
        messages=messages,
        estimated_tokens_before=50,
        compression_needed=True,
    )

    assert plan.status is CompressionPlanStatus.PLAN_READY
    assert plan.estimated_tokens_after == 15
    assert plan.estimated_tokens_saved == 35


def test_invalid_keep_recent_messages_raises_value_error() -> None:
    with pytest.raises(ValueError, match="keep_recent_messages must be greater than or equal to 1"):
        CompressionPlanner(keep_recent_messages=0)


def test_invalid_max_summary_tokens_raises_value_error() -> None:
    with pytest.raises(ValueError, match="max_summary_tokens must be greater than or equal to 1"):
        CompressionPlanner(max_summary_tokens=0)
