# ContextKeeper

ContextKeeper is a local, Ollama-compatible middleware layer for long-running AI conversations. Clients point to ContextKeeper instead of Ollama; ContextKeeper preserves the Ollama API surface while adding diagnostics, context-window awareness, automatic compression, and a live operations dashboard.

The current implementation is an active local product foundation, not a planning stub. It is still pre-1.0, but the transparent proxy, dashboard, context engine, compression engine, automatic model context discovery, Windows executable foundation, installer foundation, Conversation Inspector, runtime Settings API, explicit configuration persistence, dashboard Settings page, and managed settings reset controls are implemented.

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
Settings Management API
  |-- GET snapshot --> Runtime + persisted metadata
  |-- PATCH --------> In-memory runtime settings
  `-- PUT /config --> Active contextkeeper.yaml
```

Runtime processing and Operations visualization are deliberately separate. The proxy path handles client requests, diagnostics, context tracking, context-window enforcement, compression, and Ollama forwarding. Operations surfaces remain read-only observers built from bounded runtime snapshots. The Settings page is an explicit client of the dashboard management API: runtime Save and reset actions change shared in-memory settings through PATCH, while Save to configuration writes approved values through a separate PUT without mutating runtime state or restarting ContextKeeper.

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
- Dashboard Settings API for approved Context, Compression, and Dashboard settings, including runtime-versus-persisted snapshots, authoritative defaults and reset eligibility, validated atomic in-memory updates, and explicit atomic YAML persistence.
- Interactive Settings page inside the existing dashboard shell, with metadata-driven controls, typed draft state, individual/category/global managed-default resets, separate runtime and configuration Save actions, persistence-difference guidance, and Discard runtime changes.
- First-run configuration wizard, PyInstaller executable foundation, Windows service host foundation, Inno Setup installer foundation, and release build script.

## Current implementation status

The current working-tree implementation includes Phase 6.5F-B6.5; Product Owner and architect review are pending:

- Transparent proxy, diagnostics, context monitoring, compression, dashboard modernization, live request visualization, animated Connection Flow, Live Conversation Timeline, and Conversation Inspector Overview & Intelligence are implemented.
- Phase 6.5F-B5.6 synchronized documentation through the B5.5.2 implementation.
- Phase 6.5F-B6.1 added the backend Settings Snapshot and read API foundation.
- Phase 6.5F-B6.2 added a validated `PATCH /api/dashboard/settings` update API for temporary in-memory runtime settings changes.
- Phase 6.5F-B6.3 added a dedicated Settings page that loads API metadata dynamically, keeps confirmed and draft state separate, and provides changed-fields-only runtime Save and local Discard actions.
- Phase 6.5F-B6.4 adds schema-v2 persisted-state metadata, `PUT /api/dashboard/settings/config`, atomic configuration-file writes, and an explicit Save to configuration action that remains separate from runtime Save.
- Phase 6.5F-B6.5: Settings Reset and Recovery Controls adds metadata-authorized individual, category, and global managed-settings resets that stage built-in defaults through the existing atomic runtime PATCH path, plus Discard recovery to persisted values.

Still planned:

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

The dashboard Settings page loads categories, runtime values, persisted values, defaults, reset eligibility, constraints, types, runtime editability, persistence eligibility, and restart guidance from `GET /api/dashboard/settings`. Schema version 2 distinguishes `value` from `persisted_value`, reports `differs_from_persisted`, and marks reset-supported settings with `reset_eligible`. The browser keeps the last confirmed server snapshot separate from the editable draft.

Save runtime changes sends one `PATCH /api/dashboard/settings` containing only changed runtime-editable fields. Runtime updates are validated atomically, immediately visible through GET, and in-memory only. PATCH never writes YAML, and those changes reset when ContextKeeper restarts:

```powershell
$body = @{ context = @{ warning_threshold_percent = 70 } } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Patch -Uri http://localhost:11500/api/dashboard/settings -ContentType "application/json" -Body $body
```

Reset controls use only the server-provided `default_value` for settings marked `reset_eligible`; defaults are not duplicated in dashboard JavaScript or HTML. An individual reset immediately submits only that setting through PATCH. Category reset and **Reset managed settings to defaults** require confirmation, select all and only reset-eligible settings in scope, including eligible values already at default, and submit one atomic PATCH. A category or global action is disabled when every eligible value in its scope is already at default. A successful reset stages runtime defaults but does not write `contextkeeper.yaml`. When staged defaults differ from persisted values, Save to configuration is required for restart persistence; when persisted values already match, the UI reports that no configuration save is needed.

Discard runtime changes remains local when it only needs to abandon browser draft edits. When confirmed runtime values differ from persisted values, Discard issues one atomic PATCH that restores every runtime-editable differing value from `persisted_value`. Discard never writes YAML. A failed restore applies no partial recovery, leaves the current runtime values in place, and reports the error.

Save to configuration is a separate, explicit action. It sends only eligible draft values to `PUT /api/dashboard/settings/config`; it does not change the current runtime or restart ContextKeeper:

```powershell
$body = @{
    context = @{ warning_threshold_percent = 75 }
    compression = @{ enabled = $true }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Method Put -Uri http://localhost:11500/api/dashboard/settings/config -ContentType "application/json" -Body $body
```

A successful PUT returns `status: "saved"`, the sorted `persisted_setting_ids`, whether `configuration_created`, and a refreshed schema-v2 snapshot in `settings`. ContextKeeper re-reads the active file, validates the complete candidate, writes and verifies a UTF-8 temporary file beside the destination, checks that the source fingerprint has not changed, and atomically replaces the destination. Unrelated categories and model-specific entries are retained. PyYAML does not preserve comments or exact formatting, so a successful write may normalize the complete YAML document.

Reset applies only to dashboard-managed settings. It does not delete or recreate the configuration file, clear logs, metrics, conversations, summaries, models, or other application data, or restart ContextKeeper. Saving changes the YAML tier only and cannot override a higher-priority configuration source.

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
- `tests/test_config_persistence.py`

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
- Runtime PATCH updates, including resets to built-in defaults and Discard recovery, remain in-memory only. Persistence requires the separate explicit PUT action; no reset, discard, or save action restarts ContextKeeper automatically.
- Configuration persistence serializes writes only within one ContextKeeper process. It does not provide a distributed or multi-process file lock, configuration history, or automatic rollback UI.
- PyYAML persistence preserves configuration data but not YAML comments or exact source formatting.
- Settings reset is limited to metadata-approved dashboard-managed fields. It is not a factory reset, does not clear application data, and does not provide restart, self-diagnostic, repair, backup-history, or rollback controls.
- Authentication, multi-user permissions, cloud model providers, routing, plugins, and multi-server orchestration are future ideas, not current Version 1 behavior.
- Windows service installation hooks are still placeholders.

## Package naming note

The product is called **ContextKeeper**, but the Python package is named `ctxkeeper` to avoid conflict with an unrelated PyPI package named `contextkeeper`.
