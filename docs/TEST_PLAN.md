# ContextKeeper Test Plan

Status: Current through the Phase 6.5F-B6.5 working-tree implementation; Product Owner and architect review are pending.

This document defines automated and manual validation expectations for ContextKeeper. The automated suite is the default regression gate; manual Visual QA remains required for dashboard layout, motion, responsive behavior, and Product Owner acceptance.

## Standard automated command

```powershell
python -m pytest -q
```

Focused dashboard and inspector tests currently live in:

- `tests/test_app.py`
- `tests/test_dashboard_instrument_panel.py`
- `tests/test_dashboard_inspector.py`
- `tests/test_dashboard_settings.py`
- `tests/test_dashboard_settings_ui.py`
- `tests/test_config_persistence.py`

Other focused modules include:

- `tests/test_proxy_tags.py`
- `tests/test_diagnostics_metrics.py`
- `tests/test_activity.py`
- `tests/test_context_meter.py`
- `tests/test_context_monitor.py`
- `tests/test_compression_manager.py`
- `tests/test_model_context.py`
- `tests/test_dashboard_snapshots.py`
- `tests/test_dashboard_intelligence.py`
- `tests/test_config.py`
- `tests/test_resources.py`
- `tests/test_service_runner.py`
- `tests/test_main_wizard.py`
- `tests/test_wizard.py`

## Core proxy compatibility

Goal: ContextKeeper behaves like an Ollama-compatible server to existing clients.

Automated coverage should confirm:

- `/api/tags` passes through.
- `/api/*` passthrough behavior is preserved.
- `/v1/*` passthrough behavior is preserved.
- Ollama connectivity failures return an appropriate `502`.
- Request diagnostics record endpoint, method, model, status, latency, client host, generation sequence, and conversation id where available.

Manual smoke checks:

1. Start Ollama.
2. Start ContextKeeper.
3. Request `http://localhost:11500/api/tags`.
4. Point an Ollama-compatible client to `http://localhost:11500`.
5. Confirm models populate and chat/generation works.

## Streaming behavior

Goal: ContextKeeper must not break Ollama streaming semantics.

Validate:

- `/api/chat` streaming responses remain streamed.
- `/api/generate` streaming responses remain streamed.
- Client disconnect/cancellation does not leave active request state stuck.
- Errors during streaming are recorded without corrupting the stream contract.

## Diagnostics and metrics

Validate:

- Request count increments.
- Error count increments for failing upstream calls.
- Last endpoint, model, status, and latency are tracked.
- Recent request history is bounded.
- System metrics expose CPU and memory data.
- GPU metrics degrade safely when `nvidia-smi` is unavailable.
- Operational activity state transitions remain coherent during idle, active, streaming, failed, and completed requests.

## Context engine and Automatic Model Context Discovery

Validate:

- Conversation Snapshot creation.
- Message tracking for chat requests.
- Estimated token counts increase with message content.
- Context Usage percentage uses the resolved context-window capacity.
- Warning threshold uses `>= context.warning_threshold_percent`.
- Compression threshold uses `>= context.compression_threshold_percent`.
- Invalid threshold ordering is rejected.
- Model-specific `models.<model>.context_window_tokens` overrides take precedence.
- `/api/show` metadata can populate Automatic Model Context Discovery.
- Default context-window fallback is used when no override or discovered value exists.
- `options.num_ctx` is enforced for conversational generation requests.
- Dashboard source labels distinguish `Pre-defined`, `Discovered`, and `Default`.

## Compression

Validate:

- Compression planning preserves the configured number of recent messages.
- Compression manager returns unchanged conversations below threshold.
- Compression manager condenses older messages when threshold conditions and summarizer output support it.
- Rolling-summary metadata is maintained.
- Repeated compression is idempotent without new history.
- Dashboard compression history is shown only when confirmed rolling-summary state exists.

Current boundary:

- Durable historical original-message retrieval after compression is planned for Phase 6.5G and should not be treated as implemented.

## Dashboard baseline

Validate:

- `/dashboard` renders.
- `/health`, `/metrics`, and `/dashboard/data` return expected structures.
- The dashboard uses one refresh loop.
- Dashboard snapshot generation uses one consistent conversation snapshot during a payload build.
- Missing, idle, and partial data do not produce JavaScript errors.
- Dashboard polling continues during active traffic and while the Conversation Inspector drawer is open.

## Settings Snapshot, APIs, and dashboard UI

Validate:

