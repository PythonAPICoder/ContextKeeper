# ContextKeeper Configuration

Status: Current through the Phase 6.5F-B6.6 working-tree implementation; Product Owner and architect review are pending. Verified against `src/ctxkeeper/config.py`, `src/ctxkeeper/resources.py`, `src/ctxkeeper/dashboard/settings_snapshot.py`, `src/ctxkeeper/dashboard/config_persistence.py`, `src/ctxkeeper/dashboard/connection_test.py`, `src/ctxkeeper/dashboard/routes.py`, and `src/ctxkeeper/dashboard/template.py`.

ContextKeeper is configured through `contextkeeper.yaml`, with a small set of environment variable overrides. The first-run wizard creates this file when it is missing.

## Configuration file location

Default filename:

```text
contextkeeper.yaml
```

Source-mode behavior:

- Relative default path resolves from the current working directory.
- An explicit absolute configuration path is preserved.
- An explicit relative non-default path resolves from the current working directory.
- The persistence service receives the same resolved path used by application startup.

Packaged/frozen behavior:

- ContextKeeper first looks for `contextkeeper.yaml` beside the executable.
- If that file is absent, it can fall back to the bundled PyInstaller resource.
- A user-editable file beside `ContextKeeper.exe` overrides the bundled fallback.
- If neither file exists, resolution returns the expected path beside the executable; an explicit persistence request can create the file and missing parent directories.

For a packaged installation, place an editable `contextkeeper.yaml` beside `ContextKeeper.exe` before persisting settings. If resolution selected a bundled fallback, persistence targets that active resolved path and can fail if the bundle is not writable. API errors never disclose the resolved filesystem path.

## Complete default configuration

```yaml
app:
  name: "ContextKeeper"
  environment: "development"

server:
  host: "0.0.0.0"
  port: 11500

ollama:
  base_url: "http://localhost:11434"
  timeout_seconds: 120

logging:
  level: "INFO"
  file: "logs/contextkeeper.log"
  request_log_enabled: true
  log_request_bodies: false

metrics:
  enabled: true
  gpu_enabled: true
  refresh_interval_seconds: 2

dashboard:
  enabled: true
  title: "ContextKeeper Dashboard"
  refresh_interval_ms: 1000

context:
  enabled: true
  default_context_window_tokens: 32768
  warning_threshold_percent: 75
  compression_threshold_percent: 85
  minimum_threshold_percent: 10
  keep_recent_messages: 8

compression:
  enabled: true
  summarizer_model: "gpt-oss:20b"
  max_summary_tokens: 1200

models: {}
```

## Environment variable overrides

Only these environment variables are currently supported:

| Environment variable | Overrides |
| --- | --- |
| `CONTEXTKEEPER_HOST` | `server.host` |
| `CONTEXTKEEPER_PORT` | `server.port` |
| `CONTEXTKEEPER_OLLAMA_URL` | `ollama.base_url` |
| `CONTEXTKEEPER_LOG_LEVEL` | `logging.level` |

No environment variable currently overrides dashboard refresh timing, context thresholds, compression settings, model context overrides, or metrics settings.

## Configuration precedence

The configuration precedence policy, from highest to lowest, is:

1. Command-line setting overrides, where a command supports them.
2. Supported environment variable overrides.
3. Values loaded from `contextkeeper.yaml`.
4. Built-in defaults from `Settings`.

Current source behavior implements no command-line setting override. The `--configure` flag launches the configuration wizard and exits; it does not provide per-setting runtime overrides. Among the currently implemented value sources, loading begins with built-in defaults, overlays YAML, and finally overlays the supported environment variables. `CONTEXTKEEPER_OLLAMA_URL` can therefore make the active `ollama.base_url` differ from the saved YAML value displayed in the Connection category.

Save to configuration writes only the YAML tier. It does not edit command-line arguments or environment variables and cannot override a higher-priority source. The current settings snapshot reports the active and persisted values but does not track or label the active value's provenance; the dashboard must not imply that saving YAML supersedes an environment override.

## Dashboard Settings page and Settings Management API

The Settings destination inside the existing dashboard shell uses four deliberately separate operations:

```text
GET   /api/dashboard/settings         Read runtime and persisted metadata
PATCH /api/dashboard/settings         Update the current process only
PUT   /api/dashboard/settings/config  Persist explicitly supplied values only
POST  /api/dashboard/settings/connection/test
                                      Test draft Connection values in isolation
```

