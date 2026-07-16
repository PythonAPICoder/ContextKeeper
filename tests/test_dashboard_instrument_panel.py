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
from ctxkeeper.model_context import active_context_window_overrides, model_context_window_cache, resolve_context_window


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
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
    yield
    conversation_store.clear()
    context_history_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()
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
    assert "context_window_source_label" in response.text
    assert "context_window_state" in response.text
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


def test_dashboard_template_contains_context_capacity_badge_and_model_source_markup() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="contextInstrumentCapacity"' in response.text
    assert "instrument-header-badge" in response.text
    assert "dashboard-header-badge" in response.text
    assert "instrument-support-model" in response.text
    assert "instrument-support-source" in response.text
    assert "modelSpan.setAttribute('title', line.model_name)" in response.text


def test_dashboard_uses_shared_card_header_typography_and_actions() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert ".dashboard-card-title,.card h2.dashboard-card-title" in response.text
    assert "font-size:9.5px" in response.text
    assert "letter-spacing:.055em" in response.text
    assert "line-height:18px" in response.text
    assert response.text.count("instrument-head dashboard-card-header") == 6
    assert response.text.count("instrument-title dashboard-card-title") == 6
    assert response.text.count("instrument-head-actions dashboard-card-header-actions") == 6
    assert '<div class="dashboard-card-header"><h2 class="dashboard-card-title">Traffic</h2></div>' in response.text
    assert '<h2 class="dashboard-card-title">Active Conversation</h2>' in response.text
    assert '<h2 class="ops-health-heading dashboard-card-title">' in response.text


def test_context_usage_header_keeps_full_title_and_badge_before_info_icon() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    start = response.text.index('<div id="contextInstrumentCard"')
    end = response.text.index('<div class="instrument-body"><div id="contextInstrumentGauge"', start)
    header = response.text[start:end]
    assert "Context Usage" in header
    assert "CONTEXT USA" not in header
    assert header.index('id="contextInstrumentCapacity"') < header.index('class="instrument-info"')
    assert 'instrument-header-badge dashboard-header-badge' in header
    assert 'dashboard-card-header-actions' in header


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
    assert panel["context_usage"]["context_window_state"] == "waiting"
    assert panel["context_usage"]["context_window_source"] is None
    assert panel["context_usage"]["context_window_source_label"] is None
    assert panel["context_usage"]["context_window_label"] is None
    assert panel["context_usage"]["context_window_tokens"] is None
    assert panel["context_usage"]["header_badge"] == "--"
    assert _detail_texts(panel["context_usage"]) == [
        "No active conversation",
        "Waiting for model...",
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
        "Default context window",
        "Warn 70% • Compress 90%",
    ]
    assert panel["context_usage"]["header_badge"] == "100"


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
    assert context_usage["context_window_source"] == "configured"
    assert context_usage["context_window_source_label"] == "Pre-defined"
    assert context_usage["context_window_label"] == "200"
    assert context_usage["header_badge"] == "200"
    assert context_usage["estimated_tokens"] > 0
    assert context_usage["usage_percent"] > 0
    detail_texts = _detail_texts(context_usage)
    assert detail_texts[0].endswith(" / 200 tokens")
    assert detail_texts[1] == "test-model • Pre-defined"
    assert detail_texts[2] == "Warn 75% • Compress 90%"


def test_instrument_panel_uses_detected_model_context_window() -> None:
    conversation_store.append_message("detected-context", "user", "a" * 396)
    model_context_window_cache.store("detected-model:latest", 400)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 75,
                "compression_threshold_percent": 90,
            },
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "detected-model:latest"
    metrics_snapshot["requests"]["recent_requests"] = [
        {"endpoint": "/api/chat", "model": "detected-model:latest", "status_code": 200}
    ]

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )
    context_usage = status["instrument_panel"]["context_usage"]

    assert status["active_conversation"]["context"]["context_window_tokens"] == 400
    assert status["active_conversation"]["context"]["context_window_source"] == "detected"
    assert context_usage["context_window_tokens"] == 400
    assert context_usage["context_window_source"] == "detected"
    assert context_usage["context_window_source_label"] == "Discovered"
    assert context_usage["context_window_label"] == "400"
    assert context_usage["header_badge"] == "400"
    assert _detail_texts(context_usage)[1] == "detected-model:latest • Discovered"


