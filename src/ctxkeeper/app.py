from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .config import Settings, load_config
from .dashboard.routes import create_dashboard_router
from .logging_config import setup_logging
from .proxy.routes import create_proxy_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_config()
    setup_logging(settings)

    app = FastAPI(
        title="ContextKeeper",
        version=__version__,
        description="Transparent Ollama proxy with diagnostics and dashboard.",
    )
    app.state.settings = settings

    if settings.dashboard.enabled:
        app.include_router(create_dashboard_router(settings))

    app.include_router(create_proxy_router(settings))
    return app