- `GET /api/dashboard/settings` returns a read-only schema-v2 settings snapshot without changing runtime or disk state.
- Categories are ordered as Context, Compression, and Dashboard.
- Each setting includes stable id, category, display name, description, runtime `value`, `persisted_value`, `default_value`, `differs_from_persisted`, minimum, maximum, `runtime_editable`, `persistable`, `reset_eligible`, `restart_required`, and data type.
- Approved settings are exposed:
  - `context.enabled`
  - `context.warning_threshold_percent`
  - `context.compression_threshold_percent`
  - `context.keep_recent_messages`
  - `compression.enabled`
  - `compression.summarizer_model`
  - `compression.max_summary_tokens`
  - `dashboard.refresh_interval_ms`
- Current effective values come from the runtime `Settings` instance; persisted values come from a fresh active-file read; built-in defaults remain available for comparison.
- Reset eligibility is explicit authoritative metadata; read-only, unsupported, unmanaged, and reset-ineligible settings are excluded from reset payloads.
- Current boolean, integer, and string settings retain correctly typed authoritative defaults. An already-default individual setting has a disabled reset action; an entirely-default category or global scope is also disabled.
- Runtime/persisted divergence and equality produce the correct `differs_from_persisted` value without type coercion.
- Validation metadata includes integer minimum/maximum values where applicable.
- Output is sanitized and does not include environment variables, config file paths, secrets, server bind details, Ollama base URL, logging paths, metrics settings, or model override maps.
- `PATCH /api/dashboard/settings` supports valid partial updates and returns the complete canonical snapshot.
- Omitted settings retain prior runtime values.
- A subsequent `GET /api/dashboard/settings` returns the updated values.
- Context and compression sections can be updated together.
- Later valid updates can change earlier runtime values again.
- Invalid boolean, integer, percentage, `keep_recent_messages`, `max_summary_tokens`, blank model, unknown field, read-only field, wrong-shape, missing-body, and malformed JSON inputs are rejected.
- Threshold relationships are validated on the merged proposed state, including partial updates that conflict with retained current threshold values.
- Atomic rejection is verified: a request containing one valid setting and one invalid setting changes neither value.
- Reset and Discard recovery payloads receive the same strict complete-proposal validation and all-or-nothing mutation behavior as ordinary PATCH updates.
- Empty JSON update bodies are deliberately rejected.
- PATCH does not write configuration automatically, and a runtime update can differ from persisted metadata until an explicit PUT.
- Malformed or inaccessible persisted state causes PATCH to fail before runtime mutation rather than returning fabricated persisted metadata.
- Settings GET/PATCH disk reads are registered as synchronous FastAPI handlers so slow file I/O or lock waits use the worker pool rather than blocking unrelated async proxy work.
- `POST`, `PUT`, and `DELETE` on `/api/dashboard/settings` itself return `405`; persistence uses the separate config resource.

Settings reset and recovery coverage should confirm:

- An individual reset updates only the selected reset-eligible setting, uses its authoritative `default_value`, marks runtime/persisted divergence correctly, and does not write YAML.
- Individual reset still receives backend type, range, full-model, and cross-field validation; an invalid proposal does not mutate runtime.
- A category reset requires confirmation, includes all and only reset-eligible settings in that category, including eligible values already at default, leaves unrelated categories unchanged, and sends one atomic PATCH.
- A rejected category reset applies no partial runtime mutation and does not modify YAML.
- The global control is labeled **Reset managed settings to defaults**, requires confirmation, and stages all and only reset-eligible dashboard-managed settings in one atomic PATCH.
- Read-only, unsupported, reset-ineligible, and unmanaged settings remain unchanged; no logs, metrics, conversations, summaries, model files, or other application data are cleared; no restart is triggered.
- Cancelling category or global confirmation sends no request, changes no setting, and reports cancellation without false success.
- Successful reset feedback reports a staged count where practical, states that reset did not write configuration, and distinguishes Save-required persisted divergence from an already-matching configuration that needs no save.
- Runtime, persisted, default, unsaved, and restart-required states remain distinguishable after individual, category, and global reset.
- Discard restores browser-only drafts locally; when runtime-editable confirmed values differ from persisted state, it sends one atomic PATCH using each differing `persisted_value`, writes no YAML, and refreshes confirmed/draft metadata from the canonical response.
- Failed Discard recovery applies no partial update and does not falsely report that runtime was restored.
- Reset alone never calls `PUT /api/dashboard/settings/config`, creates/replaces YAML, or changes its bytes.
- Save after reset persists staged defaults through the existing PUT service, refreshes persisted state, retains unmanaged YAML keys/sections, and preserves restart-required guidance.
- Save validation or storage failure retains the prior valid file and staged runtime/UI state and does not falsely report success.
- Restart loading observes successfully persisted default values according to normal configuration precedence.
- No reset endpoint or unnecessary public API method is introduced; existing GET, PATCH, PUT, and unsupported-method responses remain compatible.

