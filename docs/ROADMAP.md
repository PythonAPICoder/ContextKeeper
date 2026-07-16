# ContextKeeper Roadmap

## v1.0

Completed foundation:

- Transparent Ollama proxy.
- Request logging and diagnostics.
- Context estimation.
- Compression engine.
- Automatic model context-window discovery.
- Authoritative context-window enforcement.
- Dashboard.

Version 1 product philosophy:

- Version 1 remains focused on delivering a production-quality release.
- Ideas that are not required for Version 1.0 should be captured for later versions instead of expanding v1 unnecessarily.
- Version 1 is intended to solve context-window limitations without permanently losing historical conversation details.
- Goal: "Compress active context without forgetting important information."

Version 1 Memory Architecture:

- Compression is not deletion.
- Rolling summaries reduce the amount of text sent to the model on every request.
- Original historical messages should remain durably available after they leave the active prompt.
- ContextKeeper should be capable of retrieving relevant archived details when a later request depends on them.
- Users should be able to continue a long-running conversation throughout the day without manually restarting merely because the model's active context window filled.
- Historical retrieval and active context compression are complementary systems:
  - Active context management keeps prompts efficient.
  - Historical retrieval restores specific older details when needed.
- Version 1 should not require the selected model to support tool calling for basic historical retrieval.
- ContextKeeper-controlled retrieval should be the default Version 1 design.
- A future model-invoked history-search tool may be considered later, but Version 1 should not depend upon it.
- The goal is strong, testable detail preservation and retrieval, not perfect or infallible memory.

Version 1 release direction:

- Transparent Ollama-compatible proxy.
- Client-agnostic operation.
- Diagnostics and operational visibility.
- Automatic context management.
- Context-window usage tracking.
- Rolling context summarization and compression.
- Automatic context-window discovery.
- Authoritative context-window enforcement.
- Preservation of recent messages.
- Durable preservation of original historical conversation details.
- Historical memory retrieval after compression.
- Automatic injection of relevant archived details when appropriate.
- Live dashboard.
- Validation Framework.
- AutoQA.
- Windows service.
- Standalone executable.
- Setup wizard.
- Installer.
- Release certification.
- Public documentation and GitHub release preparation.
- Production stability.
- Release-quality documentation.

Approved context-memory architecture:

- Context compression should reduce active prompt size.
- Compression should not permanently discard conversation history.
- Historical information should remain searchable and retrievable.
- ContextKeeper should retrieve relevant archived details automatically when appropriate.

Approved remaining release sequence:

1. Phase 6.5F-B5 — Live Data Visualization & Rich Widgets.
2. Phase 6.5F-B6 — Dashboard Customization & User Preferences.
3. Phase 6.5F-B7 — Release Polish & Final UX Review.
4. Phase 6.5G — Historical Memory Retrieval & Detail Preservation.
5. Phase 6.6 — Validation Framework & Release Certification.
6. Phase 7 — GitHub Release.
7. Version 1.0 Release.

Phase 6.5G must occur before Phase 6.6 so the Validation Framework can certify historical memory retrieval and detail preservation. Phase 6.6 is a dedicated pre-release QA and certification phase. It must occur before Phase 7 and before the Version 1.0 release.

### Phase 6.5F-B5 — Live Data Visualization & Rich Widgets

Status: Planned.

Planned scope:

- Expand live dashboard visualization beyond the current operations-console foundation.
- Add richer widgets where they improve operational visibility without destabilizing the dashboard layout.

### Phase 6.5F-B6 — Dashboard Customization & User Preferences

Status: Planned.

Planned scope:

- Add user-facing dashboard customization and preference controls after the live-widget pass.
- Preserve the existing dashboard implementation until this phase begins.

### Phase 6.5F-B7 — Release Polish & Final UX Review

Status: Planned.

Planned scope:

- Complete final UX review before release certification.
- Polish remaining release-blocking interface and documentation issues.

### Phase 6.5G — Historical Memory Retrieval & Detail Preservation

Status: Planned. No historical-memory retrieval implementation exists yet.

Objective:

- Preserve original conversation details after active-context compression and retrieve relevant archived details when later requests depend on them.
- Keep active prompts efficient without permanently forgetting important information.
- Allow users to continue long-running conversations throughout the day without manually restarting merely because the model's active context window filled.

Architecture decision:

