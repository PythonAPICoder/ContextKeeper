"""Deterministic health assessment primitives for dashboard intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    """Overall health states for dashboard intelligence consumers."""

    HEALTHY = "healthy"
    BUSY = "busy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass(frozen=True)
class DashboardMetrics:
    """Normalized operational metrics used by dashboard intelligence engines."""

    proxy_online: bool
    ollama_online: bool
    context_percent: float
    average_latency_ms: float
    active_requests: int

    def __post_init__(self) -> None:
        """Validate metric values before they are used for health rules."""
        if self.context_percent < 0:
            raise ValueError("context_percent must be greater than or equal to 0")
        if self.average_latency_ms < 0:
            raise ValueError("average_latency_ms must be greater than or equal to 0")
        if self.active_requests < 0:
            raise ValueError("active_requests must be greater than or equal to 0")

    def to_dict(self) -> dict[str, bool | float | int]:
        """Return a UI-friendly representation of the metrics."""
        return {
            "proxy_online": self.proxy_online,
            "ollama_online": self.ollama_online,
            "context_percent": self.context_percent,
            "average_latency_ms": self.average_latency_ms,
            "active_requests": self.active_requests,
        }


@dataclass(frozen=True)
class HealthAssessment:
    """Structured health assessment returned by the health engine."""

    status: HealthStatus
    reasons: list[str]
    indicators: dict[str, bool | float | int]

    def to_dict(self) -> dict[str, object]:
        """Return a serializable assessment for future dashboard UI cards."""
        return {
            "status": self.status.value,
            "reasons": self.reasons,
            "indicators": self.indicators,
        }


class HealthEngine:
    """Evaluate dashboard metrics with deterministic operational health rules."""

    BUSY_CONTEXT_PERCENT: float = 70.0
    WARNING_CONTEXT_PERCENT: float = 85.0
    CRITICAL_CONTEXT_PERCENT: float = 95.0
    BUSY_LATENCY_MS: float = 1_000.0
    WARNING_LATENCY_MS: float = 2_000.0
    CRITICAL_LATENCY_MS: float = 5_000.0
    BUSY_ACTIVE_REQUESTS: int = 1
    WARNING_ACTIVE_REQUESTS: int = 50
    CRITICAL_ACTIVE_REQUESTS: int = 100

    def evaluate(
        self,
        *,
        proxy_online: bool,
        ollama_online: bool,
        context_percent: float,
        average_latency_ms: float,
        active_requests: int,
    ) -> HealthAssessment:
        """Evaluate raw dashboard metrics and return structured system health."""
        metrics = DashboardMetrics(
            proxy_online=proxy_online,
            ollama_online=ollama_online,
            context_percent=context_percent,
            average_latency_ms=average_latency_ms,
            active_requests=active_requests,
        )
        return self.evaluate_metrics(metrics)

    def evaluate_metrics(self, metrics: DashboardMetrics) -> HealthAssessment:
        """Evaluate normalized metrics and return structured system health."""
        if not metrics.proxy_online:
            return self._assessment(
                HealthStatus.OFFLINE,
                ["proxy_offline"],
                metrics,
            )

        critical_reasons: list[str] = []
        if not metrics.ollama_online:
            critical_reasons.append("ollama_offline")
        if metrics.context_percent >= self.CRITICAL_CONTEXT_PERCENT:
            critical_reasons.append("context_critical")
        if metrics.average_latency_ms >= self.CRITICAL_LATENCY_MS:
            critical_reasons.append("latency_critical")
        if metrics.active_requests >= self.CRITICAL_ACTIVE_REQUESTS:
            critical_reasons.append("request_load_critical")
        if critical_reasons:
            return self._assessment(HealthStatus.CRITICAL, critical_reasons, metrics)

        warning_reasons: list[str] = []
        if metrics.context_percent >= self.WARNING_CONTEXT_PERCENT:
            warning_reasons.append("context_warning")
        if metrics.average_latency_ms >= self.WARNING_LATENCY_MS:
            warning_reasons.append("latency_warning")
        if metrics.active_requests >= self.WARNING_ACTIVE_REQUESTS:
            warning_reasons.append("request_load_warning")
        if warning_reasons:
            return self._assessment(HealthStatus.WARNING, warning_reasons, metrics)

        busy_reasons: list[str] = []
        if metrics.context_percent >= self.BUSY_CONTEXT_PERCENT:
            busy_reasons.append("context_busy")
        if metrics.average_latency_ms >= self.BUSY_LATENCY_MS:
            busy_reasons.append("latency_busy")
        if metrics.active_requests >= self.BUSY_ACTIVE_REQUESTS:
            busy_reasons.append("active_requests")
        if busy_reasons:
            return self._assessment(HealthStatus.BUSY, busy_reasons, metrics)

        return self._assessment(HealthStatus.HEALTHY, ["nominal"], metrics)

    @staticmethod
    def _assessment(
        status: HealthStatus,
        reasons: list[str],
        metrics: DashboardMetrics,
    ) -> HealthAssessment:
        return HealthAssessment(
            status=status,
            reasons=reasons,
            indicators=metrics.to_dict(),
        )
