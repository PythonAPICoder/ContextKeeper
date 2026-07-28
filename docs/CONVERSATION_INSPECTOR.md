# Conversation Inspector

Status: The B5.5.1 Foundation and B5.5.2 Overview & Intelligence slices are implemented. Phase 6.5F-B7.1 is the current dashboard release-readiness audit; Product Owner manual review is pending.

See [Dashboard Release Readiness Audit](DASHBOARD_RELEASE_READINESS_AUDIT.md) for the evidence, classifications, limitations, and release recommendation.

## Purpose

The Conversation Inspector is the implemented drill-down surface for understanding a selected ContextKeeper conversation while keeping the main dashboard visible. It complements the Live Conversation Timeline: the timeline remains the compact operational narrative, and the inspector provides current Overview and Intelligence diagnostics.

## Drawer interaction model

- The inspector opens as a right-side slide-out drawer from selectable Live Conversation Timeline entries or the Active Conversation card Open button (`opsActiveConversationInspectBtn`, tracking B7.1-PO-01).
- Wide layouts keep the dashboard visible behind and beside the drawer; the drawer is not a full-screen modal on desktop.
- Narrow layouts use a backdrop and effectively full-width presentation while retaining the current nonmodal complementary-region semantics.
- Opening moves focus to the Close button. Escape or the Close button closes the drawer and returns focus to the originating timeline entry or Open button when still available.
- The closed drawer is inert, so its hidden controls are absent from the keyboard tab order.
- Selection is owned by the dashboard frontend only. The dashboard remains a read-only observer of ContextKeeper state.
- Dashboard polling continues while the drawer is open. If the selected conversation disappears from the current snapshot, the drawer stays open and reports that details are unavailable rather than silently switching conversations.

### B7.1-PO-01: Active Conversation Inspector Trigger

**Classification**: Product Owner UX Enhancement / Release-Readiness Requirement Change

- The Active Conversation card Open control is a semantic button (`opsActiveConversationInspectBtn`).
- It begins disabled until a valid active conversation exists.
- It opens the existing right-side Conversation Inspector drawer.
- It uses the currently active conversation ID.
- It does not change the URL hash.
- It does not leave the Operations page.
- The full Conversations page remains available through main navigation.
- Focus moves into the drawer when opened.
- Escape and the drawer Close button return focus to the Open button.
- Timeline entries continue opening the same Inspector drawer.
- Closing a timeline-opened drawer returns focus to the originating timeline event.

Release-audit finding B7.1-07 remains open: at narrow widths, keyboard focus can leave the visually full-width drawer for obscured background controls. This Medium issue requires focused containment/background-inert remediation or explicit Product Owner acceptance; it does not require changing the desktop drawer into a broad modal redesign.

## Current and deferred sections

B5.5.1 implemented the shell and metadata foundation. B5.5.2 implemented two production sections:
- Overview: factual selected-conversation metadata derived from the current dashboard snapshot.
- Intelligence: deterministic context/compression health based on estimated token usage, known context capacity, configured thresholds, and confirmed compression history.

B5.5.3 and later slices are intentionally deferred. They may add sections such as:

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

## B7.1 release evidence and manual QA

The B7.1 automated baseline was **553 passing tests**. Seven focused release-gate tests were added, and the verified final full-suite result is **560 passing tests**. Inspector coverage now explicitly protects focus-on-open, Escape close, focus return, and closed-drawer inertness.

Headless overflow measurements covered CSS widths `6880`, `4587`, `3440`, `1900`, `1500`, `1350`, `1000`, `700`, and `344`, with body and document widths equal to the viewport after the scoped containment fix. This is engineering evidence, not manual visual or accessibility approval.

Product Owner QA must review the Inspector at 3440×1440 with 100% display scaling, browser zoom at 50%, 75%, and 100%, and responsive transitions down to the 344-wide layout. Exercise long conversation identifiers and status text; loading, unavailable, no-active-conversation, and no-history states; keyboard open/Close/Escape/focus-return/tab-order paths; reduced motion; visible focus; and disabled/secondary-content contrast. The effectively full-width narrow drawer remains nonmodal, but B7.1-07 must be dispositioned before release; a broad redesign is outside B7.1.

## B5.5 sub-phase breakdown

- B5.5.1 — Conversation Inspector Foundation: selectable timeline entries, right-side drawer shell, selected-conversation state, basic metadata, loading/unavailable/closed states, responsive behavior, accessibility, tests, and documentation.
- B5.5.2 — Conversation Inspector Overview & Intelligence: factual overview fields and deterministic context/compression intelligence using existing dashboard state.
- B5.5.3 — Conversation Detail Endpoint: intentionally deferred; bounded, privacy-filtered, on-demand metadata/detail API for the selected conversation.
- B5.5.4 — Message and Request Detail View: safe conversation-message/request inspection with redaction and clear exclusions.
- B5.5.5 — Context Composition View: active prompt/context-window contribution visualization without exposing private text unnecessarily.
- B5.5.6 — Compression Detail View: confirmed compression events, before/after context pressure where reliable, and summary provenance without leaking summary bodies.
- B5.5.7 — Inspector Polish and QA: keyboard refinements, cross-highlighting, responsive review, reduced-motion review, and final visual polish.
