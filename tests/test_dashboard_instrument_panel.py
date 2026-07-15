from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings
from ctxkeeper.context.compression_manager import ROLLING_SUMMARY_PREFIX
from ctxkeeper.context.conversation_store import conversation_store
from ctxkeeper.dashboard.routes import build_dashboard_status, context_history_store
from ctxkeeper.diagnostics.activity import activity_manager


class DashboardHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.pages: list[str] = []
        self.page_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
        page = attributes.get("data-page")
        if page:
            self.pages.append(page)
        page_link = attributes.get("data-page-link")
        if page_link:
            self.page_links.append(page_link)


@pytest.fixture(autouse=True)
def clear_dashboard_state() -> None:
    activity_manager.reset()
    conversation_store.clear()
    context_history_store.clear()
    yield
    conversation_store.clear()
    context_history_store.clear()
    activity_manager.reset()


def _settings(*, context_enabled: bool = True, compression_enabled: bool = True) -> Settings:
    return Settings.model_validate(
        {
            "context": {
                "enabled": context_enabled,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 70,
                "compression_threshold_percent": 90,
                "minimum_threshold_percent": 10,
            },
            "compression": {"enabled": compression_enabled},
        }
    )


def _metrics_snapshot(system: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "requests": {
            "total_requests": 0,
            "total_errors": 0,
            "last_endpoint": None,
            "last_model": None,
            "last_latency_ms": None,
            "last_status_code": None,
            "recent_requests": [],
        },
        "system": system
        or {
            "cpu_percent": None,
            "ram_percent": None,
            "ram_used_gb": None,
            "ram_total_gb": None,
            "gpu": None,
        },
    }


def _status(settings: Settings, system: dict[str, object] | None = None) -> dict[str, object]:
    return build_dashboard_status(
        settings=settings,
        metrics_snapshot=_metrics_snapshot(system),
        ollama_status={"status": "online"},
    )


def _detail_texts(instrument: dict[str, object]) -> list[str]:
    lines = instrument.get("detail_lines")
    assert isinstance(lines, list)
    assert len(lines) == 3
    texts: list[str] = []
    for line in lines:
        assert isinstance(line, dict)
        text = line.get("text")
        assert isinstance(text, str)
        texts.append(text)
    return texts


def test_dashboard_template_contains_six_instrument_cards() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Dashboard instrument panel" in response.text
    for label in [
        "CPU Usage",
        "GPU Usage",
        "Memory Usage",
        "Context Usage",
        "Context Trend",
        "Compression Status",
    ]:
        assert label in response.text
    assert "initializeInstrumentGauges" in response.text
    assert "updateInstrumentGauge" in response.text
    assert "renderContextTrend" in response.text
    assert "renderInstrumentSupport" in response.text
    assert "setInstrumentReadingNeutral" in response.text
    assert ".instrument-reading.is-neutral" in response.text
    assert ".instrument-reading .badge" in response.text
    assert "Awaiting context history." in response.text
    assert "displayState = state === 'empty' ? 'waiting'" in response.text
    assert "Collecting context history." not in response.text
    assert response.text.count('class="instrument-support"') == 5
    assert response.text.count('data-support-slot="1"') == 5
    assert response.text.count('data-support-slot="2"') == 5
    assert response.text.count('data-support-slot="3"') == 5
    assert ".instrument-support-row" in response.text
    assert "Intel Core i9-14900K" not in response.text
    assert "NVIDIA GeForce RTX 4090" not in response.text


def test_dashboard_template_has_consistent_page_targets_and_unique_ids() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")
    parser = DashboardHtmlParser()
    parser.feed(response.text)

    assert response.status_code == 200
    assert parser.pages == ["operations", "conversations", "context", "analytics", "logs", "settings"]
    assert set(parser.pages).issubset(set(parser.page_links))
    assert [element_id for element_id, count in Counter(parser.ids).items() if count > 1] == []


def test_dashboard_template_contains_visual_qa_overflow_guards() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert ".page-header > * { min-width:0; }" in response.text
    assert ".panel-item > * { min-width:0; }" in response.text
    assert "table-layout:fixed" in response.text
    assert "word-break:break-word" in response.text