None of these dashboard management routes is proxied to Ollama. Ordinary field editing sends no request. Runtime Save and runtime-editable reset/Discard recovery use PATCH and never write YAML. Connection resets are browser-draft operations and do not PATCH. Save to configuration uses PUT and never applies runtime changes or restarts ContextKeeper. Test Connection performs one isolated probe and changes neither YAML nor active state. B6.6 adds neither a reset endpoint nor a live-reconfiguration endpoint.

### GET settings snapshot

The page requests `GET /api/dashboard/settings` when Settings is first opened and constructs its category sections and controls from the response. Display metadata is rendered as text, not executable markup. The API exposes only approved Connection, Context, Compression, and Dashboard settings; it does not expose environment variables, file paths, secrets, passwords, API tokens, server bind details, logging paths, model override maps, or unrelated future configuration.

Schema version 2 includes, for each setting:

- stable `id`, `category`, display name, and description;
- current runtime `value`;
- current disk-derived `persisted_value`;
- built-in `default_value`;
- `data_type` plus `minimum` and `maximum` where applicable;
- computed `differs_from_persisted`;
- `runtime_editable`, `persistable`, `reset_eligible`, and `restart_required`.

GET freshly reads and validates the active configuration so persisted metadata reflects disk rather than only startup state. GET is read-only: it changes neither runtime state nor the file. A missing file is represented by validated built-in defaults until an explicit PUT creates it. Invalid UTF-8, malformed/non-mapping YAML, an invalid existing configuration, or a read failure returns a safe error rather than manufacturing persisted metadata.

The categories are ordered Connection, Context, Compression, and Dashboard. The eight pre-B6.6 settings remain runtime-editable, persistable, and reset-eligible. `ollama.base_url` and `ollama.timeout_seconds` are persistable and reset-eligible but not runtime-editable, and both require restart. Their successful PUT can make `persisted_value` differ from the active runtime `value` until the user manually restarts ContextKeeper; there is no automatic restart action. Reset eligibility remains an explicit server-owned contract rather than a browser-side allowlist.

### PATCH runtime settings

Save runtime changes constructs one nested PATCH body containing only draft values that differ from confirmed runtime values and are marked `runtime_editable`. Numeric, boolean, and string values retain their JSON types. The backend merges the partial update into the current complete runtime state, validates the proposal, and mutates the shared in-memory `Settings` instance only after all validation succeeds.

The Connection category is not accepted by PATCH. Saving or resetting `ollama.base_url` and `ollama.timeout_seconds` must never mutate the startup-owned active settings/client or affect active requests and streams.

Omitted settings retain their current runtime values. Failed validation is atomic, and a successful response is the complete schema-v2 snapshot. PATCH never invokes the persistence service, never writes the active YAML file, and never restarts ContextKeeper. Runtime-only differences reset at process restart unless the user separately chooses Save to configuration.

Runtime-editable reset and Discard recovery requests use the same partial update model and validation path. The frontend can assemble a multi-setting request from `default_value` or `persisted_value` metadata, but the backend still independently rejects unknown, unsupported, incorrectly typed, out-of-range, or cross-field-invalid updates before any runtime mutation.

Because a successful schema-v2 response must contain truthful persisted metadata, PATCH reads and validates the active configuration before changing runtime state. If persisted state is malformed or inaccessible, PATCH returns the same safe configuration error as GET and leaves runtime state unchanged. GET and PATCH are synchronous FastAPI handlers, so these disk reads and any wait on the process-local persistence lock run in the framework worker pool rather than blocking proxy/streaming event-loop work.

Example:

```powershell
$body = @{
    context = @{
        warning_threshold_percent = 70
        compression_threshold_percent = 88
    }
    compression = @{
        max_summary_tokens = 900
    }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
    -Method Patch `
    -Uri http://localhost:11500/api/dashboard/settings `
    -ContentType "application/json" `
    -Body $body
```

### Reset and recovery controls

Reset to defaults stages authoritative values and remains deliberately separate from Save to configuration:

- Each runtime-editable setting marked `reset_eligible` has an individual reset action that submits only that setting with its server-provided `default_value` through PATCH.
- An individual Connection reset stages its server-provided default in the browser draft without PATCH. Connection-category reset stages both Connection defaults locally after confirmation.
- The deliberate global action is labeled **Reset managed settings to defaults**. It requires native confirmation, stages all reset-eligible defaults, and sends one atomic PATCH containing only the runtime-editable subset. The Connection defaults remain persistence-only drafts until Save to configuration.
- Category and global runtime payloads are validated as complete proposals. If any value or cross-field relationship is invalid, PATCH applies none of the requested runtime changes.
- Successful feedback identifies how many settings were staged where practical and states that reset did not write configuration. It directs the user to Save to configuration when persisted values differ, or reports that no save is needed when they already match. Cancellation sends no request and changes no settings.

