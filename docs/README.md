# ContextKeeper Documentation

Status: Current through the Phase 6.5F-B6.6 working-tree implementation; Product Owner and architect review are pending.

ContextKeeper is a local Ollama-compatible middleware layer with diagnostics, Context Usage tracking, compression support, Automatic Model Context Discovery, and a live operations dashboard with separate runtime Settings updates, managed-default reset controls, explicit configuration persistence, and restart-required Ollama Connection configuration with an isolated candidate test.

Use the current implementation as the source of truth. Older planning and mockup documents are retained because they preserve product reasoning, but they do not override source behavior.

## Primary current documents

- [README](../README.md) — project landing page, quick start, current status, and limitations.
- [Architecture](ARCHITECTURE.md) — current runtime and dashboard architecture.
- [Configuration](CONFIGURATION.md) — source-verified defaults, overrides, thresholds, and model context discovery.
- [API Compatibility](API_COMPATIBILITY.md) — Ollama-compatible proxy behavior and API boundaries.
- [Roadmap](ROADMAP.md) — completed work, current milestone, upcoming phases, and future roadmap.
- [Project History](PROJECT_HISTORY.md) — phase-by-phase implementation record.
- [Test Plan](TEST_PLAN.md) — automated, manual, visual QA, and regression coverage.
- [Conversation Inspector](CONVERSATION_INSPECTOR.md) — current inspector interaction model and planned sub-phases.

## Dashboard and design references

- [Dashboard Layout](DASHBOARD_LAYOUT.md)
- [Dashboard Visualization Audit](DASHBOARD_VISUALIZATION_AUDIT.md)
- [Live Flow Visualization](LIVE_FLOW_VISUALIZATION.md)
- [Design System](DESIGN_SYSTEM.md)
- [Design Language](DESIGN_LANGUAGE.md)
- [Color System](COLOR_SYSTEM.md)
- [Typography](TYPOGRAPHY.md)
- [UI Style Guide](UI_STYLE_GUIDE.md)
- [UI Component Guide](UI_COMPONENT_GUIDE.md)
- [Component Library](COMPONENT_LIBRARY.md)
- [Animation Guidelines](ANIMATION_GUIDELINES.md)

## Planning and historical references

- [Original Project Plan](ContextKeeper_Project_Plan.md)
- [Dashboard Mockup Plan](DASHBOARD_MOCKUP_PLAN.md)
- [Dashboard Mockups](DASHBOARD_MOCKUPS.md)
- [Future Ideas](FUTURE_IDEAS.md)

## Maintained Markdown inventory

| Document | Classification | Notes |
| --- | --- | --- |
| `README.md` | Current | Modern project landing page synchronized through B6.6. |
| `docs/README.md` | Current | Documentation index and audit inventory. |
| `docs/ARCHITECTURE.md` | Current | Runtime/dashboard/settings/reset/persistence and isolated Connection-test architecture source-aligned through B6.6. |
| `docs/API_COMPATIBILITY.md` | Current | Ollama compatibility, request-observation, and local dashboard-management boundaries through B6.6. |
| `docs/CONFIGURATION.md` | Current | Source-verified defaults, overrides, Connection validation/testing, GET/PATCH/PUT/POST Settings behavior, reset/recovery controls, atomic persistence, and precedence. |
| `docs/TEST_PLAN.md` | Current | Automated/manual/visual/regression validation plan including Connection configuration/testing, Settings reset/recovery, configuration persistence, and UI integration. |
| `docs/ROADMAP.md` | Current | Active roadmap synchronized through B6.6. |
| `docs/PROJECT_HISTORY.md` | Current | Phase record through B6.6. |
| `docs/CONVERSATION_INSPECTOR.md` | Current | Current inspector contract and deferred detail phases. |
| `docs/DASHBOARD_LAYOUT.md` | Current | Current Operations and runtime-versus-persisted Settings layout, Connection result state, reset controls, and visual hierarchy. |
| `docs/DASHBOARD_VISUALIZATION_AUDIT.md` | Historical | B5.1 audit retained with current-state addendum; not a live contract for every widget. |
| `docs/LIVE_FLOW_VISUALIZATION.md` | Current | Connection Flow behavior updated from placeholder to implemented animation. |
| `docs/ANIMATION_GUIDELINES.md` | Current | Motion/reduced-motion guidance remains applicable. |
| `docs/COLOR_SYSTEM.md` | Current | Semantic color guidance remains applicable. |
| `docs/COMPONENT_LIBRARY.md` | Current | Dashboard component guidance, including timeline/inspector components. |
| `docs/DESIGN_SYSTEM.md` | Current | Visual foundation remains applicable. |
| `docs/DESIGN_LANGUAGE.md` | Current | Product design principles remain applicable. |
| `docs/TYPOGRAPHY.md` | Current | Typography guidance remains applicable. |
| `docs/UI_COMPONENT_GUIDE.md` | Current | Compact dashboard and metadata-driven runtime/reset/configuration/Connection-test Settings component guidance. |
| `docs/UI_STYLE_GUIDE.md` | Current | Spacing, radius, elevation, and icon guidance. |
| `docs/CODING_STANDARDS.md` | Current | Engineering standards; dashboard decision updated from pending to browser dashboard. |
| `docs/FUTURE_IDEAS.md` | Current | Future-ideas parking lot, not v1 commitment. |
| `docs/ContextKeeper_Project_Plan.md` | Historical | Original project plan with a current B6.6 preface retained for origin context; roadmap/history are authoritative now. |
| `docs/DASHBOARD_MOCKUP_PLAN.md` | Superseded | Pre-implementation mockup direction retained as design history. |
| `docs/DASHBOARD_MOCKUPS.md` | Superseded | Text mockups retained as historical visual planning reference. |
| `installer/README.md` | Current | Installer build notes and current service-hook limitation. |

No Markdown file was deleted during the B5.6 audit.