def test_dashboard_overview_removes_duplicate_resources_card_and_rebalances_lower_layout() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert '<div id="resources"' not in response.text
    assert "<h2>Resources</h2>" not in response.text
    assert "speedometer" not in response.text
    assert "resource-stack" not in response.text
    assert "grid-template-columns:minmax(0,3fr) minmax(280px,2fr)" in response.text
    assert 'class="traffic-stat"><div class="small">Errors</div><div id="err"' in response.text
    assert "conversation-meta compact" in response.text


def test_instrument_panel_reports_cpu_available_and_unavailable() -> None:
    available = _status(
        _settings(),
        {
            "cpu_percent": 42.5,
            "cpu": {
                "available": True,
                "usage_percent": 42.5,
                "status": "healthy",
                "status_label": "Healthy",
                "name": "Acme Compute Engine With A Very Long Dynamic Processor Name",
                "thread_count": 24,
                "logical_processor_count": 24,
                "temperature_c": 47.0,
            },
        },
    )["instrument_panel"]["cpu"]

    unavailable = _status(
        _settings(),
        {
            "cpu_percent": None,
            "cpu": {
                "available": False,
                "usage_percent": None,
                "name": None,
                "logical_processor_count": None,
            },
        },
    )["instrument_panel"]["cpu"]

    assert available["available"] is True
    assert available["usage_percent"] == 42.5
    assert available["name"] == "Acme Compute Engine With A Very Long Dynamic Processor Name"
    assert available["logical_processor_count"] == 24
    assert available["thread_count"] == 24
    assert available["temperature_c"] == 47.0
    assert available["status_label"] == "Healthy"
    assert _detail_texts(available) == [
        "Acme Compute Engine With A Very Long Dynamic Processor Name",
        "24 threads",
        "47 °C",
    ]
    assert unavailable["available"] is False
    assert unavailable["usage_percent"] is None
    assert unavailable["status"] == "unavailable"
    assert _detail_texts(unavailable) == [
        "CPU identity unavailable",
        "Thread count unavailable",
        "Temperature unavailable",
    ]


def test_instrument_panel_reports_available_cpu_without_temperature() -> None:
    cpu = _status(
        _settings(),
        {
            "cpu_percent": 18.0,
            "cpu": {
                "available": True,
                "usage_percent": 18.0,
                "status": "healthy",
                "status_label": "Healthy",
                "name": "Dynamic Processor Without Sensor",
                "thread_count": 8,
                "temperature_c": None,
            },
        },
    )["instrument_panel"]["cpu"]

    assert cpu["temperature_c"] is None
    assert _detail_texts(cpu) == [
        "Dynamic Processor Without Sensor",
        "8 threads",
        "Temperature unavailable",
    ]


def test_instrument_panel_reports_gpu_available_and_unavailable() -> None:
    available = _status(
        _settings(),
        {
            "gpu_detail": {
                "available": True,
                "telemetry_status": "available",
                "status": "warning",
                "status_label": "Warning",
                "name": "NVIDIA Test GPU With Very Long Name",
                "usage_percent": 78.0,
                "vram_used_gb": 7.5,
                "vram_total_gb": 12.0,
                "temperature_c": 66.0,
            }
        },
    )["instrument_panel"]["gpu"]

    unavailable = _status(
        _settings(),
        {
            "gpu": None,
            "gpu_detail": {
                "available": False,
                "telemetry_status": "unavailable",
                "status": "unavailable",
                "status_label": "Unavailable",
                "name": None,
                "usage_percent": None,
                "message": "nvidia-smi is not available on this system.",
            },
        },
    )["instrument_panel"]["gpu"]

    assert available["available"] is True
    assert available["usage_percent"] == 78.0
    assert available["name"] == "NVIDIA Test GPU With Very Long Name"
    assert available["vram_used_gb"] == 7.5
    assert available["vram_total_gb"] == 12.0
    assert available["temperature_c"] == 66.0
    assert available["status"] == "warning"
    assert _detail_texts(available) == [
        "NVIDIA Test GPU With Very Long Name",
        "7.5 / 12 GB VRAM",
        "66 °C",
    ]
    assert unavailable["available"] is False
    assert unavailable["usage_percent"] is None
    assert unavailable["status"] == "unavailable"
    assert "nvidia-smi" in unavailable["message"]
    assert _detail_texts(unavailable) == [
        "GPU unavailable",
        "VRAM unavailable",
        "Temperature unavailable",
    ]


