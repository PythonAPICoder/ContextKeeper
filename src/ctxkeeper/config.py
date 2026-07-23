from __future__ import annotations

from ipaddress import IPv6Address, ip_address
import os
from pathlib import Path
import posixpath
import re
from typing import Any
from urllib.parse import unquote, urlsplit, urlunsplit

import yaml
from pydantic import (
    BaseModel,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)

from .branding import PRODUCT_NAME
from .resources import DEFAULT_CONFIG_NAME, resolve_config_path

_HOST_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_INVALID_PERCENT_ESCAPE_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")


def normalize_ollama_base_url(value: str) -> str:
    """Validate and normalize one absolute HTTP(S) Ollama base URL."""

    normalized_input = value.strip()
    if not normalized_input:
        raise ValueError("ollama.base_url must not be empty.")
    try:
        normalized_input.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("ollama.base_url must contain valid Unicode characters.") from exc
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in normalized_input
    ):
        raise ValueError("ollama.base_url must not contain whitespace or control characters.")
    if "\\" in normalized_input:
        raise ValueError("ollama.base_url must not contain backslashes.")
    if _INVALID_PERCENT_ESCAPE_PATTERN.search(normalized_input):
        raise ValueError("ollama.base_url contains an invalid percent escape.")

    try:
        parsed = urlsplit(normalized_input)
    except ValueError as exc:
        raise ValueError("ollama.base_url must be a valid absolute URL.") from exc

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise ValueError("ollama.base_url must use http:// or https://.")
    if not parsed.netloc:
        raise ValueError("ollama.base_url must include a hostname or IP address.")
    if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
        raise ValueError("ollama.base_url must not include a username or password.")
    if parsed.query or "?" in normalized_input:
        raise ValueError("ollama.base_url must not include a query string.")
    if parsed.fragment or "#" in normalized_input:
        raise ValueError("ollama.base_url must not include a fragment.")

    try:
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("ollama.base_url must include a valid hostname and port.") from exc
    if not hostname:
        raise ValueError("ollama.base_url must include a hostname or IP address.")
    if parsed.netloc.endswith(":"):
        raise ValueError("ollama.base_url must include a valid port when a port separator is supplied.")
    if port == 0:
        raise ValueError("ollama.base_url port must be between 1 and 65535.")

    normalized_host, is_ipv6 = _normalize_url_host(hostname)
    if parsed.netloc.startswith("[") and not is_ipv6:
        raise ValueError("ollama.base_url bracketed hosts must be valid IPv6 addresses.")
    authority = f"[{normalized_host}]" if is_ipv6 else normalized_host
    if port is not None:
        authority = f"{authority}:{port}"

    path = parsed.path.rstrip("/")
    return urlunsplit((scheme, authority, path, "", ""))


def validate_ollama_timeout_seconds(value: int) -> int:
    """Validate the authoritative positive Ollama request timeout."""

    if value <= 0:
        raise ValueError("ollama.timeout_seconds must be greater than 0.")
    return value


def validate_ollama_not_self_proxy(
    base_url: str,
    *,
    listener_host: str,
    listener_port: int,
) -> None:
    """Reject deterministic direct loops back into ContextKeeper's proxy."""

    parsed = urlsplit(base_url)
    if parsed.scheme.lower() != "http":
        return
    decoded_path = unquote(parsed.path)
    normalized_path = posixpath.normpath(decoded_path or "/")
    reaches_proxy_route = (
        normalized_path == "/"
        or normalized_path == "/api"
        or normalized_path.startswith("/api/")
        or normalized_path == "/v1"
        or normalized_path.startswith("/v1/")
    )
    if not reaches_proxy_route:
        return
    endpoint_host = _normalize_host_alias(parsed.hostname or "")
    if not _endpoint_matches_listener_alias(endpoint_host, listener_host):
        return
    endpoint_port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    if endpoint_port == listener_port:
        raise ValueError(
            "ollama.base_url must not point directly to ContextKeeper's own listener."
        )


def _normalize_url_host(hostname: str) -> tuple[str, bool]:
    try:
        address = ip_address(hostname)
    except ValueError:
        if ":" in hostname or ("." in hostname and hostname.replace(".", "").isdigit()):
            raise ValueError("ollama.base_url must include a valid hostname or IP address.")
        trailing_dot = hostname.endswith(".")
        hostname_without_dot = hostname[:-1] if trailing_dot else hostname
        try:
            ascii_hostname = hostname_without_dot.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("ollama.base_url must include a valid hostname or IP address.") from exc
        if len(ascii_hostname) > 253:
            raise ValueError("ollama.base_url hostname is too long.")
        labels = ascii_hostname.split(".")
        if not labels or any(not _HOST_LABEL_PATTERN.fullmatch(label) for label in labels):
            raise ValueError("ollama.base_url must include a valid hostname or IP address.")
        normalized = ascii_hostname.lower()
        return (f"{normalized}." if trailing_dot else normalized), False
    return str(address), isinstance(address, IPv6Address)


def _normalize_host_alias(hostname: str) -> str:
    normalized = hostname.strip().strip("[]").rstrip(".").lower()
    try:
        address = ip_address(normalized)
    except ValueError:
        try:
            return normalized.encode("idna").decode("ascii")
        except UnicodeError:
            return normalized
    if isinstance(address, IPv6Address):
        scope_id = address.scope_id
        unscoped_address = IPv6Address(int(address))
        if unscoped_address.ipv4_mapped is not None:
            return str(unscoped_address.ipv4_mapped)
        if unscoped_address.is_loopback or unscoped_address.is_unspecified:
            return str(unscoped_address)
        if scope_id is not None:
            return f"{unscoped_address}%{scope_id}"
        return str(unscoped_address)
    return str(address)


def _listener_host_aliases(listener_host: str) -> set[str]:
    normalized = _normalize_host_alias(listener_host)
    aliases = {normalized}
    if normalized == "0.0.0.0":
        aliases.update({"127.0.0.1", "localhost"})
    elif normalized == "::":
        aliases.update({"::1", "localhost"})
    elif normalized == "127.0.0.1":
        aliases.add("localhost")
    elif normalized == "::1":
        aliases.add("localhost")
    elif normalized == "localhost":
        aliases.update({"127.0.0.1", "::1"})
    return aliases


def _endpoint_matches_listener_alias(
    endpoint_host: str,
    listener_host: str,
) -> bool:
    if endpoint_host in _listener_host_aliases(listener_host):
        return True
    if _normalize_host_alias(listener_host) != "0.0.0.0":
        return False
    try:
        address = ip_address(endpoint_host)
    except ValueError:
        return False
    return address.version == 4 and address.is_loopback


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
    base_url: StrictStr = "http://localhost:11434"
    timeout_seconds: StrictInt = 120

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        return normalize_ollama_base_url(value)

    @field_validator("timeout_seconds")
    @classmethod
    def _validate_timeout(cls, value: int) -> int:
        return validate_ollama_timeout_seconds(value)


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
    default_context_window_tokens: int = 32768
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

    @model_validator(mode="after")
    def _validate_ollama_is_not_listener(self) -> Settings:
        try:
            validate_ollama_not_self_proxy(
                self.ollama.base_url,
                listener_host=self.server.host,
                listener_port=self.server.port,
            )
        except ValueError as exc:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                [
                    {
                        "type": "value_error",
                        "loc": ("ollama", "base_url"),
                        "input": self.ollama.base_url,
                        "ctx": {"error": exc},
                    }
                ],
            ) from exc
        return self


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
