# ContextKeeper Dashboard Layout

Status: Current through the Phase 6.5F-B6.3 working-tree implementation; Product Owner review is pending.

This document describes the current dashboard shell, Operations hierarchy, Settings page, and layout contract. It defines layout and user flow; source code remains authoritative for exact CSS and DOM details.

## Purpose

The ContextKeeper Operations dashboard is the primary AI operations console for the local proxy. It should help users understand system health, request flow, Context Usage, Compression activity, and required action without reading logs or reports. The Settings page provides a focused runtime-configuration surface without replacing or duplicating Operations.

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

Active Conversation shows selected/current conversation metadata and rolling-summary availability without exposing full private content in the Operations summary.

Live Conversation Timeline is a compact chronological operational feed for the active or most recently active conversation. Timeline entries that map to a real conversation can open the Conversation Inspector.

### Conversation Inspector drawer

Purpose:

- Provide selected-conversation drill-down while preserving dashboard context.

Current behavior:

- Opens from selectable Live Conversation Timeline entries.
- Uses a right-side drawer on desktop.
- Uses a backdrop/effectively full-width drawer on narrow layouts.
- Supports close button and Escape.
- Keeps polling active.
- Shows loading, unavailable, Overview, and Intelligence states.
- Does not show prompt text, response text, rolling-summary bodies, request bodies, or retrieved private content.

See `CONVERSATION_INSPECTOR.md` for the current inspector contract.

## Secondary dashboard pages

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
- Edit only controls that API metadata marks runtime-editable.
- Keep temporary edits visible until they are saved or discarded.
- Make the runtime-only, non-persistent behavior unambiguous.

Current hierarchy:

```text
Settings header and introduction
Runtime-only notice
Accessible status and error feedback
Loading, retry, or empty state
Metadata-driven category cards
Setting labels, descriptions, metadata, and controls
Sticky unsaved-change summary with Discard and Save
```

The page loads `GET /api/dashboard/settings` when first opened. Category cards and boolean, integer, and string controls are generated from the returned metadata. Read-only and restart-required states use explicit text or badges rather than color alone.

The browser maintains separate confirmed and draft snapshots. Save sends one changed-fields-only atomic `PATCH /api/dashboard/settings`; Discard restores the most recent confirmed snapshot without a network request. Failed saves leave the draft available for correction or retry. The visible notice states that changes reset on restart and do not modify `contextkeeper.yaml`.

Switching views does not register another Settings listener or multiply the existing dashboard polling timer. Operations polling and visualization updates continue through the same refresh lifecycle.

## Responsive behavior

Requirements:

- Preserve readability at 50%, 75%, and 100% browser zoom.
- Preserve wide-display usability, including 3440×1440 with 100% Windows display scaling.
- Collapse multi-column grids cleanly at narrower widths.
- Do not introduce horizontal page overflow.
- Ensure the Conversation Inspector becomes effectively full-width on narrow layouts.
- Allow Settings labels, descriptions, constraints, badges, and controls to wrap without compressing the form into unreadable columns.
- Stack Settings rows and the Save/Discard action area at the narrow breakpoint while keeping both actions reachable.
- Keep dashboard controls reachable while preserving context.

Manual review should include:

- 3440×1440.
- 2450×1440.
- 1720×1440.
- 50%, 75%, and 100% browser zoom.
- Narrow/mobile breakpoint.

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
- Save and Discard accurately reflect clean, dirty, invalid, and saving states.
- Loading, success, validation, network/server failure, discard, and retry feedback remain understandable without color alone.
- The runtime-only notice remains visible and unambiguously states that `contextkeeper.yaml` is not modified.
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
