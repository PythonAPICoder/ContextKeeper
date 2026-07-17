# Conversation Inspector

## Purpose

The Conversation Inspector is the planned drill-down surface for understanding a selected ContextKeeper conversation while keeping the main dashboard visible. It complements the Live Conversation Timeline: the timeline remains the compact operational narrative, and the inspector becomes the place for deeper conversation-specific diagnostics.

## Drawer interaction model

- The inspector opens as a right-side slide-out drawer from selectable Live Conversation Timeline entries.
- Wide layouts keep the dashboard visible behind and beside the drawer; the drawer is not a full-screen modal on desktop.
- Narrow layouts may use a backdrop and effectively full-width drawer presentation to preserve readability.
- Closing is available through an explicit close button and Escape.
- Selection is owned by the dashboard frontend only. The dashboard remains a read-only observer of ContextKeeper state.
- Dashboard polling continues while the drawer is open. If the selected conversation disappears from the current snapshot, the drawer stays open and reports that details are unavailable rather than silently switching conversations.

## Current and planned sections

B5.5.1 established only the shell and metadata foundation. B5.5.2 adds two production sections:

- Overview: factual selected-conversation metadata derived from the current dashboard snapshot.
- Intelligence: deterministic context/compression health based on estimated token usage, known context capacity, configured thresholds, and confirmed compression history.

Later slices can add sections such as:

- Request and lifecycle metadata.
- Conversation message inspection with strict privacy boundaries.
- Context composition and active prompt contribution.
- Compression-event details and before/after context pressure.
- Timeline-to-detail cross-highlighting.
- Conversation-scoped diagnostics and operator notes.

## Privacy expectations

The inspector must never expose private data by accident. Each sub-phase should explicitly decide what is safe to display.

Default exclusions:

- User prompt text.
- Assistant response text.
- Rolling-summary body text.
- System prompts.
- Retrieved document contents.
- Request bodies.
- API secrets or headers.

Safe metadata may include:

- Conversation id.
- Status.
- Model.
- Client/source host when already present in dashboard metrics.
- Endpoint.
- Start/completion times.
- Duration.
- Request count.
- Estimated context tokens.
- Context percentage.
- Detected model context capacity.
- Message count.
- Compression count.
- Last activity and deterministic duration.

Deterministic intelligence may include:

- Context usage classification.
- Warning and compression threshold comparison.
- Remaining estimated token headroom.
- Context/compression enabled states.
- Confirmed compression-event count.
- Action recommendation only for genuine degraded states.

## On-demand data-loading strategy

B5.5.1 and B5.5.2 use only metadata already present in, or safely derived from, the existing dashboard snapshot and Live Conversation Timeline payload. B5.5.2 adds a small deterministic inspector view model to the existing `/dashboard/data` response, built from the same single conversation snapshot path used by the dashboard.

Future detailed inspection should be loaded on demand after a user selects a conversation. That avoids increasing the baseline dashboard payload with full transcript details and preserves current dashboard polling behavior.

Future detail endpoints should remain conversation-scoped, privacy-filtered, bounded, and read-only. They should not duplicate context ownership or create a second event-tracking architecture.

## B5.5 sub-phase breakdown

- B5.5.1 — Conversation Inspector Foundation: selectable timeline entries, right-side drawer shell, selected-conversation state, basic metadata, loading/unavailable/closed states, responsive behavior, accessibility, tests, and documentation.
- B5.5.2 — Conversation Inspector Overview & Intelligence: factual overview fields and deterministic context/compression intelligence using existing dashboard state.
- B5.5.3 — Conversation Detail Endpoint: bounded, privacy-filtered, on-demand metadata/detail API for the selected conversation.
- B5.5.4 — Message and Request Detail View: safe conversation-message/request inspection with redaction and clear exclusions.
- B5.5.5 — Context Composition View: active prompt/context-window contribution visualization without exposing private text unnecessarily.
- B5.5.6 — Compression Detail View: confirmed compression events, before/after context pressure where reliable, and summary provenance without leaking summary bodies.
- B5.5.7 — Inspector Polish and QA: keyboard refinements, cross-highlighting, responsive review, reduced-motion review, and final visual polish.
