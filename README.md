# ContextKeeper

ContextKeeper is a local, Ollama-compatible middleware layer for long-running AI conversations. Clients point to ContextKeeper instead of Ollama; ContextKeeper preserves the Ollama API surface while adding diagnostics, context-window awareness, automatic compression, and a live operations dashboard.

The current implementation is an active local product foundation, not a planning stub. It is still pre-1.0, but the transparent proxy, dashboard, context engine, compression engine, automatic model context discovery, Windows executable foundation, installer foundation, Conversation Inspector, runtime Settings API, and dashboard Settings page foundation are implemented.

## Architecture summary

```text
Client
  |
  v
ContextKeeper Proxy
  |
  v
Diagnostics
  |
  v
Context Engine
  |
  v
Compression
  |
  v
Ollama
  |
  v
Dashboard Snapshot
  |
  v
Operations Visualization

Dashboard Settings Page
  |
  v
Runtime Settings API
  |
  v
In-Memory Settings
```

Runtime processing and Operations visualization are deliberately separate. The proxy path handles client requests, diagnostics, context tracking, context-window enforcement, compression, and Ollama forwarding. Operations surfaces remain read-only observers built from bounded runtime snapshots. The Settings page is a separate, explicit client of the runtime Settings API and changes the shared in-memory settings only after server validation succeeds.

## Key features

- Transparent passthrough for Ollama-compatible `/api/*` and `/v1/*` endpoints.
- Streaming preservation for supported Ollama chat and generation responses.
- Request diagnostics with endpoint, model, status, latency, client host, generation sequence, and recent request history.
- System telemetry for CPU, memory, and optional NVIDIA GPU/VRAM data through `nvidia-smi`.
- Conversation Snapshot, Context Usage estimation, warning/compression threshold detection, and compression-candidate tracking.
- Automatic Model Context Discovery from Ollama `/api/show` metadata, with configured model overrides and safe fallback capacity.
- Authoritative `options.num_ctx` enforcement for conversational generation requests.
- Compression engine support for rolling summaries, recent-message preservation, and confirmed compression metadata.
- Browser Operations dashboard with health, recommendations, Request Traffic, Connection Flow, Context Trend, instrument gauges, Active Conversation, Live Conversation Timeline, and Conversation Inspector.
- Conversation Inspector drawer with Overview metadata and deterministic Intelligence based on context/compression state.
- Dashboard Settings API for approved Context, Compression, and Dashboard settings, including read snapshots and validated in-memory runtime updates.
- Interactive Settings page inside the existing dashboard shell, with metadata-driven controls, unsaved-change tracking, atomic Save, and Discard.
- First-run configuration wizard, PyInstaller executable foundation, Windows service host foundation, Inno Setup installer foundation, and release build script.

## Current implementation status

The current working-tree implementation includes Phase 6.5F-B6.3; Product Owner review is pending:

- Transparent proxy, diagnostics, context monitoring, compression, dashboard modernization, live request visualization, animated Connection Flow, Live Conversation Timeline, and Conversation Inspector Overview & Intelligence are implemented.
- Phase 6.5F-B5.6 synchronized documentation through the B5.5.2 implementation.
- Phase 6.5F-B6.1 added the backend Settings Snapshot and read API foundation.
- Phase 6.5F-B6.2 added a validated `PATCH /api/dashboard/settings` update API for temporary in-memory runtime settings changes.
- Phase 6.5F-B6.3 adds a dedicated Settings page that loads API metadata dynamically, keeps confirmed and draft state separate, and provides changed-fields-only Save and local Discard actions.

Still planned:

- Configuration-file persistence for dashboard Settings changes.
- Broader dashboard customization and preferences.
- Release polish and final UX review.
- Durable historical memory retrieval after compression.
- Validation Framework and AutoQA release certification.
- Public GitHub release preparation.

## Quick start

Install in editable source mode:

```powershell
python -m pip install -e .
```

Run ContextKeeper:

```powershell
python -m ctxkeeper.main
```

On first launch, ContextKeeper creates `contextkeeper.yaml` through an interactive configuration wizard if the file does not exist. To rerun the wizard:

```powershell
python -m ctxkeeper.main --configure
```

Default URLs:

| Surface | URL |
| --- | --- |
| Dashboard | `http://localhost:11500/dashboard` |
| Settings API | `http://localhost:11500/api/dashboard/settings` |
| ContextKeeper proxy | `http://localhost:11500` |
| Upstream Ollama | `http://localhost:11434` |

Test Ollama passthrough:

```powershell
Invoke-RestMethod http://localhost:11500/api/tags
```

Point Ollama-compatible clients such as AnythingLLM, Open WebUI, IDE extensions, or scripts to `http://localhost:11500`.

## Configuration

Runtime configuration is loaded from `contextkeeper.yaml`, with a small set of environment variable overrides:

