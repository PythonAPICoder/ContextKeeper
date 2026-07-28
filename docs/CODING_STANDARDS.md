
# ContextKeeper Coding Standards

Status: Phase 6.5F-B6 Settings implementation is complete. Updated for the current Phase 6.5F-B7.1 dashboard release-readiness audit; Product Owner manual visual and accessibility QA remains pending.

See the [Dashboard Release Readiness Audit](DASHBOARD_RELEASE_READINESS_AUDIT.md) for the B7.1 evidence and manual QA boundary.

## Project Philosophy
ContextKeeper should be built like a production application, not a growing script.

## Core Rules

1. No giant single-file scripts.
2. Every major feature belongs in its own module.
3. Use type hints.
4. Use structured logging.
5. Fail clearly and recover gracefully where possible.
6. Keep proxy behavior transparent by default.
7. Avoid modifying prompts unless a feature explicitly requires it.
8. Preserve streaming behavior.

## Current Project Layout

```text
ContextKeeper/
|-- README.md
|-- pyproject.toml
|-- requirements.txt
|-- contextkeeper.yaml
|-- contextkeeper.spec
|-- src/
|   `-- ctxkeeper/
|       |-- __init__.py
|       |-- app.py
|       |-- branding.py
|       |-- config.py
|       |-- executable.py
|       |-- logging_config.py
|       |-- main.py
|       |-- model_context.py
|       |-- resources.py
|       |-- context/
|       |   |-- compression_manager.py
|       |   |-- compression_plan.py
|       |   |-- context_meter.py
|       |   |-- context_monitor.py
|       |   |-- conversation_store.py
|       |   `-- summarizer.py
|       |-- dashboard/
|       |   |-- config_persistence.py
|       |   |-- connection_test.py
|       |   |-- insights.py
|       |   |-- inspector.py
|       |   |-- intelligence.py
|       |   |-- recommendations.py
|       |   |-- routes.py
|       |   |-- settings_snapshot.py
|       |   |-- snapshots.py
|       |   |-- template.py
|       |   |-- timeline.py
|       |   `-- trends.py
|       |-- diagnostics/
|       |   |-- activity.py
|       |   `-- metrics.py
|       |-- proxy/
|       |   |-- model_extraction.py
|       |   |-- ollama_client.py
|       |   `-- routes.py
|       |-- service/
|       |   |-- runner.py
|       |   `-- windows_service.py
|       `-- wizard/
|           |-- configuration.py
|           `-- ui.py
|-- tests/
|-- docs/
|-- installer/
`-- scripts/
```

The import package is `ctxkeeper`, not `contextkeeper`. Older planning trees that name `proxy/server.py`, `context/manager.py`, `routing/`, `memory/`, or `utils/` do not describe the implemented source tree. Module responsibilities and data-flow boundaries are maintained in [Architecture](ARCHITECTURE.md#module-layout).

## Naming

- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Modules: `snake_case.py`

## Logging

Use Python `logging`, not `print`, except for CLI startup messages.

Log:
- request path
- method
- model
- status code
- latency
- errors
- compression events

Do not log:
- full user prompts by default
- secrets
- API keys
- private documents

## Error Handling

Errors should be:
- visible to the user,
- logged with stack traces,
- returned to the client in a compatible format when possible.

## Dependencies

Prefer stable, well-supported packages.

Initial likely stack:
- `fastapi`
- `uvicorn`
- `httpx`
- `pydantic`
- `pyyaml`
- `rich`

Dashboard:
- Browser-rendered FastAPI dashboard using HTML, CSS, and vanilla JavaScript. Do not add a frontend framework without an approved phase.

## Dashboard and Settings Safety

- Escape every configuration value interpolated into server-rendered HTML. Render dynamic API/configuration strings with DOM `textContent` or the existing escaping helper before using `innerHTML`.
- Preserve the distinction between a real numeric zero and unavailable/null telemetry.
- Give interactive controls accessible names, visible focus, associated validation errors, meaningful busy/disabled state, and non-color status text.
- Remove closed drawers and other hidden interactive regions from keyboard navigation. Preserve Escape close and return focus where implemented.
- Respect `prefers-reduced-motion` and constrain long endpoint, model, path, identifier, error, and status text at supported layouts.
- Keep Settings active runtime, browser draft, persisted YAML, built-in default, and restart-required values distinct. Derive browser controls and actions from server metadata rather than duplicating the ten-field catalog in JavaScript.
- Test Connection must use draft values through an isolated client and must not mutate the active Ollama client, runtime state, persisted configuration, health state, model discovery, or retry behavior.
- Do not add listener-host/proxy-port editing, retry-count/retry-delay/backoff controls, provenance UI, or restart behavior without an approved phase.

## Testing

Use `pytest`.

Tests should cover:
- configuration loading
- proxy passthrough
- token estimation
- compression logic
- streaming behavior
