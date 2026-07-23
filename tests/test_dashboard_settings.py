import inspect
import json
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings, load_config
from ctxkeeper.dashboard.routes import create_dashboard_router
from ctxkeeper.dashboard.settings_snapshot import DashboardSetting, build_dashboard_settings_snapshot


SETTING_KEYS = {
    "id",
    "category",
    "display_name",
    "description",
    "value",
    "persisted_value",
    "default_value",
    "differs_from_persisted",
    "minimum",
    "maximum",
    "runtime_editable",
    "persistable",
    "restart_required",
    "reset_eligible",
    "data_type",
}


@pytest.fixture(autouse=True)
def _isolate_default_config_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep settings API reads and writes isolated from the repository config."""

    monkeypatch.chdir(tmp_path)


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


def _default_reset_payload(
    snapshot: dict[str, object],
    *,
    category_id: str | None = None,
    setting_id: str | None = None,
    runtime_only: bool = False,
) -> dict[str, dict[str, object]]:
    payload: dict[str, dict[str, object]] = {}
    for category in snapshot["categories"]:
        assert isinstance(category, dict)
        if category_id is not None and category["id"] != category_id:
            continue
        for setting in category["settings"]:
            assert isinstance(setting, dict)
            if not setting["reset_eligible"]:
                continue
            if runtime_only and not setting["runtime_editable"]:
                continue
            if setting_id is not None and setting["id"] != setting_id:
                continue
            payload_category, field_name = str(setting["id"]).split(".", maxsplit=1)
            assert payload_category and field_name and "." not in field_name
            payload.setdefault(payload_category, {})[field_name] = setting[
                "default_value"
            ]
    return payload


def _settings_client(
    settings: Settings | None = None,
    *,
    config_path: str | Path = "contextkeeper.yaml",
) -> TestClient:
    return TestClient(create_app(settings or Settings(), config_path=config_path))


def _write_config(path: Path, data: dict[str, object]) -> bytes:
    serialized = yaml.safe_dump(data, sort_keys=False)
    path.write_text(serialized, encoding="utf-8")
    return path.read_bytes()


def test_dashboard_settings_snapshot_schema_and_categories() -> None:
    snapshot = build_dashboard_settings_snapshot(Settings()).to_dict()

    assert set(snapshot) == {"schema_version", "categories"}
    assert snapshot["schema_version"] == 2
    categories = snapshot["categories"]
    assert isinstance(categories, list)
    assert [category["id"] for category in categories] == [
        "ollama",
        "context",
        "compression",
        "dashboard",
    ]
    assert [category["display_name"] for category in categories] == [
        "Connection",
        "Context",
        "Compression",
        "Dashboard",
    ]
    assert [category["display_name"] for category in categories].count("Connection") == 1

    for category in categories:
        assert set(category) == {"id", "display_name", "description", "settings"}
        assert isinstance(category["settings"], list)
        assert category["settings"]
        for setting in category["settings"]:
            assert set(setting) == SETTING_KEYS
            assert setting["category"] == category["id"]
            assert setting["persistable"] is True
            assert setting["reset_eligible"] is True
            assert setting["persisted_value"] == setting["value"]
            assert setting["differs_from_persisted"] is False
            assert setting["data_type"] in {"boolean", "integer", "string"}
            if category["id"] == "ollama":
                assert setting["runtime_editable"] is False
                assert setting["restart_required"] is True
            else:
                assert setting["runtime_editable"] is True
                assert setting["restart_required"] is False


def test_dashboard_settings_snapshot_values_defaults_and_validation_metadata() -> None:
    settings = Settings(
        ollama={
            "base_url": "https://ollama.example.internal/ollama",
            "timeout_seconds": 45,
        },
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

    assert (
        by_id["ollama.base_url"]["value"]
        == "https://ollama.example.internal/ollama"
    )
    assert by_id["ollama.base_url"]["default_value"] == "http://localhost:11434"
    assert by_id["ollama.base_url"]["data_type"] == "string"
    assert by_id["ollama.base_url"]["minimum"] is None
    assert by_id["ollama.base_url"]["maximum"] is None
    assert by_id["ollama.base_url"]["runtime_editable"] is False
    assert by_id["ollama.base_url"]["persistable"] is True
    assert by_id["ollama.base_url"]["restart_required"] is True
    assert by_id["ollama.base_url"]["reset_eligible"] is True

    assert by_id["ollama.timeout_seconds"]["value"] == 45
    assert by_id["ollama.timeout_seconds"]["default_value"] == 120
    assert by_id["ollama.timeout_seconds"]["data_type"] == "integer"
    assert by_id["ollama.timeout_seconds"]["minimum"] == 1
    assert by_id["ollama.timeout_seconds"]["maximum"] is None
    assert by_id["ollama.timeout_seconds"]["runtime_editable"] is False
    assert by_id["ollama.timeout_seconds"]["persistable"] is True
    assert by_id["ollama.timeout_seconds"]["restart_required"] is True
    assert by_id["ollama.timeout_seconds"]["reset_eligible"] is True

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


def test_dashboard_settings_snapshot_distinguishes_runtime_and_persisted_values() -> None:
    runtime = Settings(
        ollama={
            "base_url": "http://runtime-ollama.internal:11434",
            "timeout_seconds": 120,
        },
        context={"warning_threshold_percent": 60, "compression_threshold_percent": 90},
        compression={"enabled": False},
    )
    persisted = Settings(
        ollama={
            "base_url": "http://saved-ollama.internal:11434",
            "timeout_seconds": 45,
        },
        context={"warning_threshold_percent": 70, "compression_threshold_percent": 90},
        compression={"enabled": True},
    )

    snapshot = build_dashboard_settings_snapshot(runtime, persisted).to_dict()
    by_id = _settings_by_id(snapshot)

    warning = by_id["context.warning_threshold_percent"]
    assert warning["value"] == 60
    assert warning["persisted_value"] == 70
    assert warning["default_value"] == 75
    assert warning["differs_from_persisted"] is True
    assert warning["persistable"] is True
    compression = by_id["compression.enabled"]
    assert compression["value"] is False
    assert compression["persisted_value"] is True
    assert compression["differs_from_persisted"] is True
    assert by_id["dashboard.refresh_interval_ms"]["differs_from_persisted"] is False
    endpoint = by_id["ollama.base_url"]
    assert endpoint["value"] == "http://runtime-ollama.internal:11434"
    assert endpoint["persisted_value"] == "http://saved-ollama.internal:11434"
    assert endpoint["default_value"] == "http://localhost:11434"
    assert endpoint["differs_from_persisted"] is True
    timeout = by_id["ollama.timeout_seconds"]
    assert timeout["value"] == 120
    assert timeout["persisted_value"] == 45
    assert timeout["default_value"] == 120
    assert timeout["differs_from_persisted"] is True


def test_dashboard_setting_supports_restart_required_persisted_runtime_divergence() -> None:
    setting = DashboardSetting(
        id="example.restart_setting",
        category="example",
        display_name="Restart setting",
        description="Synthetic metadata contract coverage.",
        value=True,
        persisted_value=False,
        default_value=True,
        data_type="boolean",
        runtime_editable=False,
        persistable=True,
        restart_required=True,
        reset_eligible=True,
    )

    data = setting.to_dict()

    assert data["value"] is True
    assert data["persisted_value"] is False
    assert data["differs_from_persisted"] is True
    assert data["runtime_editable"] is False
    assert data["persistable"] is True
    assert data["restart_required"] is True
    assert data["reset_eligible"] is True


@pytest.mark.parametrize(
    ("runtime_editable", "reset_eligible", "expected"),
    [
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, False),
    ],
)
def test_dashboard_setting_reset_eligibility_is_independent_of_runtime_editability(
    runtime_editable: bool,
    reset_eligible: bool,
    expected: bool,
) -> None:
    setting = DashboardSetting(
        id="example.setting",
        category="example",
        display_name="Example setting",
        description="Synthetic reset eligibility contract coverage.",
        value=True,
        persisted_value=True,
        default_value=True,
        data_type="boolean",
        runtime_editable=runtime_editable,
        reset_eligible=reset_eligible,
    )

    assert setting.to_dict()["reset_eligible"] is expected


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
        "ollama.base_url",
        "ollama.timeout_seconds",
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
    assert by_id["ollama.base_url"]["value"] == "http://secret-ollama.local:11434"
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
    assert data["schema_version"] == 2
    assert [category["id"] for category in data["categories"]] == [
        "ollama",
        "context",
        "compression",
        "dashboard",
    ]
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
    assert [category["id"] for category in data["categories"]] == [
        "ollama",
        "context",
        "compression",
        "dashboard",
    ]
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
    connection = client.patch(
        "/api/dashboard/settings",
        json={
            "ollama": {
                "base_url": "http://candidate-ollama.internal:11434",
                "timeout_seconds": 30,
            }
        },
    )

    assert top_level.status_code == 422
    assert nested.status_code == 422
    assert connection.status_code == 422
    snapshot = client.get("/api/dashboard/settings").json()
    assert _setting_value(snapshot, "ollama.base_url") == "http://localhost:11434"
    assert _setting_value(snapshot, "ollama.timeout_seconds") == 120


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


def test_dashboard_settings_config_put_persists_and_returns_refreshed_snapshot(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_config(
        config_path,
        {
            "context": {
                "enabled": True,
                "warning_threshold_percent": 75,
                "compression_threshold_percent": 85,
            },
            "compression": {"enabled": True},
        },
    )
    runtime = Settings()
    client = _settings_client(runtime, config_path=config_path)

    response = client.put(
        "/api/dashboard/settings/config",
        json={
            "context": {"enabled": False, "warning_threshold_percent": 70},
            "compression": {"enabled": False},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "status",
        "persisted_setting_ids",
        "configuration_created",
        "settings",
    }
    assert data["status"] == "saved"
    assert data["persisted_setting_ids"] == [
        "compression.enabled",
        "context.enabled",
        "context.warning_threshold_percent",
    ]
    assert data["configuration_created"] is False
    assert data["settings"]["schema_version"] == 2
    by_id = _settings_by_id(data["settings"])
    assert by_id["context.enabled"]["value"] is True
    assert by_id["context.enabled"]["persisted_value"] is False
    assert by_id["context.enabled"]["differs_from_persisted"] is True
    assert by_id["context.warning_threshold_percent"]["value"] == 75
    assert by_id["context.warning_threshold_percent"]["persisted_value"] == 70
    assert by_id["compression.enabled"]["value"] is True
    assert by_id["compression.enabled"]["persisted_value"] is False

    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["context"]["enabled"] is False
    assert persisted["context"]["warning_threshold_percent"] == 70
    assert persisted["compression"]["enabled"] is False

    refreshed = client.get("/api/dashboard/settings")
    assert refreshed.status_code == 200
    assert _settings_by_id(refreshed.json())["context.enabled"]["persisted_value"] is False


def test_dashboard_settings_config_put_creates_missing_configuration(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "missing" / "contextkeeper.yaml"
    client = _settings_client(config_path=config_path)

    response = client.put(
        "/api/dashboard/settings/config",
        json={"dashboard": {"refresh_interval_ms": 2400}},
    )

    assert response.status_code == 200
    assert response.json()["configuration_created"] is True
    assert config_path.exists()
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted == {"dashboard": {"refresh_interval_ms": 2400}}


def test_dashboard_settings_config_put_does_not_mutate_runtime_state(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_config(config_path, {"context": {"enabled": True}})
    runtime = Settings(context={"enabled": True})
    app = create_app(runtime, config_path=config_path)
    client = TestClient(app)

    response = client.put(
        "/api/dashboard/settings/config",
        json={"context": {"enabled": False}},
    )

    assert response.status_code == 200
    assert app.state.settings is runtime
    assert runtime.context.enabled is True
    assert _setting_value(response.json()["settings"], "context.enabled") is True
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["context"]["enabled"] is False


def test_dashboard_settings_config_put_persists_connection_without_activation(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_config(
        config_path,
        {
            "ollama": {
                "base_url": "http://runtime-ollama.internal:11434",
                "timeout_seconds": 120,
            },
            "custom_future_category": {"preserve": True},
        },
    )
    runtime = Settings(
        ollama={
            "base_url": "http://runtime-ollama.internal:11434",
            "timeout_seconds": 120,
        }
    )
    app = create_app(runtime, config_path=config_path)
    client = TestClient(app)

    response = client.put(
        "/api/dashboard/settings/config",
        json={
            "ollama": {
                "base_url": "https://candidate-ollama.internal/ollama/",
                "timeout_seconds": 45,
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["persisted_setting_ids"] == [
        "ollama.base_url",
        "ollama.timeout_seconds",
    ]
    assert app.state.settings is runtime
    assert runtime.ollama.base_url == "http://runtime-ollama.internal:11434"
    assert runtime.ollama.timeout_seconds == 120
    by_id = _settings_by_id(response.json()["settings"])
    assert by_id["ollama.base_url"]["value"] == (
        "http://runtime-ollama.internal:11434"
    )
    assert by_id["ollama.base_url"]["persisted_value"] == (
        "https://candidate-ollama.internal/ollama"
    )
    assert by_id["ollama.base_url"]["differs_from_persisted"] is True
    assert by_id["ollama.timeout_seconds"]["value"] == 120
    assert by_id["ollama.timeout_seconds"]["persisted_value"] == 45
    assert by_id["ollama.timeout_seconds"]["differs_from_persisted"] is True
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["ollama"] == {
        "base_url": "https://candidate-ollama.internal/ollama",
        "timeout_seconds": 45,
    }
    assert persisted["custom_future_category"] == {"preserve": True}


def test_saved_connection_preserves_environment_endpoint_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_config(
        config_path,
        {
            "ollama": {
                "base_url": "http://yaml-ollama.internal:11434",
                "timeout_seconds": 120,
            }
        },
    )
    environment_endpoint = "http://environment-ollama.internal:11434"
    monkeypatch.setenv("CONTEXTKEEPER_OLLAMA_URL", environment_endpoint)
    runtime = load_config(config_path)
    app = create_app(runtime, config_path=config_path)
    client = TestClient(app)

    response = client.put(
        "/api/dashboard/settings/config",
        json={
            "ollama": {
                "base_url": "http://saved-ollama.internal:11434",
                "timeout_seconds": 45,
            }
        },
    )

    assert response.status_code == 200
    assert runtime.ollama.base_url == environment_endpoint
    assert runtime.ollama.timeout_seconds == 120
    by_id = _settings_by_id(response.json()["settings"])
    assert by_id["ollama.base_url"]["value"] == environment_endpoint
    assert (
        by_id["ollama.base_url"]["persisted_value"]
        == "http://saved-ollama.internal:11434"
    )
    assert by_id["ollama.base_url"]["differs_from_persisted"] is True
    reloaded = load_config(config_path)
    assert reloaded.ollama.base_url == environment_endpoint
    assert reloaded.ollama.timeout_seconds == 45
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert (
        persisted["ollama"]["base_url"]
        == "http://saved-ollama.internal:11434"
    )
    assert persisted["ollama"]["timeout_seconds"] == 45


def test_runtime_patch_remains_separate_and_does_not_write_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_config(config_path, {"context": {"enabled": True}})
    client = _settings_client(config_path=config_path)

    response = client.patch(
        "/api/dashboard/settings",
        json={"context": {"enabled": False}},
    )

    assert response.status_code == 200
    setting = _settings_by_id(response.json())["context.enabled"]
    assert setting["value"] is False
    assert setting["persisted_value"] is True
    assert setting["differs_from_persisted"] is True
    assert config_path.read_bytes() == original


def test_individual_default_reset_uses_authoritative_metadata_until_explicit_put(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_config(
        config_path,
        {
            "context": {
                "enabled": False,
                "warning_threshold_percent": 60,
                "compression_threshold_percent": 90,
                "keep_recent_messages": 12,
            },
            "custom_future_category": {"preserve": "unchanged"},
        },
    )
    runtime = Settings(
        context={
            "enabled": False,
            "warning_threshold_percent": 60,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
        }
    )
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()
    initial_by_id = _settings_by_id(initial_snapshot)
    setting_id = "context.keep_recent_messages"
    reset_payload = _default_reset_payload(
        initial_snapshot,
        setting_id=setting_id,
    )

    reset_response = client.patch("/api/dashboard/settings", json=reset_payload)

    assert reset_response.status_code == 200
    reset_by_id = _settings_by_id(reset_response.json())
    assert reset_by_id[setting_id]["value"] == initial_by_id[setting_id][
        "default_value"
    ]
    assert reset_by_id[setting_id]["persisted_value"] == initial_by_id[setting_id][
        "value"
    ]
    assert reset_by_id[setting_id]["differs_from_persisted"] is True
    for other_id, initial_setting in initial_by_id.items():
        if other_id != setting_id:
            assert reset_by_id[other_id]["value"] == initial_setting["value"]
    assert config_path.read_bytes() == original

    save_response = client.put(
        "/api/dashboard/settings/config",
        json=reset_payload,
    )

    assert save_response.status_code == 200
    assert save_response.json()["persisted_setting_ids"] == [setting_id]
    saved_by_id = _settings_by_id(save_response.json()["settings"])
    assert saved_by_id[setting_id]["value"] == initial_by_id[setting_id][
        "default_value"
    ]
    assert saved_by_id[setting_id]["persisted_value"] == initial_by_id[setting_id][
        "default_value"
    ]
    assert saved_by_id[setting_id]["differs_from_persisted"] is False
    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["context"]["keep_recent_messages"] == initial_by_id[setting_id][
        "default_value"
    ]
    assert persisted["custom_future_category"] == {"preserve": "unchanged"}


def test_discard_recovery_restores_persisted_value_after_default_reset_patch(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_config(
        config_path,
        {
            "context": {
                "warning_threshold_percent": 60,
                "compression_threshold_percent": 90,
                "keep_recent_messages": 12,
            }
        },
    )
    runtime = Settings(
        context={
            "warning_threshold_percent": 60,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
        }
    )
    client = _settings_client(runtime, config_path=config_path)
    setting_id = "context.keep_recent_messages"
    initial_snapshot = client.get("/api/dashboard/settings").json()
    initial_setting = _settings_by_id(initial_snapshot)[setting_id]
    assert initial_setting["value"] == initial_setting["persisted_value"]
    assert initial_setting["value"] != initial_setting["default_value"]

    reset_response = client.patch(
        "/api/dashboard/settings",
        json=_default_reset_payload(initial_snapshot, setting_id=setting_id),
    )

    assert reset_response.status_code == 200
    reset_setting = _settings_by_id(reset_response.json())[setting_id]
    assert reset_setting["value"] == initial_setting["default_value"]
    assert reset_setting["persisted_value"] == initial_setting["persisted_value"]
    assert reset_setting["differs_from_persisted"] is True
    assert config_path.read_bytes() == original

    category, field_name = setting_id.split(".", maxsplit=1)
    recovery_response = client.patch(
        "/api/dashboard/settings",
        json={category: {field_name: reset_setting["persisted_value"]}},
    )

    assert recovery_response.status_code == 200
    recovered_setting = _settings_by_id(recovery_response.json())[setting_id]
    assert recovered_setting["value"] == initial_setting["persisted_value"]
    assert recovered_setting["persisted_value"] == initial_setting[
        "persisted_value"
    ]
    assert recovered_setting["default_value"] == initial_setting["default_value"]
    assert recovered_setting["value"] != recovered_setting["default_value"]
    assert recovered_setting["differs_from_persisted"] is False
    assert config_path.read_bytes() == original


def test_category_default_reset_updates_only_eligible_settings_in_that_category(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    runtime = Settings(
        context={
            "enabled": False,
            "warning_threshold_percent": 60,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
        },
        compression={
            "enabled": False,
            "summarizer_model": "custom-summary:latest",
            "max_summary_tokens": 900,
        },
        dashboard={"refresh_interval_ms": 2500},
    )
    original = _write_config(config_path, runtime.model_dump())
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()
    initial_by_id = _settings_by_id(initial_snapshot)
    reset_payload = _default_reset_payload(initial_snapshot, category_id="context")

    response = client.patch("/api/dashboard/settings", json=reset_payload)

    assert response.status_code == 200
    reset_by_id = _settings_by_id(response.json())
    for setting_id, initial_setting in initial_by_id.items():
        if initial_setting["category"] == "context":
            assert initial_setting["reset_eligible"] is True
            assert reset_by_id[setting_id]["value"] == initial_setting[
                "default_value"
            ]
        else:
            assert reset_by_id[setting_id]["value"] == initial_setting["value"]
    assert config_path.read_bytes() == original


def test_category_default_reset_validation_failure_is_atomic(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    configuration = {
        "context": {
            "enabled": False,
            "minimum_threshold_percent": 80,
            "warning_threshold_percent": 82,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
        }
    }
    original = _write_config(config_path, configuration)
    runtime = Settings.model_validate(configuration)
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()
    initial_by_id = _settings_by_id(initial_snapshot)
    reset_payload = _default_reset_payload(initial_snapshot, category_id="context")

    response = client.patch("/api/dashboard/settings", json=reset_payload)

    assert response.status_code == 422
    current_by_id = _settings_by_id(client.get("/api/dashboard/settings").json())
    assert {
        setting_id: setting["value"]
        for setting_id, setting in current_by_id.items()
    } == {
        setting_id: setting["value"]
        for setting_id, setting in initial_by_id.items()
    }
    assert runtime.context.minimum_threshold_percent == 80
    assert config_path.read_bytes() == original


@pytest.mark.parametrize(
    ("setting_id", "expected_payload", "expected_default"),
    [
        (
            "ollama.base_url",
            {"ollama": {"base_url": "http://localhost:11434"}},
            "http://localhost:11434",
        ),
        (
            "ollama.timeout_seconds",
            {"ollama": {"timeout_seconds": 120}},
            120,
        ),
    ],
)
def test_individual_connection_reset_default_is_persistence_only(
    tmp_path: Path,
    setting_id: str,
    expected_payload: dict[str, dict[str, object]],
    expected_default: object,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    configuration = {
        "server": {"host": "127.0.0.1", "port": 11605},
        "ollama": {
            "base_url": "http://custom-ollama.internal:11434",
            "timeout_seconds": 45,
        },
    }
    original = _write_config(config_path, configuration)
    runtime = Settings.model_validate(configuration)
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()
    reset_payload = _default_reset_payload(
        initial_snapshot,
        setting_id=setting_id,
    )

    assert reset_payload == expected_payload
    patch_response = client.patch(
        "/api/dashboard/settings",
        json=reset_payload,
    )
    assert patch_response.status_code == 422
    assert config_path.read_bytes() == original
    assert runtime.ollama.base_url == "http://custom-ollama.internal:11434"
    assert runtime.ollama.timeout_seconds == 45

    save_response = client.put(
        "/api/dashboard/settings/config",
        json=reset_payload,
    )

    assert save_response.status_code == 200
    by_id = _settings_by_id(save_response.json()["settings"])
    assert by_id[setting_id]["persisted_value"] == expected_default
    assert by_id[setting_id]["value"] != expected_default
    assert by_id[setting_id]["differs_from_persisted"] is True
    assert runtime.ollama.base_url == "http://custom-ollama.internal:11434"
    assert runtime.ollama.timeout_seconds == 45


def test_connection_category_reset_defaults_are_saved_without_runtime_patch(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    configuration = {
        "server": {"host": "127.0.0.1", "port": 11605},
        "ollama": {
            "base_url": "http://custom-ollama.internal:11434",
            "timeout_seconds": 45,
        },
    }
    _write_config(config_path, configuration)
    runtime = Settings.model_validate(configuration)
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()

    reset_payload = _default_reset_payload(
        initial_snapshot,
        category_id="ollama",
    )

    assert reset_payload == {
        "ollama": {
            "base_url": "http://localhost:11434",
            "timeout_seconds": 120,
        }
    }
    save_response = client.put(
        "/api/dashboard/settings/config",
        json=reset_payload,
    )

    assert save_response.status_code == 200
    assert save_response.json()["persisted_setting_ids"] == [
        "ollama.base_url",
        "ollama.timeout_seconds",
    ]
    by_id = _settings_by_id(save_response.json()["settings"])
    for setting_id in ("ollama.base_url", "ollama.timeout_seconds"):
        assert by_id[setting_id]["persisted_value"] == by_id[setting_id][
            "default_value"
        ]
        assert by_id[setting_id]["value"] != by_id[setting_id]["default_value"]
        assert by_id[setting_id]["differs_from_persisted"] is True
    assert runtime.ollama.base_url == "http://custom-ollama.internal:11434"
    assert runtime.ollama.timeout_seconds == 45


def test_global_default_reset_and_put_touch_only_managed_eligible_settings(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    configuration = {
        "server": {"host": "127.0.0.1", "port": 11605},
        "ollama": {
            "base_url": "http://custom-ollama.internal:11434",
            "timeout_seconds": 45,
            "future_connection_option": "preserve me",
        },
        "context": {
            "enabled": False,
            "warning_threshold_percent": 60,
            "compression_threshold_percent": 90,
            "keep_recent_messages": 12,
            "future_context_option": "preserve me",
        },
        "compression": {
            "enabled": False,
            "summarizer_model": "custom-summary:latest",
            "max_summary_tokens": 900,
        },
        "dashboard": {
            "title": "Custom dashboard",
            "refresh_interval_ms": 2500,
        },
        "models": {"custom-model": {"context_window_tokens": 49152}},
        "custom_future_category": {"nested": {"preserve": True}},
    }
    original = _write_config(config_path, configuration)
    runtime = Settings.model_validate(configuration)
    client = _settings_client(runtime, config_path=config_path)
    initial_snapshot = client.get("/api/dashboard/settings").json()
    initial_by_id = _settings_by_id(initial_snapshot)
    reset_payload = _default_reset_payload(initial_snapshot)
    runtime_reset_payload = _default_reset_payload(
        initial_snapshot,
        runtime_only=True,
    )
    reset_setting_ids = {
        f"{category}.{field_name}"
        for category, values in reset_payload.items()
        for field_name in values
    }

    runtime_reset_setting_ids = {
        f"{category}.{field_name}"
        for category, values in runtime_reset_payload.items()
        for field_name in values
    }

    reset_response = client.patch(
        "/api/dashboard/settings",
        json=runtime_reset_payload,
    )

    assert reset_response.status_code == 200
    assert reset_setting_ids == {
        setting_id
        for setting_id, setting in initial_by_id.items()
        if setting["reset_eligible"]
    }
    assert len(reset_setting_ids) == 10
    assert len(runtime_reset_setting_ids) == 8
    reset_by_id = _settings_by_id(reset_response.json())
    for setting_id in reset_setting_ids:
        if setting_id in runtime_reset_setting_ids:
            assert reset_by_id[setting_id]["value"] == initial_by_id[setting_id][
                "default_value"
            ]
        else:
            assert reset_by_id[setting_id]["value"] == initial_by_id[setting_id][
                "value"
            ]
    assert runtime.server.host == "127.0.0.1"
    assert runtime.server.port == 11605
    assert runtime.dashboard.title == "Custom dashboard"
    assert runtime.models == {"custom-model": {"context_window_tokens": 49152}}
    assert config_path.read_bytes() == original

    save_response = client.put(
        "/api/dashboard/settings/config",
        json=reset_payload,
    )

    assert save_response.status_code == 200
    assert save_response.json()["persisted_setting_ids"] == sorted(reset_setting_ids)
    saved_by_id = _settings_by_id(save_response.json()["settings"])
    for setting_id in reset_setting_ids:
        assert saved_by_id[setting_id]["persisted_value"] == initial_by_id[
            setting_id
        ]["default_value"]
        if setting_id in runtime_reset_setting_ids:
            assert saved_by_id[setting_id]["value"] == initial_by_id[setting_id][
                "default_value"
            ]
            assert saved_by_id[setting_id]["differs_from_persisted"] is False
        else:
            assert saved_by_id[setting_id]["value"] == initial_by_id[setting_id][
                "value"
            ]
            assert saved_by_id[setting_id]["differs_from_persisted"] is True

    persisted = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert persisted["server"] == configuration["server"]
    assert persisted["ollama"]["future_connection_option"] == "preserve me"
    assert persisted["context"]["future_context_option"] == "preserve me"
    assert persisted["dashboard"]["title"] == "Custom dashboard"
    assert persisted["models"] == configuration["models"]
    assert persisted["custom_future_category"] == configuration[
        "custom_future_category"
    ]

    restarted = load_config(config_path)
    for setting_id in reset_setting_ids:
        category, field_name = setting_id.split(".", maxsplit=1)
        assert getattr(getattr(restarted, category), field_name) == initial_by_id[
            setting_id
        ]["default_value"]
    assert restarted.dashboard.title == configuration["dashboard"]["title"]
    assert restarted.models == configuration["models"]


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({}, 400),
        ({"context": {}}, 400),
        ({"server": {"port": 11600}}, 422),
        ({"ollama": {"retry_count": 3}}, 422),
        ({"ollama": {"base_url": "ollama.internal:11434"}}, 422),
        ({"ollama": {"timeout_seconds": True}}, 422),
        ({"ollama": {"timeout_seconds": 30.0}}, 422),
        ({"ollama": {"timeout_seconds": "30"}}, 422),
        ({"ollama": {"timeout_seconds": 0}}, 422),
        ({"context": {"unknown_setting": 1}}, 422),
        ({"context": {"enabled": "false"}}, 422),
        ({"context": {"warning_threshold_percent": "70"}}, 422),
        ({"context": {"warning_threshold_percent": -1}}, 422),
        ({"context": {"compression_threshold_percent": 101}}, 422),
        ({"context": {"warning_threshold_percent": 85}}, 422),
        ({"context": False}, 422),
        ({"compression": []}, 422),
        ([], 422),
    ],
)
def test_dashboard_settings_config_put_returns_meaningful_validation_statuses(
    tmp_path: Path,
    payload: object,
    expected_status: int,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    client = _settings_client(config_path=config_path)

    response = client.put("/api/dashboard/settings/config", json=payload)

    assert response.status_code == expected_status
    assert "detail" in response.json()
    assert not config_path.exists()


def test_dashboard_settings_config_put_rejects_missing_and_malformed_json(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    client = _settings_client(config_path=config_path)

    missing = client.put("/api/dashboard/settings/config")
    malformed = client.put(
        "/api/dashboard/settings/config",
        content="{not-json",
        headers={"Content-Type": "application/json"},
    )

    assert missing.status_code == 422
    assert malformed.status_code == 422
    assert not config_path.exists()


def test_dashboard_settings_config_put_reports_malformed_existing_yaml_safely(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = b"context:\n  enabled: [\n"
    config_path.write_bytes(original)
    client = _settings_client(config_path=config_path)

    response = client.put(
        "/api/dashboard/settings/config",
        json={"context": {"enabled": False}},
    )

    assert response.status_code == 409
    assert "malformed YAML" in response.json()["detail"]
    assert str(config_path) not in response.text
    assert config_path.read_bytes() == original
    assert list(tmp_path.glob(".contextkeeper.yaml.*.tmp")) == []


def test_dashboard_settings_config_put_reports_atomic_replace_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_config(config_path, {"context": {"enabled": True}})
    app = create_app(Settings(), config_path=config_path)
    persistence = app.state.configuration_persistence

    def failed_replace(temporary_path: Path) -> None:
        raise PermissionError("read-only destination")

    monkeypatch.setattr(persistence, "_replace_configuration", failed_replace)
    client = TestClient(app)

    response = client.put(
        "/api/dashboard/settings/config",
        json={"context": {"enabled": False}},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "The configuration update could not replace the active file atomically."
    )
    assert str(config_path) not in response.text
    assert config_path.read_bytes() == original
    assert list(tmp_path.glob(".contextkeeper.yaml.*.tmp")) == []


def test_dashboard_settings_get_reports_persisted_read_failure_without_stack_trace(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text("context: [\n", encoding="utf-8")
    client = _settings_client(config_path=config_path)

    response = client.get("/api/dashboard/settings")

    assert response.status_code == 409
    assert "malformed YAML" in response.json()["detail"]
    assert str(config_path) not in response.text
    assert "Traceback" not in response.text


def test_dashboard_settings_patch_rejects_unavailable_persisted_state_before_runtime_mutation(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = b"context:\n  enabled: [\n"
    config_path.write_bytes(original)
    runtime = Settings(context={"enabled": True})
    client = _settings_client(runtime, config_path=config_path)

    response = client.patch(
        "/api/dashboard/settings",
        json={"context": {"enabled": False}},
    )

    assert response.status_code == 409
    assert "malformed YAML" in response.json()["detail"]
    assert runtime.context.enabled is True
    assert config_path.read_bytes() == original


def test_settings_get_and_patch_disk_reads_use_sync_threadpool_routes() -> None:
    router = create_dashboard_router(Settings())
    endpoints = {
        (route.path, method): route.endpoint
        for route in router.routes
        if hasattr(route, "endpoint")
        for method in getattr(route, "methods", set())
    }

    assert not inspect.iscoroutinefunction(
        endpoints[("/api/dashboard/settings", "GET")]
    )
    assert not inspect.iscoroutinefunction(
        endpoints[("/api/dashboard/settings", "PATCH")]
    )


def test_dashboard_settings_base_resource_unsupported_methods_remain_unchanged() -> None:
    client = _settings_client()

    for method in ("POST", "PUT", "DELETE"):
        response = client.request(method, "/api/dashboard/settings", json={})
        assert response.status_code == 405
        assert response.json()["detail"] == "Use PATCH to update runtime settings."


def test_dashboard_settings_config_resource_unsupported_methods_use_fastapi_405() -> None:
    client = _settings_client()

    for method in ("GET", "POST", "PATCH", "DELETE"):
        response = client.request(method, "/api/dashboard/settings/config", json={})
        assert response.status_code == 405
        assert response.headers["allow"] == "PUT"
