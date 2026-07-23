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

from ..config import (
    Settings,
    normalize_ollama_base_url,
    validate_ollama_timeout_seconds,
)

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


class DashboardSettingsValidationError(ValueError):
    """Shared dashboard settings business-rule validation failure."""

    def __init__(self, detail: ValidationDetail) -> None:
        super().__init__(str(detail))
        self.detail = detail


class _StrictSettingsUpdateModel(BaseModel):
    """Strict base model for partial dashboard settings updates."""

    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def _reject_null_values(cls, value: object) -> object:
        if value is None:
            raise ValueError("Settings values may not be null.")
        return value

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


class RuntimeContextSettingsUpdate(_StrictSettingsUpdateModel):
    """Partial update payload for context runtime settings."""

    enabled: StrictBool | None = None
    warning_threshold_percent: StrictInt | None = None
    compression_threshold_percent: StrictInt | None = None
    keep_recent_messages: StrictInt | None = None


class RuntimeCompressionSettingsUpdate(_StrictSettingsUpdateModel):
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


class RuntimeDashboardSettingsUpdate(_StrictSettingsUpdateModel):
    """Partial update payload for dashboard runtime settings."""

    refresh_interval_ms: StrictInt | None = None


class RuntimeSettingsUpdate(_StrictSettingsUpdateModel):
    """Partial update payload for all runtime-editable dashboard settings."""

    context: RuntimeContextSettingsUpdate | None = None
    compression: RuntimeCompressionSettingsUpdate | None = None
    dashboard: RuntimeDashboardSettingsUpdate | None = None


class PersistedOllamaSettingsUpdate(_StrictSettingsUpdateModel):
    """Partial persisted-only update payload for Ollama connection settings."""

    base_url: StrictStr | None = None
    timeout_seconds: StrictInt | None = None

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str | None) -> str | None:
        return None if value is None else normalize_ollama_base_url(value)

    @field_validator("timeout_seconds")
    @classmethod
    def _validate_timeout_seconds(cls, value: int | None) -> int | None:
        return None if value is None else validate_ollama_timeout_seconds(value)


class PersistedSettingsUpdate(_StrictSettingsUpdateModel):
    """Partial update payload for all dashboard-persistable settings."""

    context: RuntimeContextSettingsUpdate | None = None
    compression: RuntimeCompressionSettingsUpdate | None = None
    dashboard: RuntimeDashboardSettingsUpdate | None = None
    ollama: PersistedOllamaSettingsUpdate | None = None


@dataclass(frozen=True)
class DashboardSetting:
    """One approved setting exposed to dashboard consumers."""

    id: str
    category: str
    display_name: str
    description: str
    value: SettingValue
    persisted_value: SettingValue
    default_value: SettingValue
    data_type: SettingDataType
    minimum: int | None = None
    maximum: int | None = None
    runtime_editable: bool = True
    persistable: bool = True
    restart_required: bool = False
    reset_eligible: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "category": self.category,
            "display_name": self.display_name,
            "description": self.description,
            "value": self.value,
            "persisted_value": self.persisted_value,
            "default_value": self.default_value,
            "differs_from_persisted": (
                type(self.value) is not type(self.persisted_value)
                or self.value != self.persisted_value
            ),
            "minimum": self.minimum,
            "maximum": self.maximum,
            "runtime_editable": self.runtime_editable,
            "persistable": self.persistable,
            "restart_required": self.restart_required,
            "reset_eligible": self.reset_eligible,
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


