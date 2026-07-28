# ContextKeeper Dashboard Layout

Status: Phase 6.5F-B6 is complete. Phase 6.5F-B7.1 is the current dashboard release-readiness audit; Product Owner manual review is pending.

See [Dashboard Release Readiness Audit](DASHBOARD_RELEASE_READINESS_AUDIT.md) for the evidence, classifications, limitations, and release recommendation.

This document describes the current dashboard shell, Operations hierarchy, Settings page, and layout contract. It defines layout and user flow; source code remains authoritative for exact CSS and DOM details.

## Purpose

The ContextKeeper Operations dashboard is the primary AI operations console for the local proxy. It should help users understand system health, request flow, Context Usage, Compression activity, and required action without reading logs or reports. The Settings page provides a focused runtime-and-persisted-configuration management surface without replacing or duplicating Operations.

## Layout principles

- Communicate system health quickly.
- Keep runtime status above detailed history.
- Group instruments with instruments and activity visualizations with activity visualizations.
- Preserve live dashboard context while drill-down surfaces are open.
- Keep page navigation keyboard-operable and identify the active destination.
- Avoid horizontal overflow.
- Preserve reduced-motion support.
- Keep prompt, response, rolling-summary, and request-body content out of routine dashboard surfaces.

## Current page structure

The existing shell contains persistent sidebar navigation, the topbar, and one active page at a time. Navigation uses client-side page switching, so selecting Settings or returning to Operations does not reload the application. The active link is identified visually and with `aria-current="page"`.

The Operations page currently uses this hierarchy:

```text
Topbar
Operations hero
System Instrument Panel
System Activity
Operations lower row
Conversation Inspector drawer
```

### Topbar

Purpose:

- Identify ContextKeeper.
- Show global refresh/status context.
- Surface proxy/Ollama connection metadata.

The topbar should stay compact and should not compete with the Operations hero.

### Operations hero

Purpose:

- Communicate overall health and action state.
- Show recommendations.
- Show high-level statistics.

Current content:

- health status;
- current activity;
- last refresh;
- recommendations;
- total requests;
- active conversations;
- compression savings/count;
- average response time.

### System Instrument Panel

Purpose:

- Present gauge/status-meter cards as a unified instrument row.

Current top-row cards:

1. CPU Usage.
2. GPU Usage.
3. Memory Usage.
4. Context Usage.
5. Compression Status.

Rules:

- Keep these cards visually related.
- Do not insert chart widgets into this row.
- Preserve compact three-line supporting details.
- Preserve responsive behavior that collapses the row at narrower widths.

### System Activity

Purpose:

- Group visualization widgets that explain activity and trends.

Current second-row widgets:

1. Context Trend.
2. Connection Flow.

Context Trend shows rolling active-conversation Context Usage history from dashboard samples.

Connection Flow shows the path:

```text
Client -> ContextKeeper -> Ollama -> Model
```

It includes activity state, availability state, labels, badges, and a restrained moving marker during active traffic.

### Operations lower row

Purpose:

- Present recent operational activity and active-conversation context without crowding primary health/instrument content.

Current cards:


This document describes the current dashboard shell, Operations hierarchy, Settings page, and layout contract. It defines layout and user flow; source code remains authoritative for exact CSS and DOM details.

## Purpose

The ContextKeeper Operations dashboard is the primary AI operations console for the local proxy. It should help users understand system health, request flow, Context Usage, Compression activity, and required action without reading logs or reports. The Settings page provides a focused runtime-and-persisted-configuration management surface without replacing or duplicating Operations.

## Layout principles

- Communicate system health quickly.
- Keep runtime status above detailed history.
- Group instruments with instruments and activity visualizations with activity visualizations.
- Preserve live dashboard context while drill-down surfaces are open.
- Keep page navigation keyboard-operable and identify the active destination.
- Avoid horizontal overflow.
- Preserve reduced-motion support.
- Keep prompt, response, rolling-summary, and request-body content out of routine dashboard surfaces.

## Current page structure

The existing shell contains persistent sidebar navigation, the topbar, and one active page at a time. Navigation uses client-side page switching, so selecting Settings or returning to Operations does not reload the application. The active link is identified visually and with `aria-current="page"`.

