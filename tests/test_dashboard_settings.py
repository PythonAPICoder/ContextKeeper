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


def _setting_value(snapshot: dict[str, object], setting_id: str) -> object:
    return _settings_by_id(snapshot)[setting_id]["value"]


def _settings_client(settings: Settings | None = None) -> TestClient:
    return TestClient(create_app(settings or Settings()))


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
            assert setting["runtime_editable"] is True
            assert setting["restart_required"] is False
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


def test_dashboard_settings_api_rejects_unsupported_write_methods() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.post("/api/dashboard/settings", json={"context.enabled": False})

    assert response.status_code == 405
    assert response.json()["detail"] == "Use PATCH to update runtime settings."


def test_dashboard_settings_patch_single_field_update_is_visible_on_read() -> None:
    client = _settings_client()

    patch_response = client.patch("/api/dashboard/settings", json={"context": {"enabled": False}})
    read_response = client.get("/api/dashboard/settings")

    assert patch_response.status_code == 200
    assert read_response.status_code == 200
    assert _setting_value(patch_response.json(), "context.enabled") is False
    assert _setting_value(read_response.json(), "context.enabled") is False
    assert _setting_value(read_response.json(), "context.warning_threshold_percent") == 75


def test_dashboard_settings_patch_multi_field_update_returns_full_snapshot() -> None:
    client = _settings_client()

    response = client.patch(
        "/api/dashboard/settings",
        json={
            "context": {
                "enabled": False,
                "warning_threshold_percent": 60,
                "compression_threshold_percent": 90,
                "keep_recent_messages": 12,
            },
            "compression": {
                "enabled": False,
                "summarizer_model": "summary-model:latest",
                "max_summary_tokens": 900,
            },
            "dashboard": {"refresh_interval_ms": 2500},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"schema_version", "categories"}
    assert [category["id"] for category in data["categories"]] == ["context", "compression", "dashboard"]
    assert _setting_value(data, "context.enabled") is False
    assert _setting_value(data, "context.warning_threshold_percent") == 60
    assert _setting_value(data, "context.compression_threshold_percent") == 90
    assert _setting_value(data, "context.keep_recent_messages") == 12
    assert _setting_value(data, "compression.enabled") is False
    assert _setting_value(data, "compression.summarizer_model") == "summary-model:latest"
    assert _setting_value(data, "compression.max_summary_tokens") == 900
    assert _setting_value(data, "dashboard.refresh_interval_ms") == 2500


def test_dashboard_settings_patch_omitted_fields_retain_current_values() -> None:
    client = _settings_client(
        Settings(
            context={
                "enabled": False,
                "warning_threshold_percent": 55,
                "compression_threshold_percent": 80,
                "keep_recent_messages": 6,
            },
            compression={"enabled": False, "summarizer_model": "original:latest", "max_summary_tokens": 700},
            dashboard={"refresh_interval_ms": 1300},
        )
    )

    response = client.patch("/api/dashboard/settings", json={"compression": {"max_summary_tokens": 800}})

    assert response.status_code == 200
    data = response.json()
    assert _setting_value(data, "context.enabled") is False
    assert _setting_value(data, "context.warning_threshold_percent") == 55
    assert _setting_value(data, "context.compression_threshold_percent") == 80
    assert _setting_value(data, "context.keep_recent_messages") == 6
    assert _setting_value(data, "compression.enabled") is False
    assert _setting_value(data, "compression.summarizer_model") == "original:latest"
    assert _setting_value(data, "compression.max_summary_tokens") == 800
    assert _setting_value(data, "dashboard.refresh_interval_ms") == 1300


def test_dashboard_settings_patch_context_and_compression_sections_together() -> None:
    client = _settings_client()

    response = client.patch(
        "/api/dashboard/settings",
        json={
            "context": {"warning_threshold_percent": 65, "compression_threshold_percent": 90},
            "compression": {"enabled": False, "max_summary_tokens": 500},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert _setting_value(data, "context.warning_threshold_percent") == 65
    assert _setting_value(data, "context.compression_threshold_percent") == 90
    assert _setting_value(data, "compression.enabled") is False
    assert _setting_value(data, "compression.max_summary_tokens") == 500


def test_dashboard_settings_patch_can_change_a_previous_runtime_value_again() -> None:
    client = _settings_client()

    first = client.patch("/api/dashboard/settings", json={"context": {"keep_recent_messages": 10}})
    second = client.patch("/api/dashboard/settings", json={"context": {"keep_recent_messages": 14}})

    assert first.status_code == 200
    assert second.status_code == 200
    assert _setting_value(second.json(), "context.keep_recent_messages") == 14
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.keep_recent_messages") == 14


def test_dashboard_settings_patch_rejects_invalid_boolean_input() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={"context": {"enabled": "yes"}})

    assert response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.enabled") is True


def test_dashboard_settings_patch_rejects_invalid_integer_input() -> None:
    client = _settings_client()

    string_response = client.patch("/api/dashboard/settings", json={"context": {"warning_threshold_percent": "75"}})
    float_response = client.patch("/api/dashboard/settings", json={"dashboard": {"refresh_interval_ms": 1000.5}})

    assert string_response.status_code == 422
    assert float_response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.warning_threshold_percent") == 75
    assert _setting_value(client.get("/api/dashboard/settings").json(), "dashboard.refresh_interval_ms") == 1000


def test_dashboard_settings_patch_rejects_out_of_range_percentages() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={"context": {"compression_threshold_percent": 101}})

    assert response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.compression_threshold_percent") == 85


def test_dashboard_settings_patch_rejects_invalid_threshold_ordering() -> None:
    client = _settings_client()

    response = client.patch(
        "/api/dashboard/settings",
        json={"context": {"warning_threshold_percent": 90, "compression_threshold_percent": 80}},
    )

    assert response.status_code == 422
    data = client.get("/api/dashboard/settings").json()
    assert _setting_value(data, "context.warning_threshold_percent") == 75
    assert _setting_value(data, "context.compression_threshold_percent") == 85


def test_dashboard_settings_patch_rejects_partial_threshold_conflict() -> None:
    client = _settings_client(Settings(context={"warning_threshold_percent": 60, "compression_threshold_percent": 80}))

    response = client.patch("/api/dashboard/settings", json={"context": {"warning_threshold_percent": 80}})

    assert response.status_code == 422
    data = client.get("/api/dashboard/settings").json()
    assert _setting_value(data, "context.warning_threshold_percent") == 60
    assert _setting_value(data, "context.compression_threshold_percent") == 80


def test_dashboard_settings_patch_rejects_invalid_numeric_limits() -> None:
    client = _settings_client()

    keep_recent_response = client.patch("/api/dashboard/settings", json={"context": {"keep_recent_messages": 0}})
    max_tokens_response = client.patch("/api/dashboard/settings", json={"compression": {"max_summary_tokens": -1}})

    assert keep_recent_response.status_code == 422
    assert max_tokens_response.status_code == 422
    data = client.get("/api/dashboard/settings").json()
    assert _setting_value(data, "context.keep_recent_messages") == 8
    assert _setting_value(data, "compression.max_summary_tokens") == 1200


def test_dashboard_settings_patch_rejects_blank_model_name() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={"compression": {"summarizer_model": "   "}})

    assert response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "compression.summarizer_model") == "gpt-oss:20b"


