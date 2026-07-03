from __future__ import annotations

import logging
from pathlib import Path

from .config import Settings


LOG_LEVELS = {
    "OFF": logging.CRITICAL + 10,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(settings: Settings) -> logging.Logger:
    level_name = settings.logging.level.upper().strip()
    level = LOG_LEVELS.get(level_name, logging.INFO)

    log_path = Path(settings.logging.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if level_name != "OFF":
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(level)
        root.addHandler(console)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root.addHandler(file_handler)

    logger = logging.getLogger("ctxkeeper")
    logger.info("Logging initialized at level=%s file=%s", level_name, log_path)
    return logger
