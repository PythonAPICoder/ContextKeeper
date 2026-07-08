"""Rule-based dashboard recommendations for operator workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .intelligence import DashboardMetrics, HealthEngine

RecommendationPriority = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class DashboardRecommendation:
    """Rule-based recommendation for dashboard operators."""

    code: str
    message: str
    priority: RecommendationPriority

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation of the recommendation."""
        return {
            "code": self.code,
            "message": self.message,
            "priority": self.priority,
        }


def build_recommendations(metrics: DashboardMetrics) -> list[DashboardRecommendation]:
    """Build deterministic dashboard recommendations from current metrics."""
    recommendations: list[DashboardRecommendation] = []

    if not metrics.proxy_online:
        return [
            DashboardRecommendation(
                "restore_proxy",
                "Restore the ContextKeeper proxy before handling downstream issues.",
                "high",
            )
        ]

    if not metrics.ollama_online:
        recommendations.append(
            DashboardRecommendation(
                "check_ollama",
                "Ollama is unavailable; verify the service is running and reachable.",
                "high",
            )
        )

    if metrics.context_percent >= HealthEngine.CRITICAL_CONTEXT_PERCENT:
        recommendations.append(
            DashboardRecommendation(
                "compress_now",
                "Compress context now to protect the active conversation.",
                "high",
            )
        )
    elif metrics.context_percent >= HealthEngine.WARNING_CONTEXT_PERCENT:
        recommendations.append(
            DashboardRecommendation(
                "compression_likely",
                "Compression likely within a few messages.",
                "medium",
            )
        )

    if metrics.average_latency_ms >= HealthEngine.CRITICAL_LATENCY_MS:
        recommendations.append(
            DashboardRecommendation(
                "ollama_overloaded",
                "Ollama appears overloaded.",
                "high",
            )
        )
    elif metrics.average_latency_ms >= HealthEngine.WARNING_LATENCY_MS:
        recommendations.append(
            DashboardRecommendation(
                "watch_latency",
                "Watch latency and reduce concurrent load if it continues rising.",
                "medium",
            )
        )

    if metrics.active_requests >= HealthEngine.CRITICAL_ACTIVE_REQUESTS:
        recommendations.append(
            DashboardRecommendation(
                "shed_load",
                "Reduce request concurrency until the active queue drains.",
                "high",
            )
        )
    elif metrics.active_requests >= HealthEngine.WARNING_ACTIVE_REQUESTS:
        recommendations.append(
            DashboardRecommendation(
                "monitor_load",
                "Monitor active requests for queue buildup.",
                "medium",
            )
        )

    if not recommendations:
        recommendations.append(
            DashboardRecommendation(
                "no_action",
                "No action recommended.",
                "low",
            )
        )

    return recommendations
