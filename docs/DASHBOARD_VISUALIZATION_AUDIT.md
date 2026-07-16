# Dashboard Visualization Pipeline Audit

## Purpose

This document records the Phase 6.5F-B5.1 audit of ContextKeeper's existing dashboard visualization pipeline. It is a foundation document for later rich-widget work and does not introduce new visible dashboard components.

## Scope

Phase 6.5F-B5.1 reviewed:

- live metrics currently exposed to the dashboard;
- in-memory metric stores and history buffers;
- request, conversation, context, compression, and activity history;
- dashboard refresh and polling behavior;
- duplicated calculations and potentially expensive refresh-time work;
- missing history needed for future visualizations.

## Existing Dashboard Endpoints

### `/health`

Used by the dashboard connection topology and operational status cards.

Exposed data:

- ContextKeeper app name and running status.
- Proxy URL and configured Ollama base URL.
- Client connection state derived from recent request client hosts.
- Proxy listening address.
- Ollama status, version, latency, and optional detail.
- Model status, selected model name, and user-facing model label.
- Operational activity snapshot.

### `/metrics`

Used by request statistics, request sparkline, and the recent request table.

Exposed request data:

- `total_requests`.
- `total_errors`.
- `last_sequence`.
- `last_generation_sequence`.
- `last_endpoint`.
- `last_model`.
- `last_latency_ms`.
- `last_status_code`.
- `recent_requests`, capped at 50 entries.

Each recent request may include:

- sequence number;
- timestamp;
- method;
- endpoint;
- model;
- status code;
- latency in milliseconds;
- client host;
- generation sequence for conversational generation requests;
- resolved context-window tokens/source/source label for generation requests.

Exposed system data:

- legacy `cpu_percent`, `ram_percent`, `ram_used_gb`, `ram_total_gb`, and `gpu`.
- structured `cpu` detail including availability, usage, status, status label, name, processor count, thread count, and optional temperature.
- structured `memory` detail including availability, usage, used/total GB, status, and status label.
- structured `gpu_detail` including availability, telemetry status, status, status label, name, utilization, VRAM, temperature, power, and message.

### `/dashboard/data`

Used by the main dashboard panels, intelligence cards, active conversation display, and instrument panel.

Exposed data:

- ContextKeeper status and app name.
- Ollama status.
- Operational activity snapshot.
- Request summary and latest request list.
- Context statistics across tracked conversations.
- Compression count and recent derived compression history.
- Active conversation snapshot.
- Dashboard intelligence including health, insights, recommendations, request trends, timeline, conversation risk, and source metadata.
- System metrics.
- Instrument panel data for CPU, GPU, memory, context usage, context trend, and compression status.
- Dashboard refresh interval.

## Current Metric Stores and State Holders

### `MetricsStore`

Location: `src/ctxkeeper/diagnostics/metrics.py`

Maintains:

- aggregate request counts;
- aggregate error count;
- last request metadata;
- most recent 50 request events;
- per-request timestamps and latencies.

Notes:

- Request history is count-capped, not time-windowed.
- System metrics are collected live on every `snapshot()` call and are not retained historically.
- GPU telemetry may invoke `nvidia-smi`, which is useful but comparatively expensive.

### `OperationalActivityManager`

Location: `src/ctxkeeper/diagnostics/activity.py`

Maintains:

- active generation request registry;
- aggregate activity state;
- latest active model and endpoint;
- active generation sequence;
- latest observed model.

Notes:

- This is current-state oriented.
- It does not retain a timeline of state transitions.

### `ConversationStore`

Location: `src/ctxkeeper/context/conversation_store.py`

Maintains:

- in-memory conversations;
- in-memory message lists;
- created and updated timestamps.

Notes:

- This is currently process-local memory.
- Compression can replace older active messages with a rolling summary, so it is not a durable historical archive.

### `ContextHistoryStore`

Location: `src/ctxkeeper/dashboard/routes.py`

Maintains:

- per-conversation bounded context-usage samples;
- timestamp;
- usage percentage;
- estimated tokens;
- effective context-window tokens.

Notes:

- The buffer is capped at 30 samples per conversation.
- Samples are recorded during dashboard `/dashboard/data` refreshes.
- The store is in memory and is cleared on process restart.
- It currently tracks active context usage only, not all conversations.

### Model context-window cache and active overrides

Location: `src/ctxkeeper/model_context.py`

Maintains:

- configured/detected/default model context-window resolution;
- runtime active context-window overrides while requests are in flight.

Notes:

- These values are already exposed in request events, active generation state, context status, and instrument-panel support rows.

### Compression metadata and derived compression history

Locations:

- `src/ctxkeeper/context/compression_manager.py`
- `src/ctxkeeper/dashboard/routes.py`

Current behavior:

