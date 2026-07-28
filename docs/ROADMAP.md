# ContextKeeper Roadmap

Status: Current through the Phase 6.5F-B7.1 automated engineering audit and remediation pass. Product Owner manual visual, responsive, keyboard, and accessibility approval remains pending.

This document records approved product direction. It is not a claim that planned work already exists. For completed implementation details, use [Project History](PROJECT_HISTORY.md).

## Version 1 product goal

ContextKeeper Version 1 is a production-quality local Ollama-compatible middleware tool that helps users sustain long-running AI work without losing operational visibility or context control.

Core goal:

> Compress active context without forgetting important information.

Version 1 must preserve:

- Ollama-compatible client behavior.
- Client-agnostic operation.
- Local-first execution.
- Dashboard observability.
- Context and compression transparency.
- Release-quality Windows packaging and documentation.

## Implemented foundation

Implemented work through the Phase 6.5F-B7.1 automated engineering review includes:

- Transparent Ollama-compatible proxy.
- `/api/*` and `/v1/*` passthrough.
- Streaming preservation for supported Ollama chat/generation endpoints.
- Request diagnostics and recent request history.
- Operational activity tracking.
- CPU, memory, and optional NVIDIA GPU telemetry.
- Conversation Snapshot and in-memory conversation tracking.
- Context Usage estimation.
- Warning and compression threshold detection.
- Compression engine support for rolling summaries and recent-message preservation.
- Automatic Model Context Discovery from Ollama `/api/show`.
- Authoritative context-window enforcement through `options.num_ctx`.
- Browser Operations dashboard.
- Dashboard intelligence, recommendations, Context Trend, and instrument panel.
- Request Traffic visualization.
- Animated Connection Flow.
- Live Conversation Timeline.
- Conversation Inspector foundation.
- Conversation Inspector Overview and deterministic Intelligence.
- Documentation audit and synchronization through B5.6.
- Dashboard Settings Snapshot plus read and validated in-memory update APIs on `/api/dashboard/settings`.
- Interactive metadata-driven Settings page with typed draft editing, changed-fields-only runtime Save, Discard, validation feedback, and explicit runtime-state guidance.
- Schema-v2 runtime-versus-persisted Settings metadata, explicit `PUT /api/dashboard/settings/config`, defensive atomic YAML persistence, and a separate Save to configuration UI action.
- Metadata-authorized individual, category, and global managed-settings reset controls that stage authoritative built-in defaults, using atomic runtime PATCH for runtime-editable fields, plus Discard recovery to persisted values.
- Restart-required Connection configuration for `ollama.base_url` and `ollama.timeout_seconds`, including strict endpoint/timeout validation, atomic YAML persistence, draft-only reset/discard behavior, and one isolated bounded candidate Test Connection probe with latency and Ollama version.
- Dashboard release-readiness audit coverage, seven focused regressions, and demonstrated fixes for document-title escaping, long-endpoint overflow, null telemetry, closed Inspector inertness, refresh-failure status, and unsaved-change unload protection.
- First-run configuration wizard.
- PyInstaller executable foundation.
- Windows service host foundation.
- Inno Setup installer foundation.

## Current milestone

### Phase 6.5F-B7.1: Dashboard Release Readiness Audit

Status: Automated engineering audit, focused remediation, documentation synchronization, and regression verification complete on the feature branch. Product Owner manual visual, responsive, keyboard, and accessibility approval remains pending.

Objective:

- Evaluate the complete Phase 6.5F dashboard against maintained design, accessibility, responsive-layout, state-handling, Settings-completion, and Version 1 release requirements.
- Produce a definitive capability inventory and evidence-based release-readiness audit.
- Add only focused regression coverage for important implemented behavior that was insufficiently protected.
- Remediate only demonstrated release-readiness defects without broad dashboard redesign or refactoring.

Automated engineering outcome:

- Baseline: 553 passing tests.
- Added: seven focused release-readiness regression tests.
- Final automated result: 560 passing tests.
- Remediated document-title escaping (Critical), long Connection endpoint workspace overflow (High), and null telemetry, closed Inspector inertness, visible refresh-failure status, and unsaved-change unload protection (Medium).
- Manual Product Owner review remains required; automated evidence does not constitute visual or accessibility acceptance.

## Completed Phase 6.5F-B5 live visualization workstream

Phase 6.5F-B5 expanded the dashboard from an operations-console foundation into a richer live visualization surface.

Completed B5 slices:

- B5.1 — Live Visualization Foundation and dashboard snapshot cleanup.
- B5.2 — Live Request Traffic Visualization.
- B5.3 — Live Connection Flow Animation.
- B5.4 — Live Conversation Timeline.
- B5.4.1 — Dashboard Layout Refinement: grouped instruments and activity widgets.
- B5.4.2 — Connection Flow Visibility Polish.
- B5.5.1 — Conversation Inspector Foundation.
- B5.5.1 polish — pre-merge visual polish for mutually exclusive states and hierarchy.
- B5.5.2 — Conversation Inspector Overview & Intelligence.
- B5.6 — Documentation Audit & Synchronization.

## Approved remaining Version 1 sequence

1. Phase 6.5F-B7.2 — disposition the open Medium narrow-Inspector focus-containment defect and only other accepted, narrowly scoped audit findings.
2. Phase 6.5F-B7.3 — complete Product Owner manual visual, responsive, keyboard, screen-reader, reduced-motion, contrast, and adverse-value review.
3. Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
4. Phase 6.6 — Validation Framework & Release Certification.
5. Phase 7 — GitHub Release Preparation.
6. Version 1.0 Release.

Phase 6.5G must occur before Phase 6.6 so the Validation Framework can certify historical memory retrieval and detail preservation.

