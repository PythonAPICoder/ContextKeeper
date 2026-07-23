"""Atomic persistence for dashboard-approved ContextKeeper settings."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import logging
import os
from pathlib import Path
import stat
import tempfile
from threading import RLock
from typing import Any

from pydantic import ValidationError
import yaml

from ..config import Settings, validate_ollama_not_self_proxy
from ..resources import DEFAULT_CONFIG_NAME, resolve_config_path
from . import settings_snapshot
from .settings_snapshot import (
    DashboardSettingsValidationError,
    PersistedSettingsUpdate,
    SettingValue,
    ValidationDetail,
    validate_dashboard_settings_business_rules,
    validation_error_detail,
)

logger = logging.getLogger("ctxkeeper.dashboard.settings.persistence")

_CONFIGURATION_PERSISTENCE_LOCK = RLock()


class ConfigurationPersistenceError(RuntimeError):
    """Safe, client-facing configuration persistence failure."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        detail: ValidationDetail,
    ) -> None:
        super().__init__(str(detail))
        self.status_code = status_code
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class ConfigurationPersistenceResult:
    """Successful configuration write details without filesystem disclosure."""

    persisted_setting_ids: tuple[str, ...]
    configuration_created: bool
    persisted_settings: Settings


@dataclass(frozen=True)
class _ConfigurationFileState:
    """One freshly read configuration document and its validated state."""

    data: dict[str, Any]
    settings: Settings
    existed: bool
    fingerprint: str | None


