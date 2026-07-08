"""Runtime resource path helpers for source and frozen executable modes."""

from __future__ import annotations

from pathlib import Path
import sys

DEFAULT_CONFIG_NAME = "contextkeeper.yaml"


def is_frozen() -> bool:
    """Return whether ContextKeeper is running from a frozen executable."""
    return bool(getattr(sys, "frozen", False))


def runtime_root() -> Path:
    """Return the root directory for user-editable runtime files."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def bundled_root() -> Path:
    """Return the root directory for bundled read-only resources."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(str(meipass)).resolve()
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: str | Path) -> Path:
    """Return a bundled resource path for source or frozen execution."""
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return bundled_root() / path


def runtime_path(relative_path: str | Path) -> Path:
    """Return a user-editable runtime path for source or frozen execution."""
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return runtime_root() / path


def resolve_config_path(config_path: str | Path = DEFAULT_CONFIG_NAME) -> Path:
    """Resolve the configuration path for source and packaged execution.

    Explicit absolute paths are preserved. Relative paths keep source-mode
    behavior by resolving from the current working directory. In frozen mode,
    default configuration is loaded from beside the executable when present,
    with the bundled PyInstaller resource as a fallback.
    """
    path = Path(config_path)
    if path.is_absolute():
        return path

    if path != Path(DEFAULT_CONFIG_NAME):
        return Path.cwd() / path

    if is_frozen():
        executable_config = runtime_path(path)
        if executable_config.exists():
            return executable_config

        bundled_config = resource_path(path)
        if bundled_config.exists():
            return bundled_config

        return executable_config

    return Path.cwd() / path
