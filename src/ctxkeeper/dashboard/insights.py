"""Insight generation for dashboard intelligence consumers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .intelligence import DashboardMetrics, HealthEngine

InsightSeverity = Literal["positive", "info", "warning", "critical"]


@dataclass(frozen=True)
class DashboardInsight:
    """Human-readable insight with metadata for future UI rendering."""

    code: str
    message: str
    severity: InsightSeverity

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation of the insight."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }


def build_dashboard_insights(
    metrics: DashboardMetrics,
    *,
    active_errors: int = 0,
) -> list[DashboardInsight]:
    """Build deterministic human-readable insights from dashboard metrics."""
    if active_errors < 0:
        raise ValueError("active_errors must be greater than or equal to 0")

    insights: list[DashboardInsight] = []

    if metrics.proxy_online:
        insights.append(DashboardInsight("proxy_healthy", "Proxy healthy", "positive"))
    else:
        insights.append(DashboardInsight("proxy_offline", "Proxy offline", "critical"))

    if not metrics.ollama_online:
        insights.append(DashboardInsight("ollama_offline", "Ollama unavailable", "critical"))

    if metrics.context_percent >= HealthEngine.CRITICAL_CONTEXT_PERCENT:
        insights.append(DashboardInsight("context_critical", "Context compression threshold reached", "critical"))
    elif metrics.context_percent >= HealthEngine.WARNING_CONTEXT_PERCENT:
        insights.append(DashboardInsight("context_near_compression", "Context nearing compression", "warning"))

    if metrics.average_latency_ms >= HealthEngine.WARNING_LATENCY_MS:
        insights.append(DashboardInsight("high_latency", "High latency detected", "warning"))
    elif metrics.average_latency_ms >= HealthEngine.BUSY_LATENCY_MS:
        insights.append(DashboardInsight("elevated_latency", "Latency elevated", "info"))

    if metrics.active_requests >= HealthEngine.WARNING_ACTIVE_REQUESTS:
        insights.append(DashboardInsight("request_load_high", "High active request load", "warning"))

    if active_errors == 0:
        insights.append(DashboardInsight("no_active_errors", "No active errors", "positive"))
    else:
        insights.append(DashboardInsight("active_errors", "Active errors detected", "critical"))

    return insights
