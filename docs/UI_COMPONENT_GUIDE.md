# ContextKeeper UI Component Guide

## Purpose

This guide defines reusable dashboard components for the ContextKeeper browser UI. Components should support a stable operations-console experience across full desktop, snapped desktop, and narrow browser widths.

## App Shell

The app shell contains:

- sticky left sidebar navigation
- top status/header bar
- main page container
- page-level grid layout

Rules:

- Keep sidebar navigation persistent on desktop.
- Allow sidebar width to compact at medium desktop widths.
- Treat the browser UI as a desktop application; avoid landing-page composition.
- Page containers may scroll vertically when needed.

## Hero Health Card

The hero health card summarizes overall system state.

Content:

- operational status label
- status icon
- health message
- optional live/local badges

States:

- Healthy: "All Systems Operational"
- Attention: "Attention Required"
- Degraded: "System Degraded"
- Unknown/loading: "Checking Systems"

Rules:

- Must stay compact in Operations.
- Must not push core metrics below the fold at medium desktop widths.
- Should link visually to the System Health metric card.

## Metric Cards

Metric cards summarize key operational values.

Examples:

- System Health
- Context Usage
- Request Statistics
- Average Latency
- Request Rate

Rules:

- Prefer a label, primary value, and one supporting line.
- Use gauges only when they communicate threshold pressure.
- Avoid long prose inside metric cards.
- Medium desktop layouts should allow compact metric card variants.

## Status Badges

Badges communicate concise state.

Types:

- `healthy` / `positive`
- `busy` / `info`
- `warning`
- `critical` / `offline`
- `low`, `medium`, `high`

Rules:

- Badges must have text, not color alone.
- Use uppercase sparingly.
- Keep badge copy short.

## Context Ring

The context ring visualizes context-window pressure.

Inputs:

- usage percent
- threshold state
- token count summary

Rules:

- Ring color should follow system status conventions.
- Support compact sizing for medium desktop layouts.
- Always include the numeric percentage.

## Request and Latency Widgets

Request widgets show whether traffic is flowing and whether latency is healthy.

Components:

- total request count
- request rate
- trend label
- latency gauge
- sparkline

Rules:

- Operations page shows compact traffic state.
- Analytics page may show longer history and richer charts.
- Sparkline is supportive, not the primary value.

## Compression Timeline

Compression timeline shows context compression activity.

Content:

- compression count
- recent compression events
- conversation identifiers
- timestamps

Rules:

- Operations should only show compression risk or action state.
- Detailed history belongs on the Context page.
- Empty state should clarify that no compression events have occurred.

## Connection Flow Visualization

The Connection Flow widget is the dashboard signature element.

Topology:

```text
Client -> ContextKeeper -> Ollama -> Model
```

Current state:

- static topology
- live status dots
- placeholders for future animated traffic flow

Future state:

- animated request movement along connectors
- optional flow intensity based on traffic rate
- visible degraded/offline segments

Rules:

- Do not animate until the mockup and interaction model are approved.
- Must remain readable in compact desktop layouts.
- May become a two-row or vertical topology when width is constrained.
- Never hide endpoint status labels.

## Settings Toggles

Settings should eventually include controls for:

- animations enabled
- sound enabled
- refresh interval
- log visibility/detail
- Ollama endpoint configuration

Rules:

- Sound defaults to disabled.
- Animation defaults should respect reduced-motion preferences.
- Toggles must have clear labels and visible state.

## Empty, Error, and Loading States

Empty states:

- calm
- specific
- not alarming

Examples:

- "No operator action queued."
- "No request activity yet."
- "No recent activity."

Error states:

- include clear cause when known
- provide next action when available
- avoid exposing sensitive details

Loading states:

- use stable placeholders
- avoid layout shift
- avoid large spinners in Operations
