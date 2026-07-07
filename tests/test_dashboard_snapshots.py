from ctxkeeper.context import ContextMeter, ConversationStore
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.dashboard.snapshots import ConversationSnapshotProvider


def _provider(store: ConversationStore) -> ConversationSnapshotProvider:
    return ConversationSnapshotProvider(
        store=store,
        meter=ContextMeter(
            context_window_tokens=100,
            warning_threshold_percent=70,
            compression_threshold_percent=90,
        ),
        recent_message_limit=2,
    )


def test_active_snapshot_returns_empty_state_without_conversations() -> None:
    snapshot = _provider(ConversationStore()).active_snapshot(model_name=None)

    assert snapshot.conversation_id is None
    assert snapshot.model_name is None
    assert snapshot.rolling_summary is None
    assert snapshot.recent_messages == []
    assert snapshot.context is None


def test_active_snapshot_exposes_latest_conversation_read_only_state() -> None:
    store = ConversationStore()
    store.append_message("older", "user", "first")
    store.append_message("active", "system", f"{ROLLING_SUMMARY_PREFIX}important prior context")
    store.append_message("active", "user", "hello")
    store.append_message("active", "assistant", "hi")
    store.append_message("active", "user", "latest")

    snapshot = _provider(store).active_snapshot(model_name="test-model")
    data = snapshot.to_dict()

    assert data["conversation_id"] == "active"
    assert data["model_name"] == "test-model"
    assert data["rolling_summary"] == "important prior context"
    assert [message["role"] for message in data["recent_messages"]] == ["assistant", "user"]
    assert data["recent_messages"][1]["content"] == "latest"
    assert data["context"]["usage_percent"] > 0
    assert store.get("active") is not None
