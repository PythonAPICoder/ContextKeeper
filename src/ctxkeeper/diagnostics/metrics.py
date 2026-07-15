from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from math import ceil
import os
import platform
import re
import subprocess
from threading import Lock
from typing import Any

import psutil


_ARCHITECTURE_LABELS = {
    "amd64",
    "x64",
    "x86_64",
    "i386",
    "i686",
    "arm64",
    "aarch64",
}
_CPU_SENSOR_KEYS = ("coretemp", "k10temp", "zenpower", "cpu", "cpu_thermal", "soc_thermal")
_CPU_SENSOR_LABELS = ("package", "tdie", "tctl", "cpu", "core", "ccd", "die", "soc")
_PREFERRED_CPU_SENSOR_LABELS = ("package", "tdie", "tctl", "die", "cpu")


def estimate_text_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, ceil(len(text) / 4))


@dataclass
class RequestMetrics:
    total_requests: int = 0
    total_errors: int = 0
    last_endpoint: str | None = None
    last_model: str | None = None
    last_latency_ms: float | None = None
    last_status_code: int | None = None
    recent_requests: list[dict[str, Any]] = field(default_factory=list)


class MetricsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self.requests = RequestMetrics()

    def record_request(
        self,
        *,
        method: str,
        endpoint: str,
        model: str | None,
        status_code: int,
        latency_ms: float,
        client_host: str | None,
    ) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "endpoint": endpoint,
            "model": model,
            "status_code": status_code,
            "latency_ms": round(latency_ms, 2),
            "client_host": client_host,
        }
        with self._lock:
            self.requests.total_requests += 1
            if status_code >= 400:
                self.requests.total_errors += 1
            self.requests.last_endpoint = endpoint
            self.requests.last_model = model
            self.requests.last_latency_ms = latency_ms
            self.requests.last_status_code = status_code
            self.requests.recent_requests.insert(0, event)
            self.requests.recent_requests = self.requests.recent_requests[:50]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            request_data = {
                "total_requests": self.requests.total_requests,
                "total_errors": self.requests.total_errors,
                "last_endpoint": self.requests.last_endpoint,
                "last_model": self.requests.last_model,
                "last_latency_ms": self.requests.last_latency_ms,
                "last_status_code": self.requests.last_status_code,
                "recent_requests": list(self.requests.recent_requests),
            }
        return {
            "requests": request_data,
            "system": collect_system_metrics(),
        }


def collect_system_metrics() -> dict[str, Any]:
    cpu_percent: float | None
    try:
        cpu_percent = _safe_float(psutil.cpu_percent(interval=None))
    except Exception:
        cpu_percent = None

    try:
        virtual_memory = psutil.virtual_memory()
        ram_percent = _safe_float(virtual_memory.percent)
        ram_used_gb = round(virtual_memory.used / (1024**3), 2)
        ram_total_gb = round(virtual_memory.total / (1024**3), 2)
    except Exception:
        ram_percent = None
        ram_used_gb = None
        ram_total_gb = None

    gpu_detail = collect_nvidia_metrics_detail()
    legacy_gpu = _legacy_gpu_metrics(gpu_detail)
    cpu_static = _cpu_static_info()
    cpu_thread_count = _int_or_none(cpu_static.get("logical_processor_count"))

    return {
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "ram_used_gb": ram_used_gb,
        "ram_total_gb": ram_total_gb,
        "gpu": legacy_gpu,
        "cpu": {
            "available": cpu_percent is not None,
            "usage_percent": cpu_percent,
            "status": _utilization_status(cpu_percent),
            "status_label": _utilization_status_label(cpu_percent),
            "name": _string_or_none(cpu_static.get("name")),
            "logical_processor_count": cpu_thread_count,
            "thread_count": cpu_thread_count,
            "temperature_c": _cpu_temperature_c(),
        },
        "memory": {
            "available": ram_percent is not None,
            "usage_percent": ram_percent,
            "used_gb": ram_used_gb,
            "total_gb": ram_total_gb,
            "status": _utilization_status(ram_percent),
            "status_label": _utilization_status_label(ram_percent),
        },
        "gpu_detail": gpu_detail,
    }


