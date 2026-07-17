# ContextKeeper API Compatibility

Status: Current through Phase 6.5F-B5.5.2.

ContextKeeper must behave like an Ollama-compatible API server so existing clients can point to ContextKeeper instead of Ollama without code changes.

## Compatibility goal

ContextKeeper transparently proxies Ollama-compatible API requests to a real Ollama server while observing operational metadata for diagnostics, Context Usage, dashboard visualization, and context/compression subsystems.

Default URLs:

| Component | Default URL |
| --- | --- |
| Ollama | `http://localhost:11434` |
| ContextKeeper proxy | `http://localhost:11500` |
| ContextKeeper dashboard | `http://localhost:11500/dashboard` |

## Implemented routing behavior

Source: `src/ctxkeeper/proxy/routes.py`

Implemented routes:

- `GET /api/tags`
- any method on `/api/{path:path}`
- any method on `/v1/{path:path}`

Any unknown `/api/*` or `/v1/*` route is forwarded to the configured Ollama base URL when possible.

## Common Ollama endpoints covered by passthrough

Model/server discovery:

- `GET /api/tags`
- `GET /api/version`
- `POST /api/show`
- `GET /v1/models`

Chat and generation:

- `POST /api/chat`
- `POST /api/generate`
- `POST /v1/chat/completions`
- `POST /v1/completions`

Embeddings:

- `POST /api/embed`
- `POST /api/embeddings`

Model management and operational endpoints are proxied when they use `/api/*` or `/v1/*`.

## Streaming rule

ContextKeeper preserves streaming responses for Ollama chat and generation endpoints that request streaming. It returns a streaming response to the client rather than buffering the full upstream response first.

## Request observation and modification policy

Current source behavior:

- ContextKeeper reads request bodies to inspect model information and record safe diagnostics.
- For conversational generation requests, ContextKeeper resolves an authoritative context-window capacity and updates outgoing `options.num_ctx`.
- Incoming chat messages are recorded in the in-memory conversation store for Conversation Snapshot and Context Usage calculations.
- Non-streaming `/api/chat` assistant responses are recorded when available.
- Streaming assistant response capture is deliberately deferred until a transparent stream tee can preserve chunk timing and errors.

Privacy boundary:

- Routine dashboard surfaces must not expose full prompt text, response text, request bodies, rolling-summary bodies, retrieved document contents, API keys, or headers.

## Context and compression compatibility boundary

ContextKeeper may inspect conversation messages for Context Usage estimation and context/compression decisions. The current compression subsystem supports rolling-summary condensation and confirmed compression metadata, but durable historical original-message retrieval is planned for a later phase.

Any context/compression behavior must preserve client-facing Ollama API compatibility.

## Error behavior

When ContextKeeper cannot reach Ollama or proxy a request, it returns a `502` JSON response with:

- `error`
- `detail`
- `ollama_base_url`

Failures are also recorded in request diagnostics where applicable.

## Success criteria

- Existing Ollama-compatible clients can use `http://localhost:11500`.
- Model lists populate through ContextKeeper.
- Chat and generation work through ContextKeeper.
- Streaming behavior remains compatible.
- Unknown supported Ollama endpoints pass through.
- ContextKeeper dashboard and diagnostics do not require client code changes.

## Out of scope for current Version 1 implementation

- Authentication.
- Multi-user permissions.
- Cloud model providers.
- Model routing.
- Plugin APIs.
- Historical memory retrieval after compression.
- Full OpenAI API compatibility beyond proxied `/v1/*` passthrough behavior.