def test_context_usage_uses_user_facing_source_labels_for_all_resolution_paths() -> None:
    conversation_store.append_message("source-labels", "user", "hello")

    def context_usage_for(model: str, settings: Settings) -> dict[str, object]:
        metrics_snapshot = _metrics_snapshot()
        metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
        metrics_snapshot["requests"]["last_model"] = model
        metrics_snapshot["requests"]["recent_requests"] = [
            {"endpoint": "/api/chat", "model": model, "status_code": 200}
        ]
        return build_dashboard_status(
            settings=settings,
            metrics_snapshot=metrics_snapshot,
            ollama_status={"status": "online"},
        )["instrument_panel"]["context_usage"]

    configured_settings = Settings.model_validate(
        {"models": {"gpt-oss:20b": {"context_window_tokens": 65536}}}
    )
    model_context_window_cache.store("qwen3.6:latest", 262144)

    configured = context_usage_for("gpt-oss:20b", configured_settings)
    detected = context_usage_for("qwen3.6:latest", Settings())
    default = context_usage_for("unknown-model", Settings())

    assert configured["context_window_source"] == "configured"
    assert configured["context_window_source_label"] == "Pre-defined"
    assert configured["context_window_state"] == "pre-defined"
    assert configured["header_badge"] == "64K"
    assert _detail_texts(configured)[1] == "gpt-oss:20b • Pre-defined"
    assert detected["context_window_source"] == "detected"
    assert detected["context_window_source_label"] == "Discovered"
    assert detected["context_window_state"] == "discovered"
    assert detected["header_badge"] == "256K"
    assert _detail_texts(detected)[1] == "qwen3.6:latest • Discovered"
    assert default["context_window_source"] == "default"
    assert default["context_window_source_label"] == "Default"
    assert default["context_window_state"] == "default"
    assert default["header_badge"] == "32K"
    assert _detail_texts(default)[1] == "unknown-model • Default"


def test_context_usage_model_source_line_keeps_source_visible_for_long_model_names() -> None:
    long_model = "hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M"
    conversation_store.append_message("long-model-context", "user", "hello")
    model_context_window_cache.store(long_model, 1048576)
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = long_model
    metrics_snapshot["requests"]["recent_requests"] = [
        {"endpoint": "/api/chat", "model": long_model, "status_code": 200}
    ]

    context_usage = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]
    line = context_usage["detail_lines"][1]

    assert context_usage["header_badge"] == "1M"
    assert line["text"] == f"{long_model} • Discovered"
    assert "1M" not in line["text"].replace(long_model, "")
    assert line["kind"] == "model_source"
    assert line["model_name"] == long_model
    assert line["source_label"] == "Discovered"
    assert line["title"] == f"{long_model} • Discovered"
    assert len(context_usage["detail_lines"]) == 3


def test_context_usage_startup_state_waits_for_first_model_without_default_fallback() -> None:
    status = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=_metrics_snapshot(),
        ollama_status={"status": "online"},
    )
    context_usage = status["instrument_panel"]["context_usage"]

    assert context_usage["state"] == "no_active_conversation"
    assert context_usage["context_window_state"] == "waiting"
    assert context_usage["context_window_source"] is None
    assert context_usage["context_window_source_label"] is None
    assert context_usage["context_window_label"] is None
    assert context_usage["context_window_tokens"] is None
    assert context_usage["header_badge"] == "--"
    assert status["context"]["context_window_state"] == "waiting"
    assert status["context"]["context_window_tokens"] is None
    assert status["requests"]["active_generation"]["context_window_state"] == "waiting"
    assert _detail_texts(context_usage) == [
        "No active conversation",
        "Waiting for model...",
        "Warn 75% • Compress 85%",
    ]


