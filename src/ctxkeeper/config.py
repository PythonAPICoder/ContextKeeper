from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError


class AppConfig(BaseModel):
    name: str = "ContextKeeper"
    environment: str = "development"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 11500


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/contextkeeper.log"
    request_log_enabled: bool = True
    log_request_bodies: bool = False


class MetricsConfig(BaseModel):
    enabled: bool = True
    gpu_enabled: bool = True
    refresh_interval_seconds: int = 2


class DashboardConfig(BaseModel):
    enabled: bool = True
    title: str = "ContextKeeper Dashboard"
    refresh_interval_ms: int = 1000


class ContextConfig(BaseModel):
    enabled: bool = False
    default_context_window_tokens: int = 16384
    warning_threshold_percent: int = 75
    compression_threshold_percent: int = 85
    minimum_threshold_percent: int = 10
    keep_recent_messages: int = 8


class CompressionConfig(BaseModel):
    enabled: bool = False
    summarizer_model: str = "gpt-oss:20b"
    max_summary_tokens: int = 1200


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    models: dict[str, dict[str, int]] = Field(default_factory=dict)


class ConfigError(RuntimeError):
    """Raised when ContextKeeper configuration cannot be loaded."""


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _env_overrides() -> dict[str, Any]:
    env_override: dict[str, Any] = {}

    if host := os.getenv("CONTEXTKEEPER_HOST"):
        env_override.setdefault("server", {})["host"] = host
    if port := os.getenv("CONTEXTKEEPER_PORT"):
        env_override.setdefault("server", {})["port"] = port
    if url := os.getenv("CONTEXTKEEPER_OLLAMA_URL"):
        env_override.setdefault("ollama", {})["base_url"] = url
    if level := os.getenv("CONTEXTKEEPER_LOG_LEVEL"):
        env_override.setdefault("logging", {})["level"] = level

    return env_override


def load_config(config_path: str | Path = "contextkeeper.yaml") -> Settings:
    path = Path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
        except OSError as exc:
            raise ConfigError(f"Unable to read config file {path}: {exc}") from exc

        if not isinstance(loaded, dict):
            raise ConfigError(f"Config file {path} must contain a YAML mapping.")
        data = loaded

    try:
        return Settings.model_validate(_deep_merge(data, _env_overrides()))
    except ValueError as exc:
        raise ConfigError(f"Invalid ContextKeeper configuration: {exc}") from exc
    except ValidationError as exc:
        raise ConfigError(f"Invalid ContextKeeper configuration: {exc}") from exc
