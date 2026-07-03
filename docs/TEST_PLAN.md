
# ContextKeeper Test Plan

## Purpose
This document defines how each ContextKeeper phase is validated.

## Phase 1 — Transparent Proxy

### Goal
ContextKeeper must behave like Ollama to existing clients.

### Tests

#### Test 1: Model Discovery
1. Start Ollama.
2. Start ContextKeeper.
3. Run:
   ```powershell
   Invoke-RestMethod http://localhost:11500/api/tags
   ```
4. Confirm model list is returned.

#### Test 2: AnythingLLM Connection
1. Set AnythingLLM Ollama URL to `http://localhost:11500`.
2. Open model dropdown.
3. Confirm models populate.

#### Test 3: Basic Chat
1. Select `gpt-oss:20b`.
2. Send: `Hello`.
3. Confirm model responds.

#### Test 4: Streaming
1. Send a longer prompt.
2. Confirm response streams normally.
3. Confirm no buffering breaks the client.

### Success Criteria
- Models populate.
- Chat works.
- Streaming works.
- Logs show request endpoint, model, status, and latency.

## Phase 2 — Diagnostics

### Tests
- Verify request count increments.
- Verify latency is recorded.
- Verify endpoint path is logged.
- Verify model name is captured.
- Verify errors are logged with useful messages.

## Phase 3 — Context Meter

### Tests
- Send short prompt.
- Send long prompt.
- Confirm estimated token count increases.
- Confirm context percent is calculated.
- Confirm warning threshold is detected.

## Phase 4 — Compression

### Tests
- Set compression threshold low, such as 10%.
- Send enough messages to exceed threshold.
- Confirm summary is generated.
- Confirm recent messages remain.
- Confirm old messages are replaced by rolling summary.
- Confirm conversation still makes sense.

## Phase 5 — Dashboard

### Tests
- Confirm dashboard starts.
- Confirm Ollama status is visible.
- Confirm ContextKeeper status is visible.
- Confirm requests appear live.
- Confirm context percent updates.
- Confirm compression count updates.

## Phase 6 — Windows EXE / Service

### Tests
- Build executable.
- Run executable on client PC.
- Run executable on AI server.
- Install as Windows service.
- Reboot and confirm service starts automatically.

## Regression Tests
Every release must confirm:
- `/api/tags` works.
- `/api/chat` works.
- `/api/generate` works.
- Streaming works.
- AnythingLLM connects.
- Logs are created.
