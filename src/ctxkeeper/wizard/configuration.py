"""Configuration generation helpers for the first-run wizard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..config import Settings


@dataclass(frozen=True)
class WizardConfig:
    """User-selected values collected by the configuration wizard."""

    ollama_base_url: str = "http://localhost:11434"
    proxy_host: str = "0.0.0.0"
    proxy_port: int = 11500
    dashboard_enabled: bool = True
    context_enabled: bool = False
    compression_enabled: bool = False
    logging_level: str = "INFO"


def build_settings(config: WizardConfig) -> Settings:
    """Build validated project settings from wizard answers."""
    return Settings(
        server={
            "host": config.proxy_host,
            "port": config.proxy_port,
        },
        ollama={
            "base_url": config.ollama_base_url,
        },
        dashboard={
            "enabled": config.dashboard_enabled,
        },
        context={
            "enabled": config.context_enabled,
        },
        compression={
            "enabled": config.compression_enabled,
        },
        logging={
            "level": config.logging_level,
        },
    )


def settings_to_yaml(settings: Settings) -> str:
    """Serialize settings into a valid contextkeeper.yaml document."""
    data = settings.model_dump(mode="json")
    return yaml.safe_dump(data, sort_keys=False)


def write_config_yaml(path: str | Path, config: WizardConfig) -> Path:
    """Write a validated contextkeeper.yaml file and return its path."""
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(settings_to_yaml(build_settings(config)), encoding="utf-8")
    return resolved_path