def collect_nvidia_metrics() -> dict[str, Any] | None:
    return _legacy_gpu_metrics(collect_nvidia_metrics_detail())


def collect_nvidia_metrics_detail() -> dict[str, Any]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )
    except FileNotFoundError:
        return _unavailable_gpu_detail("nvidia-smi is not available on this system.")
    except subprocess.TimeoutExpired:
        return _gpu_error_detail("nvidia-smi telemetry collection timed out.")
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "nvidia-smi returned an error.").strip()
        return _gpu_error_detail(message)
    except Exception as exc:
        return _gpu_error_detail(str(exc))

    lines = result.stdout.strip().splitlines()
    if not lines:
        return _unavailable_gpu_detail("No NVIDIA GPU telemetry was returned.")

    parts = [part.strip() for part in lines[0].split(",")]
    if len(parts) != 6:
        return _gpu_error_detail("Unexpected nvidia-smi telemetry format.")

    name, gpu_util, mem_used, mem_total, temp, power = parts
    usage_percent = _parse_nvidia_number(gpu_util)
    vram_used_gb = _nvidia_mb_to_gb(mem_used)
    vram_total_gb = _nvidia_mb_to_gb(mem_total)
    temperature_c = _parse_nvidia_number(temp)
    power_watts = _parse_nvidia_number(power)
    available_values = [
        usage_percent,
        vram_used_gb,
        vram_total_gb,
        temperature_c,
        power_watts,
    ]
    telemetry_status = "available" if all(value is not None for value in available_values[:4]) else "partial"
    status = _utilization_status(usage_percent) if usage_percent is not None else "partial"
    status_label = _utilization_status_label(usage_percent) if usage_percent is not None else "Partial"

    return {
        "available": True,
        "telemetry_status": telemetry_status,
        "status": status,
        "status_label": status_label,
        "name": name or "Unknown GPU",
        "usage_percent": usage_percent,
        "vram_used_gb": vram_used_gb,
        "vram_total_gb": vram_total_gb,
        "temperature_c": temperature_c,
        "power_watts": power_watts,
        "message": "GPU telemetry is available." if telemetry_status == "available" else "GPU telemetry is partially available.",
    }


def _legacy_gpu_metrics(gpu_detail: dict[str, Any]) -> dict[str, Any] | None:
    if not gpu_detail.get("available"):
        return None
    usage_percent = gpu_detail.get("usage_percent")
    vram_used_gb = gpu_detail.get("vram_used_gb")
    vram_total_gb = gpu_detail.get("vram_total_gb")
    temperature_c = gpu_detail.get("temperature_c")
    if usage_percent is None or vram_used_gb is None or vram_total_gb is None:
        return None
    return {
        "name": gpu_detail.get("name") or "Unknown GPU",
        "gpu_percent": usage_percent,
        "vram_used_gb": vram_used_gb,
        "vram_total_gb": vram_total_gb,
        "temperature_c": temperature_c,
        "power_watts": gpu_detail.get("power_watts"),
    }


def _safe_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, 2)


def _int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_nvidia_number(value: str) -> float | None:
    normalized = value.strip()
    if not normalized or normalized.upper() in {"N/A", "[N/A]", "NOT SUPPORTED", "[NOT SUPPORTED]"}:
        return None
    try:
        return round(float(normalized), 2)
    except ValueError:
        return None


def _nvidia_mb_to_gb(value: str) -> float | None:
    numeric = _parse_nvidia_number(value)
    if numeric is None:
        return None
    return round(numeric / 1024, 2)


