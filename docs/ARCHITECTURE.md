# ContextKeeper Architecture

Status: Current through the Phase 6.5F-B6.5 working-tree implementation; Product Owner and architect review are pending.

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
- `src/ctxkeeper/dashboard/config_persistence.py`
- `src/ctxkeeper/dashboard/trends.py`

The dashboard exposes:

- `GET /health`
- `GET /metrics`
- `GET /dashboard/data`
- `GET /api/dashboard/settings`
- `PATCH /api/dashboard/settings`
- `PUT /api/dashboard/settings/config`
- `GET /dashboard`

`/dashboard/data` builds one coherent dashboard status payload from current metrics, current Ollama status, current activity, one conversation-store snapshot, context scan results, derived compression history, active conversation data, timeline events, inspector metadata/intelligence, and instrument-panel data.

Important constraints:

- Dashboard snapshot building is read-only with respect to conversation/request ownership.
- The conversation list is captured once per dashboard payload build and reused for context, compression, active-conversation, timeline, and inspector derivation.
- Timeline and inspector data are deterministic views of existing state.
- No additional polling loop was introduced for the Conversation Inspector.
- The settings snapshot, runtime-update, and persistence APIs expose only approved Context, Compression, and Dashboard configuration metadata. They do not expose environment variables, config paths, secrets, server settings, Ollama base URLs, logging paths, model override maps, or startup-only controls.

## Settings snapshot path

Source:

