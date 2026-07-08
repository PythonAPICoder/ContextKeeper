from __future__ import annotations

from pathlib import Path
import sys

from ctxkeeper.resources import (
    DEFAULT_CONFIG_NAME,
    bundled_root,
    is_frozen,
    resolve_config_path,
    resource_path,
    runtime_path,
    runtime_root,
)


def test_source_mode_paths_use_current_working_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    assert is_frozen() is False
    assert runtime_root() == tmp_path
    assert runtime_path("logs/contextkeeper.log") == tmp_path / "logs" / "contextkeeper.log"
    assert resolve_config_path() == tmp_path / DEFAULT_CONFIG_NAME


def test_explicit_absolute_config_path_is_preserved(tmp_path: Path) -> None:
    config_path = tmp_path / "custom.yaml"

    assert resolve_config_path(config_path) == config_path


def test_relative_non_default_config_path_uses_current_working_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    assert resolve_config_path("configs/local.yaml") == tmp_path / "configs" / "local.yaml"


def test_frozen_config_prefers_file_beside_executable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    exe_dir = tmp_path / "dist"
    bundle_dir = tmp_path / "bundle"
    exe_dir.mkdir()
    bundle_dir.mkdir()
    executable_config = exe_dir / DEFAULT_CONFIG_NAME
    bundled_config = bundle_dir / DEFAULT_CONFIG_NAME
    executable_config.write_text("server:\n  port: 11600\n", encoding="utf-8")
    bundled_config.write_text("server:\n  port: 11700\n", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_dir / "ContextKeeper.exe"))
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_dir), raising=False)

    assert is_frozen() is True
    assert runtime_root() == exe_dir
    assert resolve_config_path() == executable_config


def test_frozen_config_falls_back_to_bundled_resource(
    monkeypatch,
    tmp_path: Path,
) -> None:
    exe_dir = tmp_path / "dist"
    bundle_dir = tmp_path / "bundle"
    exe_dir.mkdir()
    bundle_dir.mkdir()
    bundled_config = bundle_dir / DEFAULT_CONFIG_NAME
    bundled_config.write_text("server:\n  port: 11700\n", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_dir / "ContextKeeper.exe"))
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_dir), raising=False)

    assert bundled_root() == bundle_dir
    assert resource_path(DEFAULT_CONFIG_NAME) == bundled_config
    assert resolve_config_path() == bundled_config


def test_frozen_config_returns_executable_path_when_no_config_exists(
    monkeypatch,
    tmp_path: Path,
) -> None:
    exe_dir = tmp_path / "dist"
    bundle_dir = tmp_path / "bundle"
    exe_dir.mkdir()
    bundle_dir.mkdir()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_dir / "ContextKeeper.exe"))
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_dir), raising=False)

    assert resolve_config_path() == exe_dir / DEFAULT_CONFIG_NAME