Reset values come from authoritative snapshot metadata. Dashboard JavaScript and HTML do not contain a duplicate table of built-in defaults. Read-only, unsupported, reset-ineligible, and unmanaged fields are excluded. Reset does not delete, recreate, or replace the complete YAML document; clear logs, metrics, conversations, summaries, model files, or other application data; or restart ContextKeeper. It is not a factory reset.

Discard has two paths. Browser-only draft edits, including Connection-only edits and staged Connection defaults, are restored from the confirmed snapshot locally and send no PATCH. When confirmed runtime values differ from persisted values, Discard sends one atomic PATCH that restores every runtime-editable differing value from `persisted_value`; Connection fields are excluded. It never sends PUT or changes YAML. A validation or request failure preserves the current runtime/UI state and reports an error instead of claiming success.

After a reset, Save to configuration remains the only persistence action. It sends eligible staged defaults through the existing validated PUT service. A successful save refreshes runtime and persisted metadata, preserves unmanaged YAML content, and does not override higher-priority sources or restart ContextKeeper.

### PUT persisted configuration

Save to configuration constructs one nested body containing only draft values that differ from confirmed persisted values and are marked `persistable`. Its request shape is:

```json
{
  "ollama": {
    "base_url": "http://ai-server:11434",
    "timeout_seconds": 120
  },
  "context": {
    "warning_threshold_percent": 75
  },
  "compression": {
    "enabled": true
  }
}
```

A successful response has this top-level structure; the representative nested snapshot below is abbreviated, while the real response contains every approved category and setting:

```jsonc
{
  "status": "saved",
  "persisted_setting_ids": [
    "compression.enabled",
    "context.warning_threshold_percent"
  ],
  "configuration_created": false,
  "settings": {
    "schema_version": 2,
    "categories": [
      {
        "id": "context",
        "display_name": "Context",
        "description": "Controls context tracking, pressure thresholds, and recent-message retention.",
        "settings": [
          {
            "id": "context.enabled",
            "category": "context",
            "display_name": "Context tracking",
            "description": "Enable ContextKeeper's conversation context tracking and usage estimates.",
            "value": true,
            "persisted_value": true,
            "default_value": true,
            "differs_from_persisted": false,
            "minimum": null,
            "maximum": null,
            "runtime_editable": true,
            "persistable": true,
            "restart_required": false,
            "reset_eligible": true,
            "data_type": "boolean"
          }
          // Remaining approved Context settings, followed by complete Compression and Dashboard categories.
        ]
      }
    ]
  }
}
```

`persisted_setting_ids` is sorted and contains only fields included in the accepted request. `configuration_created` is true when the active file did not exist before the operation. The refreshed `settings` snapshot reports the unchanged runtime values alongside the newly persisted values. PUT does not implicitly PATCH the runtime and does not restart ContextKeeper.

The endpoint requires a JSON object grouped by approved category and at least one supplied setting value. It rejects missing or malformed JSON, arrays and other top-level shapes, requests with no setting values (`{}` or only empty category objects), unknown categories, unknown setting ids, fields not represented by authoritative dashboard metadata, and settings marked non-persistable. An empty approved category may accompany another category that contains a valid requested value; the empty category is simply omitted from the update. Booleans must be JSON booleans; integers must be JSON integers rather than strings, booleans, or floating-point values; strings must meet their business rules. Minimum, maximum, full-model, cross-field, Connection URL, and deterministic self-loop validation are applied to the merged candidate.

Malformed request shape and type errors return `422`; a request supplying no setting values returns `400`. Invalid existing YAML/configuration and stale fingerprints return `409`. Read, permission/read-only destination, directory, temporary-write/verification, serialization, and atomic-replacement failures return safe server errors. Cleanup failures are logged safely without replacing the primary failure. Responses do not expose stack traces, filesystem paths, or configuration contents. The original file remains intact unless the final atomic replacement succeeds.

### Atomic write and concurrency behavior

Each persistence operation:

