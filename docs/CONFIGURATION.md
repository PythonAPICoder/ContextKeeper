
# ContextKeeper Configuration Specification

## Purpose
ContextKeeper should be configurable without editing source code.

Primary configuration file:

```yaml
contextkeeper.yaml
```

## Default Configuration

```yaml
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

dashboard:
  enabled: true
  refresh_interval_ms: 1000
```

## Environment Variable Overrides

| Environment Variable | Purpose |
|---|---|
| `CONTEXTKEEPER_HOST` | Proxy bind host |
| `CONTEXTKEEPER_PORT` | Proxy bind port |
| `CONTEXTKEEPER_OLLAMA_URL` | Real Ollama base URL |
| `CONTEXTKEEPER_LOG_LEVEL` | Logging level |

## Model Context Sizes

ContextKeeper automatically discovers model context-window sizes from
Ollama-compatible model metadata when available. The proxy uses `/api/show`
metadata and caches the discovered size per model name so dashboard and context
threshold calculations do not rely on the global fallback when a model advertises
a larger window.

You can still define model-specific context windows. These overrides are useful
when you intentionally want to cap a model below its advertised capability for
RAM, VRAM, latency, or stability reasons, and they take priority over automatic
discovery:

```yaml
models:
  gpt-oss:20b:
    context_window_tokens: 32768
  qwen2.5-vl:32b:
    context_window_tokens: 32768
  llama3.2-vision:
    context_window_tokens: 128000
```

Client request options are preserved for diagnostics, but they are not
authoritative for ContextKeeper's effective context capacity. For conversational
generation requests, ContextKeeper overwrites the outgoing request body with the
resolved authoritative value:

```json
{
  "model": "qwen3.6:latest",
  "messages": [],
  "options": {
    "num_ctx": 262144
  }
}
```

Context-window resolution priority:

1. Model-specific `models.<model>.context_window_tokens`
2. Auto-discovered Ollama model metadata from `/api/show`
3. `context.default_context_window_tokens`

The dashboard uses non-technical source labels for the same priority chain:

- `Pre-defined` means a model-specific `contextkeeper.yaml` value was used.
- `Discovered` means Ollama model metadata supplied the context window.
- `Default` means ContextKeeper used the 32,768-token fallback.

The global `context.default_context_window_tokens` remains the safe fallback
when a model-specific override and usable model metadata are unavailable. The
built-in fallback is 32,768 tokens.

Examples:

- If `models.qwen3.6:latest.context_window_tokens` is `65536`, ContextKeeper
  uses and forwards `options.num_ctx = 65536` even if `/api/show` reports
  `262144`.
- If no model override exists and `/api/show` reports
  `qwen35moe.context_length = 262144`, ContextKeeper uses and forwards
  `options.num_ctx = 262144`.
- If no override or valid metadata exists, ContextKeeper uses and forwards
  `options.num_ctx = 32768`.

## Configuration Priority

1. Command-line arguments
2. Environment variables
3. `contextkeeper.yaml`
4. Built-in defaults

## Success Criteria
- User can change proxy port without editing code.
- User can change real Ollama server URL without editing code.
- Thresholds can be changed to support testing.
- Configuration errors are reported clearly.
