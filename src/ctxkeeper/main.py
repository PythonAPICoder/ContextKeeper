from __future__ import annotations

import logging
import sys

import uvicorn

from .app import create_app
from .config import ConfigError, load_config


def run() -> None:
    try:
        settings = load_config()
    except ConfigError as exc:
        print(f"ContextKeeper configuration error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    app = create_app(settings)
    logger = logging.getLogger("ctxkeeper")
    logger.info("Starting ContextKeeper on http://%s:%s", settings.server.host, settings.server.port)
    logger.info("Dashboard: http://localhost:%s/dashboard", settings.server.port)
    logger.info("Proxy target Ollama: %s", settings.ollama.base_url)
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)


if __name__ == "__main__":
    run()
