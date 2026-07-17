import json

from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.dashboard.settings_snapshot import build_dashboard_settings_snapshot


SETTING_KEYS = {
    "id",
    "category",
    "display_name",
    "description",
    "value",
    "default_value",
    "minimum",
    "maximum",
    "runtime_editable",
    "restart_required",
    "data_type",
}


def _settings_by_id(snapshot: dict[str, object]) -> dict[str, dict[str, object]]:
    settings: dict[str, dict[str, object]] = {}
    for category in snapshot["categories"]:
        assert isinstance(category, dict)
        for setting in category["settings"]:
            assert isinstance(setting, dict)
            settings[str(setting["id"])] = setting
    return settings


def test_dashboard_settings_snapshot_schema_and_categories() -> None:
    snapshot = build_dashboard_settings_snapshot(Settings()).to_dict()

    assert set(snapshot) == {"schema_version", "categories"}
    assert snapshot["schema_version"] == 1
    categories = snapshot["categories"]
    assert isinstance(categories, list)
    assert [category["id"] for category in categories] == ["context", "compression", "dashboard"]
    assert [category["display_name"] for category in categories] == ["Context", "Compression", "Dashboard"]

    for category in categories:
        assert set(category) == {"id", "display_name", "description", "settings"}
        assert isinstance(category["settings"], list)
        assert category["settings"]
        for setting in category["settings"]:
            assert set(setting) == SETTING_KEYS
            assert setting["category"] == category["id"]
            assert setting["runtime_editable"] is False
            assert setting["restart_required"] is True
            assert setting["data_type"] in {"boolean", "integer", "string"}


def test_dashboard_settings_snapshot_values_defaults_and_validation_metadata() -> None:
    settings = Settings(
        context={
            "enabled": False,
            "warning_threshold_percent": 60,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
        },
        compression={
            "enabled": False,
            "summarizer_model": "summary-model:latest",
            "max_summary_tokens": 900,
        },
        dashboard={"refresh_interval_ms": 2500},
    )

    snapshot = build_dashboard_settings_snapshot(settings).to_dict()
    by_id = _settings_by_id(snapshot)

    assert by_id["context.enabled"]["value"] is False
    assert by_id["context.enabled"]["default_value"] is True
    assert by_id["context.enabled"]["minimum"] is None
    assert by_id["context.enabled"]["maximum"] is None
    assert by_id["context.enabled"]["data_type"] == "boolean"

    assert by_id["context.warning_threshold_percent"]["value"] == 60
    assert by_id["context.warning_threshold_percent"]["default_value"] == 75
    assert by_id["context.warning_threshold_percent"]["minimum"] == 0
    assert by_id["context.warning_threshold_percent"]["maximum"] == 100

    assert by_id["context.compression_threshold_percent"]["value"] == 90
    assert by_id["context.compression_threshold_percent"]["default_value"] == 85
    assert by_id["context.compression_threshold_percent"]["minimum"] == 0
    assert by_id["context.compression_threshold_percent"]["maximum"] == 100

    assert by_id["context.keep_recent_messages"]["value"] == 12
    assert by_id["context.keep_recent_messages"]["default_value"] == 8
    assert by_id["context.keep_recent_messages"]["minimum"] == 1
    assert by_id["context.keep_recent_messages"]["maximum"] is None

    assert by_id["compression.enabled"]["value"] is False
    assert by_id["compression.summarizer_model"]["value"] == "summary-model:latest"
    assert by_id["compression.summarizer_model"]["default_value"] == "gpt-oss:20b"
    assert by_id["compression.summarizer_model"]["data_type"] == "string"
    assert by_id["compression.max_summary_tokens"]["value"] == 900
    assert by_id["compression.max_summary_tokens"]["minimum"] == 1

    assert by_id["dashboard.refresh_interval_ms"]["value"] == 2500
    assert by_id["dashboard.refresh_interval_ms"]["default_value"] == 1000
    assert by_id["dashboard.refresh_interval_ms"]["minimum"] == 1


def test_dashboard_settings_snapshot_exposes_only_approved_settings() -> None:
    settings = Settings(
        app={"name": "HiddenAppName"},
        server={"host": "secret-host.local", "port": 11999},
        ollama={"base_url": "http://secret-ollama.local:11434"},
        logging={"file": "logs/secret-contextkeeper.log", "level": "DEBUG"},
        metrics={"refresh_interval_seconds": 9},
        models={"secret-model": {"context_window_tokens": 12345}},
    )

    snapshot = build_dashboard_settings_snapshot(settings).to_dict()
    serialized = json.dumps(snapshot)
    by_id = _settings_by_id(snapshot)

    assert set(by_id) == {
        "context.enabled",
        "context.warning_threshold_percent",
        "context.compression_threshold_percent",
        "context.keep_recent_messages",
        "compression.enabled",
        "compression.summarizer_model",
        "compression.max_summary_tokens",
        "dashboard.refresh_interval_ms",
    }
    assert "HiddenAppName" not in serialized
    assert "secret-host.local" not in serialized
    assert "secret-ollama.local" not in serialized
    assert "secret-contextkeeper.log" not in serialized
    assert "secret-model" not in serialized
    assert "CONTEXTKEEPER_" not in serialized


def test_dashboard_settings_api_endpoint_returns_snapshot() -> None:
    app = create_app(
        Settings(
            context={"warning_threshold_percent": 50, "compression_threshold_percent": 80},
            dashboard={"refresh_interval_ms": 1500},
        )
    )
    client = TestClient(app)

    response = client.get("/api/dashboard/settings")

    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert [category["id"] for category in data["categories"]] == ["context", "compression", "dashboard"]
    by_id = _settings_by_id(data)
    assert by_id["context.warning_threshold_percent"]["value"] == 50
    assert by_id["context.warning_threshold_percent"]["default_value"] == 75
    assert by_id["context.compression_threshold_percent"]["value"] == 80
    assert by_id["dashboard.refresh_interval_ms"]["value"] == 1500


def test_dashboard_settings_api_is_read_only() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.post("/api/dashboard/settings", json={"context.enabled": False})

    assert response.status_code == 405
    assert response.json()["detail"] == "Settings are read-only in this version."


def test_dashboard_settings_api_does_not_change_existing_dashboard_payload(monkeypatch) -> None:
    async def fake_check_ollama(settings: Settings) -> dict[str, object]:
        return {"status": "online", "version": "test", "latency_ms": 1.0}

    monkeypatch.setattr("ctxkeeper.dashboard.routes._check_ollama", fake_check_ollama)
    app = create_app(Settings())
    client = TestClient(app)

    dashboard_response = client.get("/dashboard/data")
    settings_response = client.get("/api/dashboard/settings")

    assert dashboard_response.status_code == 200
    assert settings_response.status_code == 200
    assert "conversation_inspector" in dashboard_response.json()
    assert "categories" in settings_response.json()
    assert "categories" not in dashboard_response.json()