def test_instrument_panel_reports_partial_gpu_without_temperature() -> None:
    gpu = _status(
        _settings(),
        {
            "gpu_detail": {
                "available": True,
                "telemetry_status": "partial",
                "status": "partial",
                "status_label": "Partial",
                "name": "Generic Accelerator With Long Dynamic Name",
                "usage_percent": None,
                "vram_used_gb": None,
                "vram_total_gb": 24.0,
                "temperature_c": None,
            }
        },
    )["instrument_panel"]["gpu"]

    assert gpu["available"] is True
    assert gpu["status"] == "partial"
    assert _detail_texts(gpu) == [
        "Generic Accelerator With Long Dynamic Name",
        "24 GB VRAM",
        "Temperature unavailable",
    ]


def test_instrument_panel_reports_memory_metrics() -> None:
    memory = _status(
        _settings(),
        {
            "ram_percent": 63.25,
            "ram_used_gb": 10.5,
            "ram_total_gb": 16.0,
            "memory": {
                "available": True,
                "usage_percent": 63.25,
                "used_gb": 10.5,
                "total_gb": 16.0,
                "status": "moderate",
                "status_label": "Moderate",
            },
        },
    )["instrument_panel"]["memory"]

    assert memory["available"] is True
    assert memory["usage_percent"] == 63.25
    assert memory["used_gb"] == 10.5
    assert memory["total_gb"] == 16.0
    assert memory["status_label"] == "Moderate"
    assert "10.5 / 16 GB used" == memory["message"]
    assert _detail_texts(memory) == ["10.5 GB used", "16 GB total", "Moderate"]


def test_instrument_panel_handles_absent_cpu_gpu_diagnostic_fields() -> None:
    panel = _status(_settings(), {"cpu_percent": 33.0, "gpu": None})["instrument_panel"]

    assert panel["cpu"]["available"] is True
    assert panel["cpu"]["usage_percent"] == 33.0
    assert _detail_texts(panel["cpu"]) == [
        "CPU identity unavailable",
        "Thread count unavailable",
        "Temperature unavailable",
    ]
    assert panel["gpu"]["available"] is False
    assert panel["gpu"]["status"] == "unavailable"
    assert _detail_texts(panel["gpu"]) == [
        "GPU unavailable",
        "VRAM unavailable",
        "Temperature unavailable",
    ]


def test_instrument_panel_preserves_long_device_name_titles() -> None:
    long_name = ("Very Long Dynamic Processor Name " * 8).strip()

    cpu = _status(
        _settings(),
        {
            "cpu_percent": 22.0,
            "cpu": {
                "available": True,
                "usage_percent": 22.0,
                "name": long_name,
                "thread_count": 128,
            },
        },
    )["instrument_panel"]["cpu"]

    line = cpu["detail_lines"][0]
    assert line["text"] == long_name
    assert line["title"] == long_name


def test_instrument_panel_reports_no_active_conversation_state() -> None:
    panel = _status(_settings(context_enabled=True, compression_enabled=True))["instrument_panel"]

    assert panel["context_usage"]["state"] == "no_active_conversation"
    assert panel["context_usage"]["status"] == "waiting"
    assert panel["context_usage"]["status_label"] == "Waiting"
    assert panel["context_usage"]["status_label"] != "No Active Conversation"
    assert panel["context_usage"]["usage_percent"] == 0.0
    assert panel["context_trend"]["state"] == "empty"
    assert panel["context_trend"]["status"] == "waiting"
    assert panel["context_trend"]["status_label"] == "Waiting"
    assert panel["context_trend"]["status_label"] != "Empty"
    assert panel["context_trend"]["current_usage_percent"] == 0.0
    assert panel["context_trend"]["message"] == "Awaiting context history."
    assert panel["compression_status"]["state"] == "ready"
    assert panel["compression_status"]["status_label"] == "Ready"
    assert panel["compression_status"]["status_label"] != "Monitoring"
    assert panel["compression_status"]["message"] == "Waiting for context threshold"
    assert _detail_texts(panel["context_usage"]) == [
        "No active conversation",
        "100 token window",
        "Warn 70% • Compress 90%",
    ]
    assert _detail_texts(panel["compression_status"]) == [
        "Threshold 90%",
        "0 compression events",
        "Waiting for context threshold",
    ]