- Historical memory retrieval is an integrated ContextKeeper capability, not a separate user-facing application.
- ContextKeeper-controlled retrieval should be the default Version 1 design.
- Version 1 historical retrieval should work without requiring the selected model to support tool calling.
- A future model-invoked history-search tool may be considered later, but Version 1 should not depend upon it.
- Active context management and historical retrieval are complementary systems. Active context management keeps prompts efficient; historical retrieval restores specific older details when needed.
- Historical retrieval should selectively retrieve relevant archived details rather than reload an entire conversation.
- The design should preserve client transparency and Ollama API compatibility.

Multi-user preparation:

- Every persistent ContextKeeper object should have an owner, even when Version 1 uses only one default owner.
- Ownership may later support a hierarchy such as tenant or organization, user or owner, workspace, and conversation.
- Version 1 may use a single implicit default owner.
- Version 1 does not need to expose authentication, user accounts, permissions, organizations, or shared workspaces.
- Version 1 storage decisions should avoid making later user and workspace isolation unnecessarily difficult.
- Historical-memory design should prepare for future ownership and isolation without expanding Version 1 into a full multi-user product.

#### Phase 6.5G.1 — Durable Conversation Archive

Planned scope:

- Preserve original messages after active-context compression.
- Durable storage of message history.
- Preserve message order, role, timestamps, model, conversation identity, and relevant metadata.
- Avoid destructive replacement of historical source messages.
- Recovery behavior after ContextKeeper restart.
- Storage format and migration planning.
- Clear boundaries between active messages, summaries, and archived originals.

#### Phase 6.5G.2 — Historical Search & Ranking

Planned scope:

- Search archived conversation history.
- Conversation-scoped retrieval.
- Keyword and semantic retrieval options.
- Relevance ranking.
- Duplicate suppression.
- Recency and importance weighting.
- Deterministic fallback behavior.
- Strict prevention of cross-conversation leakage.
- Retrieval diagnostics and explainability where practical.

#### Phase 6.5G.3 — Retrieval-Aware Prompt Injection

Planned scope:

- Automatically determine when historical retrieval may be useful.
- Inject a limited set of relevant archived excerpts into outgoing requests.
- Apply a configurable retrieval token budget.
- Clearly distinguish retrieved history from recent live messages.
- Avoid repeatedly injecting the same content.
- Preserve Ollama-compatible request behavior.
- Work without requiring model-specific tool calling.
- Prevent retrieval from consuming so much context that it causes unnecessary compression.

#### Phase 6.5G.4 — Fact Preservation & Importance Controls

Planned scope:

- Important-fact detection or tagging.
- Pinned facts.
- Retention-priority metadata.
- User-approved corrections to stored facts.
- Protection against fact mutation across repeated summaries.
- Distinguish exact factual details from broad conversational summaries.
- Support facts such as names, dates, identifiers, requirements, decisions, restrictions, and project details.

#### Phase 6.5G.5 — Memory Dashboard & User Controls

Planned scope:

- Historical-memory visibility in the existing dashboard.
- Search stored conversation history.
- Show retrieved excerpts used for a request when practical.
- Display retrieval counts and memory status.
- Pin, correct, export, or remove stored facts.
- Enable or disable historical retrieval.
- Configure retrieval limits.
- Inspect summaries separately from original archived messages.

This should be an integrated ContextKeeper dashboard capability, not a separate user-facing application.

#### Phase 6.5G.6 — Privacy, Retention & Recovery

Planned scope:

- Configurable history-retention policies.
- Conversation deletion.
- Memory export.
- Local-only storage by default.
- Sensitive-data handling.
- Backup and recovery behavior.
- Corruption handling.
- Storage limits.
- Secure isolation between conversations and future owners/workspaces.
- Clear user control over what is retained.

These boundaries are planning labels and may be refined during implementation.

### Phase 6.6 — Validation Framework & Release Certification

Status: Planned. No Validation or AutoQA implementation exists yet.

Architecture decision:

- Phase 6.6 must validate Phase 6.5G historical memory retrieval and detail preservation.
- The Validation feature will be built as a first-class modular subsystem and dashboard plugin inside ContextKeeper, not as a separate user-facing application.
- The feature should use the existing ContextKeeper executable, installer, service, configuration system, logs, and dashboard.
- The approved future left-navigation label is `Validation`. Do not call the navigation item `AutoQA`, because Validation is the broader feature area and AutoQA is one capability inside it.

Important design principle:

> The Validation Engine should exercise ContextKeeper through its public Ollama-compatible APIs whenever practical. Internal interfaces should be used only for orchestration, metrics collection, controlled fault injection, and verification. This ensures AutoQA validates the same behavior experienced by AnythingLLM, Open WebUI, IDEs, Python clients, and other Ollama-compatible consumers.

The planned module may eventually resemble:

```text
src/ctxkeeper/validation/
- engine.py
- runner.py
- scenarios.py
- generator.py
- injector.py
- verifier.py
- evaluator.py
- metrics.py
- reports.py
```

This file list is architectural direction, not an implementation commitment. It may be refined later.

#### Phase 6.6.1 — Validation Engine Foundation

Planned scope:

- New modular `validation` engine inside ContextKeeper.
- Validation configuration.
- Test execution framework.
- Scenario registration and management.
- Run lifecycle management.
- Cancellation, timeout, and failure handling.
- Historical validation-run storage.
- Dashboard navigation entry named `Validation`.

#### Phase 6.6.2 — AutoQA Conversation Engine

Planned scope:

- Automated conversations through ContextKeeper's public Ollama-compatible APIs.
- Realistic multi-domain conversation scenarios.
- Configurable turn counts.
- Randomized and deterministic seeded runs.
- Multiple conversation identities.
- Multi-model support.
- Adjustable pacing and load.
- Local LLM acting as a simulated user when appropriate.
- Scripted scenarios that do not require an LLM for deterministic testing.

#### Phase 6.6.3 — Memory & Compression Validation

Planned scope:

- Controlled fact injection.
- Facts classified by expected retention priority.
- Context-window filling and overflow generation.
- Warning-threshold validation.
- Compression-threshold validation.
- Verification that compression actually occurs.
- Verification that original archived messages remain preserved after compression.
- Verification that historical retrieval works after compression.
- Verification that recent messages remain available.
- Verification that important older facts survive rolling summaries.
- Recall questions after one or more compression cycles.
- Exact-match and semantic-retention scoring.
- Detection of invented, mutated, or lost facts.
- Continued conversation-coherence checks after compression.

#### Phase 6.6.4 — Stress, Soak & Reliability Testing

Planned scope:

- Long-duration unattended soak tests.
- Thousands of automated messages.
- Repeated compression cycles.
- Model switching.
- Different model context-window sizes.
- Streaming validation.
- Concurrent conversations.
- Multiple simulated clients.
- Ollama disconnect and reconnect testing.
- Timeout and failed-discovery testing.
- ContextKeeper restart and recovery testing.
- CPU, RAM, latency, error-rate, and stability monitoring.
- Resource-leak detection where practical.

#### Phase 6.6.5 — Validation Dashboard Plugin

Planned scope:

- First-class `Validation` item in the existing left-side dashboard navigation.
- No separate user-facing application.
- Use the existing ContextKeeper executable, installer, service, configuration system, logs, and dashboard.
- Live run status.
- Start, stop, and cancel controls.
- Scenario selection.
- Model selection.
- Conversation-length and pacing controls.
- Progress indicators.
- Messages generated.
- Compression events.
- Facts injected and verified.
- Retention score.
- Streaming failures.
- Active model.
- Elapsed duration.
- Resource statistics.
- Compression timeline.
- Historical runs.
- Report viewing.

Planned Validation page structure:

- Validation
  - Dashboard
  - Scenarios
  - AutoQA
  - Stress Tests
  - Reports
  - History
  - Settings

This is a planning structure and may be refined during implementation.

The planned left-side dashboard navigation may eventually resemble:

- Overview
- Operations
- Diagnostics
- Conversations
- Compression
- Models
- Validation
- Settings

This navigation must not be implemented until the relevant implementation phase.

#### Phase 6.6.6 — Reports & Release Certification

Planned scope:

- Human-readable HTML reports.
- Machine-readable JSON export.
- Historical run archive.
- Scenario-level pass/fail results.
- Overall release-candidate pass/fail status.
- Models tested.
- Duration.
- Conversation and message counts.
- Compression-event counts.
- Fact-retention scores.
- Conversation-coherence scores.
- Streaming failures.
- Discovery failures.
- Server-recovery results.
- CPU and RAM peaks.
- Error summaries.
- Release certification report for Version 1.0.

Validation design principles:

- AutoQA is intended to eliminate hours of manual typing merely to fill a model's context window.
- Deterministic scripted tests should be preferred for repeatable release certification.
- LLM-generated conversations may supplement scripted tests for realism and exploratory coverage.
- A local evaluator model may provide semantic scoring, but release certification must not depend solely on subjective LLM judgment.
- Objective telemetry, known injected facts, event records, request outcomes, and deterministic assertions must remain authoritative.
- The framework should support seeded runs so failures can be reproduced.
- Validation traffic must be clearly tagged or isolated so it is distinguishable from normal user conversations.
- Destructive or disruptive scenarios must require explicit user selection.
- Long-running AutoQA tests should be cancellable and must not block normal ContextKeeper shutdown.
- AutoQA should be disabled by default in production installations until a user starts a validation run.
- Sensitive prompts, secrets, and private documents must not be written into validation reports.
- The framework should be extensible later for model routing, workspace memory, plugins, agents, and multi-server orchestration.

