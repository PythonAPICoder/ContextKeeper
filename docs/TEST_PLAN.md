# ContextKeeper Test Plan

Status: Current through Phase 6.5F-B6.3.

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

- `GET /api/dashboard/settings` returns a settings snapshot.
- Snapshot schema version is present.
- Categories are ordered as Context, Compression, and Dashboard.
- Each setting includes stable id, category, display name, description, value, default value, minimum, maximum, runtime-editable flag, restart-required flag, and data type.
- Approved settings are exposed:
  - `context.enabled`
  - `context.warning_threshold_percent`
  - `context.compression_threshold_percent`
  - `context.keep_recent_messages`
  - `compression.enabled`
  - `compression.summarizer_model`
  - `compression.max_summary_tokens`
  - `dashboard.refresh_interval_ms`
- Current effective values come from the runtime `Settings` instance.
- Built-in defaults are present for future UI comparison.
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
- Empty JSON update bodies are deliberately rejected.
- `POST`, `PUT`, and `DELETE` on `/api/dashboard/settings` return `405`.
- Settings navigation is an interactive keyboard-operable page target inside the existing dashboard shell, and Operations remains available.
- Opening Settings performs a guarded first `GET /api/dashboard/settings`; repeated page switching does not duplicate listeners, loads, or polling timers.
- Categories and controls are generated from API metadata rather than a hard-coded setting list.
- Boolean, integer, and string rendering paths preserve value types; supplied minimum/maximum constraints are represented.
- Labels, descriptions, status/live regions, runtime-read-only explanations, and restart-required indicators have accessible markup.
- Confirmed and draft snapshots are separate clones, and confirmed state is protected from draft mutation.
- Dirty calculation uses typed value equality, excludes non-runtime-editable fields, removes manually restored values from the change set, and drives clean/dirty Save and Discard states.
- Save guards duplicate submission and sends one nested atomic PATCH containing only changed runtime-editable fields.
- Successful save accepts the canonical response, refreshes confirmed/draft state, clears dirty state, and provides success feedback.
- Validation failures map exact API error locations to controls when possible, provide a page-level alert, preserve all draft values, preserve dirty state, and allow correction/retry.
- Network, server, and malformed-response paths fail safely, render response data as text, preserve the draft, and allow retry.
- Discard restores the latest confirmed snapshot, clears field errors and dirty state, and performs no network request.
- The visible Settings notice states that changes are runtime-only, reset on ContextKeeper restart, and do not modify `contextkeeper.yaml`.
- No persistence, YAML writing, browser storage, reset-to-defaults workflow, or per-setting autosave is added.
- Manual observation should confirm runtime changes reset after process restart.
- Existing `/dashboard/data`, proxy/streaming behavior, Conversation Inspector, Connection Flow, Request Traffic, Context Trend, instrument panel, reduced-motion, context-engine, and compression tests remain green.

Phase B6.3 Product Owner QA should exercise keyboard navigation between Operations and Settings; manual reversal, Save, retry after a validation failure, and Discard; visible runtime-only messaging; live dashboard behavior during repeated view switching; and layout at the supported desktop and narrow widths. Approval remains a manual checkpoint after automated regression passes.

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
- Settings labels, descriptions, constraints, badges, feedback, and sticky Save/Discard action bar wrap without horizontal overflow.
- Settings loading, empty, retry, success, validation-error, and network-error states remain readable without color alone.

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
- Settings Save sends one changed-fields-only update; Discard sends none; failed Save preserves the draft.
- Runtime settings reset after ContextKeeper restarts and `contextkeeper.yaml` remains unchanged.
- Reduced-motion behavior is respected.
- No prompt/response/summary content appears in routine dashboard surfaces.
