# ContextKeeper Configuration

Status: Current through Phase 6.5F-B6.1 and verified against `src/ctxkeeper/config.py`.

ContextKeeper is configured through `contextkeeper.yaml`, with a small set of environment variable overrides. The first-run wizard creates this file when it is missing.

## Configuration file location

Default filename:

```text
contextkeeper.yaml
```

Source-mode behavior:

- Relative default path resolves from the current working directory.

Packaged/frozen behavior:

- ContextKeeper first looks for `contextkeeper.yaml` beside the executable.
- If that file is absent, it can fall back to the bundled PyInstaller resource.
- A user-editable file beside `ContextKeeper.exe` overrides the bundled fallback.

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

Current source behavior:

1. Built-in defaults from `Settings`.
2. Values loaded from `contextkeeper.yaml`.
3. Supported environment variable overrides.

The `--configure` command-line flag launches the configuration wizard and exits. It does not provide per-setting runtime overrides.

## Settings read API

Phase 6.5F-B6.1 adds a read-only dashboard settings snapshot API:

```text
GET /api/dashboard/settings
```

The endpoint exposes only approved runtime configuration metadata for future dashboard Settings UI work. It does not expose environment variables, file paths, secrets, passwords, API tokens, server bind details, Ollama base URLs, logging paths, model override maps, or future configuration.

Snapshot categories:

- Context.
- Compression.
- Dashboard.

Each setting includes:

- stable id;
- category;
- display name;
- description;
- effective current value;
- built-in default value;
- data type;
- minimum/maximum validation metadata where applicable;
- runtime-editable flag;
- restart-required flag.

B6.1 is read-only. It does not implement editing, persistence, runtime updates, or dashboard UI controls. Because there is no runtime mutation mechanism yet, the approved exposed settings are currently marked `runtime_editable: false` and `restart_required: true`.

Mutating methods on `/api/dashboard/settings` are rejected with `405` and are not proxied to Ollama.

Exposed settings:

| Category | Setting |
| --- | --- |
| Context | `context.enabled` |
| Context | `context.warning_threshold_percent` |
| Context | `context.compression_threshold_percent` |
| Context | `context.keep_recent_messages` |
| Compression | `compression.enabled` |
| Compression | `compression.summarizer_model` |
| Compression | `compression.max_summary_tokens` |
| Dashboard | `dashboard.refresh_interval_ms` |

## Validation rules

- `server.port` must be between `1` and `65535`.
- `ollama.base_url` must be non-empty and start with `http://` or `https://`.
- `ollama.timeout_seconds` must be greater than `0`.
- `logging.level` must be one of `OFF`, `DEBUG`, `INFO`, `WARNING`, `WARN`, `ERROR`, or `CRITICAL`.
- `metrics.refresh_interval_seconds` must be greater than `0`.
- `dashboard.refresh_interval_ms` must be greater than `0`.
- Context thresholds must be between `0` and `100`.
- `context.minimum_threshold_percent <= context.warning_threshold_percent <= context.compression_threshold_percent`.
- `context.default_context_window_tokens` and `context.keep_recent_messages` must be greater than `0`.
- `compression.max_summary_tokens` must be greater than `0`.

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

The current dashboard uses the same refresh path for Operations, Request Traffic, Connection Flow, Context Trend, Live Conversation Timeline, and Conversation Inspector updates. No separate inspector polling interval exists.

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