AutoQA relationship to historical memory:

- AutoQA should eventually test known fact injection early in a conversation.
- AutoQA should test context-window filling, warning-threshold activation, compression-threshold activation, and one or more rolling compression cycles.
- AutoQA should verify preservation of original archived messages and historical retrieval after compression.
- AutoQA should verify exact recall of identifiers, names, dates, decisions, and restrictions.
- AutoQA should verify semantic recall of meaning.
- AutoQA should detect missing facts, mutated facts, and invented facts.
- AutoQA should verify continued conversation coherence after compression and retrieval.
- AutoQA should verify retrieval-budget behavior and duplicate suppression.
- AutoQA should verify conversation isolation.
- AutoQA should verify restart and recovery behavior.
- Deterministic test scenarios and known injected facts must remain authoritative for release certification.
- A local LLM may generate realistic simulated-user conversations, produce exploratory variations, and assist with semantic evaluation.
- Release certification must not depend solely on subjective LLM judgment.
- Objective telemetry, known facts, stored source messages, event records, request results, and deterministic assertions must remain authoritative.

### Phase 7 — GitHub Release

Status: Planned after Phase 6.6.

Likely scope:

- Public documentation.
- Examples.
- Release packaging.
- Release notes.
- GitHub release preparation.
- Community feedback readiness.

### Version 1.0 Release

Status: Planned after Phase 7.

## v1.1

- Better token estimation.
- Improved diagnostics.
- Export logs.

## v2.0

Status: Approved high-level direction. Exact scope and sequencing remain tentative. These ideas are not Version 1.0 commitments and are not implemented unless future Git history proves otherwise.

Detailed noncommittal idea parking lot: [ContextKeeper Future Ideas](FUTURE_IDEAS.md).

### Multi-User and Security

- Multi-user architecture.
- Authentication.
- User isolation.
- Workspace isolation.
- Multiple organizations / tenants.
- Shared workspaces.
- Roles and permissions.
- Per-user configuration.
- Per-user dashboards.
- Auditability.
- Cross-user data-leak prevention.

### Workspace and Project Memory

- Cross-conversation workspace memory.
- Persistent project knowledge.
- Workspace-level retrieval.
- Shared knowledge within authorized workspaces.
- Pinned memories.
- Memory prioritization.
- Memory expiration and archival policies.
- Improved semantic retrieval.
- Source attribution and provenance.

### Validation Extensions

- Multi-user AutoQA.
- Workspace-isolation tests.
- Permission tests.
- Authentication tests.
- Cross-user leakage tests.
- Shared-workspace tests.
- Tenant-isolation certification.

Example isolation scenario:

- User A stores a private fact.
- User B asks for that fact.
- Expected result: ContextKeeper does not reveal it.

### Intelligent Routing

- Automatic model routing.
- Automatic model selection.
- Capability-aware routing.
- Context-window-aware routing.
- Model-performance benchmarking.
- Resource-aware routing.
- Cost and latency optimization where applicable.
- Local-server availability awareness.

### Plugin Platform

- Plugin SDK.
- Third-party integrations.
- Custom validation scenarios.
- Custom dashboard widgets.
- Custom memory providers.
- Custom routing policies.
- Controlled plugin permissions and isolation.

### Infrastructure

- Multi-server support.
- Load balancing.
- Distributed ContextKeeper nodes.
- Failover.
- Remote execution.
- Server health and capability discovery.

### Agents and Voice

- Agent orchestration.
- Autonomous workflows.
- Voice-first interaction.
- Jarvis-style assistant integration.
- Voice and visual input integrations.
- Coordination of specialized local agents.

### Analytics and Benchmarking

- Advanced model benchmarks.
- Long-term usage analytics.
- Model comparisons.
- Historical performance trends.
- Context-compression effectiveness metrics.
- Memory-retrieval effectiveness metrics.
- Validation trend reporting.

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
- New ideas should be classified as required for Version 1, formally planned for Version 2, preserved in Future Ideas, or deliberately rejected or superseded.
- Client transparency and Ollama API compatibility remain core constraints.
- Sensitive prompts, credentials, private documents, and full conversation contents must not be exposed in routine logs or validation reports.

## v3.0

Status: Later expansion after the v2 architecture matures.

- Broader multi-server orchestration.
- Advanced load balancing.
- Deeper agent integration.
