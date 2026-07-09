from __future__ import annotations

from fastapi import FastAPI

from .branding import DESCRIPTION, PRODUCT_NAME, VERSION
from .config import Settings, load_config
from .dashboard.routes import create_dashboard_router
from .logging_config import setup_logging
from .proxy.routes import create_proxy_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_config()
    setup_logging(settings)

    app = FastAPI(
        title=PRODUCT_NAME,
        version=VERSION,
        description=DESCRIPTION,
    )
    app.state.settings = settings

    if settings.dashboard.enabled:
        app.include_router(create_dashboard_router(settings))

    app.include_router(create_proxy_router(settings))
    return app