- `CONTEXTKEEPER_HOST`
- `CONTEXTKEEPER_PORT`
- `CONTEXTKEEPER_OLLAMA_URL`
- `CONTEXTKEEPER_LOG_LEVEL`

Important defaults:

- Proxy: `0.0.0.0:11500`
- Ollama: `http://localhost:11434`
- Dashboard refresh: `1000 ms`
- Default context window: `32768` tokens
- Warning threshold: `75%`
- Compression threshold: `85%`
- Recent messages retained after compression: `8`
- Compression summarizer model: `gpt-oss:20b`

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the complete source-verified configuration reference.

The dashboard now includes a Settings page that loads categories, values, constraints, types, and runtime editability from `GET /api/dashboard/settings`. The browser keeps the last confirmed server snapshot separate from the editable draft. Save sends one `PATCH /api/dashboard/settings` request containing only changed runtime-editable fields, while Discard restores the latest confirmed values without a request. Validation and server failures preserve the draft so it can be corrected or retried.

Runtime updates are validated atomically, immediately visible through the read API, and in-memory only. They reset when ContextKeeper restarts and do not modify `contextkeeper.yaml`:

```powershell
$body = @{ context = @{ warning_threshold_percent = 70 } } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Patch -Uri http://localhost:11500/api/dashboard/settings -ContentType "application/json" -Body $body
```

## Testing

Run the automated test suite:

```powershell
python -m pytest -q
```

Focused dashboard coverage lives primarily in:

- `tests/test_app.py`
- `tests/test_dashboard_instrument_panel.py`
- `tests/test_dashboard_inspector.py`
- `tests/test_dashboard_settings.py`
- `tests/test_dashboard_settings_ui.py`

See [docs/TEST_PLAN.md](docs/TEST_PLAN.md) for manual and automated validation coverage, including the Settings page, Conversation Timeline, Conversation Inspector, Request Traffic, Connection Flow, responsive layouts, reduced motion, Windows packaging, and regression checks.

## Building a Windows executable

The standalone executable build uses PyInstaller:

```powershell
python -m pip install -e ".[build]"
pyinstaller contextkeeper.spec
```

The executable is written to:

```text
dist/ContextKeeper.exe
```

`contextkeeper.yaml` is bundled as a fallback resource. For packaged runs, place an editable `contextkeeper.yaml` beside `ContextKeeper.exe` to override the bundled default. Source runs load `contextkeeper.yaml` from the current working directory.

## Building a Windows installer

The installer foundation uses Inno Setup and expects the PyInstaller executable to exist first:

```powershell
.\scripts\build_release.ps1
```

The release script runs preflight checks, builds `dist/ContextKeeper.exe`, builds `dist/installer/ContextKeeperSetup.exe`, and copies user-facing release files into `dist/`. Service installation hooks are placeholders and remain future release work.

## Documentation index

- [Documentation index](docs/README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Configuration](docs/CONFIGURATION.md)
- [API Compatibility](docs/API_COMPATIBILITY.md)
- [Roadmap](docs/ROADMAP.md)
- [Project History](docs/PROJECT_HISTORY.md)
- [Test Plan](docs/TEST_PLAN.md)
- [Conversation Inspector](docs/CONVERSATION_INSPECTOR.md)
- [Dashboard Layout](docs/DASHBOARD_LAYOUT.md)
- [Dashboard Visualization Audit](docs/DASHBOARD_VISUALIZATION_AUDIT.md)
- [Future Ideas](docs/FUTURE_IDEAS.md)

## Roadmap summary

The Version 1 direction is to ship a production-quality local tool that preserves Ollama compatibility while solving context-window pressure through context tracking, compression, and later historical retrieval. The current roadmap sequence is:

1. Complete Phase 6.5F dashboard/documentation/release-polish work.
2. Implement historical memory retrieval and detail preservation.
3. Implement Validation Framework and AutoQA certification.
4. Prepare the public GitHub release.
5. Ship Version 1.0.

Long-term v2+ ideas are tracked in [docs/FUTURE_IDEAS.md](docs/FUTURE_IDEAS.md). They are not current implementation commitments.

## Current limitations

- Conversation history is process-local and not yet a durable historical archive.
- Compression condenses active context but does not yet provide durable original-message retrieval.
- Conversation Inspector does not yet expose transcripts, message expansion, search, export, context-composition views, or compression-event details.
- Dashboard telemetry is live and bounded; long-duration trends across restarts are not implemented.
- Runtime settings updates are in-memory only, reset when ContextKeeper restarts, and do not modify `contextkeeper.yaml`.
- Authentication, multi-user permissions, cloud model providers, routing, plugins, and multi-server orchestration are future ideas, not current Version 1 behavior.
- Windows service installation hooks are still placeholders.

## Package naming note

The product is called **ContextKeeper**, but the Python package is named `ctxkeeper` to avoid conflict with an unrelated PyPI package named `contextkeeper`.
