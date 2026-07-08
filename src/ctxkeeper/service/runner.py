"""Reusable ContextKeeper application runner."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import uvicorn
from fastapi import FastAPI

from ..app import create_app
from ..config import Settings, load_config

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
    resolved_settings = settings or load_config()
    app = create_contextkeeper_app(resolved_settings)
    _log_startup(resolved_settings)
    runner = server_runner or uvicorn.run
    runner(app, host=resolved_settings.server.host, port=resolved_settings.server.port)


def create_contextkeeper_app(settings: Settings) -> FastAPI:
    """Create the ContextKeeper ASGI application for a runtime host."""
    return create_app(settings)


def _log_startup(settings: Settings) -> None:
    logger = logging.getLogger("ctxkeeper")
    logger.info("Starting ContextKeeper on http://%s:%s", settings.server.host, settings.server.port)
    logger.info("Dashboard: http://localhost:%s/dashboard", settings.server.port)
    logger.info("Proxy target Ollama: %s", settings.ollama.base_url)