- `src/ctxkeeper/dashboard/settings_snapshot.py`
- `src/ctxkeeper/dashboard/config_persistence.py`
- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/template.py`
- `src/ctxkeeper/app.py`
- `src/ctxkeeper/resources.py`

Phase 6.5F-B6.1 added the settings snapshot/read foundation, B6.2 added validated in-memory runtime updates, B6.3 added the metadata-driven browser client, B6.4 added explicit configuration persistence, and B6.5 adds managed-default reset and runtime recovery controls without merging the runtime and persisted state concepts:

```text
GET /api/dashboard/settings
PATCH /api/dashboard/settings
PUT /api/dashboard/settings/config
```

The GET endpoint returns schema version 2 with:

- `schema_version`;
- ordered categories: Context, Compression, Dashboard;
- setting id, category, display name, description, data type, and minimum/maximum validation metadata where applicable;
- current runtime `value`, current disk-derived `persisted_value`, and built-in `default_value`;
- `differs_from_persisted`, `runtime_editable`, `persistable`, `reset_eligible`, and `restart_required` flags.

The authoritative setting catalog remains in `settings_snapshot.py`; persistence and reset behavior do not introduce a second list of dashboard-managed fields or duplicate default values in the browser. All eight approved Context, Compression, and Dashboard settings are currently runtime-editable, persistable, and reset-eligible. The metadata model and browser renderer also support future settings that are runtime-only, persistence-only, non-persistable, reset-ineligible, or restart-required.

Runtime PATCH architecture:

- `src/ctxkeeper/dashboard/settings_snapshot.py` owns the canonical dashboard settings snapshot and runtime update models.
- `PATCH /api/dashboard/settings` accepts partial updates using the same Context, Compression, and Dashboard category nesting.
- Omitted settings retain their current in-memory values.
- The update path merges submitted values into a proposed complete `Settings` state, validates the complete proposal, and mutates the shared in-memory `Settings` instance only after validation succeeds.
- Failed validation is atomic: no partial setting changes are applied.
- Individual, category, global, and Discard recovery updates reuse this same PATCH path. Reset payloads contain authoritative `default_value` metadata, while recovery payloads contain `persisted_value` for each runtime-editable setting whose confirmed runtime value differs.
- Successful updates return the same canonical snapshot shape as the read API and are immediately visible to a subsequent GET.
- PATCH reads persisted state before runtime mutation so its schema-v2 response cannot manufacture disk metadata; an unavailable or invalid active configuration fails safely before runtime changes are applied.
- Settings GET and PATCH use FastAPI synchronous handlers, keeping configuration disk I/O and process-lock waits off the async proxy/streaming event loop.
- PATCH never writes `contextkeeper.yaml`; runtime changes remain process-local and reset at restart unless separately persisted with PUT.

Configuration persistence architecture:

- Application startup resolves the active configuration path with the existing `resolve_config_path` rules and supplies that same resolved path to one `ConfigurationPersistenceService`.
- Source mode resolves the default filename from the current working directory. Frozen mode prefers an editable file beside the executable, falls back to the bundled resource when present, and otherwise returns the expected path beside the executable.
- `PUT /api/dashboard/settings/config` accepts a non-empty JSON object grouped by approved category and persists only explicitly supplied, metadata-approved, persistable fields.
- Strict Pydantic request models reject unknown categories and fields, nulls, strings/floats in integer positions, non-boolean boolean values, blank model names, malformed category shapes, and unsupported settings.
- The complete candidate is validated through `Settings` plus the same dashboard business rule used by PATCH: the warning threshold must remain strictly lower than the compression threshold.
- The persistence service re-reads the active file while holding a process-global reentrant lock. It never relies only on a startup-time settings copy.
- If the file is missing, the service begins with validated built-in defaults, creates missing parent directories, and writes a new configuration containing the explicitly supplied categories and fields. The success result reports `configuration_created: true`.
- Existing unrelated categories, values, and model-specific entries are retained in the in-memory YAML mapping and emitted with the candidate.
- The complete candidate is serialized with PyYAML `safe_dump`, `sort_keys=False`, block style, Unicode support, and UTF-8/LF output; it is parsed and validated again before any destination replacement.
- A temporary file is created in the destination directory. ContextKeeper writes the complete candidate, flushes it, calls `fsync`, closes it, reads it back, verifies the bytes, and parses it again.
- A SHA-256 fingerprint captured from the fresh read is compared with another immediate read before replacement. A mismatch returns a stale-configuration conflict instead of overwriting the newer file.
- `os.replace` performs the final same-filesystem atomic replacement. Failures retain the original destination and trigger best-effort temporary-file cleanup; cleanup failures are logged without obscuring the primary safe API error.
- PUT returns `status`, sorted `persisted_setting_ids`, `configuration_created`, and a refreshed schema-v2 snapshot under `settings`.
- Persisting does not mutate the shared runtime `Settings`, apply a PATCH, or restart ContextKeeper.

Concurrency boundary:

- One process-global `RLock` serializes persisted-state reads and writes within the running ContextKeeper process, so two in-process requests cannot interleave candidate replacement.
- The fingerprint check provides best-effort stale-write detection for external edits during preparation.
- There is no operating-system, distributed, or multi-process lock. An external writer can still race after the final fingerprint check and before `os.replace`.

Serialization and safety boundary:

- PyYAML preserves parsed configuration data, including unmanaged and model-specific mappings, but does not round-trip comments, quoting, anchors, key formatting, or exact whitespace. A successful persistence operation can normalize the complete document.
- Malformed YAML, non-mapping YAML, invalid UTF-8, invalid existing configuration, inaccessible files, directory failures, temporary-write/verification failures, stale fingerprints, and atomic-replace failures return safe client details without exposing the resolved path or configuration contents.
- Logs record safe error codes/statuses or successful setting counts and file-creation state; secrets and full configuration contents are not logged.

Settings browser architecture:

- The Settings page requests the snapshot only when first opened and constructs categories, labels, descriptions, constraints, default-value context, controls, reset actions, and editability indicators from API metadata rather than a browser-side setting list.
- The browser holds a frozen confirmed snapshot and a separately cloned draft snapshot. Edits affect only the draft until Save succeeds.
- Dirty state compares typed draft values separately with confirmed runtime and persisted values.
- Each eligible setting has a native reset button with an accessible setting-specific name. It is disabled when the confirmed runtime value already equals the authoritative built-in default.
- An individual reset immediately issues one PATCH for that setting. Each category has a confirmed reset action that includes all and only reset-eligible settings in that category, including eligible values already at default. **Reset managed settings to defaults** requires confirmation and applies the same complete selection across the current snapshot. Category and global controls are disabled when their complete eligible scope is already at default.
- Category and global reset payloads are submitted as one atomic PATCH. Cancellation sends no request; success accepts the canonical snapshot and reports that defaults are staged without writing configuration. Feedback requires Save to configuration when persisted values differ, or states that no save is needed when they already match.
- Save runtime changes derives a nested payload from metadata and issues one `PATCH` containing only changed runtime-editable fields.
- Save to configuration is a separate button, never an edit/input side effect. It issues one `PUT /api/dashboard/settings/config` containing only persistable draft values that differ from the confirmed `persisted_value`.
- While either save is pending, controls and both save actions are locked to prevent duplicate or conflicting submissions.
- The successful PATCH snapshot becomes the new authoritative confirmed state and a fresh draft while retaining any future persistence-only draft values that PATCH was not eligible to apply. If a success response cannot be interpreted, the client performs at most one settings GET to confirm the accepted state. If that confirmation also fails, the visible draft is locked and an explicit retry-load action prevents further edits against stale confirmed state.
- A successful PUT accepts the refreshed runtime/persisted snapshot while restoring the user's draft values. This allows a value to be saved for a later restart without silently applying it to the current process.
- Validation, persistence, and network failures leave the draft and dirty state intact. API error messages are rendered as text, and exact field locations are associated with controls where the response supplies them.
- Discard remains local when only browser draft edits need to be abandoned. When confirmed runtime differs from persisted state, Discard issues one atomic PATCH restoring every runtime-editable differing value from `persisted_value`; it never calls PUT or writes the configuration file.

Current B6.5 boundary:

- The Settings page is a management API client, not another source of configuration rules or setting ownership.
- Settings controls are temporary browser state; no LocalStorage or SessionStorage is used.
- Persistence occurs only after explicit PUT or Save to configuration action; PATCH and editing never persist automatically.
- No automatic restart or restart orchestration.
- Restart-required metadata is represented generically. If a future persistable setting requires restart, its persisted value can differ from the active runtime value until a manual restart; no currently approved setting is marked restart-required.
- No history browser, backup-management UI, rollback workflow, import/export, or multi-process locking.
- No authentication or multi-user setting ownership.
- Reset is limited to metadata-approved dashboard-managed settings. It does not delete or recreate YAML, clear logs, metrics, conversations, summaries, model files, or other application data, and it is not a factory reset.
- No restart control, self-diagnostic workflow, automated repair, configuration backup history, or saved-configuration rollback.
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
- a visible runtime-versus-saved notice, metadata-driven category form, individual/category/global managed-default reset controls, persisted-value/difference guidance, feedback regions, separate runtime/configuration Save actions, and Discard on Settings.

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
