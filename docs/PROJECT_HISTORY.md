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
| Dashboard modernization | Active | Current branch is `phase-6-5f-b4-2-dashboard-micro-interactions`; B4.2 is completed and B4 remains active. |
| GitHub release preparation | Planned | Tentative Phase 7 work area. |
| Version 1.0 release | Planned | Planned release target, not yet completed. |

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

Status: Active

Goal: Apply final visual polish and restrained micro-interactions without destabilizing the responsive dashboard architecture.

Current workstream:

- Branch: `phase-6-5f-b4-2-dashboard-micro-interactions`.
- Base commit: `e0228ff` (`Recover responsive dashboard layout architecture`).
- Overall B4 is not complete yet.

#### Phase 6.5F-B4.1 — Core Surface and Status Polish

Status: Completed within the active B4 workstream

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

- Current branch: `phase-6-5f-b4-2-dashboard-micro-interactions`.
- Current working tree evidence at the time this history was updated: focused CSS and vanilla JavaScript changes in `src/ctxkeeper/dashboard/template.py`, dashboard active-model and model-warm-up health interpretation changes in `src/ctxkeeper/dashboard/routes.py`, focused tests in `tests/test_app.py`, plus this history update.
- This B4.2 work was not yet represented by a committed Git revision at the time this document was updated.

## Current Project State

- Current active branch: `phase-6-5f-b4-2-dashboard-micro-interactions`.
- Current active phase: Phase 6.5F-B4 — Dashboard Visual Polish & Micro-Interactions.
- Latest verified automated test count: 122 tests passing during the B4.2 health-state acceptance-fix pass.
- Dashboard status: modern operations-console dashboard with live proxy, Ollama, request, context, compression, conversation, intelligence, health, trend, recommendation, timeline, resource surfaces, and restrained micro-interaction polish.
- Major capabilities currently present:
  - FastAPI-based transparent Ollama proxy.
  - `/api/*` and `/v1/*` passthrough with streaming preservation for supported endpoints.
  - Request diagnostics and system metrics.
  - Conversation store, context meter, context monitor, and compression candidates.
  - Summarizer-backed automatic rolling context compression.
  - Browser dashboard with live monitoring and intelligence.
  - Windows service foundation, PyInstaller executable foundation, first-run setup wizard, Inno Setup installer foundation, and release build script.
- Work still underway:
  - Overall Phase 6.5F-B4 visual polish and micro-interaction workstream.
  - Phase 6.5F-B4.3 live motion refinement remains the next planned B4 pass.
  - Later rich dashboard widgets, customization, release polish, and public release preparation.

Do not treat uncommitted active-branch work as merged, released, or available on `main` unless Git history later confirms that state.

## Planned Next Steps

This section is tentative and subject to refinement. These names and boundaries are planning labels, not completed commitments.

- Phase 6.5F-B4.3 — Live Motion Refinement.
- Phase 6.5F-B4.4 — Final UX Polish & Consistency Review.
- Phase 6.5F-B5 — Live Data Visualization & Rich Widgets.
- Phase 6.5F-B6 — Dashboard Customization & User Preferences.
- Phase 6.5F-B7 — Release Polish & Final UX Review.
- Phase 7 — GitHub Release.
- Version 1.0 Release.

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

These ideas are repository-supported post-v1 directions, not current v1 commitments:

- Improved token estimation.
- Automatic model routing.
- Project or workspace memory.
- Plugin architecture.
- Multi-server support.
- Orchestration and load balancing.
- Agent integration.

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
