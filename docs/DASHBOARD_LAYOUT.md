# ContextKeeper Dashboard Layout

Status: Current through Phase 6.5F-B5.5.2.

This document describes the current Operations dashboard visual hierarchy and layout contract. It defines layout and user flow; source code remains authoritative for exact CSS and DOM details.

## Purpose

The ContextKeeper Operations dashboard is the primary AI operations console for the local proxy. It should help users understand system health, request flow, Context Usage, Compression activity, and required action without reading logs or reports.

## Layout principles

- Communicate system health quickly.
- Keep runtime status above detailed history.
- Group instruments with instruments and activity visualizations with activity visualizations.
- Preserve live dashboard context while drill-down surfaces are open.
- Avoid horizontal overflow.
- Preserve reduced-motion support.
- Keep prompt, response, rolling-summary, and request-body content out of routine dashboard surfaces.

## Current page structure

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

These pages remain subordinate to the Operations dashboard and should not duplicate the core Operations hierarchy unless a later phase intentionally redesigns navigation.

## Responsive behavior

Requirements:

- Preserve readability at 50%, 75%, and 100% browser zoom.
- Preserve wide-display usability, including 3440×1440 with 100% Windows display scaling.
- Collapse multi-column grids cleanly at narrower widths.
- Do not introduce horizontal page overflow.
- Ensure the Conversation Inspector becomes effectively full-width on narrow layouts.
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
- No clipping or horizontal overflow.
- Request Traffic, Connection Flow, Timeline, and Inspector remain readable under active polling.
- Reduced-motion mode is calm and still informative.

## Future layout boundaries

Future dashboard customization should preserve:

- instrument grouping;
- System Activity grouping;
- dashboard-as-observer architecture;
- single dashboard refresh path unless intentionally changed;
- privacy boundaries for prompt/response/summary content.