The Operations page currently uses this hierarchy:

```text
Topbar
Operations hero
System Instrument Panel
System Activity
Operations lower row
Conversation Inspector drawer
```

### Topbar

Purpose:

- Identify ContextKeeper.
- Show global refresh/status context.
- Surface proxy/Ollama connection metadata.

The topbar should stay compact and should not compete with the Operations hero.

### Operations hero

Purpose:

- Communicate overall health and action state.
- Show recommendations.
- Show high-level statistics.

Current content:

- health status;
- current activity;
- last refresh;
- recommendations;
- total requests;
- active conversations;
- compression savings/count;
- average response time.

### System Instrument Panel

Purpose:

- Present gauge/status-meter cards as a unified instrument row.

Current top-row cards:

1. CPU Usage.
2. GPU Usage.
3. Memory Usage.
4. Context Usage.
5. Compression Status.

Rules:

- Keep these cards visually related.
- Do not insert chart widgets into this row.
- Preserve compact three-line supporting details.
- Preserve responsive behavior that collapses the row at narrower widths.

### System Activity

Purpose:

- Group visualization widgets that explain activity and trends.

Current second-row widgets:

1. Context Trend.
2. Connection Flow.

Context Trend shows rolling active-conversation Context Usage history from dashboard samples.

Connection Flow shows the path:

```text
Client -> ContextKeeper -> Ollama -> Model
```

It includes activity state, availability state, labels, badges, and a restrained moving marker during active traffic.

### Operations lower row

Purpose:

- Present recent operational activity and active-conversation context without crowding primary health/instrument content.

Current cards:

1. Traffic with Request Traffic visualization.
2. Active Conversation.
3. Live Conversation Timeline.

Traffic shows request trend, request rate, errors, and compact recent request-frequency visualization.

Active Conversation shows selected/current conversation metadata and rolling-summary availability without exposing full private content in the Operations summary. It includes a semantic Open button (`opsActiveConversationInspectBtn`, tracking B7.1-PO-01) that begins disabled until a valid active conversation exists, opening the right-side Conversation Inspector drawer for the current conversation ID without changing the URL hash or leaving the Operations page.

Live Conversation Timeline is a compact chronological operational feed for the active or most recently active conversation. Timeline entries that map to a real conversation can open the Conversation Inspector.

### Conversation Inspector drawer

Purpose:

- Provide selected-conversation drill-down while preserving dashboard context.

Current behavior:

- Opens from selectable Live Conversation Timeline entries or the Active Conversation card Open button (`opsActiveConversationInspectBtn`, tracking B7.1-PO-01).
- Uses a right-side drawer on desktop.
- Uses a backdrop and effectively full-width presentation on narrow layouts while remaining a nonmodal complementary region.
- Moves focus to the Close button on open, supports Escape close, and returns focus to the originating timeline entry or Open button.
- Is inert while closed, so hidden drawer controls do not remain in the keyboard tab order.
- Keeps polling active.
- Shows loading, unavailable, Overview, and Intelligence states.
- Does not show prompt text, response text, rolling-summary bodies, request bodies, or retrieved private content.

#### B7.1-PO-01: Active Conversation Inspector Trigger

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

The current nonmodal narrow-layout architecture is not a broad B7.1 redesign target. The release audit nevertheless records B7.1-07 as a Medium defect because keyboard focus can leave the visually full-width drawer for obscured background controls. Focused containment/background-inert remediation or explicit Product Owner acceptance is required; broader Inspector content work remains deferred to B5.5.3 and later slices.
Current source includes secondary pages for:

- Conversations.
- Context.
- Analytics.
- Logs.
- Settings.

These pages remain subordinate to the Operations dashboard and should not duplicate its core hierarchy unless a later phase intentionally redesigns navigation. Conversations, Context, Analytics, and Logs retain their existing behavior. Settings is now a dedicated interactive page within the same shell.

### Settings page

Purpose:

- Review settings exposed by the current ContextKeeper runtime.
- Edit controls that API metadata marks runtime-editable, persistable, or both.
- Keep temporary edits visible until they are saved or discarded.
- Keep runtime Save and configuration persistence separate and explicit.
- Make runtime, persisted, default, and restart-required states understandable.
- Distinguish the active Ollama connection, saved configuration, editable Connection candidate, and latest transient candidate-test result.
- Provide scoped recovery to authoritative built-in defaults without presenting it as a factory reset.

