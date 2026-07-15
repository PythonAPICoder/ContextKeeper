from __future__ import annotations

from collections import namedtuple

from ctxkeeper.diagnostics import metrics


SensorReading = namedtuple("SensorReading", ["label", "current"])
VirtualMemory = namedtuple("VirtualMemory", ["percent", "used", "total"])


def test_clean_processor_name_prefers_concise_model_identity() -> None:
    assert metrics._clean_processor_name("Acme(R) Compute(TM) 9000 CPU @ 3.20GHz") == "Acme Compute 9000"
    assert metrics._clean_processor_name("AMD64") is None
    assert metrics._clean_processor_name("Intel64 Family 6 Model 183 Stepping 1, GenuineIntel") is None


def test_cpu_temperature_uses_trustworthy_cpu_sensor(monkeypatch) -> None:
    monkeypatch.setattr(
        metrics.psutil,
        "sensors_temperatures",
        lambda fahrenheit=False: {
            "nvme": [SensorReading(label="Composite", current=61.0)],
            "coretemp": [
                SensorReading(label="Core 0", current=44.0),
                SensorReading(label="Package id 0", current=47.0),
            ],
        },
        raising=False,
    )

    assert metrics._cpu_temperature_c() == 47.0


def test_cpu_temperature_returns_none_when_no_trustworthy_cpu_sensor(monkeypatch) -> None:
    monkeypatch.setattr(
        metrics.psutil,
        "sensors_temperatures",
        lambda fahrenheit=False: {"nvme": [SensorReading(label="Composite", current=61.0)]},
        raising=False,
    )

    assert metrics._cpu_temperature_c() is None


def test_collect_system_metrics_serializes_cpu_identity_thread_count_and_temperature(monkeypatch) -> None:
    monkeypatch.setattr(metrics.psutil, "cpu_percent", lambda interval=None: 12.0)
    monkeypatch.setattr(
        metrics.psutil,
        "virtual_memory",
        lambda: VirtualMemory(percent=50.0, used=8 * 1024**3, total=16 * 1024**3),
    )
    monkeypatch.setattr(metrics, "collect_nvidia_metrics_detail", lambda: metrics._unavailable_gpu_detail("No GPU telemetry."))
    monkeypatch.setattr(metrics, "_cpu_static_info", lambda: {"name": "Acme Compute 9000", "logical_processor_count": 64})
    monkeypatch.setattr(metrics, "_cpu_temperature_c", lambda: 47.0)

    snapshot = metrics.collect_system_metrics()

    assert snapshot["cpu"]["name"] == "Acme Compute 9000"
    assert snapshot["cpu"]["logical_processor_count"] == 64
    assert snapshot["cpu"]["thread_count"] == 64
    assert snapshot["cpu"]["temperature_c"] == 47.0
