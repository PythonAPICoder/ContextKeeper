from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import logging
from pathlib import Path
import stat
from threading import Barrier, Lock
import time
from typing import Any

import pytest
import yaml

from ctxkeeper.config import load_config
from ctxkeeper.dashboard import config_persistence, settings_snapshot
from ctxkeeper.dashboard.config_persistence import (
    ConfigurationPersistenceError,
    ConfigurationPersistenceService,
)


def _write_yaml(path: Path, data: dict[str, Any]) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = yaml.safe_dump(data, sort_keys=False)
    path.write_text(serialized, encoding="utf-8")
    return path.read_bytes()


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _temporary_candidates(path: Path) -> list[Path]:
    return list(path.parent.glob(f".{path.name}.*.tmp"))


def test_persist_one_setting_updates_only_requested_value(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(
        config_path,
        {
            "context": {
                "enabled": True,
                "warning_threshold_percent": 60,
                "compression_threshold_percent": 85,
            },
            "server": {"host": "127.0.0.1", "port": 11600},
        },
    )
    service = ConfigurationPersistenceService(config_path)

    result = service.persist({"context": {"warning_threshold_percent": 70}})

    assert result.persisted_setting_ids == ("context.warning_threshold_percent",)
    assert result.configuration_created is False
    assert result.persisted_settings.context.warning_threshold_percent == 70
    data = _read_yaml(config_path)
    assert data["context"] == {
        "enabled": True,
        "warning_threshold_percent": 70,
        "compression_threshold_percent": 85,
    }
    assert data["server"] == {"host": "127.0.0.1", "port": 11600}


def test_persist_multiple_settings_in_one_category(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(config_path, {"context": {"warning_threshold_percent": 60, "compression_threshold_percent": 85}})

    result = ConfigurationPersistenceService(config_path).persist(
        {"context": {"enabled": False, "keep_recent_messages": 14}}
    )

    assert result.persisted_setting_ids == (
        "context.enabled",
        "context.keep_recent_messages",
    )
    data = _read_yaml(config_path)
    assert data["context"]["enabled"] is False
    assert data["context"]["keep_recent_messages"] == 14
    assert data["context"]["warning_threshold_percent"] == 60


def test_persist_one_connection_endpoint_normalizes_only_requested_value(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(
        config_path,
        {
            "ollama": {
                "base_url": "http://old-ollama.internal:11434",
                "timeout_seconds": 240,
                "future_connection_option": "preserve",
            },
            "server": {"host": "127.0.0.1", "port": 11600},
            "custom_future_category": {"preserve": True},
        },
    )

    result = ConfigurationPersistenceService(config_path).persist(
        {"ollama": {"base_url": "https://new-ollama.internal/ollama///"}}
    )

    assert result.persisted_setting_ids == ("ollama.base_url",)
    assert (
        result.persisted_settings.ollama.base_url
        == "https://new-ollama.internal/ollama"
    )
    data = _read_yaml(config_path)
    assert data["ollama"] == {
        "base_url": "https://new-ollama.internal/ollama",
        "timeout_seconds": 240,
        "future_connection_option": "preserve",
    }
    assert data["server"] == {"host": "127.0.0.1", "port": 11600}
    assert data["custom_future_category"] == {"preserve": True}


def test_persist_both_connection_settings_and_reload_uses_saved_values(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(
        config_path,
        {
            "ollama": {
                "base_url": "http://old-ollama.internal:11434",
                "timeout_seconds": 120,
            }
        },
    )

    result = ConfigurationPersistenceService(config_path).persist(
        {
            "ollama": {
                "base_url": "http://192.168.1.50:11434/",
                "timeout_seconds": 30,
            }
        }
    )

    assert result.persisted_setting_ids == (
        "ollama.base_url",
        "ollama.timeout_seconds",
    )
    assert _read_yaml(config_path)["ollama"] == {
        "base_url": "http://192.168.1.50:11434",
        "timeout_seconds": 30,
    }
    restarted = load_config(config_path)
    assert restarted.ollama.base_url == "http://192.168.1.50:11434"
    assert restarted.ollama.timeout_seconds == 30


def test_persist_connection_timeout_updates_only_timeout(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(
        config_path,
        {
            "ollama": {
                "base_url": "http://ollama.internal:11434",
                "timeout_seconds": 120,
            },
            "logging": {"level": "DEBUG"},
        },
    )

    result = ConfigurationPersistenceService(config_path).persist(
        {"ollama": {"timeout_seconds": 45}}
    )

    assert result.persisted_setting_ids == ("ollama.timeout_seconds",)
    assert _read_yaml(config_path) == {
        "ollama": {
            "base_url": "http://ollama.internal:11434",
            "timeout_seconds": 45,
        },
        "logging": {"level": "DEBUG"},
    }


def test_persist_settings_across_multiple_categories(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(config_path, {})

    result = ConfigurationPersistenceService(config_path).persist(
        {
            "context": {"enabled": False},
            "compression": {"enabled": False, "max_summary_tokens": 800},
            "dashboard": {"refresh_interval_ms": 2500},
        }
    )

    assert result.persisted_setting_ids == (
        "compression.enabled",
        "compression.max_summary_tokens",
        "context.enabled",
        "dashboard.refresh_interval_ms",
    )
    data = _read_yaml(config_path)
    assert data["context"]["enabled"] is False
    assert data["compression"] == {"enabled": False, "max_summary_tokens": 800}
    assert data["dashboard"]["refresh_interval_ms"] == 2500


def test_persistence_preserves_unrelated_categories_and_values(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = {
        "app": {"name": "Custom ContextKeeper", "environment": "qa"},
        "server": {"host": "127.0.0.1", "port": 11605},
        "ollama": {"base_url": "http://ollama.local:11434", "timeout_seconds": 240},
        "logging": {"level": "DEBUG", "file": "logs/custom.log"},
        "custom_future_category": {"keep_me": [1, 2, 3]},
        "context": {"warning_threshold_percent": 65, "compression_threshold_percent": 85},
    }
    _write_yaml(config_path, original)

    ConfigurationPersistenceService(config_path).persist(
        {"context": {"keep_recent_messages": 12}}
    )

    data = _read_yaml(config_path)
    for category in ("app", "server", "ollama", "logging", "custom_future_category"):
        assert data[category] == original[category]
    assert data["context"]["warning_threshold_percent"] == 65
    assert data["context"]["compression_threshold_percent"] == 85
    assert data["context"]["keep_recent_messages"] == 12


def test_persistence_preserves_model_specific_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    models = {
        "gpt-oss:20b": {"context_window_tokens": 32768},
        "qwen2.5:32b": {"context_window_tokens": 65536},
    }
    _write_yaml(config_path, {"models": models, "compression": {"max_summary_tokens": 1200}})

    ConfigurationPersistenceService(config_path).persist(
        {"compression": {"max_summary_tokens": 900}}
    )

    assert _read_yaml(config_path)["models"] == models


@pytest.mark.parametrize(
    "payload",
    [
        {"server": {"port": 12000}},
        {"context": {"unknown_setting": 1}},
        {"context": {"minimum_threshold_percent": 20}},
    ],
)
def test_persistence_rejects_unknown_or_unexposed_fields(
    tmp_path: Path,
    payload: object,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


@pytest.mark.parametrize(
    "payload",
    [
        {"ollama": {"base_url": ""}},
        {"ollama": {"base_url": "ollama.internal:11434"}},
        {"ollama": {"base_url": "ftp://ollama.internal:11434"}},
        {"ollama": {"base_url": "http://user:secret@ollama.internal:11434"}},
        {"ollama": {"base_url": "http://ollama.internal:99999"}},
        {"ollama": {"base_url": "http://ollama.internal:11434?query=yes"}},
        {"ollama": {"base_url": "http://ollama.internal:11434#fragment"}},
        {"ollama": {"timeout_seconds": 0}},
        {"ollama": {"timeout_seconds": -1}},
        {"ollama": {"timeout_seconds": True}},
        {"ollama": {"timeout_seconds": 30.0}},
        {"ollama": {"timeout_seconds": "30"}},
    ],
)
def test_persistence_rejects_invalid_connection_candidate_without_writing(
    tmp_path: Path,
    payload: object,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(
        config_path,
        {
            "server": {"host": "0.0.0.0", "port": 11500},
            "ollama": {
                "base_url": "http://ollama.internal:11434",
                "timeout_seconds": 120,
            },
            "custom_future_category": {"preserve": True},
        },
    )

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert caught.value.code == "validation_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_persistence_rejects_obvious_connection_self_loop_without_writing(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(
        config_path,
        {
            "server": {"host": "0.0.0.0", "port": 11500},
            "ollama": {
                "base_url": "http://ollama.internal:11434",
                "timeout_seconds": 120,
            },
        },
    )

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(
            {"ollama": {"base_url": "http://localhost:11500"}}
        )

    assert caught.value.status_code == 422
    assert caught.value.code == "validation_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_persistence_uses_active_listener_for_self_loop_validation(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(
        config_path,
        {
            "server": {"host": "127.0.0.1", "port": 11500},
            "ollama": {
                "base_url": "http://ollama.internal:11434",
                "timeout_seconds": 120,
            },
        },
    )
    service = ConfigurationPersistenceService(
        config_path,
        listener_host="0.0.0.0",
        listener_port=11600,
    )

    with pytest.raises(ConfigurationPersistenceError) as caught:
        service.persist({"ollama": {"base_url": "http://localhost:11600"}})

    assert caught.value.status_code == 422
    assert caught.value.code == "validation_failed"
    assert config_path.read_bytes() == original


def test_persistence_rejects_ipv4_mapped_ipv6_active_listener_loop(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(
        config_path,
        {
            "server": {"host": "127.0.0.1", "port": 11600},
            "ollama": {"base_url": "http://active-ollama.internal:11434"},
        },
    )
    service = ConfigurationPersistenceService(
        config_path,
        listener_host="0.0.0.0",
        listener_port=11500,
    )

    with pytest.raises(ConfigurationPersistenceError) as exc_info:
        service.persist(
            {
                "ollama": {
                    "base_url": "http://[::ffff:127.0.0.1]:11500/api",
                }
            }
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.code == "validation_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_persistence_rejects_unapproved_ollama_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(
            {"ollama": {"retry_count": 3}}
        )

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original


def test_persistence_rejects_authoritative_non_persistable_setting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})
    metadata = settings_snapshot.dashboard_setting_metadata_by_id()
    metadata["context.enabled"] = replace(metadata["context.enabled"], persistable=False)
    monkeypatch.setattr(
        settings_snapshot,
        "dashboard_setting_metadata_by_id",
        lambda: metadata,
    )

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 422
    assert caught.value.code == "non_persistable_setting"
    assert config_path.read_bytes() == original


@pytest.mark.parametrize(
    "payload",
    [
        {"context": {"enabled": "false"}},
        {"context": {"enabled": 0}},
        {"compression": {"enabled": "yes"}},
    ],
)
def test_persistence_validates_booleans_strictly(tmp_path: Path, payload: object) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original


@pytest.mark.parametrize(
    "payload",
    [
        {"context": {"warning_threshold_percent": "70"}},
        {"context": {"keep_recent_messages": 8.5}},
        {"compression": {"max_summary_tokens": True}},
        {"dashboard": {"refresh_interval_ms": "1000"}},
    ],
)
def test_persistence_validates_integers_strictly(tmp_path: Path, payload: object) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original


@pytest.mark.parametrize(
    "payload",
    [
        {"context": {"warning_threshold_percent": -1}},
        {"context": {"compression_threshold_percent": 101}},
        {"context": {"keep_recent_messages": 0}},
        {"compression": {"max_summary_tokens": 0}},
        {"dashboard": {"refresh_interval_ms": 0}},
    ],
)
def test_persistence_enforces_minimum_and_maximum_values(tmp_path: Path, payload: object) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original


def test_persistence_enforces_cross_field_validation_against_disk_state(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(
        config_path,
        {"context": {"warning_threshold_percent": 60, "compression_threshold_percent": 80}},
    )

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(
            {"context": {"warning_threshold_percent": 80}}
        )

    assert caught.value.status_code == 422
    assert caught.value.code == "validation_failed"
    assert config_path.read_bytes() == original


@pytest.mark.parametrize("payload", [{}, {"context": {}}, {"compression": {}, "dashboard": {}}])
def test_persistence_rejects_empty_updates(tmp_path: Path, payload: object) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 400
    assert caught.value.code == "empty_request"
    assert config_path.read_bytes() == original


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "context",
        {"context": False},
        {"context": []},
        {"compression": "enabled"},
        {"dashboard": None},
    ],
)
def test_persistence_rejects_malformed_payload_shapes(tmp_path: Path, payload: object) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist(payload)

    assert caught.value.status_code == 422
    assert config_path.read_bytes() == original


def test_persistence_rejects_malformed_existing_yaml_without_modification(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = b"context:\n  enabled: true\n  broken: [\n"
    config_path.write_bytes(original)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 409
    assert caught.value.code == "invalid_configuration_yaml"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_persistence_rejects_non_mapping_existing_yaml_without_modification(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = b"- context\n- compression\n"
    config_path.write_bytes(original)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 409
    assert caught.value.code == "invalid_configuration_shape"
    assert config_path.read_bytes() == original


@pytest.mark.parametrize("original", [b"false\n", b"0\n", b"''\n"])
def test_persistence_rejects_falsy_non_mapping_yaml_roots(
    tmp_path: Path,
    original: bytes,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_bytes(original)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 409
    assert caught.value.code == "invalid_configuration_shape"
    assert config_path.read_bytes() == original


def test_missing_configuration_is_created_with_parent_directories(tmp_path: Path) -> None:
    config_path = tmp_path / "nested" / "configuration" / "contextkeeper.yaml"

    result = ConfigurationPersistenceService(config_path).persist(
        {"context": {"warning_threshold_percent": 70}}
    )

    assert result.configuration_created is True
    assert result.persisted_settings.context.warning_threshold_percent == 70
    assert _read_yaml(config_path) == {"context": {"warning_threshold_percent": 70}}
    assert _temporary_candidates(config_path) == []


def test_configuration_read_permission_failure_is_clear(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {})
    original_read_bytes = Path.read_bytes

    def denied_read(path: Path) -> bytes:
        if path == config_path:
            raise PermissionError("denied")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", denied_read)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 500
    assert caught.value.code == "configuration_read_failed"
    assert original_read_bytes(config_path) == original


def test_read_only_destination_is_rejected_without_modification(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})
    config_path.chmod(stat.S_IREAD)

    try:
        with pytest.raises(ConfigurationPersistenceError) as caught:
            ConfigurationPersistenceService(config_path).persist(
                {"context": {"enabled": False}}
            )
    finally:
        config_path.chmod(stat.S_IREAD | stat.S_IWRITE)

    assert caught.value.status_code == 500
    assert caught.value.code == "configuration_read_only"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_temporary_file_creation_permission_failure_preserves_original(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})

    def denied_mkstemp(**kwargs: object) -> tuple[int, str]:
        raise PermissionError("read-only directory")

    monkeypatch.setattr(config_persistence.tempfile, "mkstemp", denied_mkstemp)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        ConfigurationPersistenceService(config_path).persist({"context": {"enabled": False}})

    assert caught.value.status_code == 500
    assert caught.value.code == "temporary_write_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_temporary_write_failure_preserves_original_and_cleans_up(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})
    service = ConfigurationPersistenceService(config_path)

    def failed_write(descriptor: int, serialized: str) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(service, "_write_temporary_candidate", failed_write)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        service.persist({"context": {"enabled": False}})

    assert caught.value.status_code == 500
    assert caught.value.code == "temporary_write_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_invalid_serialized_candidate_preserves_original(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})
    service = ConfigurationPersistenceService(config_path)
    monkeypatch.setattr(service, "_serialize_candidate", lambda candidate: "context: [\n")

    with pytest.raises(ConfigurationPersistenceError) as caught:
        service.persist({"context": {"enabled": False}})

    assert caught.value.status_code == 500
    assert caught.value.code == "invalid_configuration_yaml"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_atomic_replace_failure_preserves_original_and_cleans_up(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    original = _write_yaml(config_path, {"context": {"enabled": True}})
    service = ConfigurationPersistenceService(config_path)

    def failed_replace(temporary_path: Path) -> None:
        raise PermissionError("destination is read-only")

    monkeypatch.setattr(service, "_replace_configuration", failed_replace)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        service.persist({"context": {"enabled": False}})

    assert caught.value.status_code == 500
    assert caught.value.code == "atomic_replace_failed"
    assert config_path.read_bytes() == original
    assert _temporary_candidates(config_path) == []


def test_cleanup_failure_is_logged_without_raising(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class UnremovableTemporaryPath:
        def unlink(self, *, missing_ok: bool) -> None:
            raise PermissionError("cleanup denied")

    caplog.set_level(logging.WARNING, logger="ctxkeeper.dashboard.settings.persistence")

    ConfigurationPersistenceService._cleanup_temporary_file(  # type: ignore[arg-type]
        UnremovableTemporaryPath()
    )

    assert "temporary-file cleanup failed" in caplog.text


def test_stale_external_write_is_not_overwritten_and_temp_is_cleaned(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(config_path, {"context": {"enabled": True}})
    service = ConfigurationPersistenceService(config_path)
    original_writer = service._write_temporary_candidate
    external_data = {
        "context": {"enabled": True},
        "external_change": {"preserve": True},
    }

    def write_then_change_destination(descriptor: int, serialized: str) -> None:
        original_writer(descriptor, serialized)
        _write_yaml(config_path, external_data)

    monkeypatch.setattr(service, "_write_temporary_candidate", write_then_change_destination)

    with pytest.raises(ConfigurationPersistenceError) as caught:
        service.persist({"context": {"enabled": False}})

    assert caught.value.status_code == 409
    assert caught.value.code == "stale_configuration"
    assert _read_yaml(config_path) == external_data
    assert _temporary_candidates(config_path) == []


def test_concurrent_in_process_writes_are_serialized_without_lost_updates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    _write_yaml(config_path, {})
    first_service = ConfigurationPersistenceService(config_path)
    second_service = ConfigurationPersistenceService(config_path)
    original_writer = ConfigurationPersistenceService._write_temporary_candidate
    activity_lock = Lock()
    active_writers = 0
    maximum_active_writers = 0

    def observed_writer(descriptor: int, serialized: str) -> None:
        nonlocal active_writers, maximum_active_writers
        with activity_lock:
            active_writers += 1
            maximum_active_writers = max(maximum_active_writers, active_writers)
        try:
            time.sleep(0.025)
            original_writer(descriptor, serialized)
        finally:
            with activity_lock:
                active_writers -= 1

    monkeypatch.setattr(
        ConfigurationPersistenceService,
        "_write_temporary_candidate",
        staticmethod(observed_writer),
    )
    start = Barrier(3)

    def persist_after_barrier(
        service: ConfigurationPersistenceService,
        payload: dict[str, dict[str, bool]],
    ) -> None:
        start.wait()
        service.persist(payload)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            persist_after_barrier,
            first_service,
            {"context": {"enabled": False}},
        )
        second = executor.submit(
            persist_after_barrier,
            second_service,
            {"compression": {"enabled": False}},
        )
        start.wait()
        first.result(timeout=5)
        second.result(timeout=5)

    assert maximum_active_writers == 1
    data = _read_yaml(config_path)
    assert data["context"]["enabled"] is False
    assert data["compression"]["enabled"] is False
    assert _temporary_candidates(config_path) == []