def test_context_usage_header_badge_updates_when_active_model_capacity_changes() -> None:
    conversation_store.append_message("capacity-switch-context", "user", "hello")
    model_context_window_cache.store("small-model:latest", 65536)
    model_context_window_cache.store("large-model:latest", 262144)

    def context_usage_for(model: str) -> dict[str, object]:
        metrics_snapshot = _metrics_snapshot()
        metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
        metrics_snapshot["requests"]["last_model"] = model
        metrics_snapshot["requests"]["recent_requests"] = [
            {"endpoint": "/api/chat", "model": model, "status_code": 200}
        ]
        return build_dashboard_status(
            settings=Settings(),
            metrics_snapshot=metrics_snapshot,
            ollama_status={"status": "online"},
        )["instrument_panel"]["context_usage"]

    small = context_usage_for("small-model:latest")
    large = context_usage_for("large-model:latest")

    assert small["header_badge"] == "64K"
    assert _detail_texts(small)[1] == "small-model:latest • Discovered"
    assert large["header_badge"] == "256K"
    assert _detail_texts(large)[1] == "large-model:latest • Discovered"


def test_context_usage_restart_returns_to_waiting_for_first_model_state() -> None:
    conversation_store.append_message("restart-context", "user", "hello")
    model_context_window_cache.store("qwen3.6:latest", 262144)
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "qwen3.6:latest"
    metrics_snapshot["requests"]["recent_requests"] = [
        {"endpoint": "/api/chat", "model": "qwen3.6:latest", "status_code": 200}
    ]

    observed = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]

    activity_manager.reset()
    conversation_store.clear()
    context_history_store.clear()
    model_context_window_cache.clear()
    active_context_window_overrides.clear()

    restarted = build_dashboard_status(
        settings=Settings(),
        metrics_snapshot=_metrics_snapshot(),
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]

    assert observed["context_window_state"] == "discovered"
    assert observed["header_badge"] == "256K"
    assert restarted["context_window_state"] == "waiting"
    assert restarted["header_badge"] == "--"
    assert _detail_texts(restarted)[1] == "Waiting for model..."


def test_instrument_panel_reports_default_then_detected_after_cache_refresh() -> None:
    conversation_store.append_message("refresh-context", "user", "a" * 396)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 75,
                "compression_threshold_percent": 90,
            },
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "llava:latest"
    metrics_snapshot["requests"]["recent_requests"] = [
        {"endpoint": "/api/chat", "model": "llava:latest", "status_code": 200}
    ]

    pending = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]

    model_context_window_cache.store("llava:latest", 32768)

    detected = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]

    assert pending["context_window_tokens"] == 100
    assert pending["context_window_source"] == "default"
    assert pending["header_badge"] == "100"
    assert _detail_texts(pending)[1] == "llava:latest • Default"
    assert detected["context_window_tokens"] == 32768
    assert detected["context_window_source"] == "detected"
    assert detected["context_window_label"] == "32K"
    assert detected["header_badge"] == "32K"
    assert _detail_texts(detected)[1] == "llava:latest • Discovered"


def test_switching_models_does_not_reuse_previous_detected_capacity() -> None:
    conversation_store.append_message("switch-detected-context", "user", "a" * 396)
    model_context_window_cache.store("gpt-oss:20b", 131072)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 32768,
                "warning_threshold_percent": 75,
                "compression_threshold_percent": 85,
            },
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "llava:latest"
    metrics_snapshot["requests"]["recent_requests"] = [
        {
            "timestamp": "2026-07-15T12:01:00+00:00",
            "endpoint": "/api/chat",
            "model": "llava:latest",
            "status_code": 200,
        },
        {
            "timestamp": "2026-07-15T12:00:00+00:00",
            "endpoint": "/api/chat",
            "model": "gpt-oss:20b",
            "status_code": 200,
        },
    ]

    pending_llava = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )["instrument_panel"]["context_usage"]

    assert pending_llava["active_model"] == "llava:latest"
    assert pending_llava["context_window_tokens"] == 32768
    assert pending_llava["context_window_source"] == "default"
    assert pending_llava["header_badge"] == "32K"
    assert _detail_texts(pending_llava)[1] == "llava:latest • Default"


