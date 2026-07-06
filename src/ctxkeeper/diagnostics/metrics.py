from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import ceil
import subprocess
from threading import Lock
from typing import Any

import psutil


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
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": collect_nvidia_metrics(),
    }


def collect_nvidia_metrics() -> dict[str, Any] | None:
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
        first = result.stdout.strip().splitlines()[0]
        name, gpu_util, mem_used, mem_total, temp, power = [part.strip() for part in first.split(",")]
        return {
            "name": name,
            "gpu_percent": float(gpu_util),
            "vram_used_gb": round(float(mem_used) / 1024, 2),
            "vram_total_gb": round(float(mem_total) / 1024, 2),
            "temperature_c": float(temp),
            "power_watts": float(power),
        }
    except Exception:
        return None


metrics_store = MetricsStore()
