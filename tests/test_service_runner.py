from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ctxkeeper.config import Settings
from ctxkeeper.service.runner import create_contextkeeper_app, run_contextkeeper
from ctxkeeper.service.windows_service import ContextKeeperWindowsService


def test_run_contextkeeper_uses_existing_app_and_server_settings() -> None:
    settings = Settings()
    settings.server.host = "127.0.0.1"
    settings.server.port = 11650
    captured: dict[str, Any] = {}

    def fake_server_runner(app: FastAPI, *, host: str, port: int) -> None:
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port

    run_contextkeeper(settings, server_runner=fake_server_runner)

    assert isinstance(captured["app"], FastAPI)
    assert captured["app"].state.settings is settings
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 11650


def test_run_contextkeeper_prints_readable_startup_banner(capsys) -> None:
    settings = Settings()
    settings.server.host = "127.0.0.1"
    settings.server.port = 11651
    settings.ollama.base_url = "http://ollama.local:11434"

    run_contextkeeper(settings, server_runner=lambda app, *, host, port: None)

    output = capsys.readouterr().out
    assert "ContextKeeper 0.1.0" in output
    assert "Config:" in output
    assert "Ollama: http://ollama.local:11434" in output
    assert "Proxy: http://127.0.0.1:11651" in output
    assert "Dashboard: http://localhost:11651/dashboard" in output


def test_create_contextkeeper_app_preserves_dashboard_and_proxy_routes() -> None:
    app = create_contextkeeper_app(Settings())
    client = TestClient(app)

    assert client.get("/dashboard").status_code == 200
    assert client.get("/dashboard/data").status_code == 200


def test_windows_service_placeholder_exposes_metadata_and_start(monkeypatch) -> None:
    started: dict[str, Settings | None] = {}

    def fake_run_contextkeeper(settings: Settings | None = None) -> None:
        started["settings"] = settings

    monkeypatch.setattr("ctxkeeper.service.windows_service.run_contextkeeper", fake_run_contextkeeper)
    settings = Settings()
    service = ContextKeeperWindowsService(settings=settings)

    service.start()
    service.stop()

    assert service.service_name == "ContextKeeper"
    assert service.display_name == "ContextKeeper Local Proxy"
    assert started["settings"] is settings
