from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from .branding import PRODUCT_NAME
from .resources import DEFAULT_CONFIG_NAME, resolve_config_path


class AppConfig(BaseModel):
    name: str = PRODUCT_NAME
    environment: str = "development"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 11500

    @field_validator("port")
    @classmethod
    def _validate_port(cls, value: int) -> int:
        if not 1 <= value <= 65535:
            raise ValueError("server.port must be between 1 and 65535.")
        return value


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ollama.base_url must not be empty.")
        if not value.startswith(("http://", "https://")):
            raise ValueError("ollama.base_url must start with http:// or https://.")
        return value

    @field_validator("timeout_seconds")
    @classmethod
    def _validate_timeout(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ollama.timeout_seconds must be greater than 0.")
        return value


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/contextkeeper.log"
    request_log_enabled: bool = True
    log_request_bodies: bool = False

    @field_validator("level")
    @classmethod
    def _validate_level(cls, value: str) -> str:
        allowed = {"OFF", "DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"}
        normalized = value.upper().strip()
        if normalized not in allowed:
            raise ValueError("logging.level must be one of OFF, DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
        return normalized


class MetricsConfig(BaseModel):
    enabled: bool = True
    gpu_enabled: bool = True
    refresh_interval_seconds: int = 2

    @field_validator("refresh_interval_seconds")
    @classmethod
    def _validate_refresh_interval(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("metrics.refresh_interval_seconds must be greater than 0.")
        return value


class DashboardConfig(BaseModel):
    enabled: bool = True
    title: str = "ContextKeeper Dashboard"
    refresh_interval_ms: int = 1000

    @field_validator("refresh_interval_ms")
    @classmethod
    def _validate_refresh_interval(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("dashboard.refresh_interval_ms must be greater than 0.")
        return value


class ContextConfig(BaseModel):
    enabled: bool = True
    default_context_window_tokens: int = 16384
    warning_threshold_percent: int = 75
    compression_threshold_percent: int = 85
    minimum_threshold_percent: int = 10
    keep_recent_messages: int = 8

    @field_validator(
        "warning_threshold_percent",
        "compression_threshold_percent",
        "minimum_threshold_percent",
    )
    @classmethod
    def _validate_threshold_percent(cls, value: int) -> int:
        if not 0 <= value <= 100:
            raise ValueError("context threshold percentages must be between 0 and 100.")
        return value

    @field_validator("default_context_window_tokens", "keep_recent_messages")
    @classmethod
    def _validate_positive_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("context numeric limits must be greater than 0.")
        return value

    @model_validator(mode="after")
    def _validate_threshold_order(self) -> ContextConfig:
        if self.minimum_threshold_percent > self.warning_threshold_percent:
            raise ValueError("context.minimum_threshold_percent must be less than or equal to warning_threshold_percent.")
        if self.warning_threshold_percent > self.compression_threshold_percent:
            raise ValueError("context.warning_threshold_percent must be less than or equal to compression_threshold_percent.")
        return self


class CompressionConfig(BaseModel):
    enabled: bool = True
    summarizer_model: str = "gpt-oss:20b"
    max_summary_tokens: int = 1200

    @field_validator("max_summary_tokens")
    @classmethod
    def _validate_max_summary_tokens(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("compression.max_summary_tokens must be greater than 0.")
        return value


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


def load_config(config_path: str | Path = DEFAULT_CONFIG_NAME) -> Settings:
    path = resolve_config_path(config_path)
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
        raise ConfigError(f"Invalid ContextKeeper configuration: {_format_validation_error(exc)}") from exc
    except ValidationError as exc:
        raise ConfigError(f"Invalid ContextKeeper configuration: {_format_validation_error(exc)}") from exc


def _format_validation_error(exc: ValueError | ValidationError) -> str:
    if isinstance(exc, ValidationError):
        messages: list[str] = []
        for error in exc.errors():
            location = ".".join(str(part) for part in error.get("loc", ()))
            message = str(error.get("msg", "Invalid value"))
            if message.startswith("Value error, "):
                message = message.removeprefix("Value error, ")
            messages.append(f"{location}: {message}" if location else message)
        return "; ".join(messages)
    return str(exc)
