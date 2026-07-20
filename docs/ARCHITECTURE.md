# ContextKeeper Architecture

Status: Current through Phase 6.5F-B6.3.

ContextKeeper is a local FastAPI application that presents an Ollama-compatible API to clients while observing, measuring, and managing conversation context before requests reach Ollama.

## High-level flow

```text
Client
  ↓
ContextKeeper Proxy
  ↓
Diagnostics
  ↓
Context Engine
  ↓
Compression
  ↓
Ollama
  ↓
Dashboard Snapshot
  ↓
Dashboard Visualization
```

The proxy remains the only runtime component visible to Ollama-compatible clients. Dashboard code observes existing state; it must not become a second owner of conversation, request, context, or compression state.

## Runtime processing path

### Client

Examples include AnythingLLM, Open WebUI, IDE integrations, scripts, and any other Ollama-compatible consumer.

Clients use the ContextKeeper base URL, normally:

```text
http://localhost:11500
```

The upstream Ollama URL remains configurable and defaults to:

```text
http://localhost:11434
```

### ContextKeeper Proxy

Source:

- `src/ctxkeeper/app.py`
- `src/ctxkeeper/proxy/routes.py`
- `src/ctxkeeper/proxy/ollama_client.py`

Responsibilities:

- Accept `/api/*` and `/v1/*` requests.
- Preserve streaming behavior for supported chat/generate requests.
- Forward unknown Ollama-compatible endpoints when possible.
- Extract model information from request bodies.
- Resolve the authoritative context-window capacity for generation requests.
- Enforce `options.num_ctx` on conversational generation requests.
- Record incoming chat messages for the in-memory conversation store.
- Record non-streaming assistant responses when available.
- Return Ollama responses without changing the client-facing API shape except for ContextKeeper-managed context payload changes.

### Diagnostics

Source:

- `src/ctxkeeper/diagnostics/metrics.py`
- `src/ctxkeeper/diagnostics/activity.py`

Responsibilities:

- Track request counts, error counts, latency, endpoint, status code, model, client host, generation sequence, conversation id, and context-window resolution metadata.
- Maintain a bounded recent request history.
- Track operational activity states such as idle, thinking, streaming, receiving, finalizing, and ready.
- Collect current CPU, memory, and optional NVIDIA GPU telemetry for dashboard use.

Diagnostics are metadata-oriented. They must not expose prompt bodies, response bodies, secrets, or retrieved private documents in routine dashboard surfaces.

### Context Engine

Source:

- `src/ctxkeeper/context/conversation_store.py`
- `src/ctxkeeper/context/context_meter.py`
- `src/ctxkeeper/context/context_monitor.py`
- `src/ctxkeeper/dashboard/snapshots.py`
- `src/ctxkeeper/model_context.py`

Responsibilities:

- Maintain process-local Conversation Snapshots.
- Estimate Context Usage from tracked messages.
- Detect warning and compression thresholds.
- Resolve model context capacity using:
  1. configured model-specific overrides;
  2. Automatic Model Context Discovery from Ollama `/api/show` metadata;
  3. `context.default_context_window_tokens`.
- Provide active conversation metadata and safe recent-message/context metadata to the dashboard.

Thresholds use inclusive comparisons:

- warning: `usage_percent >= context.warning_threshold_percent`
- compression candidate: `usage_percent >= context.compression_threshold_percent`

### Compression

Source:

- `src/ctxkeeper/context/compression_manager.py`
- `src/ctxkeeper/context/compression_plan.py`
- `src/ctxkeeper/context/summarizer.py`

Responsibilities:

- Determine when active conversation context should be condensed.
- Generate rolling summaries using the configured summarizer model.
- Preserve a configured number of recent messages in active context.
- Replace older active context with a rolling-summary system message.

Current boundary:

- Compression reduces active prompt size.
- Durable original-message archiving and later historical retrieval are planned for Phase 6.5G and are not yet implemented.

### Ollama

Ollama remains the upstream model runtime. ContextKeeper forwards requests to the configured `ollama.base_url`, defaulting to `http://localhost:11434`.

ContextKeeper probes Ollama for dashboard health through `/api/version` and discovers model metadata through `/api/show` where applicable.

## Dashboard snapshot path

Source:

- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/insights.py`
- `src/ctxkeeper/dashboard/intelligence.py`
- `src/ctxkeeper/dashboard/recommendations.py`
- `src/ctxkeeper/dashboard/timeline.py`
- `src/ctxkeeper/dashboard/inspector.py`
- `src/ctxkeeper/dashboard/settings_snapshot.py`
- `src/ctxkeeper/dashboard/trends.py`

The dashboard exposes:

- `GET /health`
- `GET /metrics`
- `GET /dashboard/data`
- `GET /api/dashboard/settings`
- `PATCH /api/dashboard/settings`
- `GET /dashboard`

`/dashboard/data` builds one coherent dashboard status payload from current metrics, current Ollama status, current activity, one conversation-store snapshot, context scan results, derived compression history, active conversation data, timeline events, inspector metadata/intelligence, and instrument-panel data.

Important constraints:

- Dashboard snapshot building is read-only with respect to conversation/request ownership.
- The conversation list is captured once per dashboard payload build and reused for context, compression, active-conversation, timeline, and inspector derivation.
- Timeline and inspector data are deterministic views of existing state.
- No additional polling loop was introduced for the Conversation Inspector.
- The settings snapshot and update API expose only approved Context, Compression, and Dashboard configuration metadata. They do not expose environment variables, config paths, secrets, server settings, Ollama base URLs, logging paths, model override maps, or startup-only controls.

## Settings snapshot path

Source:

- `src/ctxkeeper/dashboard/settings_snapshot.py`
- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/template.py`