def test_model_switch_updates_effective_context_capacity() -> None:
    conversation_store.append_message("switch-context", "user", "a" * 396)
    model_context_window_cache.store("small-model:latest", 100)
    model_context_window_cache.store("large-model:latest", 400)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 50,
                "warning_threshold_percent": 50,
                "compression_threshold_percent": 60,
            },
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "large-model:latest"
    metrics_snapshot["requests"]["recent_requests"] = [
        {
            "timestamp": "2026-07-15T12:01:00+00:00",
            "endpoint": "/api/chat",
            "model": "large-model:latest",
            "status_code": 200,
        },
        {
            "timestamp": "2026-07-15T12:00:00+00:00",
            "endpoint": "/api/chat",
            "model": "small-model:latest",
            "status_code": 200,
        },
    ]

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["requests"]["last_model"] == "large-model:latest"
    assert status["active_conversation"]["context"]["context_window_tokens"] == 400
    assert status["instrument_panel"]["context_usage"]["context_window_tokens"] == 400
    assert status["instrument_panel"]["compression_status"]["state"] == "available"


def test_instrument_panel_detected_context_capacity_updates_context_percentage_and_threshold() -> None:
    conversation_store.append_message("detected-context", "user", "a" * 396)
    model_context_window_cache.store("detected-model", 400)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 50,
                "compression_threshold_percent": 60,
            },
        }
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "detected-model"
    metrics_snapshot["requests"]["recent_requests"] = [
        {
            "endpoint": "/api/chat",
            "model": "detected-model",
            "status_code": 200,
            "context_window_tokens": 400,
            "context_window_source": "detected",
        }
    ]

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )
    context = status["active_conversation"]["context"]
    context_usage = status["instrument_panel"]["context_usage"]
    compression = status["instrument_panel"]["compression_status"]

    assert context["context_window_tokens"] == 400
    assert context["context_window_source"] == "detected"
    assert context["usage_percent"] == pytest.approx(25.0)
    assert context_usage["context_window_tokens"] == 400
    assert context_usage["context_window_source"] == "detected"
    assert context_usage["header_badge"] == "400"
    assert _detail_texts(context_usage)[1] == "detected-model • Discovered"
    assert context_usage["status"] == "healthy"
    assert compression["state"] == "available"


def test_active_configured_context_capacity_before_streaming_request_metrics_complete() -> None:
    conversation_store.append_message("active-configured-context", "user", "a" * 396)
    settings = Settings.model_validate(
        {
            "context": {
                "enabled": True,
                "default_context_window_tokens": 100,
                "warning_threshold_percent": 50,
                "compression_threshold_percent": 60,
            },
            "models": {"configured-model": {"context_window_tokens": 400}},
        }
    )
    request_id = activity_manager.accept_request(
        method="POST",
        endpoint="/api/chat",
        model="configured-model",
    )
    active_context_window_overrides.register(
        request_id,
        resolve_context_window(settings, model_name="configured-model"),
    )
    metrics_snapshot = _metrics_snapshot()
    metrics_snapshot["requests"]["last_endpoint"] = "/api/chat"
    metrics_snapshot["requests"]["last_model"] = "configured-model"
    metrics_snapshot["requests"]["recent_requests"] = [
        {
            "endpoint": "/api/chat",
            "model": "configured-model",
            "status_code": 200,
            "context_window_tokens": 400,
            "context_window_source": "configured",
        }
    ]

    status = build_dashboard_status(
        settings=settings,
        metrics_snapshot=metrics_snapshot,
        ollama_status={"status": "online"},
    )

    assert status["activity"]["active_request_count"] == 1
    assert status["active_conversation"]["context"]["context_window_tokens"] == 400
    assert status["active_conversation"]["context"]["context_window_source"] == "configured"
    assert status["active_conversation"]["context"]["usage_percent"] == pytest.approx(25.0)
    assert status["instrument_panel"]["context_usage"]["context_window_source"] == "configured"
    assert status["instrument_panel"]["context_usage"]["header_badge"] == "400"
    assert _detail_texts(status["instrument_panel"]["context_usage"])[1] == "configured-model • Pre-defined"


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