1. Acquires the process-global configuration-persistence lock.
2. Re-reads the resolved active file and records a SHA-256 fingerprint; a missing file begins from an empty mapping validated through built-in defaults.
3. Deep-copies the parsed mapping and changes only explicitly requested approved fields, retaining unrelated categories and model-specific entries.
4. Validates the complete candidate with `Settings` and the shared dashboard cross-field rule.
5. Serializes the full candidate with PyYAML `safe_dump`, `sort_keys=False`, readable block style, and Unicode support, then parses and validates that serialization again.
6. Creates a temporary file in the destination directory, writes UTF-8 with LF newlines, flushes, calls `fsync`, closes, reads the file back, verifies exact bytes, and parses it again.
7. Re-reads the destination and compares its fingerprint with the original. If it changed, the operation returns `409` and does not replace it.
8. Calls `os.replace` for the same-directory atomic replacement.
9. Removes the temporary file after any failed preparation or replacement when cleanup is possible.

The process-global `RLock` prevents two persistence requests in the same ContextKeeper process from interleaving. The fingerprint check is best-effort stale-write protection for an external edit during preparation. There is no cross-process or distributed lock, so another process can still race after the final fingerprint check and before replacement.

PyYAML preserves parsed configuration values, including unmanaged categories and model-specific entries, but it does not preserve comments, exact whitespace, quoting choices, anchors, or original key formatting. A successful write can normalize the full document. B6.4 deliberately does not add a large round-trip YAML dependency.

### Settings page state and feedback

The browser keeps the confirmed server snapshot separate from the editable draft. It computes runtime changes against `value`, persistence changes against `persisted_value`, and reset availability against `default_value` plus `reset_eligible`, all with typed equality. Save runtime changes submits only runtime-editable draft/runtime differences through PATCH. Runtime-editable resets PATCH authoritative defaults, while Connection resets stage persistence-only defaults locally. Save to configuration submits draft/persisted differences through PUT. Save to configuration is disabled when no eligible persistence difference exists, never runs automatically from editing or reset, shows an in-progress label, and locks conflicting controls while pending.

Successful reset feedback states that defaults are staged and reset did not write configuration. It distinguishes persisted differences that require Save to configuration from an already-matching persisted state that needs no save. Successful PUT refreshes runtime/persisted metadata while restoring the user's draft values, so a newly persisted Connection value remains unapplied to runtime until restart. Validation, network, server, and malformed-response failures retain the relevant state and present inline feedback. Discard is local for browser-only drafts and uses one PATCH only when runtime-editable confirmed values must be restored from persisted metadata. Per-setting text identifies active runtime, saved configuration, built-in default, and draft values; badges identify runtime-read-only, non-persistable, runtime-different-from-saved, and restart-required states without relying on color alone.

The Connection card also has a Test Connection action and transient result region. The request uses the current endpoint and timeout drafts even when they differ from active or saved values. While the request is pending, the action is busy and disabled so repeated clicks cannot create concurrent probes. Editing either Connection draft clears the prior result so it cannot be mistaken for evidence about new values. Success displays the tested endpoint, measured latency, Ollama version, and an explicit reminder that the test did not save or activate anything. Failure displays a safe categorized explanation and states that runtime and saved configuration were not changed. A successful test is optional and is never required before Save.

`POST`, `PUT`, and `DELETE` on `/api/dashboard/settings` itself continue to return `405`; configuration persistence is available only at the separate `/api/dashboard/settings/config` resource.

Exposed settings:

| Category | Setting | Reset eligible |
| --- | --- | --- |
| Connection | `ollama.base_url` | Yes |
| Connection | `ollama.timeout_seconds` | Yes |
| Context | `context.enabled` | Yes |
| Context | `context.warning_threshold_percent` | Yes |
| Context | `context.compression_threshold_percent` | Yes |
| Context | `context.keep_recent_messages` | Yes |
| Compression | `compression.enabled` | Yes |
| Compression | `compression.summarizer_model` | Yes |
| Compression | `compression.max_summary_tokens` | Yes |
| Dashboard | `dashboard.refresh_interval_ms` | Yes |

Startup-only or unexposed fields remain rejected by both update APIs, including server host/port, logging paths, metrics settings, model override maps, `context.default_context_window_tokens`, and `context.minimum_threshold_percent`. The two approved Ollama Connection fields are accepted only by persisted configuration PUT, not runtime PATCH.

## Validation rules

