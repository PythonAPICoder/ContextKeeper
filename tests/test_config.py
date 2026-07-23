from pathlib import Path

import pytest

from ctxkeeper.config import ConfigError, Settings, load_config


def test_default_settings_load() -> None:
    settings = Settings()
    assert settings.app.name == "ContextKeeper"
    assert settings.server.port == 11500
    assert settings.ollama.base_url == "http://localhost:11434"
    assert settings.ollama.timeout_seconds == 120
    assert settings.context.enabled is True
    assert settings.context.default_context_window_tokens == 32768
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
        ("ollama:\n  base_url: ollama.local:11434\n", "ollama.base_url: ollama.base_url must use http:// or https://."),
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


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        ("http://localhost:11434", "http://localhost:11434"),
        ("http://ollama.internal:11434", "http://ollama.internal:11434"),
        ("http://192.168.1.50:11434", "http://192.168.1.50:11434"),
        ("http://[2001:db8::10]:11434", "http://[2001:db8::10]:11434"),
        ("http://ollama.internal", "http://ollama.internal"),
        ("https://ollama.example.internal", "https://ollama.example.internal"),
        (
            "https://ollama.example.internal:11434/ollama",
            "https://ollama.example.internal:11434/ollama",
        ),
        (
            "https://ollama.example.internal/ollama///",
            "https://ollama.example.internal/ollama",
        ),
        (
            "https://ollama.example.internal/ollama%20server/",
            "https://ollama.example.internal/ollama%20server",
        ),
        ("  http://ollama.internal:11434/  ", "http://ollama.internal:11434"),
    ],
)
def test_ollama_base_url_accepts_and_normalizes_supported_endpoints(
    base_url: str,
    expected: str,
) -> None:
    settings = Settings(ollama={"base_url": base_url})

    assert settings.ollama.base_url == expected


@pytest.mark.parametrize(
    "base_url",
    [
        "",
        "   ",
        "localhost:11434",
        "/ollama",
        "ftp://ollama.internal:11434",
        "http://user@ollama.internal:11434",
        "http://user:password@ollama.internal:11434",
        "http://ollama.internal:abc",
        "http://ollama.internal:0",
        "http://ollama.internal:65536",
        "http://ollama.internal:11434?model=test",
        "http://ollama.internal:11434#status",
        "http://",
        "http://:11434",
        "http://bad host:11434",
        "http://bad..host:11434",
        "http://[not-an-ipv6-address]:11434",
        "http://[v1.fe80]:11434",
        "http://ollama.internal/%",
        "http://ollama.internal/%zz",
        "http://ollama.internal/\\api",
        "http://ollama.internal/\ud800",
    ],
)
def test_ollama_base_url_rejects_invalid_or_unsafe_endpoints(
    base_url: str,
) -> None:
    with pytest.raises(ValueError):
        Settings(ollama={"base_url": base_url})


@pytest.mark.parametrize(
    ("listener_host", "candidate_url"),
    [
        ("0.0.0.0", "http://localhost:11500"),
        ("0.0.0.0", "http://127.0.0.1:11500/"),
        ("0.0.0.0", "http://127.0.0.2:11500/api"),
        ("127.0.0.1", "http://localhost:11500"),
        ("localhost", "http://127.0.0.1:11500/api"),
        ("localhost", "http://[::1]:11500/v1"),
        ("0.0.0.0", "http://[::ffff:127.0.0.1]:11500"),
        ("127.0.0.1", "http://[::ffff:7f00:1]:11500/api/version"),
        ("::", "http://[::1%251]:11500"),
        ("::1", "http://[::1%25loopback]:11500/api"),
        ("0.0.0.0", "http://[::ffff:127.0.0.2%251]:11500/v1"),
        ("fe80::1%253", "http://[fe80::1%253]:11500/api"),
        ("tést.internal", "http://xn--tst-bma.internal:11500/api"),
        ("localhost", "http://127.0.0.1:11500/%61pi"),
        ("localhost", "http://127.0.0.1:11500/api%2Fnested"),
    ],
)
def test_ollama_base_url_rejects_obvious_contextkeeper_self_proxy_loop(
    listener_host: str,
    candidate_url: str,
) -> None:
    with pytest.raises(ValueError, match="ollama.base_url"):
        Settings(
            server={"host": listener_host, "port": 11500},
            ollama={"base_url": candidate_url},
        )


@pytest.mark.parametrize(
    "candidate_url",
    [
        "http://localhost:11434",
        "http://localhost:11500/ollama",
        "http://remote-host:11500",
        "https://localhost:11500/ollama",
    ],
)
def test_ollama_base_url_self_loop_check_remains_narrow(
    candidate_url: str,
) -> None:
    settings = Settings(
        server={"host": "0.0.0.0", "port": 11500},
        ollama={"base_url": candidate_url},
    )

    assert settings.ollama.base_url == candidate_url


def test_ollama_self_loop_check_preserves_distinct_ipv6_link_local_scopes() -> None:
    settings = Settings(
        server={"host": "fe80::1%3", "port": 11500},
        ollama={"base_url": "http://[fe80::1%253]:11500/api"},
    )

    assert settings.ollama.base_url == "http://[fe80::1%253]:11500/api"


@pytest.mark.parametrize("timeout_seconds", [1, 120, 2**31])
def test_ollama_timeout_accepts_positive_strict_integers(
    timeout_seconds: int,
) -> None:
    settings = Settings(ollama={"timeout_seconds": timeout_seconds})

    assert settings.ollama.timeout_seconds == timeout_seconds


@pytest.mark.parametrize(
    "timeout_seconds",
    [0, -1, True, False, 1.0, 1.5, "1", "120", None],
)
def test_ollama_timeout_rejects_nonpositive_and_nonstrict_values(
    timeout_seconds: object,
) -> None:
    with pytest.raises(ValueError):
        Settings(ollama={"timeout_seconds": timeout_seconds})
