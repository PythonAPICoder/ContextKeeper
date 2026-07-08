"""Placeholder Windows Service host for a future pywin32 implementation."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from .runner import run_contextkeeper


@dataclass
class ContextKeeperWindowsService:
    """Non-installing placeholder for the future Windows Service integration.

    This class deliberately avoids importing pywin32 so the project remains
    installable and testable on every supported development environment.
    """

    settings: Settings | None = None

    service_name: str = "ContextKeeper"
    display_name: str = "ContextKeeper Local Proxy"
    description: str = "Runs the ContextKeeper Ollama proxy and dashboard."

    def start(self) -> None:
        """Start ContextKeeper using the shared application runner."""
        # TODO: Phase 6B should wire this into pywin32 ServiceFramework.SvcDoRun.
        run_contextkeeper(self.settings)

    def stop(self) -> None:
        """Placeholder stop hook for the future Windows Service lifecycle."""
        # TODO: Phase 6B should signal the running Uvicorn server to shut down.
        # Uvicorn is currently started in blocking mode by the shared runner.


def main() -> None:
    """Explain that service installation is intentionally not implemented yet."""
    # TODO: Phase 6B should expose install/start/stop/remove service commands.
    raise NotImplementedError("Windows Service installation is planned for a later phase.")
