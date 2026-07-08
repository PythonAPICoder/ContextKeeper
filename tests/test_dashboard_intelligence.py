from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ctxkeeper.dashboard import (
    DashboardMetrics,
    EventTimeline,
    HealthEngine,
    HealthStatus,
    RollingTrends,
    build_dashboard_insights,
    build_recommendations,
)


def _metrics(
    *,
    proxy_online: bool = True,
    ollama_online: bool = True,
    context_percent: float = 10.0,
    average_latency_ms: float = 100.0,
    active_requests: int = 0,
) -> DashboardMetrics:
    return DashboardMetrics(
        proxy_online=proxy_online,
        ollama_online=ollama_online,
        context_percent=context_percent,
        average_latency_ms=average_latency_ms,
        active_requests=active_requests,
    )


def test_health_engine_reports_healthy_when_metrics_are_nominal() -> None:
    assessment = HealthEngine().evaluate_metrics(_metrics())

    assert assessment.status is HealthStatus.HEALTHY
    assert assessment.reasons == ["nominal"]
    assert assessment.to_dict()["status"] == "healthy"


@pytest.mark.parametrize(
    ("metrics", "expected_status", "expected_reason"),
    [
        (_metrics(proxy_online=False), HealthStatus.OFFLINE, "proxy_offline"),
        (_metrics(ollama_online=False), HealthStatus.CRITICAL, "ollama_offline"),
        (_metrics(context_percent=95.0), HealthStatus.CRITICAL, "context_critical"),
        (_metrics(average_latency_ms=5_000.0), HealthStatus.CRITICAL, "latency_critical"),
        (_metrics(active_requests=100), HealthStatus.CRITICAL, "request_load_critical"),
        (_metrics(context_percent=85.0), HealthStatus.WARNING, "context_warning"),
        (_metrics(average_latency_ms=2_000.0), HealthStatus.WARNING, "latency_warning"),
        (_metrics(active_requests=50), HealthStatus.WARNING, "request_load_warning"),
        (_metrics(context_percent=70.0), HealthStatus.BUSY, "context_busy"),
        (_metrics(average_latency_ms=1_000.0), HealthStatus.BUSY, "latency_busy"),
        (_metrics(active_requests=1), HealthStatus.BUSY, "active_requests"),
    ],
)
def test_health_engine_applies_deterministic_thresholds(
    metrics: DashboardMetrics,
    expected_status: HealthStatus,
    expected_reason: str,
) -> None:
    assessment = HealthEngine().evaluate_metrics(metrics)

    assert assessment.status is expected_status
    assert expected_reason in assessment.reasons


def test_health_engine_accepts_raw_metric_inputs() -> None:
    assessment = HealthEngine().evaluate(
        proxy_online=True,
        ollama_online=True,
        context_percent=88.0,
        average_latency_ms=100.0,
        active_requests=0,
    )

    assert assessment.status is HealthStatus.WARNING
    assert assessment.indicators["context_percent"] == 88.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"context_percent": -1.0},
        {"average_latency_ms": -1.0},
        {"active_requests": -1},
    ],
)
def test_dashboard_metrics_reject_invalid_values(kwargs: dict[str, float | int]) -> None:
    with pytest.raises(ValueError):
        _metrics(**kwargs)


def test_build_dashboard_insights_returns_human_readable_structured_items() -> None:
    insights = build_dashboard_insights(
        _metrics(context_percent=86.0, average_latency_ms=2_100.0),
        active_errors=0,
    )

    messages = [insight.message for insight in insights]
    assert "Proxy healthy" in messages
    assert "Context nearing compression" in messages
    assert "High latency detected" in messages
    assert "No active errors" in messages
    assert insights[0].to_dict() == {
        "code": "proxy_healthy",
        "message": "Proxy healthy",
        "severity": "positive",
    }


def test_build_dashboard_insights_reports_service_and_error_problems() -> None:
    insights = build_dashboard_insights(
        _metrics(proxy_online=False, ollama_online=False, context_percent=96.0),
        active_errors=2,
    )

    assert {insight.code for insight in insights} >= {
        "proxy_offline",
        "ollama_offline",
        "context_critical",
        "active_errors",
    }


def test_build_recommendations_returns_no_action_for_nominal_metrics() -> None:
    recommendations = build_recommendations(_metrics())

    assert len(recommendations) == 1
    assert recommendations[0].message == "No action recommended."
    assert recommendations[0].priority == "low"


def test_build_recommendations_combines_relevant_operator_actions() -> None:
    recommendations = build_recommendations(
        _metrics(
            context_percent=90.0,
            average_latency_ms=5_200.0,
            active_requests=55,
        )
    )

    messages = [recommendation.message for recommendation in recommendations]
    assert "Compression likely within a few messages." in messages
    assert "Ollama appears overloaded." in messages
    assert "Monitor active requests for queue buildup." in messages


def test_build_recommendations_prioritizes_proxy_outage() -> None:
    recommendations = build_recommendations(_metrics(proxy_online=False, ollama_online=False))

    assert len(recommendations) == 1
    assert recommendations[0].code == "restore_proxy"
    assert recommendations[0].priority == "high"


def test_event_timeline_stores_recent_events_newest_first_with_timestamps() -> None:
    timestamps = iter(
        [
            datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 8, 12, 1, tzinfo=timezone.utc),
            datetime(2026, 7, 8, 12, 2, tzinfo=timezone.utc),
        ]
    )
    timeline = EventTimeline(clock=lambda: next(timestamps))

    timeline.add_event("Proxy started")
    timeline.add_event("Ollama checked")
    timeline.add_event("Request completed")

    recent = timeline.recent_events(limit=2)
    assert [event.message for event in recent] == ["Request completed", "Ollama checked"]
    assert recent[0].to_dict()["timestamp"] == "2026-07-08T12:02:00+00:00"


def test_event_timeline_validates_inputs() -> None:
    timeline = EventTimeline()

    with pytest.raises(ValueError):
        timeline.add_event(" ")
    with pytest.raises(ValueError):
        timeline.recent_events(limit=0)


def test_rolling_trends_calculates_request_rate_latency_and_direction() -> None:
    trends = RollingTrends(max_samples=10)
    start = datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc)

    for offset_seconds, latency_ms in [(0, 100.0), (20, 150.0), (40, 300.0), (60, 450.0)]:
        trends.record_request(
            latency_ms=latency_ms,
            timestamp=start + timedelta(seconds=offset_seconds),
        )

    assert trends.average_request_rate() == 4.0
    assert trends.average_latency() == 250.0
    assert trends.trend_direction() == "up"
    assert len(trends.samples()) == 4


def test_rolling_trends_reports_down_and_flat_latency_directions() -> None:
    start = datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc)
    down = RollingTrends()
    flat = RollingTrends()

    for index, latency_ms in enumerate([500.0, 450.0, 200.0, 150.0]):
        down.record_request(latency_ms=latency_ms, timestamp=start + timedelta(seconds=index))
    for index, latency_ms in enumerate([200.0, 205.0, 210.0, 215.0]):
        flat.record_request(latency_ms=latency_ms, timestamp=start + timedelta(seconds=index))

    assert down.trend_direction() == "down"
    assert flat.trend_direction() == "flat"


def test_rolling_trends_validates_inputs() -> None:
    with pytest.raises(ValueError):
        RollingTrends(max_samples=1)

    trends = RollingTrends()
    with pytest.raises(ValueError):
        trends.record_request(latency_ms=-1.0)
