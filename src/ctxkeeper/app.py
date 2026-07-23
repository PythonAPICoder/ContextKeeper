from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from .branding import DESCRIPTION, PRODUCT_NAME, VERSION
from .config import Settings, load_config
from .dashboard.config_persistence import ConfigurationPersistenceService
from .dashboard.routes import create_dashboard_router
from .diagnostics.activity import activity_manager
from .logging_config import setup_logging
from .proxy.routes import create_proxy_router
from .resources import DEFAULT_CONFIG_NAME, resolve_config_path


def create_app(
    settings: Settings | None = None,
    *,
    config_path: str | Path = DEFAULT_CONFIG_NAME,
) -> FastAPI:
    resolved_config_path = resolve_config_path(config_path)
    settings = settings or load_config(resolved_config_path)
    setup_logging(settings)
    activity_manager.reset()
    configuration_persistence = ConfigurationPersistenceService(
        resolved_config_path,
        listener_host=settings.server.host,
        listener_port=settings.server.port,
    )

    app = FastAPI(
        title=PRODUCT_NAME,
        version=VERSION,
        description=DESCRIPTION,
    )
    app.state.settings = settings
    app.state.config_path = resolved_config_path
    app.state.configuration_persistence = configuration_persistence

    if settings.dashboard.enabled:
        app.include_router(
            create_dashboard_router(
                settings,
                configuration_persistence=configuration_persistence,
            )
        )

    app.include_router(create_proxy_router(settings))
    return app
