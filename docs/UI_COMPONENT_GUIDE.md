# ContextKeeper UI Component Guide

Status: Current through the Phase 6.5F-B6.5 working-tree implementation; Product Owner and architect review are pending.

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
- Identify the active destination visually and with navigation semantics.
- Switch between Operations and Settings within the shell without registering duplicate listeners or refresh timers.
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

- topology nodes
- live status dots
- readable status labels and badges
- animated moving marker during active traffic
- visible degraded/offline segments

Rules:

- Animate only real request/stream activity.
- Respect `prefers-reduced-motion`.
- Must remain readable in compact desktop layouts.
- May become a two-row or vertical topology when width is constrained.
- Never hide endpoint status labels.

## Live Conversation Timeline

The Live Conversation Timeline shows a compact operational narrative for the active or most recently active conversation.

Content:

- timestamp
- event title
- short operational detail
- severity/type marker

Rules:

- Do not expose prompt text, response text, rolling-summary body text, or request bodies.
- Keep the event list bounded.
- Make conversation-backed entries selectable for the Conversation Inspector.
- Use stable event IDs to avoid duplicate DOM insertion during polling.

## Conversation Inspector

The Conversation Inspector is a right-side drawer opened from selectable timeline entries.

Current sections:

- Overview
- Intelligence

Rules:

- Keep the main dashboard visible on desktop.
- Use loading, unavailable, and metadata states that are mutually exclusive.
- Preserve keyboard access and Escape close behavior.
- Use deterministic metadata and aggregate signals only.
- Do not add transcript browsing until a later inspector phase.

## Settings Page Controls

The Settings page renders categories and controls from schema-v2 `GET /api/dashboard/settings` metadata. It does not maintain a browser-side list of setting identities, built-in defaults, reset eligibility, or persistence rules.

Components:

- visible runtime-versus-saved configuration notice;
- category cards with API-provided names and descriptions;
- category reset actions with native confirmation;
- setting labels and descriptions;
- runtime, saved configuration, default, and minimum/maximum metadata where supplied;
- dynamic draft/runtime/saved difference text;
- runtime read-only, not-persistable, runtime-differs-from-saved, and restart-required badges;
- boolean checkbox, integer number input, and string text input renderers;
- setting-specific reset buttons with accessible names and semantic disabled states;
- polite status region and assertive error summary;
- loading, retry, empty, and error states;
- typed runtime/persistence change summary;
- Discard runtime changes, Save to configuration, Save runtime changes, and **Reset managed settings to defaults** actions.

Rules:

- Use API metadata as the authority for setting identity, display text, runtime/persisted/default values, type, constraint, runtime editability, persistence eligibility, reset eligibility, difference state, and restart guidance.
- Associate every control with a visible label and descriptive metadata.
- Render API text with safe DOM text operations rather than HTML injection.
- Keep a control editable when its setting is runtime-editable or persistable; disable it only when neither action is allowed, and explain partial availability explicitly.
- Preserve boolean, numeric, and string values in the draft without type conversion artifacts.
- Keep confirmed server state separate from editable draft state.
- Calculate runtime changes against confirmed `value` and persistence changes against confirmed `persisted_value`, using strict typed equality.
- Render an individual reset only for supported metadata, and enable it only when `reset_eligible` is true, runtime differs from `default_value`, and no conflicting request is pending.
- Give every individual reset a setting-specific accessible name and native button semantics.
- Submit an individual reset immediately as a single-setting PATCH using `default_value`; do not require confirmation for this one-setting action.
- Require native keyboard-operable confirmation for category reset and **Reset managed settings to defaults**. Build one PATCH containing all and only reset-eligible settings in scope, including eligible values already at default; disable the scoped action when every eligible value is already at default. Cancellation sends no request.
- Accept the canonical PATCH snapshot after reset and announce that defaults are staged and reset did not write configuration. Report how many settings were staged where practical, direct the user to Save when persisted values differ, and state when persisted values already match and need no save.
- Enable Save runtime changes only for a valid changed runtime-editable draft; it sends one atomic PATCH containing only those values.
- Enable Save to configuration only for valid persistable draft values that differ from saved configuration; it sends one explicit PUT to `/api/dashboard/settings/config` containing only those values.
- Never persist from an input/change event, runtime form submit, page switch, refresh timer, or initial load.
- On PUT success, accept refreshed metadata and restore the user's draft values so disk-only changes are not silently applied to runtime.
- Discard restores browser-only draft edits locally. When confirmed runtime differs from persisted state, send one atomic PATCH using `persisted_value` for every runtime-editable differing setting, accept its canonical snapshot, and never write YAML.
- Preserve the draft and relevant dirty state after validation, storage, network, server, or malformed-response failure.
- Disable conflicting editing, reset, Discard, and save actions while a request is pending; change action labels where appropriate to communicate in-progress state.
- Keep the separation notice visible: reset stages built-in defaults in runtime, Discard restores persisted/effective runtime values, configuration Save is required for restart persistence, and none of these actions restarts ContextKeeper.
- Never describe managed reset as a factory reset or imply that it deletes YAML or clears logs, metrics, conversations, summaries, models, or other application data.
- Use visible focus indicators, live feedback, explicit state text, and native keyboard-operable controls.
- Stack setting rows, individual/category/global reset controls, and all save/discard controls cleanly at narrow widths.
- Respect reduced-motion preferences without removing status information.

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
- preserve Settings draft values when a save fails

Loading states:

- use stable placeholders
- avoid layout shift
- avoid large spinners in Operations
- provide a safe retry action when Settings cannot be loaded
