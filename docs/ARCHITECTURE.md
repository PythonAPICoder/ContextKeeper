# ContextKeeper Architecture

Status: Current through Phase 6.5F-B6.2.

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

Phase 6.5F-B6.1 added the backend foundation for the future Settings dashboard. Phase 6.5F-B6.2 adds validated in-memory runtime updates on the same settings resource:

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

Current B6.2 boundary:

- No Settings dashboard UI controls.
- No configuration persistence.
- No YAML writing.
- No browser storage.
- No authentication or multi-user setting ownership.
- No startup restoration of runtime overrides.

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
- secondary pages for Conversations, Context, Analytics, Logs, and Settings.

The dashboard polls the existing endpoints on the configured refresh interval, defaulting to `1000 ms`. It uses a single refresh loop and a guard to avoid overlapping refreshes.

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