## Phase 6.5F-B6 — Dashboard Customization & User Preferences

Status: Completed and merged through B6.6. B6.1 provides the Settings Snapshot/read foundation, B6.2 the validated in-memory update API, B6.3 the Settings panel UI foundation, B6.4 the configuration-persistence foundation, B6.5 the settings reset and recovery controls, and B6.6 the Connection configuration implementation.

Implemented B6 scope:

- Metadata-driven runtime Settings controls inside the existing dashboard shell.
- Separate confirmed/draft state, typed dirty detection, changed-fields-only atomic Save, Discard, and failure-preserving correction/retry.
- Explicit runtime-versus-persisted metadata and separate PATCH/runtime and PUT/configuration actions.
- Atomic same-directory YAML replacement with in-process serialization, best-effort stale-write detection, safe failures, and no runtime mutation or restart side effect.
- Authoritative reset eligibility and built-in defaults, immediate individual reset, confirmed category/global reset, and persisted-value Discard recovery, with PATCH limited to runtime-editable values.
- Persistence-only Connection settings with explicit restart metadata, draft testing through an isolated one-attempt probe, and no live active-client replacement.
- Preserve existing Operations dashboard behavior.
- Avoid destabilizing B5 live widgets.
- Keep preferences local and understandable.

Broader preferences were not part of the completed B6 scope. They remain intentionally deferred and require explicit Product Owner approval; authentication and multi-user ownership remain outside the current Version 1 implementation.

## Phase 6.5F-B7 — Release Polish & Final UX Review

Status: Active. B7.1 automated engineering review is complete; Product Owner manual approval remains pending.

Current scope:

- Final dashboard UX review before release certification.
- Visual consistency cleanup.
- Accessibility and reduced-motion review.
- Release-blocking documentation, packaging, and usability polish.
- Evidence-based capability, state, Settings, responsive, terminology, and documentation audit.
- Narrow remediation of demonstrated release-readiness defects with focused regression coverage.

## Phase 6.5G — Historical Memory Retrieval & Detail Preservation

Status: Planned. No durable historical-memory retrieval implementation exists yet.

Objective:

- Preserve original conversation details after active-context compression.
- Retrieve relevant archived details when later requests depend on them.
- Keep active prompts efficient without permanently forgetting important information.

Approved architecture:

- Historical memory retrieval is integrated into ContextKeeper, not a separate user-facing app.
- ContextKeeper-controlled retrieval is the default Version 1 design.
- Version 1 retrieval should not require the selected model to support tool calling.
- Active context management and historical retrieval are complementary systems.
- Retrieval should selectively restore relevant details rather than reload an entire conversation.
- Client transparency and Ollama API compatibility remain required.

Tentative sub-phases:

- 6.5G.1 — Durable Conversation Archive.
- 6.5G.2 — Historical Search & Ranking.
- 6.5G.3 — Retrieval-Aware Prompt Injection.
- 6.5G.4 — Fact Preservation & Importance Controls.
- 6.5G.5 — Memory Dashboard & User Controls.
- 6.5G.6 — Privacy, Retention & Recovery.

## Phase 6.6 — Validation Framework & Release Certification

Status: Planned. No Validation or AutoQA implementation exists yet.

Objective:

- Automate long-conversation, compression, historical-memory, stress, soak, recovery, and release-certification testing.
- Reduce manual typing needed to fill model context windows.
- Produce repeatable evidence for Version 1 release readiness.

Approved direction:

- Validation is a first-class ContextKeeper subsystem and dashboard area.
- `AutoQA` is one capability inside the broader Validation area.
- Validation should exercise ContextKeeper through public Ollama-compatible APIs whenever practical.
- Deterministic assertions and known facts remain authoritative.
- LLM-generated simulated users or evaluator models may supplement but not replace objective checks.

Tentative sub-phases:

- 6.6.1 — Validation Engine Foundation.
- 6.6.2 — AutoQA Conversation Engine.
- 6.6.3 — Memory & Compression Validation.
- 6.6.4 — Stress, Soak & Reliability Testing.
- 6.6.5 — Validation Dashboard Plugin.
- 6.6.6 — Reports & Release Certification.

## Phase 7 — GitHub Release Preparation

Status: Planned.

Planned scope:

- Public documentation.
- Examples.
- Release packaging.
- Release notes.
- GitHub release artifacts.
- Community feedback readiness.

## Version 1.0 Release

Status: Planned.

Release expectations:

- Core proxy compatibility verified.
- Dashboard behavior visually accepted.
- Historical memory retrieval and validation certification implemented and tested.
- Windows executable and installer release path validated.
- Documentation synchronized with implementation.
- Known limitations clearly documented.

## Version 2+ direction

Status: Future planning, not Version 1 commitment.

Long-term ideas are preserved in [Future Ideas](FUTURE_IDEAS.md). Potential areas include:

- Multi-user architecture and authentication.
- Workspace and project memory.
- User/workspace isolation.
- Model routing.
- Plugin architecture.
- Multi-server and cloud-provider orchestration.
- Agents and voice interfaces.
- Advanced analytics and benchmarking.
- Custom dashboard widgets.

Promotion rule:

- Future ideas should be promoted into the roadmap only when the Product Owner approves them as planned work.

## Roadmap guardrails

- Do not expand Version 1 by silently absorbing v2 ideas.
- Do not treat roadmap items as implemented until source and tests prove it.
- Preserve ContextKeeper terminology:
  - ContextKeeper
  - Conversation Inspector
  - Conversation Snapshot
  - Automatic Model Context Discovery
  - Context Usage
  - Compression
  - Connection Flow
  - Request Traffic
- Preserve Ollama API compatibility across implementation phases.
