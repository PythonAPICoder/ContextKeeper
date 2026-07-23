# ContextKeeper Architecture

Status: Current through the Phase 6.5F-B6.6 working-tree implementation; Product Owner and architect review are pending.

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

Ollama remains the single upstream model runtime. ContextKeeper constructs its active Ollama HTTP client from the startup-resolved `ollama.base_url` and `ollama.timeout_seconds`, defaulting to `http://localhost:11434` and `120` seconds. That active client and the canonical runtime `Settings` object are not replaced when the dashboard saves Connection settings.

ContextKeeper probes Ollama for dashboard health through `/api/version` and discovers model metadata through `/api/show` where applicable.

The Settings page candidate Test Connection operation is separate from both paths. It creates one temporary `httpx.AsyncClient` with `trust_env=False`, sends exactly one bounded request to the candidate endpoint's base-path-preserving `/api/version` URL, and closes the client through its async context manager. Its result does not replace the active endpoint/client or overwrite active health, version, metrics, model-discovery, or diagnostics state. Existing model-discovery retry/backoff remains a separate runtime behavior; candidate testing does not retry.

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
- `src/ctxkeeper/dashboard/connection_test.py`
- `src/ctxkeeper/dashboard/trends.py`

The dashboard exposes:

- `GET /health`
- `GET /metrics`
- `GET /dashboard/data`
- `GET /api/dashboard/settings`
- `PATCH /api/dashboard/settings`
- `PUT /api/dashboard/settings/config`
- `POST /api/dashboard/settings/connection/test`
- `GET /dashboard`

`/dashboard/data` builds one coherent dashboard status payload from current metrics, current Ollama status, current activity, one conversation-store snapshot, context scan results, derived compression history, active conversation data, timeline events, inspector metadata/intelligence, and instrument-panel data.

Important constraints:

- Dashboard snapshot building is read-only with respect to conversation/request ownership.
- The conversation list is captured once per dashboard payload build and reused for context, compression, active-conversation, timeline, and inspector derivation.
- Timeline and inspector data are deterministic views of existing state.
- No additional polling loop was introduced for the Conversation Inspector.
- The settings snapshot, runtime-update, persistence, and candidate-test APIs expose only approved Connection, Context, Compression, and Dashboard configuration metadata. They do not expose environment variables, config paths, secrets, server listener settings, logging paths, model override maps, or unrelated startup-only controls.

## Settings snapshot path

Source:

