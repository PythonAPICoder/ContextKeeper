from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..config import Settings

SettingDataType = Literal["boolean", "integer", "string"]
SettingValue = bool | int | str


@dataclass(frozen=True)
class DashboardSetting:
    """One read-only runtime setting exposed to dashboard consumers."""

    id: str
    category: str
    display_name: str
    description: str
    value: SettingValue
    default_value: SettingValue
    data_type: SettingDataType
    minimum: int | None = None
    maximum: int | None = None
    runtime_editable: bool = False
    restart_required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "category": self.category,
            "display_name": self.display_name,
            "description": self.description,
            "value": self.value,
            "default_value": self.default_value,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "runtime_editable": self.runtime_editable,
            "restart_required": self.restart_required,
            "data_type": self.data_type,
        }


@dataclass(frozen=True)
class DashboardSettingsCategory:
    """A dashboard settings category containing ordered setting metadata."""

    id: str
    display_name: str
    description: str
    settings: list[DashboardSetting]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "description": self.description,
            "settings": [setting.to_dict() for setting in self.settings],
        }


@dataclass(frozen=True)
class DashboardSettingsSnapshot:
    """Complete read-only settings snapshot for the dashboard Settings surface."""

    schema_version: int
    categories: list[DashboardSettingsCategory]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "categories": [category.to_dict() for category in self.categories],
        }


def build_dashboard_settings_snapshot(settings: Settings) -> DashboardSettingsSnapshot:
    """Build the sanitized read-only settings snapshot from effective runtime settings."""

    defaults = Settings()
    return DashboardSettingsSnapshot(
        schema_version=1,
        categories=[
            DashboardSettingsCategory(
                id="context",
                display_name="Context",
                description="Controls context tracking, pressure thresholds, and recent-message retention.",
                settings=[
                    DashboardSetting(
                        id="context.enabled",
                        category="context",
                        display_name="Context tracking",
                        description="Enable ContextKeeper's conversation context tracking and usage estimates.",
                        value=settings.context.enabled,
                        default_value=defaults.context.enabled,
                        data_type="boolean",
                    ),
                    DashboardSetting(
                        id="context.warning_threshold_percent",
                        category="context",
                        display_name="Warning threshold",
                        description="Context Usage percentage where the dashboard reports approaching context pressure.",
                        value=settings.context.warning_threshold_percent,
                        default_value=defaults.context.warning_threshold_percent,
                        data_type="integer",
                        minimum=0,
                        maximum=100,
                    ),
                    DashboardSetting(
                        id="context.compression_threshold_percent",
                        category="context",
                        display_name="Compression threshold",
                        description="Context Usage percentage where conversations become compression candidates.",
                        value=settings.context.compression_threshold_percent,
                        default_value=defaults.context.compression_threshold_percent,
                        data_type="integer",
                        minimum=0,
                        maximum=100,
                    ),
                    DashboardSetting(
                        id="context.keep_recent_messages",
                        category="context",
                        display_name="Recent messages retained",
                        description="Number of recent messages preserved in active context during compression planning.",
                        value=settings.context.keep_recent_messages,
                        default_value=defaults.context.keep_recent_messages,
                        data_type="integer",
                        minimum=1,
                    ),
                ],
            ),
            DashboardSettingsCategory(
                id="compression",
                display_name="Compression",
                description="Controls rolling-summary compression behavior and summarizer configuration.",
                settings=[
                    DashboardSetting(
                        id="compression.enabled",
                        category="compression",
                        display_name="Compression",
                        description="Enable rolling-summary compression support for conversations under context pressure.",
                        value=settings.compression.enabled,
                        default_value=defaults.compression.enabled,
                        data_type="boolean",
                    ),
                    DashboardSetting(
                        id="compression.summarizer_model",
                        category="compression",
                        display_name="Summarizer model",
                        description="Model name used by the compression summarizer when summaries are generated.",
                        value=settings.compression.summarizer_model,
                        default_value=defaults.compression.summarizer_model,
                        data_type="string",
                    ),
                    DashboardSetting(
                        id="compression.max_summary_tokens",
                        category="compression",
                        display_name="Maximum summary tokens",
                        description="Maximum token budget requested for rolling-summary output.",
                        value=settings.compression.max_summary_tokens,
                        default_value=defaults.compression.max_summary_tokens,
                        data_type="integer",
                        minimum=1,
                    ),
                ],
            ),
            DashboardSettingsCategory(
                id="dashboard",
                display_name="Dashboard",
                description="Controls dashboard refresh behavior.",
                settings=[
                    DashboardSetting(
                        id="dashboard.refresh_interval_ms",
                        category="dashboard",
                        display_name="Refresh interval",
                        description="Dashboard polling interval in milliseconds.",
                        value=settings.dashboard.refresh_interval_ms,
                        default_value=defaults.dashboard.refresh_interval_ms,
                        data_type="integer",
                        minimum=1,
                    ),
                ],
            ),
        ],
    )