class ConfigurationPersistenceService:
    """Persist approved dashboard settings to one resolved YAML file."""

    def __init__(
        self,
        config_path: str | Path = DEFAULT_CONFIG_NAME,
        *,
        listener_host: str | None = None,
        listener_port: int | None = None,
    ) -> None:
        self._config_path = resolve_config_path(config_path)
        self._listener_host = listener_host
        self._listener_port = listener_port

    @property
    def config_path(self) -> Path:
        """Return the resolved path used internally by this service."""

        return self._config_path

    def read_persisted_settings(self) -> Settings:
        """Freshly read and validate the configuration's effective disk values."""

        with _CONFIGURATION_PERSISTENCE_LOCK:
            return self._read_configuration_state().settings

    def persist(self, payload: object) -> ConfigurationPersistenceResult:
        """Validate and atomically persist explicitly supplied setting values."""

        updates = self._validated_updates(payload)
        persisted_ids = tuple(
            sorted(
                f"{category}.{field_name}"
                for category, values in updates.items()
                for field_name in values
            )
        )

        with _CONFIGURATION_PERSISTENCE_LOCK:
            current = self._read_configuration_state()
            candidate_data = deepcopy(current.data)
            for category, values in updates.items():
                category_data = candidate_data.setdefault(category, {})
                if not isinstance(category_data, dict):
                    raise ConfigurationPersistenceError(
                        status_code=409,
                        code="invalid_configuration",
                        detail=(
                            "The active configuration cannot be updated because an approved "
                            "settings category is not a YAML mapping."
                        ),
                    )
                category_data.update(values)

            candidate_settings = self._validate_candidate(candidate_data)
            serialized = self._serialize_candidate(candidate_data)
            self._validate_serialized_candidate(serialized)
            self._commit_candidate(
                serialized,
                expected_fingerprint=current.fingerprint,
            )

            return ConfigurationPersistenceResult(
                persisted_setting_ids=persisted_ids,
                configuration_created=not current.existed,
                persisted_settings=candidate_settings,
            )

    def _validated_updates(
        self,
        payload: object,
    ) -> dict[str, dict[str, SettingValue]]:
        if not isinstance(payload, dict):
            raise ConfigurationPersistenceError(
                status_code=422,
                code="invalid_request",
                detail=[
                    {
                        "loc": ["body"],
                        "msg": "The configuration persistence request must be a JSON object.",
                        "type": "model_attributes_type",
                    }
                ],
            )

        try:
            update = PersistedSettingsUpdate.model_validate(payload)
        except ValidationError as exc:
            raise ConfigurationPersistenceError(
                status_code=422,
                code="validation_failed",
                detail=validation_error_detail(exc),
            ) from exc

        updates = update.update_values()
        if not updates:
            raise ConfigurationPersistenceError(
                status_code=400,
                code="empty_request",
                detail="At least one setting must be supplied for configuration persistence.",
            )

        metadata_by_id = settings_snapshot.dashboard_setting_metadata_by_id()
        for category, values in updates.items():
            for field_name in values:
                setting_id = f"{category}.{field_name}"
                metadata = metadata_by_id.get(setting_id)
                if metadata is None:
                    raise ConfigurationPersistenceError(
                        status_code=422,
                        code="unsupported_setting",
                        detail=[
                            {
                                "loc": ["body", category, field_name],
                                "msg": f"{setting_id} is not an approved dashboard setting.",
                                "type": "value_error",
                            }
                        ],
                    )
                if not metadata.persistable:
                    raise ConfigurationPersistenceError(
                        status_code=422,
                        code="non_persistable_setting",
                        detail=[
                            {
                                "loc": ["body", category, field_name],
                                "msg": f"{setting_id} may not be saved to configuration.",
                                "type": "value_error",
                            }
                        ],
                    )
        return updates

    def _read_configuration_state(self) -> _ConfigurationFileState:
        try:
            raw_bytes = self._config_path.read_bytes()
        except FileNotFoundError:
            data: dict[str, Any] = {}
            return _ConfigurationFileState(
                data=data,
                settings=Settings.model_validate(data),
                existed=False,
                fingerprint=None,
            )
        except OSError as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_read_failed",
                detail="The active configuration file could not be read.",
            ) from exc

        data = self._parse_yaml_mapping(raw_bytes, existing_file=True)
        try:
            settings = Settings.model_validate(data)
        except ValidationError as exc:
            raise ConfigurationPersistenceError(
                status_code=409,
                code="invalid_configuration",
                detail=self._existing_configuration_validation_detail(exc),
            ) from exc

        return _ConfigurationFileState(
            data=data,
            settings=settings,
            existed=True,
            fingerprint=self._fingerprint(raw_bytes),
        )

    def _validate_candidate(self, candidate_data: dict[str, Any]) -> Settings:
        try:
            candidate_settings = Settings.model_validate(candidate_data)
        except ValidationError as exc:
            raise ConfigurationPersistenceError(
                status_code=422,
                code="validation_failed",
                detail=validation_error_detail(exc),
            ) from exc

        if self._listener_host is not None and self._listener_port is not None:
            try:
                validate_ollama_not_self_proxy(
                    candidate_settings.ollama.base_url,
                    listener_host=self._listener_host,
                    listener_port=self._listener_port,
                )
            except ValueError as exc:
                raise ConfigurationPersistenceError(
                    status_code=422,
                    code="validation_failed",
                    detail=[
                        {
                            "loc": ["body", "ollama", "base_url"],
                            "msg": str(exc),
                            "type": "value_error",
                        }
                    ],
                ) from exc

        try:
            validate_dashboard_settings_business_rules(candidate_settings)
        except DashboardSettingsValidationError as exc:
            raise ConfigurationPersistenceError(
                status_code=422,
                code="validation_failed",
                detail=exc.detail,
            ) from exc
        return candidate_settings

    def _serialize_candidate(self, candidate_data: dict[str, Any]) -> str:
        try:
            return yaml.safe_dump(
                candidate_data,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )
        except (TypeError, ValueError, yaml.YAMLError) as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_serialization_failed",
                detail="The configuration update could not be serialized safely.",
            ) from exc

    def _validate_serialized_candidate(self, serialized: str) -> None:
        serialized_data = self._parse_yaml_mapping(
            serialized.encode("utf-8"),
            existing_file=False,
        )
        self._validate_candidate(serialized_data)

    def _commit_candidate(
        self,
        serialized: str,
        *,
        expected_fingerprint: str | None,
    ) -> None:
        destination_mode = self._destination_mode()
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_directory_failed",
                detail="The configuration directory could not be prepared for writing.",
            ) from exc

        descriptor: int | None = None
        temporary_path: Path | None = None
        try:
            try:
                descriptor, temporary_name = tempfile.mkstemp(
                    dir=self._config_path.parent,
                    prefix=f".{self._config_path.name}.",
                    suffix=".tmp",
                )
                temporary_path = Path(temporary_name)
                self._write_temporary_candidate(descriptor, serialized)
                os.close(descriptor)
                descriptor = None
                if destination_mode is not None:
                    os.chmod(temporary_path, destination_mode)
                self._validate_written_candidate(temporary_path, serialized)
            except ConfigurationPersistenceError:
                raise
            except OSError as exc:
                raise ConfigurationPersistenceError(
                    status_code=500,
                    code="temporary_write_failed",
                    detail="The configuration update could not be written to a temporary file.",
                ) from exc

            if self._current_fingerprint() != expected_fingerprint:
                raise ConfigurationPersistenceError(
                    status_code=409,
                    code="stale_configuration",
                    detail=(
                        "The active configuration changed while this save was being prepared. "
                        "Reload settings and try again."
                    ),
                )

            try:
                self._replace_configuration(temporary_path)
            except OSError as exc:
                raise ConfigurationPersistenceError(
                    status_code=500,
                    code="atomic_replace_failed",
                    detail="The configuration update could not replace the active file atomically.",
                ) from exc
            temporary_path = None
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    logger.warning(
                        "Configuration persistence temporary descriptor cleanup failed"
                    )
            if temporary_path is not None:
                self._cleanup_temporary_file(temporary_path)

    def _destination_mode(self) -> int | None:
        try:
            mode = stat.S_IMODE(self._config_path.stat().st_mode)
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_access_failed",
                detail="The active configuration file permissions could not be checked.",
            ) from exc
        if mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_read_only",
                detail="The active configuration file is read-only and could not be saved.",
            )
        return mode

    @staticmethod
    def _write_temporary_candidate(descriptor: int, serialized: str) -> None:
        with os.fdopen(
            descriptor,
            mode="w",
            encoding="utf-8",
            newline="\n",
            closefd=False,
        ) as temporary_file:
            temporary_file.write(serialized)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

    def _validate_written_candidate(self, temporary_path: Path, serialized: str) -> None:
        try:
            written_bytes = temporary_path.read_bytes()
        except OSError as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="temporary_validation_failed",
                detail="The temporary configuration update could not be verified.",
            ) from exc
        if written_bytes != serialized.encode("utf-8"):
            raise ConfigurationPersistenceError(
                status_code=500,
                code="temporary_validation_failed",
                detail="The temporary configuration update did not match the validated content.",
            )
        self._parse_yaml_mapping(written_bytes, existing_file=False)

    def _current_fingerprint(self) -> str | None:
        try:
            return self._fingerprint(self._config_path.read_bytes())
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise ConfigurationPersistenceError(
                status_code=500,
                code="configuration_read_failed",
                detail="The active configuration file could not be re-read before saving.",
            ) from exc

    def _replace_configuration(self, temporary_path: Path) -> None:
        os.replace(temporary_path, self._config_path)

    @staticmethod
    def _cleanup_temporary_file(temporary_path: Path) -> None:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Configuration persistence temporary-file cleanup failed")

    @staticmethod
    def _fingerprint(raw_bytes: bytes) -> str:
        return hashlib.sha256(raw_bytes).hexdigest()

    @staticmethod
    def _parse_yaml_mapping(
        raw_bytes: bytes,
        *,
        existing_file: bool,
    ) -> dict[str, Any]:
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            message = (
                "The active configuration file is not valid UTF-8."
                if existing_file
                else "The configuration update could not be encoded as valid UTF-8."
            )
            raise ConfigurationPersistenceError(
                status_code=409 if existing_file else 500,
                code="invalid_configuration_encoding",
                detail=message,
            ) from exc
        try:
            loaded = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            message = (
                "The active configuration file contains malformed YAML. Correct it before saving settings."
                if existing_file
                else "The serialized configuration update is not valid YAML."
            )
            raise ConfigurationPersistenceError(
                status_code=409 if existing_file else 500,
                code="invalid_configuration_yaml",
                detail=message,
            ) from exc
        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            message = (
                "The active configuration file must contain a YAML mapping."
                if existing_file
                else "The serialized configuration update must contain a YAML mapping."
            )
            raise ConfigurationPersistenceError(
                status_code=409 if existing_file else 500,
                code="invalid_configuration_shape",
                detail=message,
            )
        return loaded

    @staticmethod
    def _existing_configuration_validation_detail(
        exc: ValidationError,
    ) -> list[dict[str, object]]:
        details = validation_error_detail(exc)
        for detail in details:
            location = detail.get("loc")
            if isinstance(location, list) and location[:1] == ["body"]:
                detail["loc"] = ["configuration", *location[1:]]
        return details