- `src/ctxkeeper/dashboard/settings_snapshot.py`
- `src/ctxkeeper/dashboard/config_persistence.py`
- `src/ctxkeeper/dashboard/connection_test.py`
- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/template.py`
- `src/ctxkeeper/app.py`
- `src/ctxkeeper/resources.py`

Phase 6.5F-B6.1 added the settings snapshot/read foundation, B6.2 added validated in-memory runtime updates, B6.3 added the metadata-driven browser client, B6.4 added explicit configuration persistence, B6.5 added managed-default reset and runtime recovery controls, and B6.6 adds restart-required Ollama Connection configuration plus isolated candidate testing without merging draft, persisted, and active runtime state:

```text
GET /api/dashboard/settings
PATCH /api/dashboard/settings
PUT /api/dashboard/settings/config
POST /api/dashboard/settings/connection/test
```

The GET endpoint returns schema version 2 with:

- `schema_version`;
- ordered categories: Connection (`ollama`), Context, Compression, Dashboard;
- setting id, category, display name, description, data type, and minimum/maximum validation metadata where applicable;
- current runtime `value`, current disk-derived `persisted_value`, and built-in `default_value`;
- `differs_from_persisted`, `runtime_editable`, `persistable`, `reset_eligible`, and `restart_required` flags.

The authoritative setting catalog remains in `settings_snapshot.py`; persistence and reset behavior do not introduce a second list of dashboard-managed fields or duplicate default values in the browser. The eight approved Context, Compression, and Dashboard settings remain runtime-editable, persistable, and reset-eligible. Connection adds `ollama.base_url` and `ollama.timeout_seconds`; both are persistable and reset-eligible, both have `runtime_editable: false`, and both have `restart_required: true`. The timeout exposes its authoritative minimum of `1` and no product-level maximum.

Runtime PATCH architecture:

- `src/ctxkeeper/dashboard/settings_snapshot.py` owns the canonical dashboard settings snapshot and runtime update models.
- `PATCH /api/dashboard/settings` accepts partial updates using the Context, Compression, and Dashboard category nesting. The `ollama` category is deliberately absent from the runtime update model.
- Omitted settings retain their current in-memory values.
- The update path merges submitted values into a proposed complete `Settings` state, validates the complete proposal, and mutates the shared in-memory `Settings` instance only after validation succeeds.
- Failed validation is atomic: no partial setting changes are applied.
- Runtime-editable individual/category resets, the runtime-editable subset of a mixed global reset, and Discard recovery reuse this same PATCH path. Reset payloads contain authoritative `default_value` metadata, while recovery payloads contain `persisted_value` for each runtime-editable setting whose confirmed runtime value differs. Persistence-only Connection resets remain browser drafts and are never included in PATCH.
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
- The managed persistence allowlist includes only the two approved Connection fields plus the existing approved settings. A candidate Connection URL receives complete Settings validation and deterministic listener-loop validation before replacement.

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
- Each eligible setting has a native reset button with an accessible setting-specific name. Runtime-editable reset availability compares confirmed runtime with the authoritative default; persistence-only Connection reset availability compares the draft with that default.
- A runtime-editable individual reset immediately issues one PATCH. A Connection individual or category reset stages authoritative defaults in the browser draft without PATCH. **Reset managed settings to defaults** requires confirmation, stages all reset-eligible defaults, and sends at most one PATCH containing only the runtime-editable subset; Connection defaults remain persistence-only drafts.
- Cancellation sends no request. Success reports that defaults are staged without writing configuration. Feedback requires Save to configuration when persisted values differ, or states that no save is needed when they already match.
- Save runtime changes derives a nested payload from metadata and issues one `PATCH` containing only changed runtime-editable fields.
- Save to configuration is a separate button, never an edit/input side effect. It issues one `PUT /api/dashboard/settings/config` containing only persistable draft values that differ from the confirmed `persisted_value`.
- While either save is pending, controls and both save actions are locked to prevent duplicate or conflicting submissions.
- The successful PATCH snapshot becomes the new authoritative confirmed state and a fresh draft while retaining any future persistence-only draft values that PATCH was not eligible to apply. If a success response cannot be interpreted, the client performs at most one settings GET to confirm the accepted state. If that confirmation also fails, the visible draft is locked and an explicit retry-load action prevents further edits against stale confirmed state.
- A successful PUT accepts the refreshed runtime/persisted snapshot while restoring the user's draft values. This allows a value to be saved for a later restart without silently applying it to the current process.
- Validation, persistence, and network failures leave the draft and dirty state intact. API error messages are rendered as text, and exact field locations are associated with controls where the response supplies them.
- Discard remains local when only browser draft edits need to be abandoned, including Connection-only drafts. When confirmed runtime differs from persisted state, Discard issues one atomic PATCH restoring every runtime-editable differing value from `persisted_value`; Connection fields are excluded, and Discard never calls PUT or writes the configuration file.

Candidate Connection test architecture:

- `POST /api/dashboard/settings/connection/test` accepts exactly `base_url` and `timeout_seconds` from the current browser draft. It does not require the values to match runtime or disk state.
- Strict request models reject unknown fields and non-string endpoints; timeout values must be JSON integers, not booleans, floats, or strings, and must be at least `1`.
- The endpoint is normalized with the same standard-library URL validation used by startup and persistence. An obvious direct reference to ContextKeeper's configured listener at the root or within its `/api` or `/v1` proxy namespace is rejected deterministically without DNS lookup; unrelated base paths remain valid.
- A valid request creates one isolated client with environment proxy discovery disabled and a timeout of `min(timeout_seconds, 10)`, then performs one GET to `{normalized_base_url}/api/version`. A configured base path is retained and trailing slashes are removed before appending `/api/version`.
- Every validated probe outcome, success or failure, returns HTTP `200` with `connected`, `tested_endpoint`, `latency_ms`, `ollama_version`, `failure_category`, and a user-readable `message`. Request validation returns HTTP `422` with the same safe result fields plus field-associated `detail`.
- Failure categories distinguish invalid endpoint/timeout/request, DNS resolution, connection refusal, timeout, TLS/certificate failure, HTTP error, malformed or non-Ollama responses, missing/invalid version, and other network errors.
- The route never writes YAML or mutates the shared runtime settings, active HTTP client reference, active endpoint, health/version snapshot, diagnostics metrics, or model-discovery state. GET, PUT, PATCH, DELETE, HEAD, and OPTIONS on this route return explicit `405` with `Allow: POST`.

Current B6.6 boundary:

- The Settings page is a management API client, not another source of configuration rules or setting ownership.
- Settings controls are temporary browser state; no LocalStorage or SessionStorage is used.
- Persistence occurs only after explicit PUT or Save to configuration action; PATCH and editing never persist automatically.
- No automatic restart or restart orchestration.
- The two Connection settings require restart. Saving can make their persisted values differ from the active runtime values until a manual restart; no dashboard action performs live backend reconfiguration or client replacement.
- `CONTEXTKEEPER_OLLAMA_URL` remains a higher-priority active source than saved YAML. The snapshot presents active and persisted values but does not track or label their provenance, so saving never claims to override an environment value.
- Test Connection is a transient one-attempt candidate probe, not a save prerequisite, active health check replacement, periodic monitor, model browser, retry control, or diagnostic/recovery subsystem.
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
- a visible runtime-versus-saved notice, metadata-driven category form including Connection, individual/category/global managed-default reset controls, persisted-value/difference guidance, isolated Test Connection action/result, feedback regions, separate runtime/configuration Save actions, and Discard on Settings.

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
