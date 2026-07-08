from __future__ import annotations

import sys

from .config import ConfigError
from .service.runner import run_contextkeeper


def run() -> None:
    try:
        run_contextkeeper()
    except ConfigError as exc:
        print(f"ContextKeeper configuration error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    run()
