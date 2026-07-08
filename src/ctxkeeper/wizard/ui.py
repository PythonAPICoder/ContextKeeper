"""Console UI for the ContextKeeper configuration wizard."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .configuration import WizardConfig, write_config_yaml

InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]

_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "OFF"}


def run_configuration_wizard(
    config_path: str | Path,
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> Path:
    """Prompt for configuration values and write contextkeeper.yaml."""
    output_func("ContextKeeper configuration wizard")
    output_func("Press Enter to accept the default shown in brackets.")
    config = prompt_for_config(input_func=input_func, output_func=output_func)
    written_path = write_config_yaml(config_path, config)
    output_func(f"Wrote configuration to {written_path}")
    return written_path


def prompt_for_config(
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> WizardConfig:
    """Collect wizard values from a console input function."""
    defaults = WizardConfig()
    return WizardConfig(
        ollama_base_url=_prompt_text(
            "Ollama Server URL",
            defaults.ollama_base_url,
            input_func=input_func,
        ),
        proxy_host=_prompt_text(
            "Proxy Host",
            defaults.proxy_host,
            input_func=input_func,
        ),
        proxy_port=_prompt_int(
            "Proxy Port",
            defaults.proxy_port,
            input_func=input_func,
            output_func=output_func,
        ),
        dashboard_enabled=_prompt_bool(
            "Enable Dashboard",
            defaults.dashboard_enabled,
            input_func=input_func,
            output_func=output_func,
        ),
        context_enabled=_prompt_bool(
            "Enable Context Engine",
            defaults.context_enabled,
            input_func=input_func,
            output_func=output_func,
        ),
        compression_enabled=_prompt_bool(
            "Enable Compression",
            defaults.compression_enabled,
            input_func=input_func,
            output_func=output_func,
        ),
        logging_level=_prompt_logging_level(
            "Logging Level",
            defaults.logging_level,
            input_func=input_func,
            output_func=output_func,
        ),
    )


def _prompt_text(label: str, default: str, *, input_func: InputFunc) -> str:
    value = input_func(f"{label} [{default}]: ").strip()
    return value or default


def _prompt_int(
    label: str,
    default: int,
    *,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> int:
    while True:
        value = input_func(f"{label} [{default}]: ").strip()
        if not value:
            return default
        try:
            parsed = int(value)
        except ValueError:
            output_func("Please enter a valid integer.")
            continue
        if parsed <= 0:
            output_func("Please enter a value greater than zero.")
            continue
        return parsed


def _prompt_bool(
    label: str,
    default: bool,
    *,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> bool:
    default_text = "true" if default else "false"
    while True:
        value = input_func(f"{label} [{default_text}]: ").strip().lower()
        if not value:
            return default
        if value in {"true", "t", "yes", "y", "1", "on"}:
            return True
        if value in {"false", "f", "no", "n", "0", "off"}:
            return False
        output_func("Please enter true or false.")


def _prompt_logging_level(
    label: str,
    default: str,
    *,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> str:
    while True:
        value = input_func(f"{label} [{default}]: ").strip().upper()
        if not value:
            return default
        if value in _LOG_LEVELS:
            return value
        output_func("Please enter one of: DEBUG, INFO, WARNING, ERROR, CRITICAL, OFF.")
