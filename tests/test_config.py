from pathlib import Path

import pytest

from ctxkeeper.config import ConfigError, Settings, load_config


def test_default_settings_load() -> None:
    settings = Settings()
    assert settings.app.name == "ContextKeeper"
    assert settings.server.port == 11500


def test_load_config_from_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text(
        """
server:
  host: "127.0.0.1"
  port: 11600
ollama:
  base_url: "http://ollama.local:11434"
logging:
  level: "DEBUG"
  file: "logs/test.log"
context:
  compression_threshold_percent: 80
models:
  gpt-oss:20b:
    context_window_tokens: 32768
""",
        encoding="utf-8",
    )

    settings = load_config(config_path)

    assert settings.server.host == "127.0.0.1"
    assert settings.server.port == 11600
    assert settings.ollama.base_url == "http://ollama.local:11434"
    assert settings.logging.level == "DEBUG"
    assert settings.context.compression_threshold_percent == 80
    assert settings.models["gpt-oss:20b"]["context_window_tokens"] == 32768


def test_environment_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text(
        """
server:
  host: "0.0.0.0"
  port: 11500
ollama:
  base_url: "http://localhost:11434"
logging:
  level: "INFO"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTEXTKEEPER_HOST", "127.0.0.1")
    monkeypatch.setenv("CONTEXTKEEPER_PORT", "11601")
    monkeypatch.setenv("CONTEXTKEEPER_OLLAMA_URL", "http://192.168.1.10:11434")
    monkeypatch.setenv("CONTEXTKEEPER_LOG_LEVEL", "WARNING")

    settings = load_config(config_path)

    assert settings.server.host == "127.0.0.1"
    assert settings.server.port == 11601
    assert settings.ollama.base_url == "http://192.168.1.10:11434"
    assert settings.logging.level == "WARNING"


def test_invalid_config_raises_clear_error(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="must contain a YAML mapping"):
        load_config(config_path)
