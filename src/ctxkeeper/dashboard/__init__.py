"""Dashboard routes and intelligence primitives for ContextKeeper."""

from .insights import DashboardInsight, build_dashboard_insights
from .intelligence import DashboardMetrics, HealthAssessment, HealthEngine, HealthStatus
from .recommendations import DashboardRecommendation, build_recommendations
from .timeline import EventTimeline, LiveConversationTimelineEvent, TimelineEvent, build_live_conversation_timeline
from .trends import RequestSample, RollingTrends

__all__ = [
    "DashboardInsight",
    "DashboardMetrics",
    "DashboardRecommendation",
    "EventTimeline",
    "HealthAssessment",
    "HealthEngine",
    "HealthStatus",
    "LiveConversationTimelineEvent",
    "RequestSample",
    "RollingTrends",
    "TimelineEvent",
    "build_dashboard_insights",
    "build_live_conversation_timeline",
    "build_recommendations",
]