Phase 6.5F-B6.1 added the settings snapshot/read foundation, Phase 6.5F-B6.2 added validated in-memory runtime updates on the same resource, and Phase 6.5F-B6.3 adds the metadata-driven browser client inside the existing dashboard shell:

```text
GET /api/dashboard/settings
PATCH /api/dashboard/settings
```

The endpoint returns:

- `schema_version`;
- ordered categories: Context, Compression, Dashboard;
- setting id, category, display name, description, value, built-in default value, data type, minimum/maximum validation metadata where applicable, runtime-editable flag, and restart-required flag.

Runtime settings architecture:

- `src/ctxkeeper/dashboard/settings_snapshot.py` owns the canonical dashboard settings snapshot and runtime update models.
- `GET /api/dashboard/settings` returns the complete sanitized snapshot.
- `PATCH /api/dashboard/settings` accepts partial updates using the same Context, Compression, and Dashboard category nesting.
- Omitted settings retain their current in-memory values.
- The update path merges submitted values into a proposed complete `Settings` state, validates the complete proposal, and mutates the shared in-memory `Settings` instance only after validation succeeds.
- Failed validation is atomic: no partial setting changes are applied.
- Successful updates return the same canonical snapshot shape as the read API and are immediately visible to a subsequent GET.
- Exposed runtime settings are marked `runtime_editable: true` and `restart_required: false`.
- The Settings page requests the snapshot only when first opened and constructs categories, labels, descriptions, constraints, default-value context, controls, and editability indicators from API metadata rather than a browser-side setting list.
- The browser holds a frozen confirmed snapshot and a separately cloned draft snapshot. Edits affect only the draft until Save succeeds.
- Dirty state compares typed confirmed and draft values. Returning a field to its confirmed value removes it from the changed set.
- Save derives the nested request shape from setting category/id metadata and issues one `PATCH` containing only changed fields that the snapshot marks runtime-editable.
- The successful PATCH snapshot becomes the new authoritative confirmed state and a fresh draft. If a success response cannot be interpreted, the client performs at most one settings GET to confirm the accepted state. If that confirmation also fails, the visible draft is locked and an explicit retry-load action prevents further edits against stale confirmed state.
- Validation and network failures leave the draft and dirty state intact. API error messages are rendered as text, and exact field locations are associated with controls where the response supplies them.
- Discard clones the latest confirmed snapshot without a PATCH, GET, browser storage, or configuration-file operation.

Current B6.3 boundary:

- The Settings page is a runtime API client, not another source of configuration rules or setting ownership.
- Settings controls are temporary browser state; no LocalStorage or SessionStorage is used.
- No configuration persistence.
- No YAML writing.
- No authentication or multi-user setting ownership.
- No startup restoration of runtime overrides.
- No reset-to-defaults workflow.
- No proxy, streaming, context-engine, or compression-engine contract changes.

## Dashboard visualization path

Source:

- `src/ctxkeeper/dashboard/template.py`

The browser dashboard is a vanilla HTML/CSS/JavaScript operations console. It currently includes:

- operations hero health and recommendations;
- hero statistics;
- system instrument panel: CPU Usage, GPU Usage, Memory Usage, Context Usage, Compression Status;
- system activity widgets: Context Trend and Connection Flow;
- Traffic with Request Traffic visualization;
- Active Conversation summary;
- Live Conversation Timeline;
- Conversation Inspector drawer with Overview and Intelligence;
- client-side navigation between Operations, Conversations, Context, Analytics, Logs, and the interactive Settings page;
- a visible runtime-only notice, metadata-driven category form, feedback regions, and Save/Discard actions on Settings.

The dashboard polls the existing endpoints on the configured refresh interval, defaulting to `1000 ms`. It uses one reschedulable interval and a guard to avoid overlapping refreshes. Page switching does not create polling timers or duplicate listeners. When the runtime refresh interval changes, the canonical `/dashboard/data` value reschedules that same timer; opening Settings adds only its guarded first-load request.

## Module layout

Implemented modules:

```text
src/ctxkeeper/
  app.py
  main.py
  branding.py
  config.py
  resources.py
  logging_config.py
  context/
  dashboard/
  diagnostics/
  model_context.py
  proxy/
  service/
  wizard/
```

Packaging and release support:

```text
contextkeeper.spec
installer/
scripts/build_release.ps1
```

Planned but not implemented as runtime subsystems:

- durable historical memory retrieval;
- Validation/AutoQA engine;
- routing engine;
- plugin engine;
- multi-user/workspace isolation.

## Source-of-truth rule

The current implementation is authoritative. Older mockup, planning, and future-ideas documents may describe target designs or historical decisions; they do not override source behavior.
