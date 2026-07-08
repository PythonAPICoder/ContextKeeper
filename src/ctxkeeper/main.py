from __future__ import annotations

import argparse
from collections.abc import Sequence
import sys

from .config import ConfigError
from .resources import DEFAULT_CONFIG_NAME, runtime_path
from .service.runner import run_contextkeeper
from .wizard.ui import run_configuration_wizard


def run(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    config_path = runtime_path(DEFAULT_CONFIG_NAME)
    if args.configure or not config_path.exists():
        run_configuration_wizard(config_path)
        return

    try:
        run_contextkeeper()
    except ConfigError as exc:
        print(f"ContextKeeper configuration error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ContextKeeper.")
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Launch the configuration wizard and exit.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    run()
