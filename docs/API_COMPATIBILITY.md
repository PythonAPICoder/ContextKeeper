
# ContextKeeper API Compatibility Specification

## Purpose
ContextKeeper must behave like an Ollama-compatible API server so existing clients can point to ContextKeeper instead of Ollama without code changes.

## v1 Compatibility Goal
ContextKeeper v1.0 will transparently proxy Ollama API requests to a real Ollama server while observing requests for logging, diagnostics, and future context management.

## Default Ports

| Component | Default URL |
|---|---|
| Ollama | `http://localhost:11434` |
| ContextKeeper | `http://localhost:11500` |

## Required Ollama Endpoints for v1

### Model / Server Discovery
- `GET /api/tags`
- `GET /api/version`
- `POST /api/show`
- `GET /v1/models`

### Chat and Generation
- `POST /api/chat`
- `POST /api/generate`

### Embeddings
- `POST /api/embed`
- `POST /api/embeddings`

### Model Management Passthrough
These should be proxied but not modified:
- `POST /api/pull`
- `POST /api/push`
- `DELETE /api/delete`
- `POST /api/create`
- `POST /api/copy`
- `GET /api/ps`

## Passthrough Rule
Any unknown `/api/*` or `/v1/*` endpoint should be forwarded to Ollama unchanged when possible.

## Streaming Rule
ContextKeeper must preserve streaming responses. If Ollama streams newline-delimited JSON, ContextKeeper must stream the same format back to the client.

## Request Modification Policy

### Phase 1
No prompt modification. ContextKeeper only proxies and logs.

### Phase 3+
ContextKeeper may inspect requests for context estimation.

### Phase 4+
ContextKeeper may modify chat history only when compression is enabled and context threshold is exceeded.

## Success Criteria
- AnythingLLM can select models through ContextKeeper.
- Chat works through ContextKeeper.
- Streaming works through ContextKeeper.
- Unknown supported Ollama endpoints pass through.
- Client behavior is unchanged except for using a different base URL.

## Out of Scope for v1
- OpenAI API compatibility beyond basic `/v1/models` passthrough.
- Authentication.
- Multi-user permissions.
- Cloud model providers.