- `server.port` must be between `1` and `65535`.
- `ollama.base_url` must satisfy the complete Connection validation rules below.
- `ollama.timeout_seconds` must be a strict integer greater than `0`; booleans, floats, numeric strings, zero, and negative values are rejected. The authoritative minimum is `1`, and there is no configured maximum.
- `logging.level` must be one of `OFF`, `DEBUG`, `INFO`, `WARNING`, `WARN`, `ERROR`, or `CRITICAL`.
- `metrics.refresh_interval_seconds` must be greater than `0`.
- `dashboard.refresh_interval_ms` must be greater than `0`.
- Context thresholds must be between `0` and `100`.
- `context.minimum_threshold_percent <= context.warning_threshold_percent <= context.compression_threshold_percent`.
- `context.default_context_window_tokens` and `context.keep_recent_messages` must be greater than `0`.
- `compression.max_summary_tokens` must be greater than `0`.

Dashboard PATCH and PUT validation additionally reject `context.warning_threshold_percent >= context.compression_threshold_percent` so dashboard-managed thresholds retain a clear warning-before-compression boundary. This is intentionally stricter than the base startup model's less-than-or-equal relationship.

## Connection settings

```yaml
ollama:
  base_url: "http://localhost:11434"
  timeout_seconds: 120
```

Accepted endpoint examples include:

```text
http://localhost:11434
http://192.168.1.50:11434
http://ai-server:11434
https://ollama.example.internal:11434
https://ai.example.internal/ollama
http://[::1]:11434
```

`ollama.base_url` validation and normalization:

- requires a non-empty absolute URL with an `http` or `https` scheme;
- accepts standards-parsed hostnames, IPv4 addresses, and bracketed IPv6 addresses;
- accepts an omitted port or an explicit port from `1` through `65535`;
- accepts a valid base path and preserves it for Ollama requests;
- trims surrounding whitespace, rejects remaining whitespace/control characters, malformed hostname/IP/port syntax, embedded username/password data, query strings, and fragments;
- normalizes scheme and hostname casing, IP representation, and unnecessary trailing slashes while preserving a valid base path;
- rejects an obvious self-proxy reference when the normalized host alias and effective port directly match ContextKeeper's configured listener and the normalized base path is the root or enters ContextKeeper's `/api` or `/v1` proxy namespace.

Self-loop detection is deliberately narrow and deterministic. It performs no DNS lookup, does not reject a remote hostname merely because DNS might resolve it locally, and permits unrelated non-root base paths such as `/ollama`. Listener wildcard aliases are handled locally: `0.0.0.0` includes `localhost`, the IPv4 loopback range, and IPv4-mapped IPv6 loopback forms; `::` includes `localhost` and `::1`; loopback/localhost forms are normalized in the corresponding direction.

Both Connection settings are:

- persistable through `PUT /api/dashboard/settings/config`;
- not runtime-editable through PATCH;
- eligible for reset to authoritative built-in defaults;
- marked restart-required.

Save updates the YAML tier atomically but leaves the canonical runtime `Settings`, active Ollama client, in-flight requests/streams, and active dashboard health/discovery state unchanged. ContextKeeper does not restart automatically. A manual restart is required before the saved values can become active, subject to higher-priority environment or command-line sources. Saving a syntactically valid but currently unreachable endpoint is allowed.

### Test Connection

Request:

```http
POST /api/dashboard/settings/connection/test
Content-Type: application/json
```

```json
{
  "base_url": "https://ai.example.internal/ollama/",
  "timeout_seconds": 120
}
```

The endpoint validates and normalizes the candidate, safely appends `/api/version` without discarding its base path, and performs exactly one `GET`. The isolated temporary client uses `trust_env=False`, follows no redirects, uses normal TLS certificate verification, and closes after success or failure. Its timeout is bounded to `min(timeout_seconds, 10)` seconds. Existing model-discovery retry/backoff is unrelated and is not used by this test.

A validated probe outcome, success or failure, returns HTTP `200`. A representative success is:

```json
{
  "connected": true,
  "tested_endpoint": "https://ai.example.internal/ollama",
  "latency_ms": 18.42,
  "ollama_version": "0.11.4",
  "failure_category": null,
  "message": "Connection successful: Ollama 0.11.4 responded in 18.42 ms. This test did not save or activate the endpoint. Save the configuration and restart ContextKeeper to use it unless a higher-priority override is active."
}
```

