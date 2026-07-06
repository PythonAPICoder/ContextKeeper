from __future__ import annotations

import pytest

from ctxkeeper.context import ContextMeter, ConversationStore


def test_empty_conversation_has_zero_usage() -> None:
    store = ConversationStore()
    conversation = store.create("conv-1")
    meter = ContextMeter(
        context_window_tokens=100,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    )

    status = meter.evaluate(conversation)

    assert status.estimated_tokens == 0
    assert status.context_window_tokens == 100
    assert status.usage_percent == 0.0
    assert status.warning_threshold_exceeded is False
    assert status.compression_threshold_exceeded is False


def test_small_conversation_below_thresholds() -> None:
    store = ConversationStore()
    store.append_message("conv-1", "user", "hello")
    conversation = store.get("conv-1")
    assert conversation is not None
    meter = ContextMeter(
        context_window_tokens=100,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    )

    status = meter.evaluate(conversation)

    assert status.estimated_tokens == 3
    assert status.usage_percent == 3.0
    assert status.warning_threshold_exceeded is False
    assert status.compression_threshold_exceeded is False


def test_warning_threshold_reached() -> None:
    store = ConversationStore()
    store.append_message("conv-1", "user", "a" * 96)
    conversation = store.get("conv-1")
    assert conversation is not None
    meter = ContextMeter(
        context_window_tokens=50,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    )

    status = meter.evaluate(conversation)

    assert status.estimated_tokens == 25
    assert status.usage_percent == 50.0
    assert status.warning_threshold_exceeded is True
    assert status.compression_threshold_exceeded is False


def test_compression_threshold_reached() -> None:
    store = ConversationStore()
    store.append_message("conv-1", "user", "a" * 156)
    conversation = store.get("conv-1")
    assert conversation is not None
    meter = ContextMeter(
        context_window_tokens=50,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    )

    status = meter.evaluate(conversation)

    assert status.estimated_tokens == 40
    assert status.usage_percent == 80.0
    assert status.warning_threshold_exceeded is True
    assert status.compression_threshold_exceeded is True


def test_different_context_window_sizes_affect_percentage() -> None:
    store = ConversationStore()
    store.append_message("conv-1", "user", "a" * 76)
    conversation = store.get("conv-1")
    assert conversation is not None

    small_window = ContextMeter(
        context_window_tokens=50,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    ).evaluate(conversation)
    large_window = ContextMeter(
        context_window_tokens=100,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    ).evaluate(conversation)

    assert small_window.estimated_tokens == large_window.estimated_tokens == 20
    assert small_window.usage_percent == 40.0
    assert large_window.usage_percent == 20.0


def test_evaluate_accepts_message_collection_and_does_not_mutate() -> None:
    store = ConversationStore()
    first = store.append_message("conv-1", "user", "first")
    second = store.append_message("conv-1", "assistant", "second")
    messages = [first, second]
    meter = ContextMeter(
        context_window_tokens=100,
        warning_threshold_percent=50,
        compression_threshold_percent=80,
    )

    status = meter.evaluate(messages)

    assert status.estimated_tokens == 8
    assert messages == [first, second]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "context_window_tokens": 0,
                "warning_threshold_percent": 50,
                "compression_threshold_percent": 80,
            },
            "context_window_tokens must be greater than 0",
        ),
        (
            {
                "context_window_tokens": 100,
                "warning_threshold_percent": -1,
                "compression_threshold_percent": 80,
            },
            "warning_threshold_percent must be between 0 and 100",
        ),
        (
            {
                "context_window_tokens": 100,
                "warning_threshold_percent": 50,
                "compression_threshold_percent": 101,
            },
            "compression_threshold_percent must be between 0 and 100",
        ),
        (
            {
                "context_window_tokens": 100,
                "warning_threshold_percent": 90,
                "compression_threshold_percent": 80,
            },
            "warning_threshold_percent must be less than or equal to compression_threshold_percent",
        ),
    ],
)
def test_invalid_context_meter_configuration_fails_clearly(
    kwargs: dict[str, int],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ContextMeter(**kwargs)