Persistence service coverage should confirm:

- one setting, multiple settings in one category, and settings across multiple categories persist successfully;
- only explicitly requested values change;
- unrelated configuration categories/values and model-specific configuration entries remain present;
- the service resolves the same active path rules as startup and creates a missing file/parent directory deliberately;
- a missing file starts from validated defaults and reports `configuration_created: true`;
- the active file is freshly re-read under the process-global lock for every operation;
- unknown categories, unknown setting ids, non-persistable settings, requests with no supplied values, malformed category payloads, nulls, strict boolean/integer violations, blank strings, range violations, and cross-field conflicts are rejected, while an empty approved category may accompany another valid populated category;
- malformed YAML, invalid UTF-8, non-mapping YAML, and invalid existing configuration fail clearly without replacing the file;
- read, directory, permission/read-only, serialization, temporary-write, temporary-verification, and atomic-replace failures return safe testable errors;
- a same-directory UTF-8 temporary candidate is flushed, `fsync`ed, read back, byte-verified, parsed, and validated before replacement;
- failed candidate preparation or replacement leaves the original destination unchanged and removes the temporary file when cleanup succeeds;
- cleanup failure is logged safely and does not expose the path or overwrite the primary failure;
- a changed fingerprint returns a stale-write conflict and retains both the external edit and request safety;
- two concurrent in-process writes serialize and do not interleave replacement work;
- persistence does not mutate the shared runtime settings instance or restart ContextKeeper;
- successful persistence refreshes metadata, including restart-required persisted/runtime divergence when metadata is configured for that generic case.
- saving staged default values changes only allowlisted managed fields and retains unknown/unmanaged YAML content under the B6.4 persistence contract.

Persistence API coverage should confirm:

- `PUT /api/dashboard/settings/config` accepts the documented category-grouped request and returns `200` with `status`, sorted `persisted_setting_ids`, `configuration_created`, and a complete schema-v2 `settings` snapshot;
- empty requests return `400`, request validation errors return `422`, invalid/stale existing configuration returns `409`, and safe storage failures return `500`;
- missing and malformed request bodies follow FastAPI validation behavior without stack traces;
- success changes disk metadata only and leaves the runtime value unchanged;
- existing GET and PATCH behavior remains valid after the new route is registered;
- unsupported methods remain `405` and dashboard management routes never fall through to Ollama proxying.

Settings UI coverage should confirm:

- Settings navigation is an interactive keyboard-operable page target inside the existing dashboard shell, and Operations remains available.
- Opening Settings performs a guarded first `GET /api/dashboard/settings`; repeated page switching does not duplicate listeners, loads, or polling timers.
- Categories and controls are generated from API metadata rather than a hard-coded setting list.
- Boolean, integer, and string rendering paths preserve value types; supplied minimum/maximum constraints are represented.
- Labels, descriptions, default/saved values, runtime/persisted difference text, status/live regions, runtime-read-only/non-persistable explanations, reset availability/disabled state, and restart-required indicators have accessible markup.
- Each eligible setting has a native reset button with a setting-specific accessible name; it is semantically and visually disabled when runtime already equals the default or reset is unavailable.
- Reset values and inclusion are derived from `default_value` and `reset_eligible` metadata without hard-coded browser defaults or a parallel setting allowlist.
- Individual reset sends one single-setting PATCH without confirmation; category and global reset use native keyboard-operable confirmation and send one multi-setting PATCH only after acceptance.
- Category reset selection is isolated to the requested category; category and global selection include all and only reset-eligible managed settings in scope, including eligible values already at default once an action is enabled.
- Reset success accepts the canonical snapshot, preserves runtime/persisted/default distinctions, and announces staged-unsaved state and count where practical.
- Reset cancellation changes no state and uses the existing feedback convention; reset failure preserves the current UI/runtime representation for retry.
- Confirmed and draft snapshots are separate clones, and confirmed state is protected from draft mutation.
- Runtime dirty calculation compares draft with runtime `value`; persistence dirty calculation compares draft with `persisted_value`; both use typed equality and metadata eligibility.
- Save runtime changes guards duplicate submission and sends one nested PATCH containing only intended changed runtime-editable fields.
- Save to configuration renders as a separate button, is disabled with no eligible persisted difference, never runs on input/edit or runtime form submission, and sends one nested PUT containing only intended changed persistable fields.
- Either loading state locks controls and both save actions to prevent duplicate/conflicting submissions.
- Successful PATCH accepts the canonical response and clears applied runtime dirty state.
- Successful PUT accepts refreshed runtime/persisted metadata while restoring the user's draft, so persisted values can remain pending runtime application.
- Validation failures map exact API error locations to controls when possible, provide a page-level alert, preserve all draft values, preserve dirty state, and allow correction/retry.
- PATCH and PUT network, server, and malformed-response paths fail safely, render response data as text, preserve the draft, and allow retry.
- Discard restores browser-only draft edits locally; when confirmed runtime differs from persisted state, it sends one atomic changed-fields-only PATCH using `persisted_value` for every runtime-editable differing setting, never PUT, and accepts the canonical response.
- Discard validation, network, server, and malformed-response failures preserve the current state and do not falsely report success.
- The visible notice distinguishes Discard runtime changes, Reset to defaults, and Save to configuration, and states that none writes YAML except Save to configuration and none restarts ContextKeeper automatically.
- No browser storage, automatic persistence, per-setting autosave, reset endpoint, factory reset, restart orchestration, application-data clearing, self-diagnostics, or repair workflow is added.
- Manual observation should confirm runtime-only changes reset after process restart, persisted changes survive restart, and restart-required guidance remains explicit where applicable.
- Existing `/dashboard/data`, proxy/streaming behavior, Conversation Inspector, Connection Flow, Request Traffic, Context Trend, instrument panel, reduced-motion, context-engine, and compression tests remain green.