def test_dashboard_settings_patch_rejects_unknown_fields() -> None:
    client = _settings_client()

    top_level = client.patch("/api/dashboard/settings", json={"server": {"port": 1234}})
    nested = client.patch("/api/dashboard/settings", json={"context": {"unknown": 1}})

    assert top_level.status_code == 422
    assert nested.status_code == 422


def test_dashboard_settings_patch_rejects_read_only_or_unexposed_fields() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={"context": {"minimum_threshold_percent": 10}})

    assert response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.warning_threshold_percent") == 75


def test_dashboard_settings_patch_is_atomic_when_valid_and_invalid_fields_are_combined() -> None:
    client = _settings_client()

    response = client.patch(
        "/api/dashboard/settings",
        json={"context": {"enabled": False, "keep_recent_messages": 0}},
    )

    assert response.status_code == 422
    data = client.get("/api/dashboard/settings").json()
    assert _setting_value(data, "context.enabled") is True
    assert _setting_value(data, "context.keep_recent_messages") == 8


def test_dashboard_settings_patch_rejects_empty_update_body() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={})
    nested_response = client.patch("/api/dashboard/settings", json={"context": {}})

    assert response.status_code == 400
    assert response.json()["detail"] == "At least one runtime setting must be supplied."
    assert nested_response.status_code == 400


def test_dashboard_settings_patch_rejects_missing_or_malformed_json_body() -> None:
    client = _settings_client()

    missing = client.patch("/api/dashboard/settings")
    malformed = client.patch(
        "/api/dashboard/settings",
        data="{not-json",
        headers={"Content-Type": "application/json"},
    )

    assert missing.status_code == 422
    assert malformed.status_code == 422


def test_dashboard_settings_patch_rejects_wrong_object_shapes() -> None:
    client = _settings_client()

    context_response = client.patch("/api/dashboard/settings", json={"context": False})
    compression_response = client.patch("/api/dashboard/settings", json={"compression": []})

    assert context_response.status_code == 422
    assert compression_response.status_code == 422


def test_dashboard_settings_patch_rejects_null_values() -> None:
    client = _settings_client()

    response = client.patch("/api/dashboard/settings", json={"context": {"enabled": None}})

    assert response.status_code == 422
    assert _setting_value(client.get("/api/dashboard/settings").json(), "context.enabled") is True


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