- `CompressionManager` maintains metadata per manager instance.
- Dashboard compression history is derived by scanning current conversation messages for rolling-summary system messages.
- The dashboard exposes recent derived compression history, capped to 10 items.

Notes:

- There is no central append-only compression event store yet.
- Derived history is sufficient for current widgets but limited for future timelines, detailed event charts, and restart recovery.

## Existing Rolling and Historical Data

| Area | Existing history | Retention | Notes |
| --- | --- | --- | --- |
| Requests | Recent request events in `MetricsStore` | 50 events | Good foundation for request rate, latency, endpoint mix, error rate, and model utilization over recent activity. |
| System metrics | Current snapshot only | None | CPU/RAM/GPU trends need a future rolling buffer if required. |
| Activity state | Current active state and latest model | Current only | Health transitions and activity timelines need event retention. |
| Conversations | In-memory messages per conversation | Until process clear/restart or compression mutation | Useful for active state; not durable archival memory. |
| Context usage | Dashboard context history samples | 30 samples per conversation | Already supports context trend sparkline; currently tied to dashboard polling. |
| Compression | Derived from current rolling-summary messages | Current conversation state | Needs event-store support for richer compression timelines. |
| Model context windows | Configured/detected/default cache and active overrides | Process memory | Useful for model utilization and capacity-aware visualizations. |

## Dashboard Refresh Cycle

The browser dashboard currently initializes once and then polls every configured dashboard refresh interval, defaulting to 1000 ms.

On every refresh cycle, the dashboard runs these requests concurrently:

- `GET /health`
- `GET /metrics`
- `GET /dashboard/data`

The client prevents overlapping refreshes with a `refreshInFlight` guard.

Refresh timing:

- The configured polling interval remains unchanged by this phase.
- No new polling timers or visible widgets were added in Phase 6.5F-B5.1.

## Duplicate Calculations and Refresh-Time Costs

Observed before Phase 6.5F-B5.1 backend cleanup:

- `/dashboard/data` read the conversation store multiple times while building context statistics, compression history, and active conversation snapshots.
- `/health` and `/dashboard/data` each perform an Ollama status probe when both are polled in the same browser refresh cycle.
- `/metrics` and `/dashboard/data` each call `metrics_store.snapshot()` when both are polled in the same browser refresh cycle.
- `metrics_store.snapshot()` collects system metrics every time, including optional GPU telemetry through `nvidia-smi`.
- Request trends are rebuilt from recent request history on each `/dashboard/data` refresh.
- Compression history is derived by scanning conversation messages on each `/dashboard/data` refresh.
- Context trend samples are recorded from dashboard polling, so trend granularity depends on the dashboard refresh interval rather than request/compression events.

Phase 6.5F-B5.1 cleanup:

- `/dashboard/data` now captures the conversation list once per status build and reuses it for context monitoring, compression history, and active-conversation snapshot creation.
- `ContextMonitor.scan()` can now accept a supplied conversation snapshot.
- `ConversationSnapshotProvider.active_snapshot()` can now accept a supplied conversation snapshot.
- The dashboard JSON shape and visible widgets are unchanged.

Remaining opportunities:

- Avoid duplicate system metric collection across `/metrics` and `/dashboard/data`.
- Avoid duplicate Ollama probing across `/health` and `/dashboard/data`.
- Introduce dedicated rolling system metrics only if richer CPU/RAM/GPU trend widgets require it.
- Introduce a dedicated append-only compression event store before building richer compression timelines.
- Consider recording context samples on meaningful events as well as, or instead of, dashboard polling.

## Future Visualization Opportunities

Existing data can already support:

- request rate over recent requests;
- recent latency trend;
- recent error-rate view;
- endpoint mix;
- client-host activity;
- active conversation context usage;
- context usage trend for the active conversation;
- compression count and recent compressed conversations;
- active model and latest model display;
- basic model utilization from request history;
- current CPU/RAM/GPU gauges.

Additional backend support is likely needed for:

- long-duration request-rate charts beyond 50 recent events;
- durable latency trends across restarts;
- health state transition timelines;
- append-only compression event timelines;
- model utilization over longer windows;
- system resource trends over time;
- historical operational statistics for reports;
- restart-stable dashboard trend history;
- exact visualization of when context warning and compression thresholds were crossed.

## B5.2 Readiness Notes

Recommended next step before visible rich widgets:

- Define one reusable dashboard visualization payload schema that can be consumed by future widgets without duplicating calculations in the frontend.
- Prefer bounded backend buffers and event stores over recalculating long histories on every refresh.
- Keep `/dashboard/data` as the authoritative dashboard status source unless a later phase intentionally changes the polling model.
- Preserve the existing refresh interval and current widgets until a specific B5.2 implementation requires visible changes.
