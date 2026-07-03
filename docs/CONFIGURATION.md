
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
  enabled: false
  default_context_window_tokens: 16384
  warning_threshold_percent: 75
  compression_threshold_percent: 85
  minimum_threshold_percent: 10
  keep_recent_messages: 8

compression:
  enabled: false
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

ContextKeeper should allow model-specific context window definitions:

```yaml
models:
  gpt-oss:20b:
    context_window_tokens: 32768
  qwen2.5-vl:32b:
    context_window_tokens: 32768
  llama3.2-vision:
    context_window_tokens: 128000
```

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
