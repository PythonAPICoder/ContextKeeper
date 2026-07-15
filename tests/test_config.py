from pathlib import Path

import pytest

from ctxkeeper.config import ConfigError, Settings, load_config


def test_default_settings_load() -> None:
    settings = Settings()
    assert settings.app.name == "ContextKeeper"
    assert settings.server.port == 11500
    assert settings.context.enabled is True
    assert settings.compression.enabled is True


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


def test_context_and_compression_can_be_disabled_by_config(tmp_path: Path) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text(
        """
context:
  enabled: false
compression:
  enabled: false
""",
        encoding="utf-8",
    )

    settings = load_config(config_path)

    assert settings.context.enabled is False
    assert settings.compression.enabled is False


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


def test_load_config_uses_frozen_resource_resolution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exe_dir = tmp_path / "dist"
    exe_dir.mkdir()
    config_path = exe_dir / "contextkeeper.yaml"
    config_path.write_text(
        """
server:
  host: "127.0.0.1"
  port: 11675
""",
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(exe_dir / "ContextKeeper.exe"))

    settings = load_config()

    assert settings.server.host == "127.0.0.1"
    assert settings.server.port == 11675


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        ("server:\n  port: 70000\n", "server.port: server.port must be between 1 and 65535."),
        ("dashboard:\n  refresh_interval_ms: 0\n", "dashboard.refresh_interval_ms: dashboard.refresh_interval_ms must be greater than 0."),
        ("context:\n  warning_threshold_percent: 90\n  compression_threshold_percent: 80\n", "context: context.warning_threshold_percent must be less than or equal to compression_threshold_percent."),
        ("context:\n  warning_threshold_percent: 101\n", "context.warning_threshold_percent: context threshold percentages must be between 0 and 100."),
        ("ollama:\n  base_url: ollama.local:11434\n", "ollama.base_url: ollama.base_url must start with http:// or https://."),
        ("logging:\n  level: TRACE\n", "logging.level: logging.level must be one of OFF, DEBUG, INFO, WARNING, ERROR, or CRITICAL."),
    ],
)
def test_invalid_config_values_raise_actionable_errors(
    tmp_path: Path,
    yaml_text: str,
    message: str,
) -> None:
    config_path = tmp_path / "contextkeeper.yaml"
    config_path.write_text(yaml_text, encoding="utf-8")

    with pytest.raises(ConfigError, match=message.replace(".", r"\.")):
        load_config(config_path)