def _utilization_status(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if value >= 90:
        return "critical"
    if value >= 75:
        return "warning"
    if value >= 55:
        return "moderate"
    return "healthy"


def _utilization_status_label(value: float | None) -> str:
    return {
        "healthy": "Healthy",
        "moderate": "Moderate",
        "warning": "Warning",
        "critical": "Critical",
        "unavailable": "Unavailable",
    }[_utilization_status(value)]


@lru_cache(maxsize=1)
def _cpu_static_info() -> dict[str, Any]:
    return {
        "name": _processor_name(),
        "logical_processor_count": _logical_processor_count(),
    }


def _processor_name() -> str | None:
    candidates = [
        _windows_processor_name(),
        _linux_processor_name(),
        _macos_processor_name(),
        platform.processor(),
        getattr(platform.uname(), "processor", ""),
        os.getenv("PROCESSOR_IDENTIFIER"),
    ]
    for candidate in candidates:
        cleaned = _clean_processor_name(candidate)
        if cleaned:
            return cleaned
    return None


def _windows_processor_name() -> str | None:
    if platform.system().lower() != "windows":
        return None
    try:
        import winreg

        with winreg.OpenKey(  # type: ignore[attr-defined]
            winreg.HKEY_LOCAL_MACHINE,  # type: ignore[attr-defined]
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "ProcessorNameString")  # type: ignore[attr-defined]
    except Exception:
        return None
    return value if isinstance(value, str) else None


def _linux_processor_name() -> str | None:
    if platform.system().lower() != "linux":
        return None
    try:
        with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as cpuinfo:
            for line in cpuinfo:
                key, separator, value = line.partition(":")
                if separator and key.strip().lower() in {"model name", "hardware"}:
                    return value.strip()
    except Exception:
        return None
    return None


def _macos_processor_name() -> str | None:
    if platform.system().lower() != "darwin":
        return None
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            check=True,
            timeout=1,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _clean_processor_name(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.replace("\x00", " ").split())
    if not normalized:
        return None
    lower = normalized.lower()
    if lower in _ARCHITECTURE_LABELS or lower in {"genuineintel", "authenticamd"}:
        return None
    if "family" in lower and "model" in lower and "stepping" in lower:
        return None

    normalized = re.sub(r"\((?:r|tm)\)", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bCPU\b", "", normalized)
    normalized = re.sub(r"\s*@\s*\d+(?:\.\d+)?\s*GHz\b", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,-")
    if not normalized:
        return None
    if normalized.lower() in _ARCHITECTURE_LABELS:
        return None
    return normalized


@lru_cache(maxsize=1)
def _logical_processor_count() -> int | None:
    try:
        return psutil.cpu_count(logical=True)
    except Exception:
        return None


def _cpu_temperature_c() -> float | None:
    sensors_temperatures = getattr(psutil, "sensors_temperatures", None)
    if not callable(sensors_temperatures):
        return None
    try:
        sensors = sensors_temperatures(fahrenheit=False)
    except (AttributeError, NotImplementedError):
        return None
    except Exception:
        return None
    if not isinstance(sensors, dict):
        return None

    candidates: list[tuple[int, float]] = []
    for sensor_name, entries in sensors.items():
        sensor_key = str(sensor_name or "").lower()
        sensor_key_is_cpu = any(keyword in sensor_key for keyword in _CPU_SENSOR_KEYS)
        if not isinstance(entries, (list, tuple)):
            continue
        for entry in entries:
            label = str(getattr(entry, "label", "") or "").lower()
            current = _safe_float(getattr(entry, "current", None))
            if current is None or current < -20 or current > 150:
                continue
            label_is_cpu = any(keyword in label for keyword in _CPU_SENSOR_LABELS)
            if not sensor_key_is_cpu and not label_is_cpu:
                continue
            preferred = any(keyword in label for keyword in _PREFERRED_CPU_SENSOR_LABELS)
            score = 2 if preferred else 1
            candidates.append((score, current))

    if not candidates:
        return None
    best_score = max(score for score, _ in candidates)
    return max(value for score, value in candidates if score == best_score)


def _unavailable_gpu_detail(message: str) -> dict[str, Any]:
    return {
        "available": False,
        "telemetry_status": "unavailable",
        "status": "unavailable",
        "status_label": "Unavailable",
        "name": None,
        "usage_percent": None,
        "vram_used_gb": None,
        "vram_total_gb": None,
        "temperature_c": None,
        "power_watts": None,
        "message": message,
    }


def _gpu_error_detail(message: str) -> dict[str, Any]:
    return {
        "available": False,
        "telemetry_status": "error",
        "status": "error",
        "status_label": "Error",
        "name": None,
        "usage_percent": None,
        "vram_used_gb": None,
        "vram_total_gb": None,
        "temperature_c": None,
        "power_watts": None,
        "message": message,
    }


metrics_store = MetricsStore()
