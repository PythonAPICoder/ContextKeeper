from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


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


class ContextConfig(BaseModel):
    enabled: bool = False
    default_context_window_tokens: int = 16384
    warning_threshold_percent: int = 75
    compression_threshold_percent: int = 85
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


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(config_path: str | Path = "contextkeeper.yaml") -> Settings:
    path = Path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

    env_override: dict[str, Any] = {
        "server": {},
        "ollama": {},
        "logging": {},
    }

    if host := os.getenv("CONTEXTKEEPER_HOST"):
        env_override["server"]["host"] = host
    if port := os.getenv("CONTEXTKEEPER_PORT"):
        env_override["server"]["port"] = int(port)
    if url := os.getenv("CONTEXTKEEPER_OLLAMA_URL"):
        env_override["ollama"]["base_url"] = url
    if level := os.getenv("CONTEXTKEEPER_LOG_LEVEL"):
        env_override["logging"]["level"] = level

    env_override = {k: v for k, v in env_override.items() if v}
    return Settings.model_validate(_deep_merge(data, env_override))
