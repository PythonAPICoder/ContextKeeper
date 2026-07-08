from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ctxkeeper.config import load_config
from ctxkeeper.wizard.configuration import WizardConfig, build_settings, settings_to_yaml, write_config_yaml
from ctxkeeper.wizard.ui import prompt_for_config


def test_settings_to_yaml_generates_valid_existing_schema() -> None:
    settings = build_settings(
        WizardConfig(
            ollama_base_url="http://ollama.local:11434",
            proxy_host="127.0.0.1",
            proxy_port=11600,
            dashboard_enabled=False,
            context_enabled=True,
            compression_enabled=True,
            logging_level="DEBUG",
        )
    )

    data = yaml.safe_load(settings_to_yaml(settings))

    assert data["ollama"]["base_url"] == "http://ollama.local:11434"
    assert data["server"]["host"] == "127.0.0.1"
    assert data["server"]["port"] == 11600
    assert data["dashboard"]["enabled"] is False
    assert data["context"]["enabled"] is True
    assert data["compression"]["enabled"] is True
    assert data["logging"]["level"] == "DEBUG"


def test_write_config_yaml_can_be_loaded_by_existing_loader(tmp_path: Path) -> None:
    config_path = write_config_yaml(
        tmp_path / "contextkeeper.yaml",
        WizardConfig(proxy_port=11601, logging_level="WARNING"),
    )

    settings = load_config(config_path)

    assert settings.server.port == 11601
    assert settings.logging.level == "WARNING"
    assert settings.ollama.base_url == "http://localhost:11434"


def test_prompt_for_config_accepts_defaults() -> None:
    answers = iter(["", "", "", "", "", "", ""])

    config = prompt_for_config(input_func=lambda prompt: next(answers), output_func=lambda message: None)

    assert config == WizardConfig()


def test_prompt_for_config_collects_custom_values() -> None:
    answers = iter(
        [
            "http://192.168.1.10:11434",
            "127.0.0.1",
            "11602",
            "no",
            "yes",
            "true",
            "error",
        ]
    )

    config = prompt_for_config(input_func=lambda prompt: next(answers), output_func=lambda message: None)

    assert config.ollama_base_url == "http://192.168.1.10:11434"
    assert config.proxy_host == "127.0.0.1"
    assert config.proxy_port == 11602
    assert config.dashboard_enabled is False
    assert config.context_enabled is True
    assert config.compression_enabled is True
    assert config.logging_level == "ERROR"


def test_prompt_for_config_reprompts_invalid_values() -> None:
    answers = iter(["", "", "abc", "-1", "11501", "maybe", "true", "later", "false", "off", "trace", "INFO"])
    messages: list[str] = []

    config = prompt_for_config(input_func=lambda prompt: next(answers), output_func=messages.append)

    assert config.proxy_port == 11501
    assert config.dashboard_enabled is True
    assert config.context_enabled is False
    assert config.compression_enabled is False
    assert config.logging_level == "INFO"
    assert "Please enter a valid integer." in messages
    assert "Please enter a value greater than zero." in messages
    assert "Please enter true or false." in messages
    assert "Please enter one of: DEBUG, INFO, WARNING, ERROR, CRITICAL, OFF." in messages


def test_build_settings_validates_port() -> None:
    with pytest.raises(ValueError):
        build_settings(WizardConfig(proxy_port="not-an-int"))  # type: ignore[arg-type]