Current hierarchy:

```text
Settings header and introduction
Runtime-versus-saved configuration notice
Accessible status and error feedback
Loading, retry, or empty state
Metadata-driven category cards
Category reset controls
Setting labels, descriptions, runtime/saved/default metadata, difference text, badges, controls, and individual reset actions
Connection candidate Test action and success/failure result
Sticky change summary with Discard changes, Save to configuration, and Save runtime changes
Reset managed settings to defaults
```

The page loads `GET /api/dashboard/settings` when first opened. The general renderer generates category cards, labels, metadata, and boolean, integer, and string controls from the schema-v2 snapshot. The specialized Connection presentation recognizes category id `ollama` and field ids `ollama.base_url` and `ollama.timeout_seconds` to provide the endpoint control, candidate test, stale-result clearing, and result panel. Runtime-read-only, non-persistable, runtime-different-from-saved, and restart-required states use explicit text, badges, or disabled controls rather than color alone; an individual reset action is omitted when metadata marks the setting reset-ineligible. Every setting displays built-in default and saved configuration values plus dynamic text describing how the draft compares with the current runtime and persisted value.

The browser maintains separate confirmed and draft snapshots. Save runtime changes sends one changed-fields-only atomic `PATCH /api/dashboard/settings`. Save to configuration is a separate non-submit button that sends one changed-fields-only `PUT /api/dashboard/settings/config` containing only eligible draft values that differ from saved configuration. Editing and reset never trigger persistence automatically.

Each reset-eligible setting has a native button with a setting-specific accessible name. A runtime-editable individual reset submits only its authoritative default through PATCH. Connection individual/category reset stages persistence-only defaults in the draft and sends no PATCH. Category reset and **Reset managed settings to defaults** use keyboard-operable native confirmation and include all and only reset-eligible settings in scope. A mixed global reset sends one PATCH containing only its runtime-editable subset while retaining Connection defaults in the draft. Cancellation changes nothing. Success feedback reports the staged count where practical, states that reset did not write configuration, and distinguishes Save-required divergence from an already-matching persisted state.

**Discard changes** restores browser-only draft edits locally, including Connection-only drafts, without sending PATCH. When the confirmed runtime differs from the persisted state, **Discard changes** sends one atomic PATCH containing `persisted_value` for every runtime-editable differing setting, then refreshes the confirmed and draft presentation from the canonical response. Connection fields are never included. **Discard changes** does not write YAML. Reset and **Discard changes** failures retain the current state and use the existing accessible error feedback.

A PUT success refreshes runtime/persisted metadata while restoring the user's draft, so a Connection setting can be saved to disk yet remain pending runtime application. Failed runtime or configuration saves leave the draft available for correction or retry. While either save is pending, controls and actions are locked to prevent duplicate submission. The visible notice explains that runtime Save does not write YAML, configuration Save does not change runtime state, and neither action restarts ContextKeeper. Both Connection fields display restart-required state; activation requires a manual restart and may still be superseded by a higher-priority environment override.

The Connection category contains **AI Server Endpoint**, **Request Timeout**, and **Test Connection**. The action posts the current draft values, not the saved or active values. While testing, it exposes a busy state, disables duplicate submission, and does not block ordinary dashboard polling. Success displays Connected status, normalized tested endpoint, measured latency, Ollama version, and text explaining that the test neither saved nor activated the candidate. Failure displays Failed status and a safe categorized explanation stating that runtime and saved configuration were unchanged. Editing either draft after a result clears that result so the UI never implies that modified values were tested. The candidate result does not replace the Operations page's active Ollama health or version.

Switching views does not register another Settings listener or multiply the existing dashboard polling timer. Operations polling and visualization updates continue through the same refresh lifecycle.

## Responsive behavior

Requirements:

- Preserve readability at 50%, 75%, and 100% browser zoom.
- Preserve wide-display usability, including 3440×1440 with 100% Windows display scaling.
- Collapse multi-column grids cleanly at narrower widths.
- Do not introduce horizontal page overflow.
- Ensure the Conversation Inspector becomes effectively full-width on narrow layouts.
- Allow Settings labels, descriptions, constraints, badges, and controls to wrap without compressing the form into unreadable columns.
- Keep the Connection action and tested endpoint, latency, version, and failure result readable without clipping or relying on color.
- Stack Settings rows, per-setting/category reset controls, the global reset control, and the Discard/runtime Save/configuration Save action area at the narrow breakpoint while keeping all actions reachable.
- Keep dashboard controls reachable while preserving context.

### B7.1 engineering evidence and required manual review

The automated baseline entering B7.1 was **553 passing tests**. Seven focused release-gate tests were added, and the verified final full-suite result is **560 passing tests**.

Headless Microsoft Edge engineering measurements exercised CSS viewport widths `6880`, `4587`, and `3440`, plus `1900`, `1500`, `1350`, `1000`, `700`, and `344`. After the scoped containment fix, body and document-element scroll widths equaled the viewport at every measured width. A 683-character endpoint remained contained in the topbar and used ellipsis. These measurements are automated overflow evidence, not manual visual or accessibility approval.

Product Owner QA remains required at 3440×1440 with 100% display scaling; browser zoom at 50%, 75%, and 100%; widths around every measured responsive transition; and with long endpoint URLs, model names, connection and validation errors, conversation identifiers, request paths, and status text. The review must cover loading, empty, warning, failure, disabled, unsaved, persisted/runtime-divergent, restart-required, and conversation-absence states; keyboard paths through navigation, Settings, Test Connection, reset, **Discard changes**, saves, and the Inspector; reduced motion; visible focus; and disabled/secondary-content contrast.

## Motion and reduced motion

Motion should communicate real state, not decoration.

Current motion surfaces:

- refresh/status micro-interactions;
- gauge transitions;
- Request Traffic updates;
- Connection Flow moving marker during active traffic;
- timeline entry updates;
- Conversation Inspector drawer transition.

Reduced-motion behavior must disable or simplify continuous animation and should never hide status information.

## Visual QA checklist

Before accepting layout changes, verify:

- Operations hero remains above the instrument panel.
- Top row contains only CPU Usage, GPU Usage, Memory Usage, Context Usage, and Compression Status.
- Second row contains Context Trend and Connection Flow.
- Traffic, Active Conversation, and Live Conversation Timeline remain grouped as operational/history content.
- Conversation Inspector opens without causing unpredictable card reflow.
- Settings navigation works by keyboard and the active page is announced by navigation semantics.
- Settings categories and controls remain readable at wide, standard, and narrow widths.
- Runtime Save, Save to configuration, and **Discard changes** accurately reflect clean, runtime-dirty, persistence-dirty, invalid, and in-progress states.
- Connection displays active, saved, default, and draft values distinctly, and both settings carry restart-required guidance.
- Test Connection uses the current drafts, prevents duplicate concurrent requests, shows latency/version on success and a clear reason on failure, and clears the old result after either draft changes.
- Candidate testing neither saves nor activates values and never overwrites the Operations page's active health/version presentation.
- Individual reset buttons have accessible setting-specific names and are visually and semantically disabled when already at default or otherwise unavailable.
- Category and global reset confirmations work by keyboard; Connection-only reset sends no PATCH, mixed reset PATCHes only runtime-editable values, cancellation changes no settings, and successful feedback distinguishes staged defaults from saved configuration.
- Loading, runtime success, reset-staged success, reset-cancelled, configuration success, validation, storage/network/server failure, discard, and retry feedback remain understandable without color alone.
- The separation notice remains visible and unambiguously explains PATCH, PUT, draft preservation, and no automatic restart.
- Reset does not clear application data, replace the full YAML document, or present itself as a factory reset.
- No clipping or horizontal overflow.
- Request Traffic, Connection Flow, Timeline, and Inspector remain readable under active polling.
- Reduced-motion mode is calm and still informative.

## Future layout boundaries

Future dashboard customization should preserve:

- instrument grouping;
- System Activity grouping;
- the Operations dashboard-as-observer architecture and the Settings page's explicit API-client boundary;
- single dashboard refresh path unless intentionally changed;
- privacy boundaries for prompt/response/summary content.
