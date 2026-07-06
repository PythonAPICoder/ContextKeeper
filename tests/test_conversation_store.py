from __future__ import annotations

from datetime import timezone

from ctxkeeper.context import Conversation, ConversationMessage, ConversationStore


def test_create_conversation_with_generated_id() -> None:
    store = ConversationStore()

    conversation = store.create()

    assert isinstance(conversation, Conversation)
    assert conversation.conversation_id.startswith("ck_conv_")
    assert conversation.messages == []
    assert conversation.created_at.tzinfo is timezone.utc
    assert conversation.updated_at.tzinfo is timezone.utc
    assert store.get(conversation.conversation_id) is conversation


def test_create_conversation_with_supplied_id() -> None:
    store = ConversationStore()

    conversation = store.create("conv-1")

    assert conversation.conversation_id == "conv-1"
    assert store.get("conv-1") is conversation


def test_append_message_updates_conversation() -> None:
    store = ConversationStore()
    conversation = store.create("conv-1")

    message = store.append_message("conv-1", "user", "Hello")

    assert isinstance(message, ConversationMessage)
    assert message.role == "user"
    assert message.content == "Hello"
    assert message.timestamp.tzinfo is timezone.utc
    assert conversation.messages == [message]
    assert conversation.updated_at == message.timestamp


def test_append_message_auto_creates_unknown_conversation() -> None:
    store = ConversationStore()

    message = store.append_message("conv-new", "assistant", "Hi")
    conversation = store.get("conv-new")

    assert conversation is not None
    assert conversation.conversation_id == "conv-new"
    assert conversation.messages == [message]
    assert conversation.created_at == message.timestamp
    assert conversation.updated_at == message.timestamp


def test_get_unknown_conversation_returns_none() -> None:
    store = ConversationStore()

    assert store.get("missing") is None


def test_delete_existing_and_missing_conversation() -> None:
    store = ConversationStore()
    store.create("conv-1")

    assert store.delete("conv-1") is True
    assert store.get("conv-1") is None
    assert store.delete("conv-1") is False


def test_clear_removes_all_conversations() -> None:
    store = ConversationStore()
    store.create("conv-1")
    store.append_message("conv-2", "user", "Hello")

    store.clear()

    assert store.get("conv-1") is None
    assert store.get("conv-2") is None
    assert store.stats() == {"conversation_count": 0, "message_count": 0}


def test_stats_counts_conversations_and_messages() -> None:
    store = ConversationStore()
    store.create("empty")
    store.append_message("conv-1", "user", "One")
    store.append_message("conv-1", "assistant", "Two")
    store.append_message("conv-2", "user", "Three")

    assert store.stats() == {
        "conversation_count": 3,
        "message_count": 3,
    }


def test_message_ordering_is_preserved() -> None:
    store = ConversationStore()

    first = store.append_message("conv-1", "user", "First")
    second = store.append_message("conv-1", "assistant", "Second")
    third = store.append_message("conv-1", "user", "Third")

    conversation = store.get("conv-1")
    assert conversation is not None
    assert conversation.messages == [first, second, third]
    assert [message.content for message in conversation.messages] == [
        "First",
        "Second",
        "Third",
    ]