Focused B6.5 command:

```powershell
python -m pytest -q tests/test_config_persistence.py tests/test_dashboard_settings.py tests/test_dashboard_settings_ui.py
```

Latest B6.5 implementation evidence: the focused command passed 132 tests, and the complete `python -m pytest -q` suite passed 396 tests. Both runs reported only the two existing third-party deprecation warnings documented in Project History.

Phase 6.5F-B6.5 Product Owner QA should exercise keyboard navigation between Operations and Settings; individual reset; category/global confirmation and cancellation; already-default disabled states; staged-count and unsaved feedback; Discard recovery to persisted values; Save to configuration after reset; retry after reset, validation, or storage failure; runtime-versus-persisted/default messaging; restart-required guidance; live dashboard behavior during repeated view switching; and layout at supported desktop and narrow widths. Approval remains a manual checkpoint after automated regression passes.

## Request Traffic

Validate:

- Request Traffic markup exists.
- Empty/idle state is readable.
- Recent request history maps to the visualization.
- Rate, trend, and error states update from existing request metrics.
- Existing live traffic and connection-flow behavior remain intact after changes.

Manual Visual QA:

- Confirm the Request Traffic sparkline/bars remain compact.
- Confirm no flicker during polling.
- Confirm labels remain readable at 50%, 75%, and 100% browser zoom.

## Connection Flow

Validate:

- Client, ContextKeeper, Ollama, and Model nodes render.
- Active/idle/warning/offline states are communicated with text and badges, not color alone.
- The moving marker is visible during active traffic and inactive when idle.
- Animation timing/direction remains unchanged unless intentionally scoped.
- Reduced-motion mode disables continuous motion without losing state readability.

Manual Visual QA:

- Review idle, active request, upstream failure, and model observed states.
- Confirm no horizontal overflow.
- Confirm the marker does not distract from labels or nodes.

## Conversation Timeline

Validate:

- Empty timeline state appears when no conversation activity exists.
- Timeline payload has stable event structure and stable event IDs.
- Events are chronological and bounded.
- Request received/completed/failed events are represented when supported by current data.
- Context warning and compression events appear only when supported by existing state.
- No prompt, response, rolling-summary, or private message body leaks into timeline events.
- Polling does not duplicate DOM entries or visibly flicker.

Manual Visual QA:

- Confirm the timeline reads as a compact operational narrative.
- Confirm bounded internal scrolling works.
- Confirm selecting a conversation entry opens the Conversation Inspector.

## Conversation Inspector

Validate:

- Drawer markup, title, close control, accessible labels, loading state, unavailable state, Overview, and Intelligence render.
- Timeline entries that map to a real conversation are keyboard and mouse selectable.
- Selected-entry highlight follows active selection.
- Closing by button and Escape works.
- Focus returns to the opening timeline entry where practical.
- Selection persists across dashboard refresh when the selected conversation remains available.
- If the selected conversation disappears, the drawer reports unavailable instead of silently switching.
- No additional polling interval is introduced.

## Conversation Inspector: Overview & Intelligence

Validate Overview:

- Stable DOM hooks exist for core fields.
- Conversation identifier, state, model, client/source, endpoint, request type, message count, request count, estimated tokens, context-window capacity, Context Usage, compression count, last activity, and duration map correctly when available.
- Missing values render safe placeholders.
- Externally derived strings are escaped.

Validate Intelligence:

- Insufficient-data state.
- Healthy below warning threshold.
- Just below warning threshold.
- Exactly at warning threshold.
- Just below compression threshold.
- Exactly at compression threshold.
- Above compression threshold.
- Compression-history behavior.
- Context-disabled behavior.
- Compression-disabled behavior.
- Critical pressure when usage exhausts or exceeds known capacity.
- Recommendation appears only for genuine action-required states.

Privacy checks:

- No prompt text.
- No assistant response text.
- No rolling-summary body text.
- No request body, headers, API secrets, or retrieved document contents.

## Responsive layout and Visual QA

Manual dashboard review should include:

- 3440×1440.
- 2450×1440.
- 1720×1440.
- 50%, 75%, and 100% browser zoom.
- 100% Windows display scaling where practical.
- Narrow/mobile breakpoint behavior.
- No clipping.
- No horizontal page overflow.
- Balanced spacing.
- System instrument panel: CPU Usage, GPU Usage, Memory Usage, Context Usage, Compression Status.
- System Activity row: Context Trend and Connection Flow.
- Operations lower row: Traffic, Active Conversation, Live Conversation Timeline.
- Conversation Inspector desktop drawer and narrow full-width/backdrop behavior.
- Settings categories and fields at desktop, tablet/narrow desktop, and mobile widths.
- Settings labels, runtime/saved/default difference text, constraints, badges, individual/category/global reset controls, feedback, and the sticky Discard/runtime Save/configuration Save action bar wrap without horizontal overflow.
- Settings loading, empty, retry, runtime-save success, reset-staged success, reset-cancelled, discard-recovery success, configuration-save success, validation-error, storage-error, and network-error states remain readable without color alone.
- Reset controls and native confirmation remain keyboard-operable, disabled states remain semantic, and reduced-motion behavior is unchanged.

## Reduced motion

Validate:

- `prefers-reduced-motion` disables or simplifies continuous animations.
- Connection Flow marker animation does not continue under reduced motion.
- Timeline/inspector transitions remain readable without motion.
- No feature communicates status only through animation.

## Dashboard idle, active, completed, and failed states

Validate:

- Fresh startup with no traffic.
- Ollama offline.
- Ollama online but no model observed.
- Active generation request.
- Streaming request.
- Completed request.
- Failed request.
- Active conversation with context estimates.
- Completed/idle conversation snapshot.
- Compression present.
- Context warning and compression threshold states.

## Windows executable, service, and installer

Validate:

- PyInstaller build creates `dist/ContextKeeper.exe`.
- Packaged executable loads editable config beside the executable when present.
- Packaged executable can fall back to bundled config.
- First-run wizard can create `contextkeeper.yaml`.
- Release build script creates installer output when prerequisites are installed.
- Windows service host foundation can construct the ContextKeeper application runner.

Current boundary:

- Service installation hooks remain placeholder work until a later release phase.

## Regression checklist

Every release candidate should confirm:

- `/api/tags` works.
- `/api/chat` works.
- `/api/generate` works.
- Streaming works.
- AnythingLLM or another Ollama-compatible client connects.
- Logs are created when logging is enabled.
- Dashboard renders and refreshes.
- Request Traffic updates.
- Connection Flow updates.
- Context Usage and Context Trend update.
- Live Conversation Timeline updates.
- Conversation Inspector opens, updates, and closes.
- Settings navigation opens the metadata-driven form and returns to Operations without a page reload.
- Settings runtime Save sends one changed-fields-only PATCH; individual/category/global reset sends one scope-limited atomic PATCH; Save to configuration sends one changed-fields-only PUT only after explicit action; Discard sends no request for browser-only drafts and one atomic PATCH when restoring persisted runtime values; failed operations preserve recoverable state.
- Runtime-only setting changes, including staged defaults, return to effective startup values after ContextKeeper restarts; persisted values survive restart, and no dashboard settings action restarts ContextKeeper automatically.
- Configuration writes retain unrelated/model-specific data, fail atomically, leave no temporary file after ordinary failure cleanup, and do not expose filesystem paths or configuration contents.
- Reset and Discard never clear logs, metrics, conversations, summaries, model files, or other application data and never alter Ollama-compatible proxy or streaming behavior.
- Reduced-motion behavior is respected.
- No prompt/response/summary content appears in routine dashboard surfaces.
