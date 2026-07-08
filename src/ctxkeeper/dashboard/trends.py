"""Rolling request and latency trend calculations for the dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

TrendDirection = Literal["up", "down", "flat"]


@dataclass(frozen=True)
class RequestSample:
    """A single request sample used for rolling trend calculations."""

    timestamp: datetime
    latency_ms: float

    def to_dict(self) -> dict[str, str | float]:
        """Return a serializable representation of the request sample."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms,
        }


class RollingTrends:
    """Maintain rolling request and latency statistics for dashboard cards."""

    def __init__(self, *, max_samples: int = 120) -> None:
        """Create a rolling trend buffer limited to max_samples entries."""
        if max_samples <= 1:
            raise ValueError("max_samples must be greater than 1")
        self.max_samples = max_samples
        self._samples: deque[RequestSample] = deque(maxlen=max_samples)

    def record_request(
        self,
        *,
        latency_ms: float,
        timestamp: datetime | None = None,
    ) -> RequestSample:
        """Record one completed request and return the stored sample."""
        if latency_ms < 0:
            raise ValueError("latency_ms must be greater than or equal to 0")

        sample = RequestSample(
            timestamp=_ensure_timezone(timestamp or datetime.now(timezone.utc)),
            latency_ms=latency_ms,
        )
        self._samples.append(sample)
        return sample

    def average_request_rate(self) -> float:
        """Return the rolling average request rate in requests per minute."""
        if not self._samples:
            return 0.0
        if len(self._samples) == 1:
            return 1.0

        first = self._samples[0].timestamp
        last = self._samples[-1].timestamp
        elapsed_seconds = max((last - first).total_seconds(), 1.0)
        requests_per_minute = (len(self._samples) / elapsed_seconds) * 60.0
        return round(requests_per_minute, 2)

    def average_latency(self) -> float:
        """Return the rolling average latency in milliseconds."""
        if not self._samples:
            return 0.0
        total_latency = sum(sample.latency_ms for sample in self._samples)
        return round(total_latency / len(self._samples), 2)

    def trend_direction(self) -> TrendDirection:
        """Return whether recent latency is trending up, down, or flat."""
        if len(self._samples) < 4:
            return "flat"

        midpoint = len(self._samples) // 2
        earlier = list(self._samples)[:midpoint]
        recent = list(self._samples)[midpoint:]
        earlier_average = sum(sample.latency_ms for sample in earlier) / len(earlier)
        recent_average = sum(sample.latency_ms for sample in recent) / len(recent)
        delta = recent_average - earlier_average

        if abs(delta) < 50.0:
            return "flat"
        if delta > 0:
            return "up"
        return "down"

    def samples(self) -> list[RequestSample]:
        """Return request samples in oldest-first order."""
        return list(self._samples)


def _ensure_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
