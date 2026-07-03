from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

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


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def setup_logging(settings: Settings) -> logging.Logger:
    level_name = settings.logging.level.upper().strip()
    level = LOG_LEVELS.get(level_name, logging.INFO)

    log_path = Path(settings.logging.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_formatter = JsonFormatter()

    if level_name != "OFF":
        console = logging.StreamHandler()
        console.setFormatter(console_formatter)
        console.setLevel(level)
        root.addHandler(console)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        root.addHandler(file_handler)

    logger = logging.getLogger("ctxkeeper")
    logger.info("Logging initialized at level=%s file=%s", level_name, log_path)
    return logger
