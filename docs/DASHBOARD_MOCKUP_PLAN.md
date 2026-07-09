# ContextKeeper Dashboard Mockup Plan

## Purpose

This document defines the target for the next high-fidelity dashboard mockup. The mockup must be reviewed and approved before additional UI code changes are made.

## Mockup Requirement

The high-fidelity mockup must be approved before UI implementation continues.

The mockup should show the intended dashboard composition, hierarchy, density, component states, and visual language clearly enough that implementation can proceed without redesigning in code.

## Overall Dashboard Layout

The dashboard remains a browser-rendered local operations console with these pages:

- Operations
- Conversations
- Context
- Analytics
- Logs
- Settings

Operations is the primary launch page. It should answer:

- Is everything healthy?
- Is traffic flowing?
- Do I need to act?

Detailed reports belong on secondary pages.

## Visual Hierarchy

Priority order:

1. Overall health state
2. Required operator action
3. Traffic and connection flow
4. Context pressure
5. Resource pressure
6. Detailed logs and history

The mockup should make the first three items understandable within seconds.

## Signature Connection Flow Widget

The Connection Flow widget should be the signature visual element.

Required topology:

```text
Client -> ContextKeeper -> Ollama -> Model
```

The mockup should define:

- node shape and styling
- connector styling
- healthy, waiting, warning, and offline states
- compact desktop layout
- full desktop layout
- future animation placeholders

Animation should not be implemented until the visual and interaction model is approved.

## System Health Score Concept

The mockup should explore a health score or health assessment concept.

Possible presentation:

- status phrase: "All Systems Operational"
- score or ring: 0-100
- state label: healthy, busy, warning, critical, offline
- short operator-readable explanation

The score must be understandable without requiring users to inspect raw metrics.

## Primary Dashboard Sections

Operations mockup must include:

- hero health/status area
- Recommendations / action area
- System Health metric
- Context Usage metric
- Request Statistics metric
- Connection Flow widget
- compact Traffic panel
- compact Resources panel
- compact Active Conversation summary

Secondary page mockups should cover:

- Conversations: active conversation, rolling summary, recent messages
- Context: token pressure, compression history, candidates
- Analytics: request trends, latency, insights, timelines
- Logs: live request activity
- Settings: proxy, Ollama, refresh, animation, and sound controls

## Responsive Targets

The mockup must include desktop states for:

- full ultrawide
- 3/4 ultrawide browser window
- half ultrawide browser window
- narrow desktop window

The dashboard should not require browser zoom below 100%.

Vertical scrolling is acceptable when needed, but no core card should feel clipped or accidentally squeezed.

## What Must Be Shown Before Implementation

Before UI code changes, the mockup must show:

- complete Operations page
- compact desktop Operations page
- Connection Flow full and compact layouts
- health states: healthy, attention, degraded
- empty Recommendations state
- active Recommendations state
- resource gauges
- context pressure states
- navigation active state
- loading or checking state

## Approval Gate

Do not make further UI implementation changes from this plan until the high-fidelity mockup has been approved.

Implementation work after approval should preserve:

- existing backend routes
- dashboard data contracts
- JavaScript-targeted DOM IDs unless a migration plan is approved
- browser-based local UI model