def test_instrument_panel_reports_context_tracking_disabled_state() -> None:
    conversation_store.append_message("disabled-context", "user", "hello")

    panel = _status(_settings(context_enabled=False, compression_enabled=True))["instrument_panel"]

    assert panel["context_usage"]["state"] == "disabled"
    assert panel["context_usage"]["status_label"] == "Off"
    assert panel["context_usage"]["usage_percent"] is None
    assert panel["context_trend"]["state"] == "disabled"
    assert panel["compression_status"]["state"] == "unavailable"
    assert _detail_texts(panel["context_usage"]) == [
        "Context Tracking OFF",
        "100 token window",
        "Warn 70% • Compress 90%",
    ]


def test_instrument_panel_reports_active_context_data_with_model_window() -> None:
    conversation_store.append_message("active-context", "user", "a" * 396)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 75,
                "compression_threshold_percent": 90,
            },
            "models": {"test-model": {"context_window_tokens": 200}},
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "test-model"
    metrics_snapshot["requests"]["recent_requests"] = [
        {"endpoint": "/api/chat", "model": "test-model", "status_code": 200}
    ]

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )
    context_usage = status["instrument_panel"]["context_usage"]

    assert status["active_conversation"]["context"]["context_window_tokens"] == 200
    assert context_usage["state"] == "active"
    assert context_usage["active_model"] == "test-model"
    assert context_usage["context_window_tokens"] == 200
    assert context_usage["context_window_source"] == "model_config"
    assert context_usage["estimated_tokens"] > 0
    assert context_usage["usage_percent"] > 0
    detail_texts = _detail_texts(context_usage)
    assert detail_texts[0].endswith(" / 200 tokens")
    assert detail_texts[1] == "test-model"
    assert detail_texts[2] == "Warn 75% • Compress 90%"


def test_instrument_panel_reports_compression_disabled_and_enabled_states() -> None:
    conversation_store.append_message("compression-context", "user", "a" * 356)

    disabled = _status(_settings(context_enabled=True, compression_enabled=False))["instrument_panel"][
        "compression_status"
    ]
    enabled = _status(
        Settings.model_validate(
            {
                "context": {
                    "enabled": True,
                    "default_context_window_tokens": 100,
                    "warning_threshold_percent": 50,
                    "compression_threshold_percent": 60,
                },
                "compression": {"enabled": True},
            }
        )
    )["instrument_panel"]["compression_status"]

    assert disabled["state"] == "disabled"
    assert disabled["status_label"] == "Off"
    assert disabled["threshold_percent"] == 90
    assert disabled["message"] == "Compression OFF"
    assert _detail_texts(disabled) == [
        "Compression OFF",
        "Threshold 90%",
        "0 compression events",
    ]
    assert enabled["state"] == "approaching"
    assert enabled["threshold_percent"] == 60
    assert enabled["proximity_percent"] == 100.0
    assert _detail_texts(enabled)[0] == "Threshold 60%"
    assert _detail_texts(enabled)[2] == "Active context is at or beyond the configured compression threshold."


def test_instrument_panel_reports_completed_compression_history() -> None:
    conversation_store.append_message("compressed-context", "user", "hello")
    conversation_store.append_message(
        "compressed-context",
        "system",
        f"{ROLLING_SUMMARY_PREFIX}prior summary",
    )

    compression = _status(_settings(context_enabled=True, compression_enabled=True))["instrument_panel"][
        "compression_status"
    ]

    assert compression["state"] == "completed"
    assert compression["event_count"] == 1
    assert compression["active_conversation_event_count"] == 1
    assert _detail_texts(compression)[1] == "1 compression event"


def test_instrument_panel_context_trend_empty_and_populated_states() -> None:
    empty = _status(_settings(context_enabled=True))["instrument_panel"]["context_trend"]
    assert empty["state"] == "empty"
    assert empty["status"] == "waiting"
    assert empty["status_label"] == "Waiting"
    assert empty["current_usage_percent"] == 0.0
    assert empty["message"] == "Awaiting context history."
    assert empty["samples"] == []

    conversation_store.append_message("trend-context", "user", "first message")
    first = _status(_settings(context_enabled=True))["instrument_panel"]["context_trend"]
    second = _status(_settings(context_enabled=True))["instrument_panel"]["context_trend"]

    assert first["state"] == "collecting"
    assert first["message"] == "Awaiting context history."
    assert len(first["samples"]) == 1
    assert second["state"] == "ready"
    assert len(second["samples"]) == 2
    assert second["estimate_label"] == "Estimate unavailable"
