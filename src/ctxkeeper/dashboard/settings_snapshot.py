from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
)

from ..config import Settings

SettingDataType = Literal["boolean", "integer", "string"]
SettingValue = bool | int | str
ValidationDetail = str | list[dict[str, object]]

_RUNTIME_SETTINGS_LOCK = RLock()


class RuntimeSettingsUpdateError(ValueError):
    """Client-facing runtime settings update validation failure."""

    def __init__(self, *, status_code: int, detail: ValidationDetail) -> None:
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


class _RuntimeSettingsUpdateModel(BaseModel):
    """Strict base model for partial runtime settings updates."""

    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def _reject_null_values(cls, value: object) -> object:
        if value is None:
            raise ValueError("Runtime settings values may not be null.")
        return value


class RuntimeContextSettingsUpdate(_RuntimeSettingsUpdateModel):
    """Partial update payload for context runtime settings."""

    enabled: StrictBool | None = None
    warning_threshold_percent: StrictInt | None = None
    compression_threshold_percent: StrictInt | None = None
    keep_recent_messages: StrictInt | None = None


class RuntimeCompressionSettingsUpdate(_RuntimeSettingsUpdateModel):
    """Partial update payload for compression runtime settings."""

    enabled: StrictBool | None = None
    summarizer_model: StrictStr | None = None
    max_summary_tokens: StrictInt | None = None

    @field_validator("summarizer_model")
    @classmethod
    def _validate_summarizer_model(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("compression.summarizer_model must not be blank.")
        return normalized


class RuntimeDashboardSettingsUpdate(_RuntimeSettingsUpdateModel):
    """Partial update payload for dashboard runtime settings."""

    refresh_interval_ms: StrictInt | None = None


class RuntimeSettingsUpdate(_RuntimeSettingsUpdateModel):
    """Partial update payload for all runtime-editable dashboard settings."""

    context: RuntimeContextSettingsUpdate | None = None
    compression: RuntimeCompressionSettingsUpdate | None = None
    dashboard: RuntimeDashboardSettingsUpdate | None = None

    def update_values(self) -> dict[str, dict[str, SettingValue]]:
        """Return explicitly supplied setting values, omitting empty sections."""

        supplied = self.model_dump(exclude_unset=True)
        updates: dict[str, dict[str, SettingValue]] = {}
        for category, category_values in supplied.items():
            if not isinstance(category_values, dict):
                continue
            values = {
                key: value
                for key, value in category_values.items()
                if value is not None
            }
            if values:
                updates[category] = values
        return updates


@dataclass(frozen=True)
class DashboardSetting:
    """One runtime setting exposed to dashboard consumers."""

    id: str
    category: str
    display_name: str
    description: str
    value: SettingValue
    default_value: SettingValue
    data_type: SettingDataType
    minimum: int | None = None
    maximum: int | None = None
    runtime_editable: bool = True
    restart_required: bool = False

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
    """Complete settings snapshot for the dashboard Settings surface."""

    schema_version: int
    categories: list[DashboardSettingsCategory]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "categories": [category.to_dict() for category in self.categories],
        }


def build_dashboard_settings_snapshot(settings: Settings) -> DashboardSettingsSnapshot:
    """Build the sanitized settings snapshot from effective runtime settings."""

    defaults = Settings()
    with _RUNTIME_SETTINGS_LOCK:
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


def update_runtime_settings(
    settings: Settings,
    update: RuntimeSettingsUpdate,
) -> DashboardSettingsSnapshot:
    """Atomically validate and apply a partial runtime settings update."""

    updates = update.update_values()
    if not updates:
        raise RuntimeSettingsUpdateError(
            status_code=400,
            detail="At least one runtime setting must be supplied.",
        )

    with _RUNTIME_SETTINGS_LOCK:
        proposed_data = settings.model_dump()
        for category, category_values in updates.items():
            proposed_data[category].update(category_values)

        try:
            proposed = Settings.model_validate(proposed_data)
        except ValidationError as exc:
            raise RuntimeSettingsUpdateError(
                status_code=422,
                detail=_validation_error_detail(exc),
            ) from exc

        _validate_runtime_threshold_order(proposed)

        settings.context = proposed.context
        settings.compression = proposed.compression
        settings.dashboard = proposed.dashboard

        return build_dashboard_settings_snapshot(settings)


def _validate_runtime_threshold_order(settings: Settings) -> None:
    if settings.context.warning_threshold_percent >= settings.context.compression_threshold_percent:
        raise RuntimeSettingsUpdateError(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "context", "warning_threshold_percent"],
                    "msg": "context.warning_threshold_percent must be less than compression_threshold_percent.",
                    "type": "value_error",
                }
            ],
        )


def _validation_error_detail(exc: ValidationError) -> list[dict[str, object]]:
    details: list[dict[str, object]] = []
    for error in exc.errors():
        detail: dict[str, object] = {
            "loc": ["body", *error.get("loc", ())],
            "msg": str(error.get("msg", "Invalid runtime settings update.")),
            "type": str(error.get("type", "value_error")),
        }
        ctx = error.get("ctx")
        if isinstance(ctx, dict):
            detail["ctx"] = {str(key): str(value) for key, value in ctx.items()}
        details.append(detail)
    return details