def build_dashboard_settings_snapshot(
    settings: Settings,
    persisted_settings: Settings | None = None,
) -> DashboardSettingsSnapshot:
    """Build a sanitized snapshot from runtime and persisted settings state.

    Callers that do not provide a persisted settings object retain the B6.1/B6.2
    behavior of describing the supplied settings as the confirmed state. API
    routes provide a freshly read persisted settings object so disk differences
    are represented explicitly.
    """

    defaults = Settings()
    persisted = persisted_settings or settings
    with _RUNTIME_SETTINGS_LOCK:
        return DashboardSettingsSnapshot(
            schema_version=2,
            categories=[
                DashboardSettingsCategory(
                    id="ollama",
                    display_name="Connection",
                    description="Configures the Ollama backend used after the next ContextKeeper restart.",
                    settings=[
                        DashboardSetting(
                            id="ollama.base_url",
                            category="ollama",
                            display_name="AI Server Endpoint",
                            description="Complete HTTP or HTTPS URL for the single Ollama backend.",
                            value=settings.ollama.base_url,
                            persisted_value=persisted.ollama.base_url,
                            default_value=defaults.ollama.base_url,
                            data_type="string",
                            runtime_editable=False,
                            persistable=True,
                            restart_required=True,
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="ollama.timeout_seconds",
                            category="ollama",
                            display_name="Request Timeout",
                            description="Maximum request duration in seconds for Ollama operations.",
                            value=settings.ollama.timeout_seconds,
                            persisted_value=persisted.ollama.timeout_seconds,
                            default_value=defaults.ollama.timeout_seconds,
                            data_type="integer",
                            minimum=1,
                            runtime_editable=False,
                            persistable=True,
                            restart_required=True,
                            reset_eligible=True,
                        ),
                    ],
                ),
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
                            persisted_value=persisted.context.enabled,
                            default_value=defaults.context.enabled,
                            data_type="boolean",
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="context.warning_threshold_percent",
                            category="context",
                            display_name="Warning threshold",
                            description="Context Usage percentage where the dashboard reports approaching context pressure.",
                            value=settings.context.warning_threshold_percent,
                            persisted_value=persisted.context.warning_threshold_percent,
                            default_value=defaults.context.warning_threshold_percent,
                            data_type="integer",
                            minimum=0,
                            maximum=100,
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="context.compression_threshold_percent",
                            category="context",
                            display_name="Compression threshold",
                            description="Context Usage percentage where conversations become compression candidates.",
                            value=settings.context.compression_threshold_percent,
                            persisted_value=persisted.context.compression_threshold_percent,
                            default_value=defaults.context.compression_threshold_percent,
                            data_type="integer",
                            minimum=0,
                            maximum=100,
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="context.keep_recent_messages",
                            category="context",
                            display_name="Recent messages retained",
                            description="Number of recent messages preserved in active context during compression planning.",
                            value=settings.context.keep_recent_messages,
                            persisted_value=persisted.context.keep_recent_messages,
                            default_value=defaults.context.keep_recent_messages,
                            data_type="integer",
                            minimum=1,
                            reset_eligible=True,
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
                            persisted_value=persisted.compression.enabled,
                            default_value=defaults.compression.enabled,
                            data_type="boolean",
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="compression.summarizer_model",
                            category="compression",
                            display_name="Summarizer model",
                            description="Model name used by the compression summarizer when summaries are generated.",
                            value=settings.compression.summarizer_model,
                            persisted_value=persisted.compression.summarizer_model,
                            default_value=defaults.compression.summarizer_model,
                            data_type="string",
                            reset_eligible=True,
                        ),
                        DashboardSetting(
                            id="compression.max_summary_tokens",
                            category="compression",
                            display_name="Maximum summary tokens",
                            description="Maximum token budget requested for rolling-summary output.",
                            value=settings.compression.max_summary_tokens,
                            persisted_value=persisted.compression.max_summary_tokens,
                            default_value=defaults.compression.max_summary_tokens,
                            data_type="integer",
                            minimum=1,
                            reset_eligible=True,
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
                            persisted_value=persisted.dashboard.refresh_interval_ms,
                            default_value=defaults.dashboard.refresh_interval_ms,
                            data_type="integer",
                            minimum=1,
                            reset_eligible=True,
                        ),
                    ],
                ),
            ],
        )


def dashboard_setting_metadata_by_id() -> dict[str, DashboardSetting]:
    """Return the authoritative dashboard setting metadata indexed by id."""

    defaults = Settings()
    snapshot = build_dashboard_settings_snapshot(defaults, defaults)
    return {
        setting.id: setting
        for category in snapshot.categories
        for setting in category.settings
    }


def update_runtime_settings(
    settings: Settings,
    update: RuntimeSettingsUpdate,
    *,
    persisted_settings: Settings | None = None,
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
                detail=validation_error_detail(exc),
            ) from exc

        try:
            validate_dashboard_settings_business_rules(proposed)
        except DashboardSettingsValidationError as exc:
            raise RuntimeSettingsUpdateError(
                status_code=422,
                detail=exc.detail,
            ) from exc

        settings.context = proposed.context
        settings.compression = proposed.compression
        settings.dashboard = proposed.dashboard

        return build_dashboard_settings_snapshot(settings, persisted_settings)


def validate_dashboard_settings_business_rules(settings: Settings) -> None:
    """Validate cross-field rules shared by runtime and persistence updates."""

    if settings.context.warning_threshold_percent >= settings.context.compression_threshold_percent:
        raise DashboardSettingsValidationError(
            [
                {
                    "loc": ["body", "context", "warning_threshold_percent"],
                    "msg": "context.warning_threshold_percent must be less than compression_threshold_percent.",
                    "type": "value_error",
                }
            ],
        )


def validation_error_detail(exc: ValidationError) -> list[dict[str, object]]:
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
