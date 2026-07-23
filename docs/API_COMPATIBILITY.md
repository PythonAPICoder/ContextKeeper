# ContextKeeper API Compatibility

Status: Current through the Phase 6.5F-B6.6 working-tree implementation; Product Owner and architect review are pending.

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

## Dashboard management API boundary

The dashboard management routes share the `/api/` prefix but are owned by ContextKeeper and are never forwarded to Ollama:

| Method and path | Responsibility |
| --- | --- |
| `GET /api/dashboard/settings` | Read the sanitized schema-v2 runtime, persisted, default, and reset-eligibility settings snapshot. |
| `PATCH /api/dashboard/settings` | Validate and atomically update approved in-memory runtime settings, including reset and Discard recovery payloads. |
| `PUT /api/dashboard/settings/config` | Validate and atomically persist explicitly supplied approved settings only. |
| `POST /api/dashboard/settings/connection/test` | Validate and test draft Ollama Connection values with one isolated bounded version probe. |

PATCH, PUT, and candidate testing are intentionally separate. Runtime-editable resets and persisted-value Discard recovery reuse PATCH; Connection-only reset/discard remains local to the browser, while a mixed global reset PATCHes only its runtime-editable subset. PATCH does not write YAML. PUT can persist `ollama.base_url` and `ollama.timeout_seconds` but does not mutate the running `Settings` instance, replace the active Ollama client, invoke PATCH, restart ContextKeeper, or alter an in-flight proxied request.

The Connection test accepts `{ "base_url": ..., "timeout_seconds": ... }`, validates the values, and performs one isolated `GET` to the normalized base-path-preserving `/api/version` URL. The temporary client uses `trust_env=False`, a timeout capped at `min(timeout_seconds, 10)`, no retries, and normal TLS verification. HTTP `200` carries every validated probe outcome, connected or failed; request validation returns `422` with field detail. GET, PUT, PATCH, DELETE, HEAD, and OPTIONS on the test resource return explicit `405` with `Allow: POST`.

The management API exposes no Ollama credentials, request bodies, prompt/response text, configuration paths, model override maps, or full configuration contents. Candidate-test failures expose only a normalized endpoint when safe, latency when attempted, a bounded failure category, and a user-readable message. Persistence and candidate-test errors use safe local-management details and do not use the upstream `502` proxy error contract.

Phase 6.5F-B6.6: Connection Configuration extends only the local management client, approved settings metadata, configuration validation/persistence allowlist, and isolated candidate probe. Testing or saving a candidate never changes the active endpoint/client, health/version metrics, diagnostics, model discovery, forwarded method, request body, response, or streaming behavior of Ollama-compatible `/api/*` and `/v1/*` clients. A manual restart is required to activate saved Connection values.

## Error behavior

When ContextKeeper cannot reach Ollama or proxy a request, it returns a `502` JSON response with:

- `error`
- `detail`
- `ollama_base_url`

Failures are also recorded in request diagnostics where applicable.

Candidate Test Connection failures are deliberately different: identifiable DNS, refusal, timeout, TLS/certificate, HTTP, malformed/non-Ollama, missing/invalid-version, and other network failures return a safe structured management result without being recorded as a proxied client request. They never overwrite the active dashboard Ollama health/version state.

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
- Runtime backend switching, active-client replacement, automatic restart, authentication/credentials, multiple AI servers, failover/load balancing, cloud providers, TLS trust management, retry settings, or background Connection monitoring.
