from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from uuid import uuid4


GENERATION_ACTIVITY_ENDPOINTS = frozenset(
    {
        "/api/chat",
        "/api/generate",
        "/v1/chat/completions",
        "/v1/completions",
    }
)

METADATA_ENDPOINTS = frozenset(
    {
        "/api/show",
        "/api/tags",
        "/api/version",
        "/api/ps",
    }
)


class ActivityState(str, Enum):
    """Operational activity states exposed to dashboard consumers."""

    STARTING = "starting"
    CONNECTING = "connecting"
    READY = "ready"
    RECEIVING = "receiving"
    THINKING = "thinking"
    STREAMING = "streaming"
    FINALIZING = "finalizing"
    IDLE = "idle"


_STATE_LABELS: dict[ActivityState, str] = {
    ActivityState.STARTING: "Starting",
    ActivityState.CONNECTING: "Connecting to Ollama",
    ActivityState.READY: "Ready",
    ActivityState.RECEIVING: "Receiving Request",
    ActivityState.THINKING: "Thinking",
    ActivityState.STREAMING: "Streaming Response",
    ActivityState.FINALIZING: "Finalizing Request",
    ActivityState.IDLE: "Idle",
}

_ACTIVE_STATE_PRECEDENCE: tuple[ActivityState, ...] = (
    ActivityState.STREAMING,
    ActivityState.THINKING,
    ActivityState.RECEIVING,
    ActivityState.FINALIZING,
)


@dataclass(frozen=True)
class ActivitySnapshot:
    state: ActivityState
    label: str
    active_request_count: int
    updated_at: datetime
    details: str
    active_model: str | None
    active_model_state: str
    active_generation_sequence: int | None
    active_endpoint: str | None
    active_request_id: str | None
    active_accepted_at: datetime | None
    latest_model: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "label": self.label,
            "active_request_count": self.active_request_count,
            "updated_at": self.updated_at.isoformat(),
            "details": self.details,
            "active_model": self.active_model,
            "active_model_state": self.active_model_state,
            "active_generation_sequence": self.active_generation_sequence,
            "active_endpoint": self.active_endpoint,
            "active_request_id": self.active_request_id,
            "active_accepted_at": self.active_accepted_at.isoformat() if self.active_accepted_at is not None else None,
            "latest_model": self.latest_model,
        }


@dataclass
class _TrackedRequest:
    request_id: str
    method: str
    endpoint: str
    model: str | None
    generation_sequence: int | None
    state: ActivityState
    accepted_at: datetime
    updated_at: datetime


def is_generation_activity_request(method: str, endpoint: str) -> bool:
    """Return True when an inbound request should affect operational activity."""

    return method.upper() == "POST" and endpoint in GENERATION_ACTIVITY_ENDPOINTS