Failure categories are `dns_resolution`, `connection_refused`, `timeout`, `tls_error`, `http_error`, `malformed_response`, `non_ollama_response`, `missing_version`, `invalid_version`, and `network_error`. These responses set `connected: false`, omit the Ollama version, and explain that runtime and saved configuration were not changed. Latency is reported when a probe was attempted.

Invalid request values return HTTP `422` with the same safe result fields, an `invalid_endpoint`, `invalid_timeout`, or `invalid_request` category, and a field-associated `detail` list suitable for accessible error focus. GET, PUT, PATCH, DELETE, HEAD, and OPTIONS return explicit `405 Method Not Allowed` with `Allow: POST`.

Test Connection does not write YAML, mutate canonical runtime settings, replace the active HTTP client or endpoint, change active health/Ollama version/metrics/diagnostics/model-discovery state, or become a prerequisite for Save. It is transient candidate information, not background monitoring or live backend switching.

## Dashboard settings

```yaml
dashboard:
  enabled: true
  title: "ContextKeeper Dashboard"
  refresh_interval_ms: 1000
```

- `dashboard.enabled` controls whether dashboard routes are registered.
- `dashboard.title` controls the HTML document title.
- `dashboard.refresh_interval_ms` controls the browser dashboard polling interval.

The current dashboard uses the same refresh path for Operations, Request Traffic, Connection Flow, Context Trend, Live Conversation Timeline, and Conversation Inspector updates. Opening Settings or switching between Settings and Operations does not create another dashboard polling timer. No separate inspector or Settings polling interval exists.

## Context thresholds

```yaml
context:
  enabled: true
  default_context_window_tokens: 32768
  warning_threshold_percent: 75
  compression_threshold_percent: 85
  minimum_threshold_percent: 10
  keep_recent_messages: 8
```

Threshold comparisons are inclusive:

- warning threshold reached when `usage_percent >= warning_threshold_percent`;
- compression threshold reached when `usage_percent >= compression_threshold_percent`.

`minimum_threshold_percent` is validated and retained in configuration for threshold ordering, but it is not a separate dashboard classification threshold.

`keep_recent_messages` controls how many recent messages remain in active context when compression condenses older context.

## Compression settings

```yaml
compression:
  enabled: true
  summarizer_model: "gpt-oss:20b"
  max_summary_tokens: 1200
```

When enabled and context usage crosses the configured compression threshold, ContextKeeper can summarize older active messages into a rolling summary while preserving recent messages.

Current boundary:

- Rolling summaries reduce active prompt size.
- Durable original-message archival retrieval is planned, not implemented.

## Automatic Model Context Discovery

ContextKeeper resolves effective context-window capacity in this order:

1. Model-specific `models.<model>.context_window_tokens`.
2. Automatically discovered Ollama model metadata from `/api/show`.
3. `context.default_context_window_tokens`.

Example model overrides:

```yaml
models:
  gpt-oss:20b:
    context_window_tokens: 32768
  qwen2.5-vl:32b:
    context_window_tokens: 32768
  llama3.2-vision:
    context_window_tokens: 128000
```

For conversational generation requests, ContextKeeper resolves the authoritative capacity and updates the outgoing request body with that value:

```json
{
  "options": {
    "num_ctx": 32768
  }
}
```

Dashboard source labels:

| Label | Meaning |
| --- | --- |
| `Pre-defined` | model-specific `contextkeeper.yaml` override |
| `Discovered` | Ollama `/api/show` metadata |
| `Default` | `context.default_context_window_tokens` fallback |

Discovery is process-local. It improves live context and dashboard accuracy but is not durable across process restart.

## Logging settings

```yaml
logging:
  level: "INFO"
  file: "logs/contextkeeper.log"
  request_log_enabled: true
  log_request_bodies: false
```

`log_request_bodies` defaults to `false` and should remain disabled for normal use. Prompt text, response text, request bodies, secrets, and private document content should not appear in routine documentation or dashboard surfaces.

## Metrics settings

```yaml
metrics:
  enabled: true
  gpu_enabled: true
  refresh_interval_seconds: 2
```

System metrics include CPU and memory telemetry. GPU telemetry is optional and depends on `nvidia-smi` availability.

## Wizard behavior

The first-run wizard prompts for:

- Ollama base URL.
- Proxy host.
- Proxy port.
- Dashboard enabled.
- Context engine enabled.
- Compression enabled.

Run it explicitly with:

```powershell
python -m ctxkeeper.main --configure
```

The wizard writes a validated `contextkeeper.yaml`.
