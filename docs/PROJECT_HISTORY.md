# ContextKeeper Project History

## Table of Contents

- [Purpose](#purpose)
- [Project Vision](#project-vision)
- [Role and Workflow](#role-and-workflow)
- [Naming Convention](#naming-convention)
- [Major Milestones](#major-milestones)
- [Phase History](#phase-history)
- [Current Project State](#current-project-state)
- [Planned Next Steps](#planned-next-steps)
- [Lessons Learned](#lessons-learned)
- [Longer-Term Direction](#longer-term-direction)
- [Maintenance Rules](#maintenance-rules)
- [Status Legend](#status-legend)

## Purpose

This file tracks ContextKeeper phases, milestones, implementation history, and planned next steps.

It complements the roadmap:

- The roadmap describes intended direction.
- This history records what was actually completed and how the work evolved.

Use this document as a maintenance reference for future ChatGPT and Codex work. It should stay grounded in repository evidence: Git history, current source, tests, and durable project documentation.

## Project Vision

ContextKeeper is a transparent Ollama-compatible middleware layer between AI clients and Ollama. It preserves client compatibility while adding context monitoring and management, diagnostics, automatic compression, and a live local dashboard.

The product direction is a local Windows-ready operations tool: transparent proxy, context engine, compression, dashboard intelligence, executable and installer packaging, and future capabilities such as model routing, workspace memory, plugins, multi-server support, orchestration, and agent integration.

## Role and Workflow

- User: Product Owner and hands-on tester.
- ChatGPT: Architect, designer, reviewer, and prompt author.
- Codex: Implementation engineer.
- Work proceeds on a Git feature branch per meaningful phase or workstream.
- Tests and manual validation are expected before merge.
- Risky UI work is split into small incremental implementation passes, especially where layout stability is involved.

## Naming Convention

The later phase labels evolved organically during development. They are planning and coordination labels, not a formal semantic-versioning system, and not every historical phase follows this exact pattern.

Example: `Phase 6.5F-B4.2`

- `6` — major production phase.
- `.5` — intermediate modernization program added between major roadmap phases.
- `F` — UI/design workstream identifier.
- `B` — dashboard redesign feature group.
- `4` — primary phase within that group.
- `.2` — incremental implementation pass.

## Major Milestones

| Milestone | Status | Evidence or current state |
| --- | --- | --- |
| Planning and architecture | Completed | Planning, architecture, compatibility, configuration, coding standards, and test-plan docs exist. |
| Transparent Ollama proxy | Completed | `phase-1-transparent-proxy`; `/api/*` and `/v1/*` passthrough implemented. |
| Diagnostics | Completed | Request metrics, latency, token estimation, and conversation identity evidence in source/tests. |
| Context engine | Completed | Conversation store, context meter, context monitor, and compression candidates implemented. |
| Automatic compression | Completed | Summarizer, compression manager, rolling summaries, and automatic compression implemented. |
| Live dashboard and intelligence | Completed | Dashboard routes, live metrics, health, insights, recommendations, trends, and timeline implemented. |
| Windows executable/service foundation | Completed | PyInstaller spec, executable entry point, service runner, and service placeholder present. |
| Setup wizard and installer | Completed | First-run wizard, Inno Setup foundation, and release build script present. |
| Dashboard modernization B4 workstream | Completed | Phase 6.5F-B4.8 automatic model context discovery is implemented and documented. |
| Live data visualization and rich widgets | Completed through B5.5.2 | Request Traffic, Connection Flow, Live Conversation Timeline, layout refinement, Connection Flow visibility polish, Conversation Inspector foundation, and Conversation Inspector Overview & Intelligence are implemented; B5.6 synchronized documentation to that state. |
| Documentation audit and synchronization | Completed | Phase 6.5F-B5.6 audited maintained Markdown documents and aligned documentation with the implementation through B5.5.2. |
| Dashboard customization and user preferences | Active | Phase 6.5F-B6 has delivered the Settings Snapshot/read API, validated in-memory update API, Settings panel UI foundation, B6.4 explicit configuration persistence, B6.5 managed settings reset/recovery controls, and B6.6 restart-required Ollama Connection configuration with isolated candidate testing; B6.6 Product Owner and architect review are pending. |
| Release polish and final UX review | Planned | Phase 6.5F-B7 planned before historical memory retrieval and validation certification. |
| Historical memory retrieval and detail preservation | Planned | Dedicated Phase 6.5G approved before Phase 6.6; no implementation exists yet. |
| Validation framework and release certification | Planned | Dedicated Phase 6.6 approved after Phase 6.5G and before Phase 7; no implementation exists yet. |
| GitHub release preparation | Planned | Phase 7 planned after Phase 6.6 certification. |
| Version 1.0 release | Planned | Planned release target after Phase 7, not yet completed. |
| Version 2+ architectural vision | Planned | Long-term approved ideas are captured in `docs/FUTURE_IDEAS.md`; these are planning concepts, not v1 commitments. |

## Phase History

### Phase 0 — Planning and Architecture

Status: Completed

Goal: Establish the initial project direction, architecture, coding standards, API compatibility goals, configuration shape, and testing strategy.

Principal outcomes:

- Created planning and reference documents including `docs/ContextKeeper_Project_Plan.md`, `docs/ARCHITECTURE.md`, `docs/API_COMPATIBILITY.md`, `docs/CONFIGURATION.md`, `docs/CODING_STANDARDS.md`, and `docs/TEST_PLAN.md`.
- Defined ContextKeeper as an Ollama-compatible transparent middleware layer.
- Established modular source layout, configuration expectations, and phase-based delivery.

Evidence:

- Initial repository commits: `2993784` (`Initial project setup`), `df6ebc3` (`Add Phase 1 project skeleton`).
- Historical tags present: `v0.1.0`, `v0.1.0-alpha`.

### Phase 1 — Transparent Proxy

Status: Completed

Goal: Make ContextKeeper behave like an Ollama-compatible server while preserving client behavior.

Principal outcomes:

- Added FastAPI application foundation.
- Implemented `/api/*` and `/v1/*` proxy passthrough.
- Preserved streaming behavior for chat and generate endpoints.
- Added model discovery support, YAML configuration, structured logging, and basic test coverage.

Evidence:

- Branch: `phase-1-transparent-proxy`.
- Commit: `6e7b654` (`Complete Phase 1 transparent proxy`).
- Current source evidence: `src/ctxkeeper/proxy/routes.py`, `src/ctxkeeper/proxy/ollama_client.py`, `src/ctxkeeper/app.py`.

### Phase 2 — Diagnostics

Status: Completed

Goal: Add request diagnostics and runtime visibility without breaking transparent proxy behavior.

Principal outcomes:

- Added request log entry modeling and registry behavior.
- Captured response metadata, latency, endpoint, model, status, and client details.
- Added token estimation support.
- Added conversation identity design and diagnostics.

Evidence:

- Branch: `phase-2-diagnostics`.
- Notable commits: `22ecf07`, `367e509`, `c3583c3`, `7c41949`, `07be15a`, `65a2e42`, `280ee19`, `eef8d6e`.
- Current source evidence: `src/ctxkeeper/diagnostics/metrics.py`, proxy metrics recording in `src/ctxkeeper/proxy/routes.py`.

### Phase 3 — Context Engine

Status: Completed

Goal: Track conversations, estimate context usage, detect thresholds, and expose context monitoring data.

Principal outcomes:

- Added in-memory conversation storage.
- Integrated chat request and non-streaming assistant response capture into the proxy.
- Added context meter and threshold detection.
- Added context monitoring scans, warning conversations, compression candidates, and statistics.

Evidence:

- Branches: `phase-3-conversation-store`, `phase-3b-proxy-integration`, `phase-3d-context-monitoring`.
- Notable commits: `1a5fe74`, `c5072b2`, `cb937e0`, `d8eebbc`.
- Current source evidence: `src/ctxkeeper/context/conversation_store.py`, `src/ctxkeeper/context/context_meter.py`, `src/ctxkeeper/context/context_monitor.py`.
- Test evidence: `tests/test_conversation_store.py`, `tests/test_context_meter.py`, `tests/test_context_monitor.py`, `tests/test_proxy_tags.py`.

### Phase 3.5 — Compression Planning

Status: Completed

Goal: Define the safe rolling-context compression strategy before automatic mutation of conversation history.

Principal outcomes:

- Added compression planning primitives.
- Defined keep-recent-message behavior.
- Calculated estimated token savings and readiness states.
- Kept the planning phase independent from live automatic compression.

Evidence:

- Branch: `phase-3-5-compression-planning`.
- Commit: `f20df8f` (`Add compression planning`).
- Current source evidence: `src/ctxkeeper/context/compression_plan.py`.
- Test evidence: `tests/test_compression_plan.py`.

### Phase 4 — Compression

Status: Completed

Goal: Implement summarization-backed rolling compression while preserving recent conversational context.

#### Phase 4A — Local Summarizer

Status: Completed

Principal outcomes:

- Added a local Ollama summarizer abstraction.
- Added prompt generation and failure-safe summarization behavior.

Evidence:

- Branch: `phase-4a-local-summarizer`.
- Commit: `a4f1e3a` (`Add local Ollama summarizer`).
- Current source evidence: `src/ctxkeeper/context/summarizer.py`.
- Test evidence: `tests/test_summarizer.py`.

#### Compression Manager Architecture

Status: Completed

Principal outcomes:

- Added compression manager, summary records, metadata tracking, archive planning placeholder, and message-selection logic.
- Preserved recent messages while preparing older messages for summarization.

Evidence:

- Notable commit: `a977fd4` (`Add compression manager architecture`).
- A dedicated Phase 4B branch name was not found in Git history.
- Current source evidence: `src/ctxkeeper/context/compression_manager.py`.
- Test evidence: `tests/test_compression_manager.py`.

#### Phase 4C — Automatic Context Compression

Status: Completed

Principal outcomes:

- Added threshold-driven automatic compression behavior.
- Stored rolling summaries with the `[ContextKeeper rolling summary]` prefix.
- Updated compression metadata and conversation message state when compression succeeds.

Evidence:

- Branch: `phase-4c-automatic-compression`.
- Commit: `049d060` (`Add automatic context compression`).
- Current source evidence: `src/ctxkeeper/context/compression_manager.py`.

### Phase 5 — Dashboard

Status: Completed

Goal: Build a live browser dashboard for ContextKeeper operations, metrics, context state, and intelligence.

#### Phase 5A — Dashboard Foundation

Status: Completed

Principal outcomes:

- Added the dashboard route and HTML surface.
- Exposed basic dashboard data through FastAPI.

Evidence:

- Branch: `phase-5a-dashboard-foundation`.
- Commit: `1b70568` (`Add dashboard foundation`).

#### Phase 5B — Live Monitoring Dashboard

Status: Completed

Principal outcomes:

- Added live status polling and operational metrics.
- Connected request and system metrics to dashboard display.

Evidence:

- Branch: `phase-5b-live-monitoring-dashboard`.
- Commit: `c05a734` (`Implement live monitoring dashboard`).

#### Phase 5C — Context Visualization

Status: Completed

Principal outcomes:

- Added active conversation visualization.
- Exposed rolling summaries, recent messages, context usage, and compression-related conversation state.

Evidence:

- Branch: `phase-5c-context-visualization`.
- Commit: `81d0658` (`Add dashboard conversation visualization`).
- Current source evidence: `src/ctxkeeper/dashboard/snapshots.py`.
- Test evidence: `tests/test_dashboard_snapshots.py`.

#### Phase 5D — Dashboard Intelligence

Status: Completed

Principal outcomes:

- Added deterministic health state evaluation.
- Added insights, recommendations, timeline events, trends, conversation risk, and dashboard intelligence integration.

Evidence:

- Branch: `phase-5d-dashboard-intelligence`.
- Notable commits: `74d857c` (`Add dashboard intelligence engine`), `8b9e7be` (`Integrate dashboard intelligence into UI`).
- Current source evidence: `src/ctxkeeper/dashboard/intelligence.py`, `src/ctxkeeper/dashboard/insights.py`, `src/ctxkeeper/dashboard/recommendations.py`, `src/ctxkeeper/dashboard/timeline.py`, `src/ctxkeeper/dashboard/trends.py`, `src/ctxkeeper/dashboard/routes.py`.
- Test evidence: `tests/test_dashboard_intelligence.py`.

### Phase 6 — Windows Production Foundation

Status: Completed

Goal: Prepare ContextKeeper for local Windows operation and packaged distribution.

#### Phase 6A — Windows Service Foundation

Status: Completed

Principal outcomes:

- Added service runner structure.
- Added a Windows service placeholder class and metadata.
- Preserved dashboard and proxy routes through service runner creation.

Evidence:

- Branch: `phase-6a-windows-service-foundation`.
- Commit: `17e2d62` (`Add Windows service foundation`).
- Current source evidence: `src/ctxkeeper/service/runner.py`, `src/ctxkeeper/service/windows_service.py`.
- Note: installer service hooks remain placeholders in `scripts/install_service.ps1` and `scripts/uninstall_service.ps1`.

#### Phase 6B — Standalone Executable

Status: Completed

Principal outcomes:

- Added PyInstaller executable entry point and spec file.
- Added resource-loading support for packaged configuration defaults.

Evidence:

- Branch: `phase-6b-standalone-executable`.
- Commit: `c1be8e9` (`Add standalone executable foundation`).
- Current source evidence: `src/ctxkeeper/executable.py`, `src/ctxkeeper/resources.py`, `contextkeeper.spec`.

#### Phase 6C — Setup Wizard

Status: Completed

Principal outcomes:

- Added first-run configuration wizard.
- Added `--configure` CLI flow.
- Added YAML generation helpers.

Evidence:

- Branch: `phase-6c-configuration-wizard`.
- Commit: `2ab403f` (`Add configuration wizard`).
- Current source evidence: `src/ctxkeeper/wizard/`.
- Test evidence: `tests/test_main_wizard.py`, `tests/test_wizard.py`.

#### Phase 6D — Installer

Status: Completed

Principal outcomes:

- Added Inno Setup installer foundation.
- Added installer metadata and release build automation.
- Added scripts for building the PyInstaller executable and Inno Setup installer.

Evidence:

- Branch: `phase-6d-installer`.
- Notable commits: `10c68fe` (`Add installer foundation`), `d4b81a1` (`Add release build automation`), `e9b0940` (`Polish installer release metadata`).
- Current source evidence: `installer/ContextKeeper.iss`, `installer/README.md`, `scripts/build_release.ps1`.

#### Phase 6E — Product Polish

Status: Completed

Principal outcomes:

- Added product branding metadata.
- Polished startup output and package metadata.
- Updated installer and release metadata.

Evidence:

- Branch: `phase-6e-product-polish`.
- Commit: `ad7a83d` (`Polish product startup and branding`).
- Current source evidence: `src/ctxkeeper/branding.py`, `README.md`, installer metadata, release script updates.
- Test evidence: `tests/test_branding.py`.

### Phase 6.5 — Dashboard and Desktop UI Modernization

Status: Active overall, with several completed sub-phases

Goal: Modernize the browser dashboard into a stable desktop operations console with a design system, responsive architecture, dashboard polish, and future rich widgets.

#### Phase 6.5 — Desktop UI Modernization

Status: Completed

Principal outcomes:

- Extracted the dashboard template.
- Redesigned the dashboard as a tabbed operations console.
- Modernized the responsive desktop layout.

Evidence:

- Branch: `phase-6-5-desktop-ui-modernization`.
- Notable commits: `74ce0c7`, `cc963fe`, `a7650ab`, `6cd7f9d`.
- Current source evidence: `src/ctxkeeper/dashboard/template.py`.

#### Phase 6.5E — Desktop Layout Stability

Status: Completed

Principal outcomes:

- Stabilized the desktop dashboard layout and responsive behavior.
- Protected the operations viewport architecture from later visual-only polish passes.

Evidence:

- A dedicated `phase-6-5e` branch was not found.
- Relevant commits include `6cd7f9d` (`Modernize responsive desktop dashboard layout`) and the later recovery commit `e0228ff` (`Recover responsive dashboard layout architecture`).

#### Phase 6.5F-A — Design System

Status: Completed

Principal outcomes:

- Added durable visual-language, color, component, layout, and interaction guidance for the dashboard.
- Established the operations-console direction: health first, flow second, action third.

Evidence:

- Notable commits: `dd90d5e` (`Add UI design language documentation`), `e4ec53f` (`Add UI color system documentation`), `96f72cf` (`Add dashboard layout specification`), `dcb20cc` (`Add UI component library documentation`).
- Current documentation evidence: `docs/DESIGN_LANGUAGE.md`, `docs/COLOR_SYSTEM.md`, `docs/DASHBOARD_LAYOUT.md`, `docs/COMPONENT_LIBRARY.md`.

#### Phase 6.5F-B1 — Visual Concept (No Code)

Status: Completed

Principal outcomes:

- Defined the dashboard visual concept before implementation.
- Established layout hierarchy, component intent, responsive targets, and approval gates for later UI work.

Evidence:

- Documentation evidence: `docs/DASHBOARD_LAYOUT.md`, `docs/DASHBOARD_MOCKUP_PLAN.md`, `docs/DASHBOARD_MOCKUPS.md`, `docs/DESIGN_SYSTEM.md`.
- A dedicated B1 implementation branch was not found.

#### Phase 6.5F-B1a — Dashboard Visual Design Completion

Status: Completed

Principal outcomes:

- Completed the dashboard visual design specification set.
- Added animation, mockup, typography, UI component, style, and live-flow visualization guidance.

Evidence:

- Branch: `phase-6-5f-b1a-dashboard-visual-design-completion`.
- Commit: `93a9692` (`Complete dashboard visual design specification`).
- Current documentation evidence: `docs/ANIMATION_GUIDELINES.md`, `docs/DASHBOARD_MOCKUPS.md`, `docs/DASHBOARD_MOCKUP_PLAN.md`, `docs/DESIGN_SYSTEM.md`, `docs/LIVE_FLOW_VISUALIZATION.md`, `docs/TYPOGRAPHY.md`, `docs/UI_COMPONENT_GUIDE.md`, `docs/UI_STYLE_GUIDE.md`.

#### Phase 6.5F-B2 — Dashboard Implementation

Status: Completed

Principal outcomes:

- Implemented the modern dashboard shell.
- Added hero statistics cards, System Health panel, connection flow panel, and animated topology.
- Kept the dashboard as browser-rendered HTML/CSS/JavaScript inside the FastAPI dashboard route.

Evidence:

- Notable commits: `6401f49` (`Modernize dashboard shell layout`), `3dbe8b6` (`Redesign dashboard hero statistics cards`), `26f83e4` (`Enhance dashboard system health panel`), `7d380fe` (`Polish dashboard connection flow panel`), `6d54d2d` (`Add animated dashboard connection topology`).
- Current source evidence: `src/ctxkeeper/dashboard/template.py`.
- A dedicated B2 branch name was not found.

#### Phase 6.5F-B2.5a — Fix Operations Viewport Scrolling Regression

Status: Completed

Principal outcomes:

- Investigated and recovered operations viewport behavior.
- Re-established the responsive layout architecture after scrolling and viewport-fit regressions.

Evidence:

- Notable commits: `bad28f9` (`Checkpoint responsive layout investigation`), `e0228ff` (`Recover responsive dashboard layout architecture`).
- A dedicated B2.5a branch name was not found.

#### Phase 6.5F-B3 — Responsive Layout Architecture Review

Status: Completed

Principal outcomes:

- Reviewed and recovered the responsive dashboard layout architecture.
- Established the current protected layout constraints for subsequent visual-only dashboard work.

Evidence:

- Branch: `phase-6-5f-b3-responsive-layout-review`.
- Commit: `e0228ff` (`Recover responsive dashboard layout architecture`).

#### Phase 6.5F-B3.2 — System Health Mini-Card Recovery

Status: Completed

Principal outcomes:

- Recovered the System Health mini-card inside the operations hero.
- Preserved the compact health-detail rows and gauge inside the stabilized responsive architecture.

Evidence:

- Notable commit: `9033839` (`WIP checkpoint System Health card refinement`).
- Current source evidence: System Health markup and CSS in `src/ctxkeeper/dashboard/template.py`.
- A dedicated B3.2 branch name was not found.

#### Phase 6.5F-B4 — Dashboard Visual Polish & Micro-Interactions

Status: Completed

Goal: Apply final visual polish and restrained micro-interactions without destabilizing the responsive dashboard architecture.

Historical workstream:

- Branch: `phase-6-5f-b4-4-dashboard-instrument-panel`.
- Base commit: `85dd3cf` (Phase 6.5F-B4.2 merged into `main`).
- Overall B4 is complete; later B5 work added live visualization widgets and inspector capabilities.

#### Phase 6.5F-B4.1 — Core Surface and Status Polish

Status: Completed

Principal outcomes:

- CSS-only visual polish.
- Added reusable surface, border, inset-highlight, shadow, and status-glow tokens.
- Polished hero health status, hero statistics cards, badges, and System Health rows.
- Added restrained hover/focus treatments and reduced-motion handling.
- Preserved the protected responsive architecture.

Validation:

- Latest automated validation recorded for this pass: `pytest` full suite, 115 tests passing.
- Manual dashboard validation recorded for 50%, 75%, and 100% browser zoom.
- No scrolling or clipping regression recorded for the protected operations layout.

Evidence:

- Branch at the time of the B4.1 pass: `phase-6-5f-b4-dashboard-visual-polish`.
- Current working tree evidence at the time this history was created: CSS changes in `src/ctxkeeper/dashboard/template.py`.
- This B4.1 work was not yet represented by a committed Git revision at the time this document was created.

#### Phase 6.5F-B4.2 — Dashboard Micro-Interactions

Status: Completed within the active B4 workstream

Principal outcomes:

- Added restrained, professional micro-interaction polish to the existing browser dashboard without changing the stabilized card layout, responsive grid, breakpoints, or backend behavior.
- Refined sidebar hover, active, pressed, and keyboard-focus states, including `aria-current` management for active navigation items.
- Calmed general informational card hover behavior while preserving responsive feedback for live metric cards, connection nodes, focus-within card surfaces, and badge-styled links.
- Added accessible badge/link feedback for hover, focus, pressed, disabled, and status-change states.
- Reworked live value update feedback so metric values animate only when their displayed value changes, and status badges animate only when their state class changes.
- Removed refresh-cycle animation churn from status badges that previously changed text twice per poll.
- Added subtle refresh busy feedback during polling without introducing spinners, layout shifts, or additional polling timers.
- Refined the Client → ContextKeeper → Ollama → Model flow so request packets pulse only when total request count increases, while connector and status transitions remain smooth.
- Completed an acceptance fix that made the request pulse visibly observable during a real request-count increase by adding a restrained flow-stage sweep, connector emphasis, pipe-node pulse, and slightly longer one-shot pulse duration while preserving the static idle topology.
- Corrected dashboard active-model selection so the model shown in the Connection Flow and active conversation state comes from the latest applicable chat/generate request instead of model metadata requests such as `/api/show`.
- Added model-transition warm-up health interpretation so the first slow successful chat/generate request after switching from one active model to another reports a non-alarming `Model warming`/busy state instead of immediately warning about elevated latency or recommending reduced concurrent load.
- Preserved raw latency metrics and trend reporting while requiring repeated elevated applicable-request latency before latency warnings and latency recommendations are emitted.
- Extended reduced-motion support so nonessential animations and transitions are disabled or made static while preserving state labels and clarity.
- Added an inline dashboard favicon declaration to prevent browser `/favicon.ico` console errors during dashboard validation.

Validation:

- Python syntax validation: `python -m py_compile src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py`.
- Focused acceptance tests added for dashboard active-model selection, `/health` model reporting, model warm-up health interpretation, sustained latency warnings after warm-up, and request-load warnings during a model transition.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 122 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Headless Microsoft Edge dashboard validation at browser zoom-equivalent desktop viewports:
  - 100%: 1600 × 900 CSS viewport.
  - 75%: 2133 × 1200 CSS viewport.
  - 50%: 3200 × 1800 CSS viewport.
- Browser validation confirmed no viewport scroll regression, no app/page overflow, no out-of-bounds card clipping, no detected card overlap, no layout instability (`maxLayoutDeltaPx: 0`), and no console errors at 50%, 75%, or 100%.
- Browser interaction validation confirmed `triggerTopologyPulse()` runs after a request-count increase, one `request-pulse` class addition occurs for one new request, unchanged polling does not add another pulse, and the pulse cleanup leaves the topology static afterward.
- Model-selection tests confirmed `/api/show` metadata requests no longer override the dashboard active model when a newer applicable `/api/chat`, `/api/generate`, `/v1/chat/completions`, or `/v1/completions` model is available in recent metrics.
- Headless browser validation with synthetic request history confirmed a qwen2.5:32b -> llava:latest model switch displays `Model warming`, keeps the active model as `llava:latest`, avoids the reduce-concurrent-load recommendation for the single slow cold-start request, and returns to a normal latency warning after a second slow successful llava request.
- Reduced-motion emulation confirmed `prefers-reduced-motion: reduce` matched, status-dot and flow-packet animations resolved to `none`, and nav/badge transition durations resolved to `0s`.

Evidence:

- Branch: `phase-6-5f-b4-2-dashboard-micro-interactions`.
- Merge baseline recorded for later work: B4.2 was merged into `main` at commit `85dd3cf`.
- Current working tree evidence at the time this history was updated: focused CSS and vanilla JavaScript changes in `src/ctxkeeper/dashboard/template.py`, dashboard active-model and model-warm-up health interpretation changes in `src/ctxkeeper/dashboard/routes.py`, focused tests in `tests/test_app.py`, plus this history update.

#### Phase 6.5F-B4.3 — Dashboard Operational State Machine

Status: Implemented on the active feature branch; not yet merged

This phase was renamed from the planned "Live Motion Refinement" pass to "Dashboard Operational State Machine".

Principal outcomes:

- Added a centralized, strongly typed operational activity manager separate from the dashboard Health Engine.
- Introduced explicit activity states for `starting`, `connecting`, `ready`, `receiving`, `thinking`, `streaming`, `finalizing`, and `idle`.
- Tracked generation request lifecycle events for applicable inference endpoints, including `/api/chat`, `/api/generate`, `/v1/chat/completions`, and `/v1/completions`.
- Preserved metadata endpoints such as `/api/show`, `/api/tags`, `/api/version`, and `/api/ps` as non-activity requests.
- Added per-request lifecycle tracking and aggregate precedence so overlapping requests do not return the global activity state to idle while another generation request remains active.
- Added cleanup paths for upstream errors, streaming failures, client cancellation/disconnect, and request exceptions so stale active states are removed.
- Exposed dashboard activity through an explicit `activity` API object with state, label, active request count, update timestamp, and details.
- Updated the Operations view to distinguish System Health from Current Activity without replacing or weakening the existing Health Engine.
- Integrated activity state into the existing connection topology so receiving can trigger an intake pulse and streaming can show restrained flow motion while idle and ready remain calm.
- Extended reduced-motion handling so activity remains understandable without animation.

Health/activity separation:

- Health remains the existing assessment of whether ContextKeeper is operating normally: healthy, busy, warning, critical, or offline.
- Activity answers what ContextKeeper is doing now: starting, connecting, ready, receiving, thinking, streaming, finalizing, or idle.
- Valid combinations remain possible, such as Health `healthy` with Activity `streaming`, Health `busy` with Activity `thinking`, and Health `critical` with Activity `idle`.
- Existing model warm-up health behavior remains independent from the activity state machine.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\diagnostics\activity.py src\ctxkeeper\proxy\routes.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py src\ctxkeeper\app.py`.
- Focused automated validation: `.\.venv\Scripts\python.exe -m pytest tests\test_activity.py tests\test_proxy_tags.py tests\test_app.py`, 28 tests passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 137 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Static rendered dashboard JavaScript syntax check: extracted the dashboard `<script>` from `render_dashboard_html(Settings())` and ran `node --check -`, passing.
- Real Ollama availability check against configured upstream `http://192.168.0.100:11434/api/version`: HTTP 200.
- Real generation validation through ContextKeeper using `/api/generate` and `llama3.2:latest` observed dashboard activity samples: `ready -> thinking -> streaming -> idle`.
- The same real-generation validation confirmed activity did not remain stale after completion and health remained independently reported.
- Real sequential model-switch validation in one app process (`llama3.2:latest` then `llava:latest`) confirmed model warm-up health still reports `Model warming` for the first successful request after switching models.

Acceptance fix:

- Manual AnythingLLM validation found that activity correctly returned to `idle`, but System Health could remain `critical` after a successful completed generation because dashboard health assembly still treated recent request-history length as active in-flight request load and treated full LLM generation duration as service-health latency.
- Corrected dashboard health assembly so `DashboardMetrics.active_requests` comes from the operational activity manager's live `active_request_count`, not from `len(recent_requests)`.
- Corrected latency-health semantics so successful full-generation `latency_ms` remains raw performance telemetry for dashboard display, trends, timelines, and request history, but is not used by itself to produce warning/critical service-health states.
- Retained future support for explicit service-responsiveness fields such as `service_latency_ms`, `time_to_first_token_ms`, or `first_token_latency_ms` when those metrics are available.
- Added a dashboard-health warning for recent request errors so genuine failed generation requests still affect health without relying on duration.
- Updated pre-request model wording from "No active model yet" to "No model observed yet" without inferring models from metadata requests.

Acceptance-fix validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py`.
- Focused automated validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py tests\test_activity.py tests\test_proxy_tags.py tests\test_dashboard_intelligence.py`, 58 tests passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 141 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Static rendered dashboard JavaScript syntax check: extracted the dashboard `<script>` from `render_dashboard_html(Settings())` and ran `node --check -`, passing.
- Real successful `/api/generate` validation through ContextKeeper using `llama3.2:latest` settled to Health `healthy`, Activity `idle`, active request count `0`, Ollama `online`, errors `0`, raw last latency about `2748.94 ms`, and recommendation `no_action`.
- Real failed `/api/generate` validation with an unavailable model returned HTTP 404 and settled to Health `warning` with reason `recent_request_errors`, while activity still cleaned up to `idle`.

Model-switch acceptance fix:

- Manual AnythingLLM validation found that after switching models and sending a new request, ContextKeeper processed the new request but the dashboard Active Model could remain on the previous model.
- Initial inspection of proxy logs showed client inference traffic using `POST /api/chat` with `stream=true`; the logged model value is extracted from the inbound JSON request body.
- Root cause: dashboard-facing model selection still depended on completed request metrics, while streaming request metrics are recorded only at stream finalization. During the active streaming request, and after later metadata requests updated raw `last_model`, the dashboard could select stale completed-request data even though the activity manager had observed the new applicable request.
- Extended `OperationalActivityManager` to retain the latest observed applicable inference model at request acceptance and expose it in the activity snapshot.
- Routed dashboard data, `/health`, and active conversation snapshot model selection through the same latest-observed-model helper, preferring the activity manager's accepted inference model and falling back to completed applicable request metrics.
- Preserved metadata exclusion: `/api/show`, `/api/tags`, `/api/version`, and `/api/ps` do not become the active/latest model source.
- Made completed-metrics fallback deterministic by sorting applicable request history by timestamp when timestamps are available, so list ordering cannot cause an older model to win.
- Preserved model warm-up behavior, health/activity separation, and the existing operational activity lifecycle.

Model-switch acceptance-fix validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\diagnostics\activity.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\proxy\routes.py`.
- Focused automated validation: `.\.venv\Scripts\python.exe -m pytest tests/test_activity.py tests/test_app.py -q`, 36 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 149 tests passing, with the same existing third-party `StarletteDeprecationWarning`.
- Regression tests now cover sequential model switch from model A to model B, active-request model update before stream completion, metadata requests not overriding the switched model, all supported applicable inference endpoints, request-history ordering, `/health` and dashboard data model consistency, active conversation snapshot consistency, model warm-up preservation, activity lifecycle preservation, and health acceptance preservation.
- Real `/api/chat` streaming validation through ContextKeeper against configured Ollama `http://192.168.0.100:11434` switched from `llama3.2:latest` to `llava:latest`; dashboard data showed `llava:latest` during the active switched request with Activity `thinking` and active request count `1`, kept `llava:latest` after completion, reported `Model warming` for the first successful switched-model request, and returned to Health `healthy`, Activity `idle`, active request count `0`, Ollama `online`, and errors `0` after a second successful `llava:latest` request.

Repeated model-switch acceptance finding:

- A later manual model-switch retest still showed the Operations Console retaining the previous model after a new request, even though operational activity moved through Thinking, Streaming, and Idle correctly.
- The failing request path observed in ContextKeeper logs remained a generic Ollama-compatible `POST /api/chat` request with `stream=true`.
- The compatible model field path at the ContextKeeper proxy boundary is the top-level JSON `model` field used by Ollama chat/generate and OpenAI-compatible completion payloads.
- ContextKeeper production code remains client-agnostic: no AnythingLLM-specific imports, product-name checks, user-agent checks, headers, configuration, endpoint branches, or client UI/API dependencies were added.
- Centralized request model extraction in `src/ctxkeeper/proxy/model_extraction.py`; it normalizes the generic top-level `model` field and intentionally ignores prompt text and message content.
- Added privacy-safe DEBUG diagnostics for applicable generation requests that can record only request id, endpoint, normalized model, model field path, top-level JSON keys, and streaming flag.
- Corrected active model semantics so the dashboard prefers the newest in-flight request with a known model while requests are active.
- Corrected missing-model semantics so an active applicable request without an extractable model is surfaced as `Unknown model` and does not inherit or display the previous completed model as if it belonged to the new request.
- When no applicable request is active, the dashboard retains the most recently observed applicable inference model.
- The same model state feeds OperationalActivityManager snapshots, `/health`, `/dashboard/data`, the Operations Active Model card, request state, and the active conversation snapshot.

Repeated model-switch validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\diagnostics\activity.py src\ctxkeeper\proxy\model_extraction.py src\ctxkeeper\proxy\routes.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py`.
- Focused automated validation: `.\.venv\Scripts\python.exe -m pytest tests/test_activity.py tests/test_app.py tests/test_proxy_tags.py -q`, 52 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 161 tests passing, with the same existing third-party `StarletteDeprecationWarning`.
- Generic regression tests now cover compatible model extraction for `/api/chat`, `/api/generate`, `/v1/chat/completions`, and `/v1/completions`; activity and metrics receiving the same extracted model; active known model selection; active unknown model display; previous model not overwriting a model-less active request; metadata not overwriting the model; health/activity preservation; and model warm-up preservation.
- Direct client-independent `/api/chat` streaming validation through ContextKeeper against configured Ollama `http://192.168.0.100:11434` switched `llama3.2:latest -> llava:latest -> llama3.2:latest`; dashboard data showed each switched model while its request was active, retained the model after completion, preserved model-warm-up Busy state for first switched-model responses, and settled to Health `healthy`, Activity `idle`, active request count `0`, Ollama `online`, and errors `0` after a final same-model request.

Known validation limits:

- `receiving` and `finalizing` are intentionally event-driven and short-lived; the real dashboard polling sample did not reliably catch them, though automated manager and proxy lifecycle tests assert those transitions.
- No explicit time-to-first-token or service-responsiveness metric is currently persisted in request history; until one exists, full successful generation duration is treated as telemetry rather than direct health evidence.
- Browser-console and responsive viewport validation at 100%, 75%, and 50% zoom-equivalent desktop viewports were not executed in this coding environment because browser automation is not installed. Static JavaScript syntax validation and automated dashboard-rendering tests passed.
- A live external-client UI retest is still required for final manual acceptance in the user's environment; repository-side direct validation confirmed the generic compatible request path and state handling.

Evidence:

- Current branch: `phase-6-5f-b4-3-dashboard-operational-state-machine`.
- Current source evidence: `src/ctxkeeper/diagnostics/activity.py`, request lifecycle wiring in `src/ctxkeeper/proxy/routes.py`, dashboard API integration in `src/ctxkeeper/dashboard/routes.py`, dashboard activity UI and motion integration in `src/ctxkeeper/dashboard/template.py`, app bootstrap reset in `src/ctxkeeper/app.py`.
- Test evidence: `tests/test_activity.py`, activity lifecycle assertions in `tests/test_proxy_tags.py`, dashboard API/UI assertions in `tests/test_app.py`.
- This B4.3 work is active-branch work and should not be treated as merged until Git history confirms a merge.

#### Phase 6.5F-B4.4 — Dashboard Instrument Panel

Status: Implemented on the active feature branch; not yet merged

Principal outcomes:

- Added the approved six-card dashboard instrument panel to the existing Operations dashboard architecture without replacing the dashboard shell, sidebar, proxy flow, activity state machine, or existing secondary pages.
- Implemented six instrument cards: CPU Usage, GPU Usage, Memory Usage, Context Usage, Context Trend, and Compression Status.
- Extended system telemetry into structured dashboard-ready CPU, memory, and GPU detail payloads while preserving legacy metric keys used by existing dashboard widgets.
- Added honest unavailable, partial, disabled, and empty states for resource telemetry, GPU collection, active context, context tracking, and compression readiness.
- Added reusable SVG semicircle gauge architecture initialized from shared lightweight markup and used by CPU, GPU, memory, context usage, and compression status.
- Added bounded in-memory rolling context-history support keyed by active conversation id; trend samples are recorded only from real active-context observations and are not backfilled or manufactured.
- Added a compact SVG context trend card with warning and compression threshold guidance and a collecting/empty state when insufficient history exists.
- Added compression-state visualization as an operational state (`Available`, `Disabled`, `Monitoring`, `Approaching`, `Completed`, `Unavailable`) rather than a fake utilization value.
- Preserved reduced-motion support and the existing refresh cycle; the panel updates existing DOM nodes instead of rebuilding cards per poll.

Backend/data payload changes:

- `/dashboard/data` now includes an `instrument_panel` object with `cpu`, `gpu`, `memory`, `context_usage`, `context_trend`, and `compression_status` sections.
- `system` metrics now include structured `cpu`, `memory`, and `gpu_detail` objects in addition to existing `cpu_percent`, `ram_percent`, `ram_used_gb`, `ram_total_gb`, and `gpu` keys.
- Active conversation snapshots now use a model-specific configured context window when `settings.models[model].context_window_tokens` is available, falling back to the configured default context window.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\diagnostics\metrics.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py tests\test_dashboard_instrument_panel.py`.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` and ran `node --check -`, passing.
- New focused instrument-panel tests: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py -q`, 10 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Broader dashboard/context-focused validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_context_monitor.py tests\test_context_meter.py -q`, 68 tests passing, with the same existing warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 171 tests passing, with the same existing warning.

Follow-up:

- Phase 6.5F-B4.5 superseded the earlier planned "Final UX Polish & Consistency Review" label with a narrower Overview Layout Convergence pass.
- Manual browser validation should still cover wide desktop, narrower desktop, 100%, 75%, and 50% zoom-equivalent layouts, browser resize, no active conversation, active conversation, compression disabled/enabled, GPU telemetry unavailable, long hardware/model names, reduced motion, and absence of unexpected page or nested horizontal scrollbars.

#### Phase 6.5F-B4.5 — Overview Layout Convergence

Status: Implemented on the active feature branch; not yet merged

This phase superseded the earlier planned "Final UX Polish & Consistency Review" label with a focused Overview layout convergence pass.

Principal outcomes:

- Removed the duplicate lower-dashboard Resources card now that CPU, GPU, memory, context, trend, and compression telemetry live authoritatively in the instrument panel.
- Rebalanced the lower Operations layout into a wider Traffic panel and a narrower Active Conversation panel using an intentional approximately 60/40 split on desktop widths.
- Expanded the Traffic panel presentation with clearer metric grouping, spacing, alignment, and an existing request-error count moved into the traffic context.
- Expanded the Active Conversation panel presentation with cleaner metadata grouping, longer-value wrapping, improved spacing, and more room for context usage and risk text.
- Improved the Overview information hierarchy by eliminating duplicate resource telemetry and keeping lower-dashboard space focused on traffic and active conversation state.
- Removed stale Resources-card frontend selectors and JavaScript update paths for the deleted CPU/RAM/VRAM widgets.

Validation:

- Focused dashboard validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py -q`, 63 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\template.py tests\test_dashboard_instrument_panel.py`.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` and ran `node --check -`, passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 172 tests passing, with the same existing warning.
- Browser zoom/overflow validation at 100%, 75%, and 50% could not be executed in this environment because no Edge, Chrome, Chromium, or Firefox binary was available on PATH or standard Windows install paths.

#### Phase 6.5F-B4.6 — Instrument Panel Standardization

Status: Implemented on the active feature branch; not yet merged

Principal outcomes:

- Standardized the gauge-style instrument cards for CPU Usage, GPU Usage, Memory Usage, Context Usage, and Compression Status around a shared visual structure.
- Added a strict three-support-line layout rule for gauge-style instruments so supporting details reserve the same vertical region across cards and missing data does not collapse the layout.
- Corrected the visibly offset gauge root cause by replacing variable detail/footer card rows with a shared instrument row contract for header, gauge, primary reading, and support rows.
- Simplified CPU visible hardware detail to dynamically detected CPU identity, thread count, and CPU temperature when a trustworthy sensor is available.
- Preserved dynamic GPU model, VRAM, and temperature presentation while reducing supporting-detail clutter and keeping graceful unavailable/partial telemetry states.
- Preserved the existing instrument-panel color language, gauge component, refresh cycle, reduced-motion behavior, responsive architecture, and `.dashboard-main` scroll-owner model.
- Kept the Context Trend card behavior unchanged except for coexistence with the standardized gauge cards.

Backend/data payload changes:

- `system.cpu` now includes a cached static `thread_count` alias alongside `logical_processor_count`, plus `temperature_c` with a stable `None` fallback when trustworthy CPU temperature cannot be obtained.
- CPU identity collection now prefers clean OS-exposed processor names, filters architecture/platform-only strings, and caches static hardware details to avoid repeated expensive probes.
- CPU temperature collection uses the existing psutil diagnostics path when available and only accepts defensible CPU sensor mappings such as CPU package/core sensor groups.
- `/dashboard/data.instrument_panel` now includes exactly three `detail_lines` for CPU, GPU, memory, context usage, and compression status. Each line carries display text and a title for long-name tooltips.
- Missing CPU/GPU diagnostic fields now serialize into honest unavailable detail lines instead of collapsing frontend support text.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\diagnostics\metrics.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py tests\test_diagnostics_metrics.py tests\test_dashboard_instrument_panel.py`.
- Focused diagnostic tests: `.\.venv\Scripts\python.exe -m pytest tests\test_diagnostics_metrics.py -q`, 4 tests passing.
- Focused dashboard/template validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py -q`, 67 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Responsive/layout-related regression validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_dashboard_snapshots.py -q`, 17 tests passing, with the same existing warning.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 180 tests passing, with the same existing warning.
- Browser zoom/overflow validation at 100%, 75%, and 50% could not be executed in this environment because no Edge, Chrome, Chromium, or Firefox binary was available on PATH or standard Windows install paths.

Follow-up:

- Recommended next review step: Phase 6.5F-B4.7 — Manual Visual QA & Acceptance Review.
- Steve should launch the dashboard locally and manually verify gauge alignment, long hardware names, unavailable CPU/GPU temperature states, 100%, 75%, and 50% zoom, browser resize, reduced motion, and absence of unexpected page or nested horizontal scrollbars.

#### Phase 6.5F-B4.7 — Visual QA & Acceptance Review

Status: Implemented on the active feature branch; not yet merged

Scope reviewed:

- Reviewed the current dashboard page set: Operations, the Overview section within Operations, Conversations, Context, Analytics, Logs, and Settings.
- Treated Context, Analytics, and Logs as the current diagnostics/history equivalents because the dashboard does not currently expose separate pages named Diagnostics or History.
- Verified rendered HTML page targets, sidebar page links, and duplicate-id behavior through static parsing.
- Reviewed dashboard layout, typography, card consistency, gauge consistency, status indicator classes, animation/reduced-motion CSS, overflow behavior, and accessibility affordances available in the template.

Accepted UI refinements:

- Added CSS wrapping guards for dashboard page headers so long titles or subtitles do not distort page layout.
- Added flex-child min-width guards for dashboard panel items so long insight and recommendation text wraps instead of crowding badges.
- Added fixed table layout and cell wrapping for the Logs / Live Activity table so long client, endpoint, model, or status values wrap instead of clipping or causing hidden horizontal overflow.
- Standardized disabled-state presentation for Context Usage and Compression Status so inactive states use a single neutral gauge reading and three concise support lines instead of repeated disabled labels or duplicate badges.
- Standardized enabled no-active/no-history context and compression instrument labels to short operational words: Context Usage and Context Trend now present `WAITING`, and Compression Status presents `READY` instead of long phrases or wrapping labels.
- Kept the visual changes focused and did not alter dashboard APIs, proxy behavior, feature scope, page structure, or the established visual design.

Configuration refinements:

- Changed the default `context.enabled` value to `true` so fresh installations enable completed context tracking by default.
- Changed the default `compression.enabled` value to `true` so fresh installations enable completed compression behavior by default.
- Updated first-run wizard defaults and configuration documentation to match the new core-feature defaults.
- Preserved the existing configuration options so users can explicitly disable context tracking or compression in `contextkeeper.yaml`.

Validation:

- Static rendered HTML QA: confirmed page targets for `operations`, `conversations`, `context`, `analytics`, `logs`, and `settings`; confirmed no duplicate ids in the rendered dashboard.
- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\template.py tests\test_dashboard_instrument_panel.py`.
- Focused dashboard panel validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py -q`, 17 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Broader dashboard-focused validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_diagnostics_metrics.py -q`, 73 tests passing, with the same existing warning.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused dashboard/config/wizard validation for the final B4.7 refinement: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_config.py tests\test_wizard.py -q`, 35 tests passing, with the same existing warning.
- Broader dashboard/config validation for the final B4.7 refinement: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_diagnostics_metrics.py tests\test_config.py tests\test_wizard.py -q`, 91 tests passing, with the same existing warning.
- Full automated suite after the final B4.7 refinement: `.\.venv\Scripts\python.exe -m pytest`, 183 tests passing, with the same existing warning.
- Browser zoom validation at 50%, 75%, and 100% could not be executed in this environment because no Edge, Chrome, Chromium, or Firefox binary was available on PATH or standard Windows install paths.

Remaining deferred items:

- Manual browser acceptance remains required for 50%, 75%, and 100% zoom, common desktop resolutions, Chromium-family rendering, reduced-motion mode, and visual confirmation of subtle animation timing.
- No additional dashboard redesign, feature expansion, or proxy behavior changes were accepted during this QA pass.

### Phase 6.5F-B4.8 — Automatic Model Context Discovery

Branch: `phase-6-5f-b4-8-automatic-model-context-discovery`

Status: Completed; merged to `main` at commit `fdd9478`

Objective:

- Automatically discover Ollama model context-window sizes so context usage and compression thresholds use the effective model capacity instead of always falling back to `context.default_context_window_tokens`.

Implemented scope:

- Added isolated model context-window parsing, normalization, caching, and resolution logic.
- Added diagnostics for incoming runtime `options.num_ctx`, while effective context-window resolution now uses model-specific configured overrides, auto-detected Ollama metadata, and global fallback in that order.
- Parsed Ollama-compatible `/api/show` metadata including architecture-prefixed `*.context_length`, generic `context_length`, `num_ctx`, and `context_window_tokens` fields while ignoring malformed, boolean, zero, negative, implausible, and unrelated metadata values.
- Cached discovered model context windows by normalized model name and preserved explicit user model overrides as authoritative over detected metadata.
- Preserved `/api/show` passthrough response bodies while opportunistically caching usable metadata from them.
- Added dashboard serialization fields for effective context-window tokens, compact label, and user-facing source labels such as Pre-defined, Discovered, and Default.
- Updated active conversation and instrument-panel context calculations to use the resolved active model/request context window.
- Documented automatic discovery, override behavior, outbound `num_ctx` enforcement, resolution priority, and fallback behavior in `docs/CONFIGURATION.md`.

Manual QA correction:

- Manual QA found that the Context Usage card could keep showing a stale prior model after a newer completed generation request and did not visibly show whether the context-window capacity came from Runtime, Configured, Detected, or Default resolution.
- Corrected idle dashboard active-model selection so active in-flight requests still come from the activity manager, but completed idle state uses the newest applicable generation request from request metrics before falling back to activity history.
- Preserved metadata exclusion so `/api/show`, `/api/tags`, and `/api/ps` cannot replace the active conversational model.
- Verified the installed Ollama `/api/show` metadata fields: `gptoss.context_length=131072` for `gpt-oss:20b` and `llama.context_length=32768` for `llava:latest`.
- Updated Context Usage presentation to visibly show model and source in support line 2 while keeping compact capacity available in the card presentation.
- Strengthened discovery runtime behavior by retaining background discovery tasks until completion, adding lightweight retry/backoff after failed discovery attempts, and supporting `llava` / `llava:latest` cache alias resolution without collapsing non-latest tags.
- Added serialization coverage confirming that the dashboard can show Default while discovery is pending and then update to Discovered on a later refresh without restarting ContextKeeper.

Second manual QA correction:

- A second manual QA pass still showed `gpt-oss:20b • Runtime 16K` after the client was switched to a Qwen model.
- Existing logs from the failed window showed metadata traffic for Qwen but the only logged completed conversational `/api/chat` requests still carried `model=gpt-oss:20b`; earlier logging did not include request sequence, top-level keys, or `num_ctx`, so it could not prove whether the client sent Qwen through another compatibility shape.
- Added privacy-safe `B4.8_DIAG` log lines for each conversational generation request, including monotonic generation sequence, endpoint, method, extracted model, model-field presence/path, top-level JSON keys, `num_ctx` presence/value, lifecycle event, metric sequence/timestamp, active runtime override register/cleanup, and dashboard-selected model/context source/capacity.
- Added deterministic metric sequence numbers and changed dashboard generation-request ordering to prefer sequence over timestamps, preventing same-timestamp ties from selecting the wrong model.
- Added a coherent dashboard `ActiveGenerationState` so model, endpoint, request sequence, runtime context value, resolved context-window source, and capacity are selected from one active/completed generation state instead of independent sources.
- Added top-level `name` as a safe request model fallback after `model` for compatibility clients while preserving the exact observed model value.
- Verified configured Ollama metadata: `qwen2.5:35b` is not installed and `/api/show` returns 404; installed `qwen2.5:32b` exposes `qwen2.context_length=32768`; installed `qwen3.6:latest` exposes `qwen35moe.context_length=262144`.
- Added public proxy route coverage for `/api/chat`, `/api/generate`, `/v1/chat/completions`, streaming, model switches, equal timestamp ordering, runtime/default/detected source behavior, failure cleanup, cancellation cleanup, and no inheritance of model A runtime context by model B.

Third intermittent manual QA correction:

- Manual QA reproduced an intermittent sequence where a fresh GPT request selected `gpt-oss:20b`, an immediate switch to `qwen2.5:32b` failed to replace the displayed model, a different model switch did update, and Qwen later updated after an idle period.
- Root cause: the proxy assigned a generation sequence at request entry, but that shared sequence was not preserved through active activity state, runtime context overrides, completed metrics, and dashboard selection. Dashboard selection still gave absolute priority to any active request, so an older still-active GPT observation could mask a newer completed Qwen generation.
- Verified that the relevant sequence counters were in different namespaces: proxy generation sequence, metrics request sequence, and activity request identity. The correction uses the proxy generation sequence as the authoritative ordering key for generation observations and keeps metrics sequence only as a fallback.
- No ContextKeeper five-minute TTL was found in the dashboard, activity manager, metrics store, or model-context cache. The approximate idle behavior matched an older active request eventually clearing outside the dashboard selection path; the fix removes correctness dependence on that expiration.
- Added `generation_sequence` to activity snapshots, completed request metrics, active runtime override records, and dashboard `ActiveGenerationState` so model, endpoint, runtime context source, and capacity are selected from the same newest generation observation.
- Added privacy-safe dashboard candidate-rejection diagnostics so a rejected active/completed candidate records candidate model, selected model, generation sequence, status, age, and rejection reason without logging prompts or message content.
- Verified installed Qwen metadata against the configured Ollama server: exact model `qwen2.5:32b`, `/api/show` key `qwen2.context_length`, value `32768`, parser result `32768`, normalized cache key `qwen2.5:32b`, and dashboard lookup key `qwen2.5:32b`.
- Recorded the then-current AnythingLLM runtime behavior that a client `options.num_ctx=16384` remained authoritative. This was later superseded by the product-owner authority revision below.
- Added route-level and dashboard serialization regressions for GPT then immediate Qwen, same-conversation Qwen switching, Qwen with tools and `options.num_ctx=16384`, streaming generation sequence preservation, simulated five-minute idle, alternate-model switching between Qwen attempts, no wall-clock expiration dependency, and no cross-namespace sequence comparison.

Product-owner authority revision:

- Product direction changed so client-supplied `options.num_ctx` is diagnostics-only and no longer authoritative for effective context capacity.
- New context-window priority: model-specific configured override, auto-detected `/api/show` model capability, then a 32,768-token global fallback.
- ContextKeeper now overwrites outgoing conversational generation request bodies with the resolved authoritative `options.num_ctx` before forwarding to Ollama.
- Configured model overrides remain authoritative over detected metadata so users can intentionally cap large models for RAM, VRAM, latency, or stability.
- For uncached models without configured overrides, ContextKeeper performs a bounded first-call `/api/show` lookup before forwarding the generation request, shares in-flight discovery for concurrent requests to the same normalized model key, caches successful metadata, and falls back to 32K if discovery fails or times out.
- Verified target behavior for `qwen3.6:latest`: client-supplied `options.num_ctx=16384` is overwritten when `/api/show` reports `qwen35moe.context_length=262144`, and the dashboard uses a 262,144-token denominator with a `Discovered` source.
- Refined dashboard-visible context-window source labels for non-technical clarity: internal `detected` renders as `Discovered`, internal `configured` renders as `Pre-defined`, and `default` remains `Default`, with regression coverage for all three visible paths.
- Manual QA then confirmed authoritative context discovery and enforcement live with `qwen3.6:latest`: client requested `num_ctx=16384`, Ollama reported `qwen35moe.context_length=262144`, ContextKeeper used `262144`, the dashboard denominator was `262,144 tokens`, source was discovered, and usage displayed at approximately 0.9%.
- Final presentation polish moved the compact effective context-window capacity into a Context Usage header badge next to the info icon, leaving support line 1 as full token usage, support line 2 as `model • source`, and support line 3 as warning/compression thresholds.
- Added frontend support for long model-name truncation in Context Usage line 2 so the model segment ellipsizes with a full-name tooltip while the source label remains visible.
- Final startup-state refinement introduced an explicit `waiting` context-window presentation state so a fresh dashboard shows `--`, `No active conversation`, and `Waiting for model...` until the first conversational model is observed, rather than implying that the 32K Default fallback has already been selected.
- Final card-header presentation pass normalized shared dashboard header typography and actions so instrument titles, related Operations card titles, optional badges, and info/action icons use one compact header pattern. This prevents `Context Usage` from truncating when the effective-capacity badge is present and does not change context-discovery behavior.
- Updated the built-in config, sample `contextkeeper.yaml`, generated wizard config, configuration documentation, resolver tests, proxy route tests, dashboard serialization tests, and instrument-panel tests for the new 32K fallback and authoritative detected/configured behavior.

Validation:

- Focused dashboard/instrument validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py -q`, 31 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Focused resolver/proxy/dashboard/app source-label validation: `.\.venv\Scripts\python.exe -m pytest tests\test_model_context.py tests\test_dashboard_instrument_panel.py tests\test_proxy_tags.py tests\test_app.py -q`, 108 tests passing, with the same existing warning.
- Broader config/context/compression/dashboard/proxy validation: `.\.venv\Scripts\python.exe -m pytest tests\test_model_context.py tests\test_config.py tests\test_wizard.py tests\test_context_meter.py tests\test_context_monitor.py tests\test_compression_manager.py tests\test_dashboard_instrument_panel.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_app.py tests\test_proxy_tags.py tests\test_activity.py -q`, 197 tests passing, with the same existing warning.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 237 tests passing, with the same existing warning.
- Diff hygiene: `git diff --check`, passing with line-ending normalization warnings only.

### Phase 6.5F-B5.1 — Live Visualization Foundation

Branch: `phase-6-5f-b5-live-data-visualization`

Status: Completed; on `main` and `origin/main` at commit `e35e891`.

Objective:

- Audit the existing dashboard visualization pipeline before adding new live data widgets.
- Determine what live metrics, stores, history buffers, request history, conversation history, context history, compression history, polling mechanisms, duplicated calculations, refresh-time costs, and missing histories already exist.
- Prepare backend data flow for later richer widgets without redesigning the dashboard, replacing current widgets, adding external charting frameworks, or changing dashboard refresh timing.

Audit findings:

- Added `docs/DASHBOARD_VISUALIZATION_AUDIT.md` to preserve the B5.1 inventory of dashboard endpoints, exposed metrics, in-memory stores, rolling buffers, refresh behavior, duplicate calculations, expensive refresh-time work, missing history, and B5.2 visualization opportunities.
- Confirmed current dashboard polling uses the configured dashboard interval, defaulting to 1000 ms, and concurrently calls `/health`, `/metrics`, and `/dashboard/data` with a client-side `refreshInFlight` guard.
- Confirmed request metrics are retained in `MetricsStore` with aggregate counts and the 50 most recent request events.
- Confirmed system metrics are collected live on each metrics snapshot and are not historically retained.
- Confirmed operational activity is current-state oriented and does not retain a state-transition timeline.
- Confirmed conversation history is in-memory and active-state oriented; compression can replace older active messages with rolling summaries, so it is not yet a durable historical archive.
- Confirmed context trend history exists in `ContextHistoryStore` as a bounded in-memory per-conversation buffer of 30 samples, recorded from `/dashboard/data` refreshes.
- Confirmed compression history for the dashboard is derived from current rolling-summary messages rather than a central append-only compression event store.
- Confirmed future richer visualizations can reuse existing recent request history, context trend samples, activity state, model context-window metadata, active conversation snapshots, and instrument-panel data, but longer-duration request trends, durable latency trends, health-state transition timelines, append-only compression events, system resource trends, restart-stable trend history, and historical operational statistics will need additional backend support.

Implemented foundation work:

- Refactored `/dashboard/data` status assembly so it captures the conversation list once per dashboard status build and reuses that snapshot for context monitoring, compression history, and active-conversation snapshot creation.
- Extended `ContextMonitor.scan()` to accept an optional supplied conversation snapshot while preserving existing behavior when no snapshot is supplied.
- Extended `ConversationSnapshotProvider.active_snapshot()` to accept an optional supplied conversation snapshot while preserving existing behavior when no snapshot is supplied.
- Added regression coverage confirming the reusable snapshot path works and that `build_dashboard_status()` reads the conversation store once per status build.
- Preserved existing dashboard JSON shape, refresh interval, polling endpoints, visible widgets, and frontend implementation.

Validation:

- Focused reusable dashboard snapshot validation: `.\.venv\Scripts\python.exe -m pytest tests\test_context_monitor.py tests\test_dashboard_snapshots.py tests\test_app.py::test_dashboard_status_reuses_single_conversation_snapshot -q`, 11 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Broader dashboard/app/context validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_context_monitor.py -q`, 100 tests passing, with the same existing warning.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 240 tests passing, with the same existing warning.

### Phase 6.5F-B5.2 — Live Request Traffic Visualization

Branch: `phase-6-5f-b5-2-live-request-traffic`

Status: Completed; on `main` and `origin/main` at commit `7181b69`.

Objective:

- Add the first live visualization for the Mission Control dashboard, focused only on request traffic.
- Build on the Phase 6.5F-B5.1 audit and reusable dashboard foundation without redesigning the dashboard, changing the card layout, replacing existing gauges, adding external charting frameworks, or changing refresh timing.
- Communicate request frequency, recent activity, idle periods, and burst activity as compact operational telemetry.

Implemented scope:

- Added a compact SVG request-traffic strip inside the existing Traffic panel, preserving the existing Request Trend, Rate, and Errors statistics.
- Reused the existing `/metrics.recent_requests` payload from `MetricsStore`; no new backend history store, endpoint, polling loop, or unbounded buffer was added.
- Bucketed recent request timestamps client-side into 24 bounded buckets across the last 60 seconds so the visualization scrolls naturally as dashboard refreshes occur.
- Added idle, active, and burst visual states, plus empty-state text for no request history and no recent requests in the last minute.
- Preserved the existing dashboard refresh interval and single `setInterval()` refresh loop.
- Preserved reduced-motion behavior by disabling request-traffic bar transitions when `prefers-reduced-motion: reduce` is active.
- Added dashboard-rendering assertions for the request-traffic SVG, bounded-history constants, idle text, renderer wiring, and single refresh interval.

Performance notes:

- Rendering is limited to 24 SVG bars and two grid lines per refresh.
- The visualization uses only the already bounded 50-event recent request list maintained by `MetricsStore`.
- No expensive backend calculation, persistent storage migration, external dependency, chart framework, or extra network request was introduced.

Deferred visualization opportunities:

- Longer-duration request-rate trends, restart-stable traffic history, latency-history charts, health-state transition timelines, append-only compression events, and historical operational statistics still require additional backend history support in later B5 work.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\template.py tests\test_app.py`, passing.
- Focused dashboard endpoint validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py::test_dashboard_endpoint -q`, 1 test passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused dashboard/rendering validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py -q`, 93 tests passing, with the same existing warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 240 tests passing, with the same existing warning.

### Phase 6.5F-B5.3 — Live Connection Flow Animation

Branch: `phase-6-5f-b5-3-live-connection-flow`

Status: Implemented; Product Owner visual QA remains the acceptance checkpoint for final visual tuning.

Objective:

- Animate the existing Mission Control connection topology so generation traffic direction is understandable without redesigning the dashboard, replacing widgets, changing dashboard polling, or adding backend state.
- Represent outbound request flow as Client -> ContextKeeper -> Ollama -> Active Model.
- Represent inbound response flow as Active Model -> Ollama -> ContextKeeper -> Client.
- Keep idle topology calm and readable, and keep long-running active requests restrained rather than replaying the complete path continuously.

Implementation summary:

- Added explicit topology traffic states: `idle`, `outbound`, `processing`, and `inbound`.
- Added stable markup hooks for topology nodes, connector pipes, and SVG path segments using `data-flow-node`, `data-flow-link`, and `data-flow-segment`.
- Added a deterministic frontend transition state machine driven by `activity.active_request_count`.
- Used the established applicable-generation activity payload from `/health` and `/dashboard/data`, including `active_request_count`, `active_endpoint`, `active_generation_sequence`, and `active_request_id`.
- Removed the prior topology pulse trigger based on total request count so metadata requests and non-generation proxy requests cannot animate the conversational connection flow.
- Preserved the B5.2 request-traffic visualization and its bounded `/metrics.recent_requests` source.
- Preserved the existing dashboard refresh interval and polling endpoints.

Topology state model:

- Initial load with no active applicable request settles to `idle`.
- A `0 -> positive` active request-count transition triggers `outbound`.
- Sustained `positive -> positive` active traffic settles to `processing`.
- A `positive -> 0` transition triggers `inbound`, then returns to `idle`.
- If overlapping applicable requests keep the active request count positive, the topology stays in `processing` and does not show the inbound response sequence until the count reaches zero.
- If a new applicable request starts while an inbound transition is still settling, the timer is superseded and the topology starts a new outbound transition.

Reduced-motion behavior:

- The new outbound, inbound, processing, pipe, and packet animations are covered by the existing `prefers-reduced-motion: reduce` media query.
- Under reduced motion, traveling particles and sweeping stage movement are disabled while state text and restrained static connector/node emphasis remain available.

Files changed:

- `src/ctxkeeper/dashboard/template.py` for topology state markup, CSS animation states, reduced-motion coverage, and frontend transition logic.
- `tests/test_app.py` for dashboard structural and behavior-contract coverage.
- `docs/PROJECT_HISTORY.md` for this phase record and current-state updates.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\template.py`, passing.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused dashboard flow-contract validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py::test_dashboard_endpoint tests\test_app.py::test_dashboard_connection_flow_animation_contract -q`, 2 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Broader dashboard/activity/proxy validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py tests\test_dashboard_instrument_panel.py tests\test_dashboard_snapshots.py tests\test_dashboard_intelligence.py tests\test_activity.py tests\test_proxy_tags.py -q`, 133 tests passing, with the same existing warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 241 tests passing, with the same existing warning.

Visual QA requirement:

- Final acceptance still requires Product Owner screenshot or live-browser validation at 50%, 75%, and 100% zoom/scaling equivalents, including idle, outbound, processing, inbound, rapid requests, and reduced-motion behavior.
- This entry records implementation and automated validation only; it does not claim final visual acceptance.

### Phase 6.5F-B5.4 — Live Conversation Timeline

Branch: `phase-6-5f-b5-4-live-conversation-timeline`

Status: Implemented; Product Owner visual QA remains the acceptance checkpoint for final visual tuning.

Objective:

- Add a compact live operational timeline for the active or most recently active conversation.
- Help users understand what ContextKeeper has done during a conversation without exposing private prompts, assistant responses, rolling-summary text, request bodies, retrieved content, secrets, or system prompts.
- Preserve existing dashboard behavior, Ollama API compatibility, request metrics, active conversation display, traffic visualization, connection-flow animation, context instruments, and compression status behavior.

Architectural approach:

- Added a deterministic, read-only live timeline builder in `src/ctxkeeper/dashboard/timeline.py`.
- Reused the existing single conversation snapshot captured by `build_dashboard_status()` rather than reading the conversation store again.
- Reused existing bounded request metrics, active activity state, active conversation/context snapshot data, and rolling-summary compression evidence.
- Added safe `conversation_id` metadata to existing request metric events when the proxy already knows the chat conversation identity, allowing exact request filtering for current non-legacy chat metrics.
- Added only one minimal activity-snapshot field, `active_accepted_at`, exposing the already tracked accepted timestamp for the currently active generation request so an in-flight `request_received` event can be represented accurately.
- Did not add persistent event storage, a new append-only event store, export, filtering, Conversation Inspector, AutoQA, or a competing event-tracking architecture.

Event derivation strategy:

- `conversation_started` derives from the selected active conversation object's `created_at`.
- `request_received` derives only from current active generation activity with an active request id and accepted timestamp.
- `request_completed` and `request_failed` derive from existing bounded `MetricsStore.recent_requests` records for conversational generation endpoints, filtered by request `conversation_id` when available and by the selected conversation's start time for legacy metrics without a conversation id.
- `model_selected` and `model_changed` derive from chronological generation request history and current active generation activity.
- `context_warning` derives from the active conversation context snapshot when warning or compression thresholds are currently exceeded.
- `compression_completed` derives only from confirmed rolling-summary system messages in the active conversation.
- Events are sorted chronologically, capped at 40 recent events, and assigned stable hash-based event ids from deterministic metadata such as request sequence, generation sequence, timestamp, model, endpoint, status, and conversation id.

Privacy protections:

- Timeline events include only operational metadata: timestamp/time label, event type, severity, title, endpoint, model name, status code, latency, context percentage/token estimates, and compression count-style detail.
- The timeline builder checks rolling-summary prefixes only to confirm compression completion and never serializes summary content.
- The timeline does not include user prompt text, assistant response text, rolling-summary body text, request bodies, system prompts, retrieved document contents, or API secrets.
- Focused tests assert that prompt, response, and summary sentinel strings do not appear in timeline payload events.

UI behavior:

- Added a new Operations lower-row card titled `Live Conversation Timeline`, placed with Traffic and Active Conversation rather than among the primary resource gauges.
- The card renders a compact vertical event feed with timestamp, title, optional detail, and small severity markers for informational, success, warning, and error states.
- The list uses an internal scroll area so newer activity is visible without making the page excessively tall.
- The empty state reads `Waiting for conversation activity` and explains that request, context, and compression events will appear without prompt or response content.
- Polling uses a stable event-id signature to avoid rebuilding the timeline DOM when events have not changed.
- If events change, the timeline only auto-scrolls to the newest event when the user was already near the newest event.
- Reduced-motion coverage disables timeline event transitions along with the existing dashboard motion reductions.

Tests added or updated:

- Added focused `tests/test_app.py` coverage for empty timeline state, payload structure, chronological ordering, stable event identifiers, maximum event bound, safe incomplete-data handling, model information, successful request events, failed request events, request conversation identity filtering, active request-received events, context warning events, confirmed compression events, and prompt/response/summary non-leakage.
- Updated dashboard HTML tests to assert the Live Conversation Timeline card, empty-state treatment, frontend renderer, and lower-row layout.
- Updated activity tests to cover the new `active_accepted_at` snapshot field.
- Existing live traffic and connection-flow tests remain intact.
- Existing single conversation snapshot consistency coverage remains intact and still confirms one conversation-store read per dashboard status build.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\timeline.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py src\ctxkeeper\diagnostics\activity.py src\ctxkeeper\diagnostics\metrics.py src\ctxkeeper\proxy\routes.py tests\test_app.py tests\test_activity.py tests\test_dashboard_instrument_panel.py`, passing.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused app validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py -q`, 42 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Focused activity/instrument validation: `.\.venv\Scripts\python.exe -m pytest tests\test_activity.py tests\test_dashboard_instrument_panel.py -q`, 46 tests passing, with the same existing warning.
- Focused dashboard intelligence/snapshot/context/compression validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_intelligence.py tests\test_dashboard_snapshots.py tests\test_context_monitor.py tests\test_compression_manager.py -q`, 48 tests passing.
- Combined affected-suite validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py tests\test_activity.py tests\test_dashboard_instrument_panel.py tests\test_dashboard_intelligence.py tests\test_dashboard_snapshots.py tests\test_context_monitor.py tests\test_compression_manager.py tests\test_proxy_tags.py -q`, 160 tests passing, with the same existing warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 249 tests passing, with the same existing warning.

Files changed:

- `src/ctxkeeper/dashboard/timeline.py`
- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/template.py`
- `src/ctxkeeper/dashboard/__init__.py`
- `src/ctxkeeper/diagnostics/activity.py`
- `src/ctxkeeper/diagnostics/metrics.py`
- `src/ctxkeeper/proxy/routes.py`
- `tests/test_app.py`
- `tests/test_activity.py`
- `tests/test_dashboard_instrument_panel.py`
- `docs/PROJECT_HISTORY.md`

Deliberately deferred:

- Persistent timeline/event storage.
- Compression started and compression failed events, because existing state confirms completed rolling summaries but does not retain reliable start/failure events.
- Context utilization reduced after compression and context-recovered amount, because current rolling-summary evidence does not retain reliable before/after utilization deltas.
- Request-received events for already completed historical requests, because existing request metrics record completion timestamp but not historical request-start timestamp.
- Long-duration historical timelines, export, filtering, Conversation Inspector, and AutoQA.

Visual QA still pending:

- Product Owner should visually validate the Operations page at 50%, 75%, and 100% zoom/scaling equivalents.
- Validate empty timeline state, active request received, completed request, failed request, context warning, compression completed, scrolling behavior, and no horizontal overflow.
- Validate that the timeline complements Traffic and Active Conversation without dominating the gauges or connection flow.
- This entry records implementation and automated validation only; it does not claim final visual acceptance.

### Phase 6.5F-B5.4.2 — Connection Flow Visibility Polish

Branch: `phase-6-5f-b5-4-2-connection-flow-visibility`

Status: Implemented; Product Owner visual QA remains the acceptance checkpoint for final visual tuning.

Objective:

- Apply a Product Owner-requested presentation-only polish to make the animated Connection Flow travel marker easier to see during active traffic.
- Preserve connection-flow behavior, dashboard payloads, backend activity tracking, request instrumentation, animation timing/direction, connection state logic, inactive appearance, and reduced-motion behavior.

Implementation summary:

- Increased the moving packet core from radius `5` to radius `6.5`.
- Added a restrained SVG halo ring behind the moving packet with matching outbound/inbound path animation.
- Increased active packet contrast and opacity while keeping the marker aligned with the existing dark mission-control visual language.
- Kept idle, processing, waiting, offline, and reduced-motion states from displaying the travel marker or implying active traffic.

Files changed:

- `src/ctxkeeper/dashboard/template.py`
- `tests/test_app.py`
- `docs/PROJECT_HISTORY.md`

Validation:

- Focused dashboard validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_instrument_panel.py tests\test_app.py -q`, 73 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 249 tests passing, with the same existing warning.

Visual QA still pending:

- Product Owner should validate the Connection Flow marker at 3440×1440, 2450×1440, and 1720×1440.
- Validate idle, outbound, processing, inbound, rapid request, and reduced-motion states.
- Confirm the marker is more visible without clipping, overflow, distracting flashing, or visual dominance over node labels.

### Phase 6.5F-B5.5 — Conversation Inspector

Status: Active sub-phase track; B5.5.1 and B5.5.2 implemented, later detail slices planned.

Purpose:

- Add a dashboard drill-down surface for a selected conversation while preserving the main Operations dashboard context.
- Let the Live Conversation Timeline remain the compact operational narrative, while the Conversation Inspector becomes the future location for deeper selected-conversation diagnostics.

Design decision:

- Use a right-side slide-out drawer instead of navigating away from the dashboard or reserving a permanent column.
- On wide displays the drawer should preserve visible dashboard context; on narrow displays it may become effectively full-width with a backdrop.
- Keep the dashboard as a read-only observer. Do not duplicate conversation ownership or create a competing event-tracking architecture for inspector presentation.

Why B5.5 is sliced:

- Full conversation inspection touches privacy, on-demand detail loading, message visibility, context composition, compression provenance, and cross-highlighting.
- Splitting the work keeps each slice testable and prevents the foundation from accidentally exposing prompt, response, summary, retrieved-document, or request-body content.
- B5.5.1 intentionally establishes interaction and layout primitives before adding detailed data surfaces.

Durable design note:

- `docs/CONVERSATION_INSPECTOR.md` captures the approved architectural direction, drawer interaction model, planned sections, privacy expectations, on-demand loading strategy, and proposed B5.5 sub-phase breakdown.

### Phase 6.5F-B5.5.1 — Conversation Inspector Foundation

Branch: `phase-6-5f-b5-5-1-conversation-inspector-foundation`

Status: Implemented; Product Owner visual QA remains the acceptance checkpoint for final visual tuning.

Scope:

- Added selectable Live Conversation Timeline entries for events that map to the current timeline conversation.
- Added explicit frontend inspector state for selected conversation id, open/closed state, loading state, and unavailable/error state.
- Added a right-side, nonmodal Conversation Inspector drawer shell with close button, loading state, unavailable state, metadata summary area, accessible labelling, Escape-close behavior, and narrow-screen backdrop behavior.
- Derived initial metadata from the existing dashboard snapshot and Live Conversation Timeline data only.
- Kept dashboard polling as the only refresh path; no new polling loop or backend detail endpoint was added.

Privacy protections:

- B5.5.1 shows operational metadata only.
- Prompt text, assistant response text, rolling-summary body text, system prompts, retrieved document content, request bodies, API secrets, and full conversation messages remain excluded.

Deliberately deferred:

- Full conversation-message inspection.
- Conversation-detail backend endpoint.
- Context-composition visualization.
- Compression-event detail views.
- Prompt/request/response body display.
- Timeline-to-detail cross-highlighting beyond selected-entry state.
- Modal focus trap; the desktop drawer is a complementary nonmodal panel.

Tests added or updated:

- Dashboard HTML/JS contract coverage for inspector drawer markup, title, close control, loading/unavailable states, selected-entry support, explicit inspector state fields, accessibility hooks, Escape-close logic, and reduced-motion styling coverage.

Pre-merge visual polish:

- Tightened Conversation Inspector state rendering so Loading, Unavailable, and Metadata panels are mutually exclusive.
- Condensed loading/unavailable cards, strengthened Metadata Summary hierarchy, and reduced the visual weight of the privacy/phase-scope note without changing drawer width, polling, payloads, or backend behavior.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\template.py tests\test_app.py`, passing.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused dashboard validation: `.\.venv\Scripts\python.exe -m pytest tests\test_app.py tests\test_dashboard_instrument_panel.py -q`, 74 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 250 tests passing, with the same existing warning.

Visual QA still pending:

- Product Owner should open and close the drawer, select multiple timeline entries, confirm selected-entry highlighting follows the active conversation, confirm Escape closes the drawer, confirm no horizontal overflow, confirm timeline polling continues with the drawer open, confirm an active conversation remains selected during refresh, confirm unavailable state wording is honest and readable, review 50%, 75%, and 100% browser zoom, review 3440×1440 at 100% Windows display scaling, and confirm reduced-motion mode does not use distracting transitions.

### Phase 6.5F-B5.5.2 — Conversation Inspector: Overview & Intelligence

Branch: `phase-6-5f-b5-5-2-conversation-inspector-overview-intelligence`

Status: Implemented; Product Owner visual QA remains the acceptance checkpoint for final visual tuning.

Objective:

- Extend the Conversation Inspector foundation with a factual `Overview` section and deterministic `Intelligence` section for the selected/current conversation.
- Reuse the existing dashboard snapshot and refresh path without adding transcript browsing, message expansion, search, export, LLM-generated analysis, or a new conversation persistence system.

Architecture:

- Added a small deterministic inspector view-model helper in `src/ctxkeeper/dashboard/inspector.py`.
- Built the inspector snapshot from the same conversation list, active conversation snapshot, recent request metrics, context thresholds, compression history, and activity state already used by `build_dashboard_status()`.
- Added the resulting `conversation_inspector` object to the existing `/dashboard/data` payload.
- Kept the inspector tied to the existing dashboard polling interval; no new polling loop, endpoint, or secondary conversation snapshot was introduced.

Overview fields added:

- Conversation identifier.
- Conversation state.
- Model.
- Client/source.
- Endpoint.
- Request type.
- Message count.
- Request count.
- Estimated token count.
- Context-window capacity.
- Context usage percentage.
- Compression count.
- Last activity time.
- Deterministic conversation duration.

Intelligence states:

- `insufficient_data`: no conversation, context disabled, or required context estimates unavailable.
- `healthy`: context usage is below the warning threshold and no compression history is present.
- `warning`: context usage is at or above the warning threshold and below the compression threshold.
- `compression_threshold`: context usage is at or above the compression threshold while compression is enabled and capacity is not exhausted.
- `compression_present`: one or more confirmed rolling-summary compression events exist while current usage is otherwise below warning.
- `critical`: context usage has exhausted or exceeded known capacity, or context is at/above the compression threshold while compression is disabled.

Threshold behavior:

- Warning and compression comparisons use the same inclusive semantics as the context engine: `usage_percent >= threshold`.
- No separate dashboard-only "growing" or "compression approaching" state was introduced because existing state does not provide a reliable trend or distinct threshold.

Compression behavior:

- Confirmed compression history is derived from existing rolling-summary evidence.
- Compression history is shown as a supporting condition unless current context pressure or disabled compression creates a more urgent classification.

Privacy boundaries:

- The inspector view model includes metadata and aggregate metrics only.
- Prompt text, assistant response text, rolling-summary body text, request bodies, retrieved document content, secrets, transcript previews, and LLM-generated analysis remain excluded.

Tests added:

- Direct classification tests for healthy, just below warning, exactly warning, just below compression, exactly compression, above compression, compression history, context disabled, compression disabled, no conversation, insufficient data, and exhausted-capacity behavior.
- Dashboard payload mapping tests for overview metadata, safe missing values, compression count, and prompt/summary non-leakage.
- Dashboard HTML contract tests for Overview/Intelligence sections, stable field hooks, escaped rendering, and preservation of a single polling interval.

Files changed:

- `src/ctxkeeper/dashboard/inspector.py`
- `src/ctxkeeper/dashboard/routes.py`
- `src/ctxkeeper/dashboard/template.py`
- `src/ctxkeeper/dashboard/__init__.py`
- `tests/test_dashboard_inspector.py`
- `tests/test_app.py`
- `docs/CONVERSATION_INSPECTOR.md`
- `docs/PROJECT_HISTORY.md`

Deferred:

- Transcript inspection.
- Individual message expansion.
- Conversation search and filtering.
- Export.
- Editing and deletion.
- LLM-generated summaries, analysis, or recommendations.
- Cross-conversation comparison.
- Historical conversation selection beyond the current timeline/current-conversation foundation.
- On-demand detail endpoint and detailed context-composition/compression views.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src\ctxkeeper\dashboard\inspector.py src\ctxkeeper\dashboard\routes.py src\ctxkeeper\dashboard\template.py tests\test_app.py tests\test_dashboard_inspector.py`, passing.
- Rendered dashboard JavaScript syntax validation: extracted `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Focused inspector/dashboard validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_inspector.py tests\test_app.py tests\test_dashboard_instrument_panel.py -q`, 88 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 264 tests passing, with the same existing warning.

Visual QA still pending:

- Product Owner should validate the Overview and Intelligence sections in no-conversation, healthy, warning, compression-threshold, compression-present, critical, unavailable, refresh, reduced-motion, and narrow/wide responsive states.

### Phase 6.5F-B5.6 — Documentation Audit & Synchronization

Status: Implemented in the working tree; Product Owner documentation QA pending.

Objective:

- Audit every maintained Markdown document.
- Classify each document as current, historical, superseded, or archive candidate.
- Synchronize documentation with the current implementation through Phase 6.5F-B5.5.2.
- Preserve current source behavior as authoritative.
- Avoid runtime feature work, dashboard redesign, and production-code refactoring.

Architectural approach:

- Treated source files under `src/ctxkeeper/` and current tests as the source of truth.
- Rewrote only documentation and added status/classification notes to older planning references.
- Preserved older planning/mockup documents rather than deleting them.
- Recorded the durable Markdown inventory in `docs/README.md`.

Key contradictions corrected:

- README still described the dashboard as basic and implied the product was closer to planning than current implementation.
- Architecture still listed unimplemented routing, memory, and plugin engines as initial modules.
- Configuration priority incorrectly listed command-line setting overrides; current source supports built-in defaults, `contextkeeper.yaml`, and a small environment override set.
- Test plan stopped before B5 live dashboard widgets, Conversation Timeline, Conversation Inspector, reduced-motion QA, and responsive visual QA.
- Roadmap still marked B5 live data visualization as planned even though B5.1 through B5.5.2 are implemented.
- Dashboard layout and live-flow docs still contained pre-implementation or placeholder wording for widgets now implemented.

Documentation updated:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_COMPATIBILITY.md`
- `docs/CONFIGURATION.md`
- `docs/TEST_PLAN.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_HISTORY.md`
- `docs/ContextKeeper_Project_Plan.md`
- `docs/DASHBOARD_LAYOUT.md`
- `docs/DASHBOARD_VISUALIZATION_AUDIT.md`
- `docs/DASHBOARD_MOCKUP_PLAN.md`
- `docs/DASHBOARD_MOCKUPS.md`
- `docs/LIVE_FLOW_VISUALIZATION.md`
- `docs/COMPONENT_LIBRARY.md`
- `docs/UI_COMPONENT_GUIDE.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/CODING_STANDARDS.md`
- `docs/ANIMATION_GUIDELINES.md`
- `docs/COLOR_SYSTEM.md`
- `docs/DESIGN_LANGUAGE.md`
- `docs/TYPOGRAPHY.md`
- `docs/UI_STYLE_GUIDE.md`
- `docs/CONVERSATION_INSPECTOR.md`
- `docs/FUTURE_IDEAS.md`
- `installer/README.md`

Deferred:

- Runtime feature work.
- Dashboard redesign.
- Production-code refactoring.
- Deletion or archival movement of superseded documents.
- Screenshot replacement or image asset work.

Validation:

- Maintained Markdown relative-link check: passing.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 264 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- `git diff --check`: passing with Git line-ending normalization warnings for edited Markdown files; no whitespace errors reported.

### Phase 6.5F-B6.1 — Settings State & Read API

Status: Implemented in the working tree; Product Owner QA pending.

Objective:

- Establish the backend foundation for the future Settings dashboard.
- Provide a single authoritative read-only runtime settings snapshot.
- Expose the current effective values and metadata for approved Context, Compression, and Dashboard settings.
- Avoid UI editing, persistence, runtime updates, dashboard redesign, or changes to proxy/context/compression behavior.

Architecture:

- Added `src/ctxkeeper/dashboard/settings_snapshot.py` as the typed internal settings snapshot model.
- Added `DashboardSetting`, `DashboardSettingsCategory`, and `DashboardSettingsSnapshot` dataclasses.
- Added `build_dashboard_settings_snapshot(settings)` to derive the sanitized snapshot from the existing `Settings` instance.
- Added `GET /api/dashboard/settings` on the existing dashboard router.
- Added an explicit `405` response for mutating methods on `/api/dashboard/settings` so the internal settings path cannot be used as an edit API or fall through to the Ollama proxy.
- Kept the endpoint read-only and independent from `/dashboard/data`, dashboard rendering, proxy routing, conversation inspection, context monitoring, and compression logic.

Settings exposed:

- `context.enabled`
- `context.warning_threshold_percent`
- `context.compression_threshold_percent`
- `context.keep_recent_messages`
- `compression.enabled`
- `compression.summarizer_model`
- `compression.max_summary_tokens`
- `dashboard.refresh_interval_ms`

Snapshot metadata:

- stable id;
- category;
- display name;
- description;
- effective runtime value;
- built-in default value;
- minimum/maximum validation limits when applicable;
- data type;
- `runtime_editable`;
- `restart_required`.

Read-only boundary:

- No Settings dashboard UI controls were added.
- No editing API was added.
- No persistence or config write path was added.
- No runtime settings mutation was added.
- Because no runtime mutation mechanism exists yet, all approved settings are exposed as `runtime_editable: false` and `restart_required: true`.

Sanitization:

- The endpoint does not expose environment variables, config file paths, secrets, tokens, passwords, server bind details, Ollama base URL, logging paths, metrics settings, model override maps, or future configuration.

Tests added:

- Added `tests/test_dashboard_settings.py` covering snapshot schema, category order, expected fields, current/default values, validation metadata, sanitized output, endpoint response, and preservation of the existing dashboard data payload.

Documentation updated:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_HISTORY.md`
- `docs/TEST_PLAN.md`

Validation:

- Focused settings tests: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_settings.py -q`, 6 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient.
- Focused dashboard/settings validation: `.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_settings.py tests\test_app.py -q`, 49 tests passing, with the same existing warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 270 tests passing, with the same existing warning.

### Phase 6.5F-B6.2 - Runtime Settings Update API

Status: Implemented in the working tree; Product Owner and architect review pending.

Date: 2026-07-17.

Objective:

- Extend the Phase 6.5F-B6.1 Settings Snapshot foundation with a validated runtime update API.
- Accept partial runtime settings updates for the approved Context, Compression, and Dashboard settings.
- Validate the complete proposed settings state before mutation.
- Apply valid updates atomically to the existing in-memory `Settings` instance.
- Return the canonical settings snapshot after successful updates.
- Keep runtime changes temporary and reset on process restart.

Architecture:

- Extended `src/ctxkeeper/dashboard/settings_snapshot.py` rather than creating a second settings store.
- Added strict typed Pydantic update models for Context, Compression, Dashboard, and the top-level runtime update body.
- Added `update_runtime_settings(settings, update)` as the canonical update interface.
- Reused the existing shared `Settings` instance owned by application startup and dashboard routing.
- Added a small standard-library lock around snapshot reads and runtime mutation so GET and PATCH observe coherent settings state.
- Added `PATCH /api/dashboard/settings` on the existing dashboard settings resource.
- Kept `GET /api/dashboard/settings` response shape unchanged apart from B6.2 metadata values showing approved settings as runtime-editable and not restart-required.
- Kept `POST`, `PUT`, and `DELETE` rejected with `405`.

Update semantics:

- Request bodies use the same category nesting as the settings snapshot, for example `context.warning_threshold_percent` under `context`.
- Omitted settings retain their current runtime values.
- Submitted values are merged into the current full settings state, then the merged state is validated before mutation.
- Successful PATCH responses return the full canonical settings snapshot.
- A subsequent GET returns the same updated values.
- Empty JSON objects are rejected rather than treated as no-op updates.

Validation:

- Booleans must be JSON booleans.
- Integers must be JSON integers, not strings or floating-point values.
- Runtime threshold percentages must remain within the configured percentage range.
- Runtime `context.warning_threshold_percent` must be less than `context.compression_threshold_percent`.
- Existing configuration validation continues to enforce positive numeric limits and the retained `context.minimum_threshold_percent` ordering rule.
- `compression.summarizer_model` must be a non-blank string.
- Unknown top-level fields, unknown nested fields, read-only/unexposed fields, null values, wrong object shapes, missing bodies, and malformed JSON are rejected.
- Invalid updates are atomic: no supplied value is applied if any part of the request fails validation.

Settings update scope:

- Runtime-mutable fields:
  - `context.enabled`
  - `context.warning_threshold_percent`
  - `context.compression_threshold_percent`
  - `context.keep_recent_messages`
  - `compression.enabled`
  - `compression.summarizer_model`
  - `compression.max_summary_tokens`
  - `dashboard.refresh_interval_ms`
- Startup-only or unexposed fields remain unavailable through the runtime API, including server bind settings, Ollama URL, logging paths, metrics settings, model override maps, `context.default_context_window_tokens`, and `context.minimum_threshold_percent`.

Explicit non-persistence:

- No YAML writing was added.
- No settings database was added.
- No browser storage was added.
- No startup restoration of runtime overrides was added.
- Runtime overrides reset when ContextKeeper restarts.

Tests added or updated:

- Expanded `tests/test_dashboard_settings.py` from the B6.1 read-only coverage to B6.2 read/update coverage.
- Covered schema compatibility, runtime-editable metadata, successful single-field updates, successful multi-field updates, omitted-field retention, full snapshot responses, read-after-write consistency, cross-section updates, repeated valid updates, strict type rejection, range validation, threshold ordering, partial threshold conflicts, numeric limits, blank model rejection, unknown/read-only fields, atomic rejection, empty body behavior, malformed/missing bodies, wrong object shapes, and null rejection.

Documentation updated:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_HISTORY.md`
- `docs/README.md`
- `docs/TEST_PLAN.md`

Deferred:

- Settings dashboard UI controls.
- Persistence to `contextkeeper.yaml` or another durable store.
- Reset-to-default controls.
- Authentication, multi-user settings, and ownership.
- Browser storage.
- Broad integration refactoring outside the existing `Settings` instance.

Validation:

- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src/ctxkeeper/dashboard/settings_snapshot.py src/ctxkeeper/dashboard/routes.py src/ctxkeeper/dashboard/__init__.py tests/test_dashboard_settings.py`, passing.
- Focused settings tests: `.\.venv\Scripts\python.exe -m pytest tests/test_dashboard_settings.py -q`, 25 tests passing, with one existing third-party `StarletteDeprecationWarning` from FastAPI/Starlette TestClient and one `httpx` deprecation warning from the malformed-JSON request test.
- Related app tests: `.\.venv\Scripts\python.exe -m pytest tests/test_app.py -q`, 43 tests passing, with the existing third-party `StarletteDeprecationWarning`.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 289 tests passing, with the same existing FastAPI/Starlette warning and the malformed-JSON request-test `httpx` warning.

### Phase 6.5F-B6.3 — Settings Panel UI Foundation

Status: Implemented in the working tree; Product Owner QA pending.

Date: 2026-07-20.

Objective:

- Activate the existing Settings destination inside the dashboard shell.
- Load setting categories, identities, values, types, constraints, descriptions, editability, and restart metadata dynamically from `GET /api/dashboard/settings`.
- Provide typed draft editing, meaningful dirty-state detection, one atomic Save action, Discard, and accessible loading/success/error feedback.
- Keep all changes runtime-only and avoid configuration-file persistence, browser storage, proxy changes, or a frontend toolchain.

Architecture and state:

- Replaced the static Settings placeholder in `src/ctxkeeper/dashboard/template.py` without adding a separate application, frontend framework, build pipeline, dependency, or endpoint.
- Extended the existing hash-based page switcher; Operations remains the primary dashboard view, and active navigation continues to use `.active` plus `aria-current="page"`.
- Added a guarded first-load request when Settings opens. Repeated view switching does not duplicate the settings load, event listeners, or dashboard polling timers.
- Added snapshot shape validation for the current `boolean`, `integer`, and `string` metadata contract. Unexpected or malformed data produces an error/retry state rather than fallback controls.
- API-supplied display names, descriptions, values, constraints, identifiers, and error messages are created with DOM nodes and `textContent`; Settings rendering does not interpolate API data through `innerHTML`.
- The browser stores a recursively frozen confirmed snapshot and a separately cloned draft snapshot. Editing mutates only draft setting values.
- Dirty calculation uses strict type-and-value comparison, excludes non-runtime-editable settings, and returns to clean when values are manually restored.

Save, validation, and Discard behavior:

- Generic render paths create native checkbox, numeric, and text controls from API metadata, including min/max constraints, default-value context, runtime-read-only explanations, and restart-required badges.
- Save is disabled for a clean or invalid draft and guarded while a request is pending. Editing and Discard are also disabled during the in-flight update so the canonical response cannot overwrite newer edits.
- The client derives category/field nesting from setting metadata and sends exactly one `PATCH /api/dashboard/settings` containing only changed runtime-editable values. Numeric and boolean values remain JSON numbers and booleans.
- The successful canonical PATCH snapshot replaces confirmed state and creates the next clean draft; the client performs one confirming GET only if the success response is not a usable snapshot.
- Field-level API validation locations are associated with controls where possible, while category-level and other errors remain visible in the page alert.
- Validation, network, server, and confirmation failures preserve the complete draft and dirty state for correction or retry.
- Discard clones the latest confirmed snapshot, clears validation feedback and dirty state, and performs no request.

Accessibility, responsive behavior, and lifecycle:

- Added an always-visible notice that dashboard changes apply only to the current runtime, reset at restart, and do not modify `contextkeeper.yaml`.
- Added explicit labels/descriptions, `aria-describedby`, invalid-state association, polite status updates, an assertive page error alert, visible focus styling, native keyboard controls, and text in addition to color for state communication.
- Added responsive category, field, and action layouts that collapse cleanly at narrow widths without introducing horizontal page overflow.
- Preserved reduced-motion behavior and the existing dashboard visualization lifecycle.
- Converted the fixed polling interval into one reschedulable timer. `/dashboard/data.refresh_interval_ms` updates that same timer after a runtime setting change; only one interval can remain active.

Tests added:

- Added `tests/test_dashboard_settings_ui.py` with 13 focused rendered HTML/JavaScript contract tests for Settings navigation/page structure, accessible feedback, runtime-only messaging, canonical GET/PATCH integration, metadata-driven safe rendering, supported types, read-only/restart branches, separate confirmed/draft state, typed dirty behavior, one nested changed-fields-only update, duplicate-save guard, authoritative success, draft-preserving failures, no-request Discard, retry/malformed-data handling, responsive CSS, reduced motion, and polling/listener lifecycle guards.
- Retained the existing 25 Settings API tests for strict request types, validation, atomicity, canonical responses, and read-after-write behavior.
- Preserved existing dashboard, proxy, streaming, conversation, visualization, context, compression, and packaging regressions.

Documentation updated:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/TEST_PLAN.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_HISTORY.md`
- `docs/DASHBOARD_LAYOUT.md`
- `docs/UI_COMPONENT_GUIDE.md`

Deferred:

- Persistence to `contextkeeper.yaml` or another durable store.
- LocalStorage, SessionStorage, database, or startup restoration of runtime overrides.
- Reset-to-defaults, import/export, per-setting autosave, and undo history.
- Authentication, authorization, accounts, multi-user settings, and remote administration.
- Broader dashboard customization, proxy/streaming changes, and context/compression redesign.

Validation:

- Focused settings/dashboard suite: `.\.venv\Scripts\python.exe -m pytest tests/test_dashboard_settings_ui.py tests/test_dashboard_settings.py tests/test_app.py::test_dashboard_endpoint tests/test_dashboard_instrument_panel.py::test_dashboard_template_has_consistent_page_targets_and_unique_ids -q`, 40 tests passing with the two existing third-party deprecation warnings.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest`, 302 tests passing with one existing FastAPI/Starlette TestClient deprecation warning and one existing `httpx` malformed-request test deprecation warning; no skipped tests.
- Python syntax validation: `.\.venv\Scripts\python.exe -m py_compile src/ctxkeeper/dashboard/template.py tests/test_dashboard_settings_ui.py`, passing.
- Rendered dashboard JavaScript syntax validation: extracted the dashboard `<script>` from `render_dashboard_html(Settings())` with UTF-8 output and ran `node --check -`, passing.
- Headless Microsoft Edge engineering smoke checks exercised the real Settings page at `3440×1440` and narrow width, field-specific validation focus, draft preservation, Discard, successful numeric Save, accepted-update reconciliation, and runtime refresh-timer rescheduling; the temporary runtime was stopped afterward.
- Product Owner visual and interaction QA remains the acceptance checkpoint; this phase is not committed, merged, pushed, or released by this working-tree implementation.

### Phase 6.5F-B6.4 — Configuration Persistence Foundation

Status: Implemented in the working tree; Product Owner and architect review pending.

Date: 2026-07-20.

Objective:

- Keep temporary runtime updates and durable configuration writes as separate, explicit operations.
- Persist only approved dashboard settings selected by the user.
- Preserve unrelated and model-specific configuration data while replacing the active YAML file atomically and defensively.
- Expose runtime-versus-persisted metadata and add Save to configuration to the existing draft-based Settings page.
- Preserve Ollama proxy/streaming behavior and the completed B6.1, B6.2, and B6.3 contracts.

Architecture:

- Added `src/ctxkeeper/dashboard/config_persistence.py` as the focused persistence service rather than expanding routes or creating a second settings catalog.
- Reused `RuntimeSettingsUpdate`, strict Pydantic models, authoritative `DashboardSetting` metadata, complete `Settings` validation, and the shared dashboard threshold-order business rule.
- Application startup now resolves the active configuration path once and supplies that path to both loading and `ConfigurationPersistenceService`; the service uses the existing source/frozen `resolve_config_path` rules.
- The service reads disk state freshly for GET metadata and immediately before each PUT; it does not write from an old startup-time configuration copy.
- Added one process-global `RLock` around persisted-state reads and persistence operations. The boundary serializes competing operations only inside one running ContextKeeper process.

Settings snapshot and API contract:

- Advanced the canonical settings snapshot to schema version 2.
- Added `persisted_value`, `differs_from_persisted`, and `persistable` while retaining `value`, `default_value`, validation constraints, `runtime_editable`, `restart_required`, and existing display metadata.
- `GET /api/dashboard/settings` remains read-only and now reports runtime and freshly read persisted state.
- `PATCH /api/dashboard/settings` remains the temporary runtime-only update operation. It does not call persistence or write YAML.
- GET and PATCH run as synchronous FastAPI handlers so disk reads and persistence-lock waits use the worker pool rather than blocking the async proxy/streaming event loop.
- PATCH validates that persisted state is available before runtime mutation, preventing an error path from returning fabricated persisted metadata.
- Added `PUT /api/dashboard/settings/config` with the same category-grouped partial request shape.
- Successful PUT returns `status: "saved"`, sorted `persisted_setting_ids`, `configuration_created`, and a refreshed schema-v2 snapshot in `settings`.
- PUT changes disk state only: it does not mutate the shared runtime `Settings`, apply PATCH implicitly, or restart ContextKeeper.
- `POST`, `PUT`, and `DELETE` on `/api/dashboard/settings` itself remain `405`; persistence is available only through the dedicated `/api/dashboard/settings/config` resource.

Validation and safe errors:

- Requests containing no setting values return `400`; malformed structures, unknown categories/fields, non-persistable fields, nulls, strict boolean/integer violations, range violations, blank model names, and cross-field conflicts return `422`.
- Existing malformed/non-mapping YAML, invalid UTF-8, invalid configuration, and detected stale writes return `409` without replacing the file.
- Read, directory, serialization, temporary-write/verification, and atomic-replace failures return safe server errors without stack traces, filesystem paths, secrets, or full configuration contents.
- A missing file is handled deliberately: validated defaults supply effective persisted metadata, an explicit PUT creates missing parent directories/file, and success reports `configuration_created: true`.
- Logs record safe error code/status metadata or success setting counts and creation state, not configuration bodies or secret values.

Atomic persistence behavior:

- The service parses the active YAML mapping, deep-copies it, and changes only explicitly supplied approved fields, preserving unmanaged categories, values, and model-specific entries.
- The merged complete candidate is validated before serialization.
- PyYAML `safe_dump` emits readable block-style Unicode YAML with source key order retained where possible; the serialized candidate is parsed and validated again.
- A temporary file is created in the destination directory, written as UTF-8/LF, flushed, `fsync`ed, closed, read back, byte-verified, and parsed before replacement.
- A SHA-256 source fingerprint is checked immediately before commit. A detected intervening edit returns `409` rather than overwriting the newer content.
- `os.replace` performs the same-directory atomic replacement only after all preparation succeeds.
- Failed preparation/replacement retains the original destination and triggers best-effort temporary-file cleanup; cleanup failures are logged safely.

Settings UI behavior:

- Replaced the earlier runtime-only notice with explicit runtime-versus-saved guidance.
- Runtime form submission remains changed-fields-only PATCH and is labeled Save runtime changes.
- Added a separate button labeled Save to configuration; editing/input never invokes it automatically.
- Persistence payloads include only metadata-approved persistable draft values that differ from confirmed `persisted_value`.
- Each setting shows its saved configuration value, typed runtime/persisted/draft difference text, and applicable runtime-read-only, non-persistable, runtime-differs-from-saved, and restart-required badges.
- Save to configuration is disabled when nothing eligible differs, displays an in-progress state, and locks both save actions and controls while pending to prevent duplicate/conflicting requests.
- Successful persistence accepts the refreshed snapshot while restoring the user's current draft, allowing disk-only changes to remain pending runtime application.
- Persistence validation, storage, network, and malformed-response failures retain the draft and use the existing inline status/error/focus patterns.
- No restart button or automatic restart behavior was added.

Tests added or updated:

- Added `tests/test_config_persistence.py` for single/multi-setting persistence, preservation, strict validation, malformed/missing/inaccessible files, temporary and replacement failures, original-file retention, cleanup, fingerprint conflicts, and concurrent in-process serialization.
- Expanded `tests/test_dashboard_settings.py` for schema-v2/refreshed metadata, generic restart-required divergence, PUT success/response/status/error behavior, no runtime mutation, GET/PATCH preservation, and unsupported-method regression.
- Expanded `tests/test_dashboard_settings_ui.py` rendered HTML/JavaScript contract coverage for the explicit persistence action, request selection, no autosave, loading/duplicate guards, draft-preserving success/failure, runtime/persisted differences, and restart guidance.
- Preserved proxy, streaming, dashboard, context, compression, service, wizard, packaging, and existing Settings regressions.

Documentation updated:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_COMPATIBILITY.md`
- `docs/CONFIGURATION.md`
- `docs/TEST_PLAN.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_HISTORY.md`
- `docs/ContextKeeper_Project_Plan.md`
- `docs/DASHBOARD_LAYOUT.md`
- `docs/UI_COMPONENT_GUIDE.md`

Limitations and boundaries:

- The lock is process-local; no operating-system, distributed, or multi-process lock was added. Fingerprinting is best-effort and cannot close the final external-writer race between the check and `os.replace`.
- PyYAML preserves parsed data but not comments, exact whitespace, anchors, quoting choices, or original source formatting. B6.4 does not add a complex round-trip YAML dependency.
- No automatic persistence after PATCH or editing, automatic restart, service orchestration, reset-to-defaults, rollback history, backup UI, import/export, secrets management, authentication, multi-user conflict resolution, database, or cloud synchronization was added.

Validation:

- Focused persistence/service/API/UI validation: `.\.venv\Scripts\python.exe -m pytest tests/test_config_persistence.py tests/test_dashboard_settings.py tests/test_dashboard_settings_ui.py -q`, 117 tests passing in 1.27 seconds with one third-party FastAPI/Starlette TestClient deprecation warning and one existing `httpx` raw-content deprecation warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 381 tests passing in 6.53 seconds with the same two third-party deprecation warnings and no skipped tests.
- Python syntax validation for the changed source and tests with `py_compile`, passing.
- Rendered dashboard JavaScript syntax validation with `node --check`, passing.
- Whitespace/error validation with `git diff --check`, passing.
- Product Owner and architect review remain the acceptance checkpoint; this phase is not committed, merged, pushed, or released by this working-tree implementation.

### Phase 6.5F-B6.5: Settings Reset and Recovery Controls

Status: Implemented in the working tree; Product Owner and architect review pending.

Date: 2026-07-20.

Objective:

- Add safe recovery controls for restoring one setting, one category, or all dashboard-managed settings to built-in defaults.
- Keep reset as an explicit runtime-only operation and preserve Save to configuration as the only dashboard YAML write.
- Preserve authoritative backend metadata, validation, atomicity, runtime/persisted separation, restart guidance, and unmanaged configuration content.
- Preserve proxy compatibility, streaming, dashboard refresh, context, compression, and application data.

Settings metadata and architecture:

- Added additive `reset_eligible` metadata to the canonical schema-v2 Settings snapshot.
- Kept `src/ctxkeeper/dashboard/settings_snapshot.py` as the single authoritative catalog for setting identity, type, constraints, built-in `default_value`, runtime editability, persistence eligibility, reset eligibility, and restart requirements.
- Kept built-in defaults out of dashboard JavaScript and HTML. The browser derives every reset value and inclusion decision from the current validated server snapshot.
- Reused `PATCH /api/dashboard/settings` for reset and recovery. No reset endpoint or second validation path was added.
- The backend continues to merge a request into the complete proposed runtime Settings state, validate it fully, and mutate shared runtime state only after validation succeeds.

Reset behavior:

- Added an accessible reset action for each `reset_eligible` setting. It is disabled when the confirmed runtime value already equals the built-in default and submits only the selected setting when used.
- Added one reset action to each settings category. Native confirmation is required, all and only reset-eligible settings in that category are included, including eligible values already at default, and the complete category payload is sent in one atomic PATCH.
- Added the deliberate global control labeled **Reset managed settings to defaults**. Native confirmation is required, and one atomic PATCH contains all and only reset-eligible settings from the current snapshot, including eligible values already at default. Category and global actions are disabled when their complete eligible scope is already at default.
- Confirmation cancellation sends no request and changes no settings. Successful feedback identifies the number staged where practical, states that reset did not write configuration, and distinguishes Save-required persisted divergence from an already-matching configuration.
- Reset never calls the persistence service, writes or recreates YAML, restarts ContextKeeper, or clears logs, metrics, conversations, summaries, model files, or other application data. It is not a factory reset.

Discard and persistence behavior:

- Discard remains a local operation when it only abandons unsaved browser draft edits.
- When confirmed runtime values differ from persisted values, Discard constructs updates for every runtime-editable differing setting from authoritative `persisted_value` metadata and sends one atomic PATCH. It never sends PUT or writes YAML.
- Save to configuration remains a separate explicit `PUT /api/dashboard/settings/config`. Staged default values persist through the existing allowlisted validation and atomic replacement service.
- Successful Save refreshes runtime/persisted metadata. Failed reset, Discard, or Save operations preserve recoverable UI/runtime state and do not report false success.
- Unmanaged and unknown YAML keys remain outside the dashboard reset allowlist and remain protected by the B6.4 persistence contract. Saving affects the YAML tier only and cannot override a higher-priority source.

State presentation and accessibility:

- The page continues to distinguish draft, current runtime, persisted, and built-in default values, plus unsaved and restart-required state.
- Individual controls use native button semantics and setting-specific accessible names. Disabled reset states are represented visually and semantically.
- Category and global confirmation use the browser's native keyboard-operable confirmation interaction.
- Existing status/live regions announce staged, cancelled, successful, and failed outcomes without relying on color alone.
- Responsive layout, focus visibility, reduced-motion behavior, page switching, and the single dashboard refresh lifecycle remain intact.

Tests added or updated:

- Expanded `tests/test_dashboard_settings.py` for `reset_eligible` snapshot compatibility, authoritative defaults, supported eligibility, atomic reset/update behavior, runtime-versus-persisted synchronization, API compatibility, and no persistence side effects.
- Expanded `tests/test_dashboard_settings_ui.py` for individual/category/global reset selection, exact global label, native confirmation/cancellation, accessible and disabled states, staged-unsaved feedback, Discard recovery, Save integration, failure preservation, responsive behavior, and lifecycle regression.
- Expanded configuration-persistence coverage for saving staged defaults, allowlisted-only changes, unknown/unmanaged content preservation, validation/write failures, atomic replacement safeguards, and restart loading.
- Preserved the complete proxy, streaming, dashboard, context, compression, configuration, logging, service, and controlled-shutdown regression suite.

Documentation updated:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_COMPATIBILITY.md`
- `docs/CONFIGURATION.md`
- `docs/DASHBOARD_LAYOUT.md`
- `docs/ROADMAP.md`
- `docs/TEST_PLAN.md`
- `docs/PROJECT_HISTORY.md`
- `docs/UI_COMPONENT_GUIDE.md`
- `docs/ContextKeeper_Project_Plan.md`

Limitations and boundaries:

- Reset applies only to metadata-approved dashboard-managed settings.
- No restart control, Windows service restart, force-stop, self-diagnostics, automated repair, configuration backup history, rollback, import/export, profiles, environment-variable editing, command-line editing, authentication, or multi-user management was added.
- Restart-required settings still require a manual restart when their metadata indicates one.
- Configuration precedence and the B6.4 atomic persistence limitations remain unchanged.

Validation:

- Focused Settings persistence/API/UI validation: `.\.venv\Scripts\python.exe -m pytest -q tests\test_config_persistence.py tests\test_dashboard_settings.py tests\test_dashboard_settings_ui.py`, 132 tests passing in 1.34 seconds with one third-party FastAPI/Starlette TestClient deprecation warning and one existing `httpx` raw-content deprecation warning.
- Full automated suite: `.\.venv\Scripts\python.exe -m pytest -q`, 396 tests passing in 6.62 seconds with the same two third-party deprecation warnings and no skipped tests.
- Python syntax validation for the changed source and tests with `py_compile`, passing.
- Rendered dashboard JavaScript syntax validation with `node --check`, passing.
- Headless Microsoft Edge engineering smoke validation exercised native reset controls, cancellation, a four-setting Context category reset, runtime/default/persisted presentation, three-setting Discard recovery, unchanged YAML, and zero observed JavaScript errors. A follow-up aligned-state smoke check verified truthful no-save-needed feedback, disabled configuration Save, and programmatic focus recovery after the initiating reset button rerendered.
- Product Owner and architect review remain the acceptance checkpoint; this phase is not committed, merged, pushed, or released by this working-tree implementation.

### Phase 6.5F-B6.6: Connection Configuration

Status: Implemented in the working tree; Product Owner and architect review pending.

Date: 2026-07-23.

Objective:

- Add a Connection category to the existing Settings page for ContextKeeper's single Ollama backend.
- Expose AI Server Endpoint (`ollama.base_url`) and Request Timeout (`ollama.timeout_seconds`) through the existing authoritative snapshot, persistence, reset, discard, and validation architecture.
- Test the current browser draft through one bounded isolated Ollama version probe and report normalized endpoint, latency, version, or a safe failure category.
- Keep Connection settings restart-required and protect the active runtime Settings, Ollama HTTP client, proxy/streaming requests, health/version, metrics, diagnostics, and model-discovery state.

Configuration model and validation:

- Replaced the former prefix-only Ollama URL check with standards-based `urllib.parse.urlsplit` validation and normalization shared by startup, persistence, and candidate testing.
- Accepted complete HTTP/HTTPS URLs using ordinary hostnames, IPv4, and bracketed IPv6 syntax, with optional valid ports and base paths.
- Preserved a configured base path, trimmed surrounding whitespace, removed unnecessary trailing slashes, normalized scheme/host/IP representation, and rejected empty/relative URLs, remaining whitespace/control characters, unsupported schemes, malformed hosts/IPs/ports, embedded credentials, query strings, and fragments.
- Added narrow deterministic self-proxy-loop detection for root, `/api`, and `/v1` endpoints whose normalized listener/localhost/loopback alias and effective port directly match ContextKeeper's configured listener. IPv4 wildcard listeners cover the deterministic loopback range and IPv4-mapped IPv6 forms. No DNS lookup or speculative remote-host rejection was added, and unrelated non-root base paths are not treated as obvious loops.
- Kept `ollama.timeout_seconds` authoritative default `120`, strict integer typing, minimum `1`, and no product-level maximum. Booleans, floats, strings, zero, and negative values are rejected.

Settings metadata, persistence, reset, and discard:

- Added one `ollama` category displayed as Connection before Context, Compression, and Dashboard in the schema-v2 snapshot.
- Added `ollama.base_url` and `ollama.timeout_seconds` with active runtime `value`, freshly read `persisted_value`, built-in `default_value`, typed constraints, and accurate difference state.
- Marked both fields `persistable: true`, `runtime_editable: false`, `restart_required: true`, and `reset_eligible: true`.
- Added only those two fields to the existing managed persistence allowlist. PUT continues to re-read and validate the complete candidate, preserve unknown/unmanaged YAML, verify a same-directory temporary file, detect stale source changes, and atomically replace the destination.
- Saving Connection values changes only YAML. It does not mutate canonical runtime settings, replace the active client, affect active requests/streams, or restart ContextKeeper. A successful reachability test is not required before Save.
- Connection individual/category reset stages authoritative defaults in the browser draft and sends no PATCH. A mixed global reset PATCHes only runtime-editable values and retains the Connection defaults as persistence-only drafts.
- Connection-only Discard is local and sends no PATCH. Discard recovery continues to PATCH only runtime-editable values whose active and persisted values differ.
- Preserved configuration precedence: `CONTEXTKEEPER_OLLAMA_URL` can override the YAML endpoint. The snapshot distinguishes active and persisted values but does not track source provenance or imply that saving YAML overrides the environment.

Isolated Test Connection:

- Added `src/ctxkeeper/dashboard/connection_test.py` as a focused candidate-validation/probe service and `POST /api/dashboard/settings/connection/test` on the existing dashboard management router.
- The request body is exactly `{base_url, timeout_seconds}` and uses strict models plus the shared endpoint/timeout and listener-loop validation.
- Valid requests create one temporary `httpx.AsyncClient` with `trust_env=False`, redirects disabled, normal TLS verification, and timeout `min(timeout_seconds, 10)`.
- The service performs exactly one GET to the normalized base-path-preserving `/api/version` URL and closes the client on success or failure. Existing Automatic Model Context Discovery retry/backoff remains separate; the candidate test never retries.
- HTTP `200` represents every validated probe outcome, successful or failed, with `connected`, `tested_endpoint`, `latency_ms`, `ollama_version`, `failure_category`, and a user-readable `message`.
- HTTP `422` represents invalid endpoint, timeout, or request values with the same safe result fields plus field-associated `detail`. GET, PUT, PATCH, DELETE, HEAD, and OPTIONS return explicit `405` with `Allow: POST`.
- Failure categories cover DNS resolution, connection refusal, timeout, TLS/certificate failure, HTTP error, malformed/non-Ollama response, missing/invalid version, and other network errors without exposing stack traces or unsafe exception detail.
- The test changes no YAML, canonical runtime value, active client reference/endpoint, active dashboard Ollama health/version, metrics, diagnostics, discovery state, proxied request, or stream.

Settings UI:

- Added Connection to the metadata-driven Settings navigation/content with AI Server Endpoint, Request Timeout, active/saved/default/draft presentation, and explicit restart-required guidance.
- Test Connection submits the current typed draft, prevents duplicate concurrent requests with a busy/disabled state, and renders safe success/failure status, normalized tested endpoint, measured latency, Ollama version when available, and save/restart guidance.
- Editing either Connection draft clears the prior result so stale candidate evidence is not presented as current.
- Candidate results remain distinct from Operations active Ollama health/version. The UI states that testing did not save or activate the candidate and does not require success before Save.
- Existing responsive layout, accessible label/error association and focus recovery, native confirmations, reduced-motion behavior, single dashboard polling lifecycle, and B6.5 recovery protections remain in scope.

Tests added or updated:

- Expanded `tests/test_config.py` for endpoint formats/normalization, prohibited URL components, malformed syntax, narrow listener-loop validation, and strict positive timeout typing.
- Expanded `tests/test_dashboard_settings.py` for the Connection category, both fields' active/persisted/default values and metadata, runtime PATCH exclusion, explicit methods, and unchanged existing categories/settings.
- Added `tests/test_dashboard_connection.py` for request validation, normalized base-path probe URLs, bounded isolated client lifecycle, success/latency/version, failure categories, explicit methods, and protection of runtime/YAML/client/health/discovery state.
- Expanded `tests/test_config_persistence.py` for one/both Connection fields, allowlisted-only changes, unmanaged YAML preservation, invalid-candidate atomicity, runtime/client protection, restart loading, and environment precedence.
- Expanded `tests/test_dashboard_settings_ui.py` for Connection rendering/navigation, draft request payload, busy/duplicate guard, results/stale clearing, accessible validation, restart guidance, Save/Discard, persistence-only reset, mixed reset, and existing-category regression.
- Preserved the complete proxy, streaming, dashboard, model discovery, context, compression, persistence, logging, service, wizard, packaging, and controlled-shutdown regression suite.

Documentation updated:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/API_COMPATIBILITY.md`
- `docs/DASHBOARD_LAYOUT.md`
- `docs/UI_COMPONENT_GUIDE.md`
- `docs/TEST_PLAN.md`
- `docs/ROADMAP.md`
- `docs/ContextKeeper_Project_Plan.md`
- `docs/PROJECT_HISTORY.md`

Limitations and boundaries:

- No runtime backend switching, active-client replacement, atomic live rollback, automatic/service restart, authentication, credentials, multiple servers/profiles, failover, load balancing, cloud providers, TLS trust/bypass controls, listener editing, retry settings, background monitoring, periodic testing, Connection model listing, self-diagnostics, recovery system, or environment/command-line editing was added.
- HTTPS uses normal client certificate verification. Saving a valid but unreachable endpoint remains allowed.
- Candidate self-loop protection covers safely detectable direct root and proxy-namespace references only; it deliberately does not use DNS to infer remote aliases.
- The settings snapshot does not expose configuration-source provenance.

Validation:

- Focused B6.6 automated result: 300 tests passed with two existing third-party deprecation warnings.
- Full B6.6 automated result: 552 tests passed with the same two warnings.
- Product Owner visual and interaction QA remains the acceptance checkpoint; this phase is not committed, merged, pushed, or released by this working-tree implementation.

### Phase 6.5G — Historical Memory Retrieval & Detail Preservation (Approved Plan)

Status: Planned; approved for the roadmap, not implemented.

Planning record:

- Product Owner approved Phase 6.5G before the Validation Framework, GitHub release, and Version 1.0 release.
- Reason: users should be able to use ContextKeeper throughout the day without manually restarting conversations or losing important details after compression.
- Product direction was clarified so Version 1 historical compression must not permanently lose underlying details.
- Approved Version 1 product principle: "Compress active context without forgetting important information."
- Compression is not deletion. Rolling summaries reduce the amount of text sent to the model on every request, while original historical messages should remain durably available after they leave the active prompt.
- Historical retrieval and active context compression are complementary systems. Active context management keeps prompts efficient; historical retrieval restores specific older details when needed.
- ContextKeeper should be capable of retrieving relevant archived details when a later request depends on them.
- ContextKeeper-controlled retrieval should be the default Version 1 design.
- Version 1 should not require the selected model to support tool calling for basic historical retrieval.
- A future model-invoked history-search tool may be considered later, but Version 1 should not depend upon it.
- The goal is strong, testable detail preservation and retrieval, not perfect or infallible memory.
- Phase 6.5G should be an integrated ContextKeeper capability, including dashboard visibility and user controls where appropriate, not a separate user-facing application.

Approved roadmap sequence:

- Phase 6.5F-B5 — Live Data Visualization & Rich Widgets.
  - Phase 6.5F-B5.1 — Live Visualization Foundation complete.
  - Phase 6.5F-B5.2 — Live Request Traffic Visualization complete.
  - Phase 6.5F-B5.3 — Live Connection Flow Animation implemented in the current branch baseline.
  - Phase 6.5F-B5.4 — Live Conversation Timeline QA review.
  - Later B5 rich widget implementation based on the B5.1 audit, B5.2 request-traffic visualization, B5.3 connection-flow animation, and B5.4 live timeline.
- Phase 6.5F-B6 — Dashboard Customization & User Preferences.
- Phase 6.5F-B7 — Release Polish & Final UX Review.
- Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
- Phase 6.6 — Validation Framework & Release Certification.
- Phase 7 — GitHub Release.
- Version 1.0 Release.

Tentative sub-phases:

- Phase 6.5G.1 — Durable Conversation Archive.
- Phase 6.5G.2 — Historical Search & Ranking.
- Phase 6.5G.3 — Retrieval-Aware Prompt Injection.
- Phase 6.5G.4 — Fact Preservation & Importance Controls.
- Phase 6.5G.5 — Memory Dashboard & User Controls.
- Phase 6.5G.6 — Privacy, Retention & Recovery.

Planned scope summary:

- Preserve original messages after active-context compression.
- Store durable message history with order, role, timestamps, model, conversation identity, and relevant metadata.
- Keep clear boundaries between active messages, rolling summaries, and archived originals.
- Search and rank archived conversation history with conversation-scoped retrieval, duplicate suppression, relevance ranking, deterministic fallback behavior, and strict prevention of cross-conversation leakage.
- Inject a limited set of relevant archived excerpts into outgoing requests when useful, while preserving Ollama-compatible behavior and avoiding unnecessary context pressure.
- Support important-fact detection or tagging, pinned facts, retention-priority metadata, user-approved corrections, and protection against fact mutation across repeated summaries.
- Provide dashboard visibility and user controls for historical memory, retrieval status, retained facts, summaries, original archived messages, export, correction, deletion, and retrieval limits where practical.
- Support privacy, retention, recovery, storage limits, corruption handling, local-only storage by default, and clear user control over what is retained.

Multi-user preparation:

- Multi-user support is a potential Version 2 capability, not a Version 1 implementation requirement.
- Approved architectural preparation principle: "Every persistent ContextKeeper object should have an owner, even when Version 1 uses only one default owner."
- Ownership may later support a hierarchy such as tenant or organization, user or owner, workspace, and conversation.
- Version 1 may use a single implicit default owner and does not need to expose authentication, user accounts, permissions, organizations, or shared workspaces.
- Version 1 architecture should avoid storage decisions that make later user and workspace isolation unnecessarily difficult.
- Historical-memory design should prepare for future ownership and isolation without expanding Version 1 into a full multi-user product.

AutoQA certification relationship:

- Phase 6.6 must validate Phase 6.5G.
- AutoQA should eventually test known fact injection early in a conversation, context-window filling, warning-threshold activation, compression-threshold activation, one or more rolling compression cycles, preservation of original archived messages, historical retrieval after compression, exact recall of identifiers, names, dates, decisions, and restrictions, semantic recall of meaning, missing facts, mutated facts, invented facts, continued conversation coherence, retrieval-budget behavior, duplicate suppression, conversation isolation, and restart/recovery behavior.
- Deterministic test scenarios and known injected facts must remain authoritative for release certification.
- A local LLM may generate realistic simulated-user conversations, produce exploratory variations, and assist with semantic evaluation.
- Release certification must not depend solely on subjective LLM judgment. Objective telemetry, known facts, stored source messages, event records, request results, and deterministic assertions must remain authoritative.

Scope boundary:

- This entry does not claim durable conversation archiving, historical search, retrieval-aware prompt injection, memory dashboard controls, privacy controls, AutoQA validation of historical memory, or multi-user ownership behavior already exists.

### Phase 6.6 — Validation Framework & Release Certification (Approved Plan)

Status: Planned; approved for the roadmap, not implemented.

Planning record:

- Product Owner approved a dedicated Phase 6.6 after Phase 6.5G, before GitHub release, and before Version 1.0 release.
- Reason: eliminate hours of manual chat entry needed to fill a model's context window and provide evidence that ContextKeeper preserves conversation quality through repeated compression cycles.
- Phase 6.6 is intended to automate long-conversation, compression, memory-retention, historical-retrieval, stress, soak, recovery, and release-certification testing.
- Phase 6.6 must validate Phase 6.5G historical memory retrieval and detail preservation.
- Approved roadmap sequence:
  - Phase 6.5F-B5 — Live Data Visualization & Rich Widgets.
  - Phase 6.5F-B6 — Dashboard Customization & User Preferences.
  - Phase 6.5F-B7 — Release Polish & Final UX Review.
  - Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
  - Phase 6.6 — Validation Framework & Release Certification.
  - Phase 7 — GitHub Release.
  - Version 1.0 Release.
- Validation will be built as a first-class modular subsystem and dashboard plugin inside ContextKeeper, not as a separate user-facing application.
- The approved future left-navigation label is `Validation`. `AutoQA` is a capability inside the broader Validation area, not the navigation label.
- The planned Validation page structure is: Dashboard, Scenarios, AutoQA, Stress Tests, Reports, History, and Settings. This is planning guidance and may be refined during implementation.
- The planned dashboard navigation may eventually include Overview, Operations, Diagnostics, Conversations, Compression, Models, Validation, and Settings. This is an approved plan only and is not implemented by this documentation branch.

Planned sub-phases:

- Phase 6.6.1 — Validation Engine Foundation.
- Phase 6.6.2 — AutoQA Conversation Engine.
- Phase 6.6.3 — Memory & Compression Validation.
- Phase 6.6.4 — Stress, Soak & Reliability Testing.
- Phase 6.6.5 — Validation Dashboard Plugin.
- Phase 6.6.6 — Reports & Release Certification.

Architecture direction:

- The planned module may eventually resemble `src/ctxkeeper/validation/` with `engine.py`, `runner.py`, `scenarios.py`, `generator.py`, `injector.py`, `verifier.py`, `evaluator.py`, `metrics.py`, and `reports.py`.
- This file list is architectural direction, not an implementation commitment, and may be refined later.
- The feature should use the existing ContextKeeper executable, installer, service, configuration system, logs, and dashboard.

Validation principles:

- “The Validation Engine should exercise ContextKeeper through its public Ollama-compatible APIs whenever practical. Internal interfaces should be used only for orchestration, metrics collection, controlled fault injection, and verification. This ensures AutoQA validates the same behavior experienced by AnythingLLM, Open WebUI, IDEs, Python clients, and other Ollama-compatible consumers.”
- Deterministic scripted tests should be preferred for repeatable release certification.
- Deterministic test scenarios and known injected facts must remain authoritative for release certification.
- LLM-generated conversations may supplement scripted tests for realism and exploratory coverage.
- A local LLM may generate realistic simulated-user conversations, produce exploratory variations, and assist with semantic evaluation.
- A local evaluator model may provide semantic scoring, but release certification must not depend solely on subjective LLM judgment.
- Objective telemetry, known injected facts, stored source messages, event records, request outcomes, and deterministic assertions must remain authoritative.
- The framework should support seeded runs so failures can be reproduced.
- Validation traffic must be clearly tagged or isolated so it is distinguishable from normal user conversations.
- Destructive or disruptive scenarios must require explicit user selection.
- Long-running AutoQA tests should be cancellable and must not block normal ContextKeeper shutdown.
- AutoQA should be disabled by default in production installations until a user starts a validation run.
- Sensitive prompts, secrets, and private documents must not be written into validation reports.
- The framework should be extensible later for model routing, workspace memory, plugins, agents, and multi-server orchestration.

Historical-memory validation scope:

- AutoQA should eventually test known fact injection early in a conversation, context-window filling, warning-threshold activation, compression-threshold activation, one or more rolling compression cycles, preservation of original archived messages, historical retrieval after compression, exact recall of identifiers, names, dates, decisions, and restrictions, semantic recall of meaning, detection of missing facts, detection of mutated facts, detection of invented facts, continued conversation coherence, retrieval-budget behavior, duplicate suppression, conversation isolation, and restart/recovery behavior.

Certification boundary:

- Phase 6.6 is an approved planned phase only. This entry does not claim Validation code, AutoQA scenarios, dashboard navigation changes, reports, tests, historical-memory certification, or release-certification evidence already exist.

### Version 2 Roadmap and Future Vision (Approved Plan)

Status: Planned; approved future direction, not implemented.

Planning record:

- Product direction was clarified so Version 1 remains focused on a production-quality release rather than absorbing every future idea.
- Ideas that are not required for Version 1.0 should be intentionally captured for later versions instead of expanding v1 unnecessarily.
- Adopted a three-document planning structure:
  - `docs/PROJECT_HISTORY.md` records what happened, what was approved, why decisions were made, and repository evidence for completed work.
  - `docs/ROADMAP.md` records approved planned work, including committed or formally approved phases and milestones.
  - `docs/FUTURE_IDEAS.md` records promising noncommitted concepts that should not be forgotten and may later be promoted, revised, deferred, combined, superseded, or rejected.
- Created `docs/FUTURE_IDEAS.md` as a curated idea parking lot for future architectural ideas. It is not a feature commitment.
- Version 1 direction now explicitly includes transparent Ollama-compatible proxy behavior, client-agnostic operation, diagnostics and operational visibility, context-window usage tracking, automatic model context-window discovery, authoritative context-window enforcement, rolling context summarization and compression, preservation of recent messages, durable preservation of original historical conversation details, historical detail retrieval after compression, automatic injection of relevant archived details when appropriate, live browser dashboard, Windows service, standalone executable, setup wizard, installer, Validation Framework, AutoQA, release certification, public documentation, GitHub release preparation, production stability, and release-quality documentation.
- Version 1 is intended to solve context-window limitations without permanently losing historical conversation details.
- Approved memory architecture principle: context compression should reduce active prompt size, compression should not permanently discard conversation history, historical information should remain searchable and retrievable, and ContextKeeper should retrieve relevant archived details automatically when appropriate.
- Approved goal statement: "Compress active context without forgetting important information."
- Version 2 direction includes multi-user architecture, authentication, user isolation, workspace isolation, multiple tenants or organizations, shared workspaces, roles and permissions, per-user configuration, per-user dashboards, auditability, cross-user data-leak prevention, workspace and project memory, validation extensions for isolation and security, intelligent routing, plugin platform capabilities, infrastructure expansion, agents and voice, and analytics/benchmarking.
- Exact Version 2 scope and sequencing remain tentative.

Architectural principles:

- Every persistent object should have an owner, even if Version 1 uses a single default owner.
- Compression is not deletion. Conversation history should remain available for retrieval.
- Active context and durable historical memory serve different purposes.
- Relevant historical details should be retrieved selectively rather than reloading an entire conversation.
- Validation should exercise public APIs whenever practical.
- Internal interfaces should be used for orchestration, controlled fault injection, metrics, and verification.
- Deterministic evidence must remain authoritative for release certification.
- LLM-based generation and judging may supplement, but not replace, objective validation.
- Future features should extend the architecture instead of replacing it.
- ContextKeeper should remain modular. New capabilities should become additional engines rather than expanding existing ones excessively.
- Client transparency and Ollama API compatibility remain core constraints.
- Sensitive prompts, credentials, private documents, and full conversation contents must not be exposed in routine logs or validation reports.

Scope boundary:

- This planning record does not move v2 work into v1.
- This planning record does not claim any multi-user, workspace-memory, routing, plugin, multi-server, voice, agent, analytics, or v2 validation functionality is implemented.

## Current Project State

- Current active implementation phase: Phase 6.5F-B6.6: Connection Configuration; Product Owner and architect review pending.
- Phase 6.5F-B4.8 — Automatic Model Context Discovery is implemented.
- Phase 6.5F-B5.1 through the B6.6 working tree are represented in source, tests, and maintained documentation.
- Latest focused B6.6 Settings/Connection validation result: 300 tests passed with two existing third-party deprecation warnings.
- Latest full B6.6 automated validation result: 552 tests passed with the same two warnings.
- Dashboard status: modern operations-console dashboard with live proxy, Ollama, request, context, compression, conversation, intelligence, health, operational activity, recommendations, grouped five-card system instrument panel, Context Trend, Request Traffic, animated Connection Flow, Live Conversation Timeline, Conversation Inspector drawer, Conversation Inspector Overview, deterministic Conversation Inspector Intelligence, and an interactive metadata-driven runtime-versus-persisted Settings page with managed-default reset/recovery controls plus restart-required Ollama Connection configuration and isolated candidate testing.
- Major capabilities currently present:
  - FastAPI-based transparent Ollama proxy.
  - `/api/*` and `/v1/*` passthrough with streaming preservation for supported endpoints.
  - Request diagnostics and system metrics.
  - Conversation store, context meter, context monitor, and compression candidates.
  - Compression manager, compression planning, rolling-summary support, and confirmed compression metadata.
  - Automatic Model Context Discovery and context-window enforcement.
  - Browser dashboard with live monitoring and intelligence.
  - Dashboard schema-v2 Settings snapshot, read API, validated in-memory runtime update API, explicit atomic configuration-persistence API, authoritative reset eligibility, and interactive Settings UI for approved Connection, Context, Compression, and Dashboard settings.
  - Isolated one-attempt candidate Ollama Connection testing with normalized endpoint, measured latency, version, safe failures, and no active-state mutation.
  - Windows service foundation, PyInstaller executable foundation, first-run setup wizard, Inno Setup installer foundation, and release build script.
- Planned work still ahead:
  - Product Owner and architect review for Phase 6.5F-B6.6.
  - Later broader dashboard preference work after explicit approval.
  - Phase 6.5F-B7 — Release Polish & Final UX Review.
  - Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
  - Phase 6.6 — Validation Framework & Release Certification.
  - Phase 7 — GitHub Release.
  - Version 1.0 Release.
  - Version 2+ architectural ideas tracked in `docs/FUTURE_IDEAS.md`, intentionally outside the Version 1.0 release scope.

Do not treat remaining planned Phase 6.5F-B6/B7, Phase 6.5G, Phase 6.6, Phase 7, or Version 2+ roadmap content as implemented until source and tests confirm that state.

## Planned Next Steps

This section is tentative and subject to refinement. These names and boundaries are planning labels, not completed commitments.

- Phase 6.5F-B5 — Live Data Visualization & Rich Widgets.
- Phase 6.5F-B6 — Dashboard Customization & User Preferences.
  - Product Owner and architect review for Phase 6.5F-B6.6: Connection Configuration.
  - Later broader dashboard preference work after explicit approval.
- Phase 6.5F-B7 — Release Polish & Final UX Review.
- Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
  - Phase 6.5G.1 — Durable Conversation Archive.
  - Phase 6.5G.2 — Historical Search & Ranking.
  - Phase 6.5G.3 — Retrieval-Aware Prompt Injection.
  - Phase 6.5G.4 — Fact Preservation & Importance Controls.
  - Phase 6.5G.5 — Memory Dashboard & User Controls.
  - Phase 6.5G.6 — Privacy, Retention & Recovery.
- Phase 6.6 — Validation Framework & Release Certification.
  - Phase 6.6.1 — Validation Engine Foundation.
  - Phase 6.6.2 — AutoQA Conversation Engine.
  - Phase 6.6.3 — Memory & Compression Validation.
  - Phase 6.6.4 — Stress, Soak & Reliability Testing.
  - Phase 6.6.5 — Validation Dashboard Plugin.
  - Phase 6.6.6 — Reports & Release Certification.
- Phase 7 — GitHub Release.
- Version 1.0 Release.
- Post-v1: use `docs/FUTURE_IDEAS.md` to guide Version 2+ architectural planning without expanding the Version 1.0 release scope.

Likely Phase 7 work areas:

- Public documentation.
- Examples.
- Release packaging.
- Release notes.
- GitHub release preparation.
- Community feedback readiness.

## Lessons Learned

### Responsive Dashboard Architecture

Viewport-fit and overflow behavior became tightly coupled during UI modernization. Broad layout changes caused clipping or scrolling regressions at some browser zoom levels.

Later visual polish should prefer paint-only changes such as border, background, opacity, shadow, and restrained transforms. Protected responsive, grid, sizing, and overflow rules should not be changed without a demonstrated layout defect.

Manual checks at 50%, 75%, and 100% browser zoom proved useful for catching regressions that automated tests do not cover.

### Incremental UI Delivery

Risky visual work is safer when split into audit, implementation, automated validation, and manual screenshot review. Small passes make regressions easier to isolate.

Uncommitted work should not be described as merged or released.

### Repository Evidence

Git history and current repository contents should take precedence over memory or older roadmap files.

Planned phase names must remain clearly separated from completed work.

## Longer-Term Direction

These ideas are repository-supported post-v1 directions, not current v1 commitments. The detailed planning record is `docs/FUTURE_IDEAS.md`.

Version 1 philosophy:

- Deliver a production-quality Version 1.0 release before expanding scope.
- Preserve the architecture needed to compress active context without forgetting important information.
- Keep historical conversation details searchable and retrievable after compression.

Version 2+ planning areas:

- Multi-user and security: authentication, ownership, user isolation, workspace isolation, tenants or organizations, shared workspaces, roles and permissions, per-user configuration, per-user dashboards, auditability, and cross-user data-leak prevention.
- Workspace and project memory: cross-conversation workspace memory, persistent project knowledge, workspace-level retrieval, authorized shared knowledge, pinned memories, prioritization, expiration and archival policies, improved semantic retrieval, source attribution, and provenance.
- Validation extensions: multi-user AutoQA, workspace-isolation tests, permission tests, authentication tests, cross-user leakage tests, shared-workspace tests, and tenant-isolation certification.
- Intelligent routing: automatic model routing, capability-aware model selection, context-window-aware routing, model-performance benchmarking, resource-aware routing, cost and latency optimization, and local-server availability awareness.
- Plugin platform: plugin SDK, third-party integrations, custom validation scenarios, custom dashboard widgets, custom memory providers, custom routing policies, and controlled plugin permissions and isolation.
- Infrastructure: multi-server support, load balancing, distributed ContextKeeper nodes, failover, remote execution, server health, and capability discovery.
- Agents and voice: agent orchestration, autonomous workflows, voice-first interaction, Jarvis-style assistant integration, voice and visual input integrations, and coordination of specialized local agents.
- Analytics and benchmarking: advanced model benchmarks, long-term usage analytics, model comparisons, historical performance trends, context-compression effectiveness metrics, memory-retrieval effectiveness metrics, and validation trend reporting.

Architectural principles:

- Every persistent object should have an owner, even if Version 1 uses a single default owner.
- Compression is not deletion.
- Active context and durable historical memory serve different purposes.
- Relevant historical details should be retrieved selectively rather than reloading an entire conversation.
- Validation should exercise public APIs whenever practical.
- Deterministic evidence must remain authoritative for release certification.
- LLM-based generation and judging may supplement, but not replace, objective validation.
- Future features should extend the architecture instead of replacing it.
- ContextKeeper should remain modular; new capabilities should become additional engines rather than expanding existing ones excessively.
- Client transparency and Ollama API compatibility remain core constraints.

## Maintenance Rules

1. Update this document whenever a phase, sub-phase, milestone, or planned next step is added, renamed, completed, merged, superseded, or materially changed.
2. Update it when a major feature branch is created or merged.
3. Update the Table of Contents and Major Milestones summary when major sections or project states change.
4. Record validation evidence, such as test counts and manual acceptance checks, when a phase is completed.
5. Keep completed history separate from tentative planning.
6. Never rewrite earlier history merely to match a newer roadmap.
7. Prefer Git history and repository evidence over conversational memory.
8. Do not include sensitive information, private prompts, credentials, or full chat transcripts.
9. Keep entries concise enough that the file remains useful as an index.

## Status Legend

- Completed: Work is implemented and supported by repository evidence or recorded validation.
- Active: Work is currently underway and should not be treated as complete.
- Planned: Work is proposed or expected but not yet completed.
- Superseded: Work was replaced, renamed, or materially changed by a later phase or decision.