class OperationalActivityManager:
    """Thread-safe lifecycle registry for current generation activity."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._requests: dict[str, _TrackedRequest] = {}
        self._state = ActivityState.STARTING
        self._updated_at = _utcnow()
        self._ollama_available: bool | None = None
        self._has_completed_generation = False
        self._latest_model: str | None = None

    def reset(self) -> None:
        """Reset manager state. Intended for isolated tests and app bootstrap."""

        with self._lock:
            self._requests.clear()
            self._state = ActivityState.STARTING
            self._updated_at = _utcnow()
            self._ollama_available = None
            self._has_completed_generation = False
            self._latest_model = None

    def observe_ollama_status(self, status: object) -> None:
        """Update availability from a dashboard Ollama probe result."""

        available = status == "online"
        with self._lock:
            self._ollama_available = available
            self._refresh_aggregate_state_locked()

    def observe_ollama_available(self, available: bool) -> None:
        """Update availability from a direct request outcome."""

        with self._lock:
            self._ollama_available = available
            self._refresh_aggregate_state_locked()

    def accept_request(
        self,
        *,
        method: str,
        endpoint: str,
        model: str | None,
        request_id: str | None = None,
        generation_sequence: int | None = None,
    ) -> str:
        """Register an accepted generation request in RECEIVING state."""

        now = _utcnow()
        tracked_id = request_id or uuid4().hex
        with self._lock:
            if model:
                self._latest_model = model
            self._requests[tracked_id] = _TrackedRequest(
                request_id=tracked_id,
                method=method.upper(),
                endpoint=endpoint,
                model=model,
                generation_sequence=generation_sequence,
                state=ActivityState.RECEIVING,
                accepted_at=now,
                updated_at=now,
            )
            self._refresh_aggregate_state_locked(force_updated_at=now)
        return tracked_id

    def mark_thinking(self, request_id: str) -> None:
        self._set_request_state(request_id, ActivityState.THINKING)

    def mark_streaming(self, request_id: str) -> None:
        self._set_request_state(request_id, ActivityState.STREAMING)

    def mark_finalizing(self, request_id: str) -> None:
        self._set_request_state(request_id, ActivityState.FINALIZING)

    def complete_request(self, request_id: str, *, ollama_available: bool | None = None) -> None:
        """Remove a completed request and recompute global activity."""

        with self._lock:
            if request_id in self._requests:
                del self._requests[request_id]
                self._has_completed_generation = True
            if ollama_available is not None:
                self._ollama_available = ollama_available
            self._refresh_aggregate_state_locked()

    def snapshot(self) -> ActivitySnapshot:
        with self._lock:
            state = self._state
            active_request_count = len(self._requests)
            active_request = self._active_request_locked()
            active_model = active_request.model if active_request is not None else None
            details = self._details_locked(state)
            return ActivitySnapshot(
                state=state,
                label=_STATE_LABELS[state],
                active_request_count=active_request_count,
                updated_at=self._updated_at,
                details=details,
                active_model=active_model,
                active_model_state=_active_model_state(active_request_count, active_model),
                active_generation_sequence=active_request.generation_sequence if active_request is not None else None,
                active_endpoint=active_request.endpoint if active_request is not None else None,
                active_request_id=active_request.request_id if active_request is not None else None,
                active_accepted_at=active_request.accepted_at if active_request is not None else None,
                latest_model=self._latest_model,
            )

    def _set_request_state(self, request_id: str, state: ActivityState) -> None:
        now = _utcnow()
        with self._lock:
            tracked = self._requests.get(request_id)
            if tracked is None:
                return
            tracked.state = state
            tracked.updated_at = now
            self._refresh_aggregate_state_locked(force_updated_at=now)

    def _refresh_aggregate_state_locked(self, *, force_updated_at: datetime | None = None) -> None:
        next_state = self._aggregate_state_locked()
        if next_state != self._state or force_updated_at is not None:
            self._state = next_state
            self._updated_at = force_updated_at or _utcnow()

    def _aggregate_state_locked(self) -> ActivityState:
        if self._requests:
            active_states = {request.state for request in self._requests.values()}
            for state in _ACTIVE_STATE_PRECEDENCE:
                if state in active_states:
                    return state

        if self._ollama_available is True:
            return ActivityState.IDLE if self._has_completed_generation else ActivityState.READY
        if self._ollama_available is False:
            return ActivityState.CONNECTING
        return ActivityState.STARTING

    def _details_locked(self, state: ActivityState) -> str:
        request = self._latest_request_for_state_locked(state)
        if request is not None:
            target = request.model or "unknown model"
            if state is ActivityState.RECEIVING:
                return f"Accepted generation request for {target}."
            if state is ActivityState.THINKING:
                return f"Waiting for upstream response from {target}."
            if state is ActivityState.STREAMING:
                return f"Streaming response from {target}."
            if state is ActivityState.FINALIZING:
                return f"Completing bookkeeping for {target}."

        if state is ActivityState.STARTING:
            return "ContextKeeper is initializing."
        if state is ActivityState.CONNECTING:
            return "Waiting for Ollama connection."
        if state is ActivityState.READY:
            return "Ollama is available; waiting for the first generation request."
        if state is ActivityState.IDLE:
            return "Connected and available after completed generation work."
        return _STATE_LABELS[state]

    def _latest_request_for_state_locked(self, state: ActivityState) -> _TrackedRequest | None:
        candidates = [
            request
            for request in self._requests.values()
            if request.state is state
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda request: request.updated_at)

    def _active_request_locked(self) -> _TrackedRequest | None:
        candidates = [
            request
            for request in self._requests.values()
            if isinstance(request.model, str) and request.model
        ]
        if not candidates:
            return None
        return max(
            candidates,
            key=lambda request: (
                request.generation_sequence if request.generation_sequence is not None else -1,
                request.accepted_at,
            ),
        )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _active_model_state(active_request_count: int, active_model: str | None) -> str:
    if active_model:
        return "known"
    return "unknown" if active_request_count else "none"


activity_manager = OperationalActivityManager()
