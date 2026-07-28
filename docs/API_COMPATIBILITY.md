# ContextKeeper API Compatibility

Status: Phase 6.5F-B6 Settings implementation is complete. Updated for the current Phase 6.5F-B7.1 dashboard release-readiness audit; Product Owner manual visual and accessibility QA remains pending.

ContextKeeper must behave like an Ollama-compatible API server so existing clients can point to ContextKeeper instead of Ollama without code changes.

Phase 6.5F-B7.1 preserves the API and streaming contracts in this document. Its implementation changes are narrow dashboard hardening only. See the [Dashboard Release Readiness Audit](DASHBOARD_RELEASE_READINESS_AUDIT.md) for the evidence and remaining manual QA.

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

The Test Connection payload always represents the current browser draft. A successful candidate response does not mean the endpoint is active or persisted, does not replace active proxy health, and is never a prerequisite for either Save action. The active runtime value, disk-derived persisted value, built-in default, and browser draft remain separate states.

The management API exposes no Ollama credentials, request bodies, prompt/response text, configuration paths, model override maps, or full configuration contents. Candidate-test failures expose only a normalized endpoint when safe, latency when attempted, a bounded failure category, and a user-readable message. Persistence and candidate-test errors use safe local-management details and do not use the upstream `502` proxy error contract.

The completed Phase 6.5F-B6 Connection Configuration work extends only the local management client, approved settings metadata, configuration validation/persistence allowlist, and isolated candidate probe. Testing or saving a candidate never changes the active endpoint/client, health/version metrics, diagnostics, model discovery, forwarded method, request body, response, or streaming behavior of Ollama-compatible `/api/*` and `/v1/*` clients. A manual restart is required to activate saved Connection values. If `CONTEXTKEEPER_OLLAMA_URL` is set, that currently implemented higher-priority environment source can continue to determine the active URL after restart; no current command provides a per-setting command-line override.

Listener-host and ContextKeeper proxy-port editing, retry-count/retry-delay/backoff controls, configuration-source provenance UI, environment-variable editing, and command-line editing are intentionally absent from this management API. Existing model-discovery retry behavior remains internal and is not reused by Test Connection.

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

## Planned later in Version 1

These approved Version 1 phases are planned but not implemented by the current API:

- Phase 6.5G durable historical-memory preservation, search, retrieval, and detail recovery after compression.
- Phase 6.6 Validation Framework, AutoQA, stress/soak verification, reports, and release certification. It is expected to exercise the public Ollama-compatible API where practical, but no Validation API shape is promised by this document.

Current compression and dashboard behavior must not be described as if either later phase already exists.

## Intentionally deferred or post-Version 1

- Authentication, credentials, accounts, multi-user permissions, ownership, and workspace isolation.
- Multiple AI servers or profiles, cloud model providers, failover, load balancing, and background Connection monitoring.
- Runtime backend switching, active-client replacement, automatic or manual restart controls, Windows service controls, self-diagnostics, and automated recovery.
- Listener-host editing, ContextKeeper proxy-port editing, retry-count/retry-delay/backoff controls, configuration-source provenance UI, environment-variable editing, and command-line editing.
- TLS trust or certificate management, credential storage, and secrets-management UI.
- Model routing, plugin APIs, and full OpenAI API compatibility beyond transparent `/v1/*` passthrough behavior.
