
# ContextKeeper Coding Standards

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

## Recommended Project Layout

```text
ContextKeeper/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── contextkeeper.yaml
│
├── src/
│   └── contextkeeper/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── logging_config.py
│       │
│       ├── proxy/
│       │   ├── server.py
│       │   ├── routes.py
│       │   └── ollama_client.py
│       │
│       ├── context/
│       │   ├── manager.py
│       │   ├── tokenizer.py
│       │   └── compressor.py
│       │
│       ├── diagnostics/
│       │   ├── metrics.py
│       │   └── request_log.py
│       │
│       ├── dashboard/
│       │   ├── app.py
│       │   └── widgets.py
│       │
│       ├── routing/
│       │   └── router.py
│       │
│       ├── memory/
│       │   └── manager.py
│       │
│       └── utils/
│           └── time.py
│
├── tests/
├── docs/
└── examples/
```

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

Dashboard later:
- `PySide6` or web dashboard, decision pending.

## Testing

Use `pytest`.

Tests should cover:
- configuration loading
- proxy passthrough
- token estimation
- compression logic
- streaming behavior
