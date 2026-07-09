"""Reusable ContextKeeper application runner."""

from __future__ import annotations

import logging
import platform
from collections.abc import Callable
from typing import Any

import uvicorn
from fastapi import FastAPI

from ..app import create_app
from ..branding import PRODUCT_INFO
from ..config import Settings, load_config
from ..resources import DEFAULT_CONFIG_NAME, is_frozen, resolve_config_path

ServerRunner = Callable[..., Any]


def run_contextkeeper(
    settings: Settings | None = None,
    *,
    server_runner: ServerRunner | None = None,
) -> None:
    """Start ContextKeeper with the configured FastAPI application.

    The normal command-line entry point and the future Windows Service host use
    this function so application creation, logging, and Uvicorn startup stay in
    one place.
    """
    config_path = resolve_config_path(DEFAULT_CONFIG_NAME)
    resolved_settings = settings or load_config(config_path)
    app = create_contextkeeper_app(resolved_settings)
    _print_startup_banner(resolved_settings, str(config_path))
    _log_startup(resolved_settings, str(config_path))
    runner = server_runner or uvicorn.run
    runner(app, host=resolved_settings.server.host, port=resolved_settings.server.port)


def create_contextkeeper_app(settings: Settings) -> FastAPI:
    """Create the ContextKeeper ASGI application for a runtime host."""
    return create_app(settings)


def _print_startup_banner(settings: Settings, config_path: str) -> None:
    dashboard_status = (
        f"http://localhost:{settings.server.port}/dashboard"
        if settings.dashboard.enabled
        else "disabled"
    )
    print(f"{PRODUCT_INFO.name} {PRODUCT_INFO.version}")
    print(PRODUCT_INFO.description)
    print(f"Config: {config_path}")
    print(f"Ollama: {settings.ollama.base_url}")
    print(f"Proxy: http://{settings.server.host}:{settings.server.port}")
    print(f"Dashboard: {dashboard_status}")
    print()


def _log_startup(settings: Settings, config_path: str) -> None:
    logger = logging.getLogger("ctxkeeper")
    runtime_mode = "frozen" if is_frozen() else "source"
    logger.info("Starting %s version=%s", PRODUCT_INFO.name, PRODUCT_INFO.version)
    logger.info("Runtime mode=%s python=%s", runtime_mode, platform.python_version())
    logger.info("Config path=%s", config_path)
    logger.info("Starting ContextKeeper on http://%s:%s", settings.server.host, settings.server.port)
    if settings.dashboard.enabled:
        logger.info("Dashboard: http://localhost:%s/dashboard", settings.server.port)
    else:
        logger.info("Dashboard disabled")
    logger.info("Proxy target Ollama: %s", settings.ollama.base_url)
