# ContextKeeper Component Library

Status: Current through Phase 6.5F-B5.5.2.

## 1. Purpose

This document defines the reusable UI component library for ContextKeeper.

The component library standardizes visual components used throughout the application so the interface remains consistent, scalable, and maintainable as ContextKeeper grows from a local AI Operations Console into broader multi-server, plugin, routing, memory, and agent workflows.

This document defines component behavior and usage. It does not define page layouts, color tokens, backend contracts, or implementation code.

## 2. Component Philosophy

Components should be:

- reusable
- compact
- readable
- state-aware
- consistent across screens
- suitable for dense operational workflows

Every component should answer one clear question. If a component needs to answer multiple unrelated questions, it should be split into smaller components or moved to a detail view.

Components should support:

- full desktop layouts
- compact desktop layouts
- narrow stacked layouts
- loading states
- empty states
- warning and error states

## 3. Card Components

### Health Card

Purpose:

- Communicates overall health or service health.

Primary information:

- status label
- short status message
- health indicator or score

Supported states:

- normal
- loading
- healthy
- warning
- critical
- offline

Recommended sizing:

- Full desktop: medium or large card.
- Compact desktop: reduced height and shorter message.
- Narrow layout: full-width stacked card.

Usage rules:

- Use for health state, not historical reporting.
- Do not include long explanations.
- Pair status color with text.

### Status Card

Purpose:

- Shows state for a specific service, connection, model, or subsystem.

Primary information:

- entity name
- status
- short supporting detail

Supported states:

- connected
- idle
- active
- warning
- disconnected
- error

Usage rules:

- Use one card per entity.
- Avoid duplicating the same status in adjacent cards.

### Metric Card

Purpose:

- Shows a numeric operational measurement.

Primary information:

- label
- primary value
- unit
- optional trend or sparkline

Supported states:

- normal
- loading
- warning
- error

Usage rules:

- One metric card should focus on one value.
- Detailed charts belong in Analytics.

### Summary Card

Purpose:

- Summarizes secondary information or a detail-page preview.

Primary information:

- title
- concise summary
- optional link to detail page

Usage rules:

- Keep summaries short.
- Use for launch-pad behavior, not full reports.

## 4. Status Components

### Status Badge

Purpose:

- Provides compact status labeling.

Primary information:

- state text

Supported states:

- healthy
- success
- busy
- warning
- critical
- offline
- unknown

Recommended sizing:

- Compact pill.
- Short labels only.

Usage rules:

- Do not rely on color alone.
- Use consistent state names across pages.

### Health Indicator

Purpose:

- Shows health state visually beside text.

Primary information:

- icon or dot
- health label

Supported states:

- healthy
- attention
- degraded
- offline
- checking

Usage rules:

- Pair with explicit text.
- Avoid decorative status pulses unless the state is live.

### Connection Indicator

Purpose:

- Shows whether a connection endpoint is reachable or active.

Primary information:

- connection state
- endpoint label

Supported states:

- connected
- idle
- streaming
- warning
- disconnected
- error

Usage rules:

- Use inside Connection Flow and service status cards.
- State should map to connection health, not general system health.

## 5. Metric Components

### Counter

Purpose:

- Shows a count, such as total requests or errors.

Primary information:

- number
- label

States:

- normal
- loading
- warning
- error

Usage rules:

- Use stable formatting.
- Avoid unnecessary animation for every refresh.

### Gauge

Purpose:

- Shows capacity, pressure, or load.

Primary information:

- value
- threshold state
- label

Usage rules:

- Use for percentages or bounded values.
- Always show the number.

### Progress Ring

Purpose:

- Shows circular progress for context, health, or capacity.

Primary information:

- percent
- threshold state

Usage rules:

- Avoid rings for unbounded metrics.
- Keep compact rings readable.

### Sparkline

Purpose:

- Shows a compact trend.

Primary information:

- recent directional movement

Usage rules:

- Sparkline is supporting information.
- Detailed charts belong in Analytics.

### Trend Indicator

Purpose:

- Shows whether a metric is improving, stable, or worsening.

Primary information:

- direction
- short label

States:

- up
- down
- flat
- unknown

Usage rules:

- Direction meaning must be clear. For latency, up may be bad; for throughput, up may be good.

## 6. Context Components

### Context Ring

Purpose:

- Shows context-window usage pressure.

Primary information:

- usage percent
- threshold state
- token estimate

Supported states:

- safe
- elevated
- warning
- compression threshold
- critical

Usage rules:

- Pair percentage with threshold label.
- Detailed token breakdown belongs on the Context page.

### Token Meter

Purpose:

- Shows token usage or estimated token count.

Primary information:

- used tokens
- total or estimated limit

Usage rules:

- Use when token count matters more than percentage.
- Include units.

### Threshold Indicator

Purpose:

- Marks warning and compression thresholds.

Primary information:

- threshold label
- threshold value

Usage rules:

- Use alongside context meters or rings.
- Avoid threshold-only cards.

## 7. Compression Components

### Compression Status

Purpose:

- Shows whether compression is normal, recommended, completed, or critical.

Primary information:

- compression state
- short reason

Supported states:

- none
- recommended
- in progress
- completed
- failed

Usage rules:

- Distinguish completed success from ongoing healthy state.
- Explain automated compression actions.

### Compression History

Purpose:

- Shows recent compression activity.

Primary information:

- timestamp
- conversation
- result

Usage rules:

- Operations should show only a summary.
- Full history belongs on the Context page.

### Summary Badge

Purpose:

- Indicates that a rolling summary or compressed memory exists.

Primary information:

- summary availability

Usage rules:

- Use in conversation and context views.
- Do not use as a generic status badge.

## 8. Connection Flow Components

### Connection Node

Purpose:

- Represents one point in the request path.

Primary information:

- node label
- status
- short detail

Supported nodes:

- Client
- ContextKeeper
- Ollama
- Model

Usage rules:

- Nodes should remain readable in compact layouts.
- Node state should not depend on color alone.

### Connection Line

Purpose:

- Represents a connection or request path between nodes.

Primary information:

- connection state

Supported states:

- idle
- active
- streaming
- warning
- disconnected
- error

Usage rules:

- Lines are muted unless active or degraded.
- Degraded lines should include supporting text or node state.

### Flow Packet

Purpose:

- Represents request movement during active traffic.

Primary information:

- request direction
- activity state

Usage rules:

- Do not implement decorative packets.
- Packet motion should represent real request flow or streaming activity.
- Preserve reduced-motion behavior.

## 9. Timeline Components

### Timeline Entry

Purpose:

- Represents one chronological operational event.

Primary information:

- timestamp
- event summary
- severity or type

Usage rules:

- Keep entries concise.
- Link to detail view when needed.

### Timestamp

Purpose:

- Shows when an event occurred.

Usage rules:

- Use consistent local time formatting.
- Avoid ambiguous relative-only times.

### Event Marker

Purpose:

- Visually marks event type or severity.

Usage rules:

- Pair marker with text.
- Avoid using marker color alone.

## 10. Conversation Inspector Components

### Inspector Drawer

Purpose:

- Provides selected-conversation drill-down while preserving the main Operations dashboard context.

Usage rules:

- Open from selectable Live Conversation Timeline entries.
- Use a right-side drawer on desktop.
- Use effectively full-width presentation on narrow layouts.
- Provide a visible close control and Escape close behavior.
- Do not add an independent polling loop.

### Inspector Overview Field

Purpose:

- Shows one factual selected-conversation metadata value.

Supported examples:

- conversation identifier
- state
- model
- client/source
- endpoint
- request type
- message count
- request count
- estimated tokens
- context-window capacity
- Context Usage
- Compression count
- last activity
- duration

Usage rules:

- Use stable DOM hooks for testable core fields.
- Truncate long identifiers visually while preserving the full value in an accessible title or equivalent.
- Use a calm placeholder for missing values.
- Escape externally derived display strings.

### Inspector Intelligence Card

Purpose:

- Shows deterministic context/compression health for the selected conversation.

Supported states:

- insufficient data
- healthy
- warning
- compression threshold reached
- compression present
- action required

Usage rules:

- Do not call an LLM.
- Base status only on existing context, threshold, compression, and conversation metadata.
- Show readable status text and supporting signals.
- Use red only for genuine degraded or critical states.
- Show recommendations only when action is genuinely appropriate.
- Do not expose prompts, responses, rolling-summary bodies, or request bodies.

## 11. Event Components

### Event Card

Purpose:

- Shows a recent operational event.

Primary information:

- event title
- short description
- severity

Usage rules:

- Use for important events, not every log line.

### Notification Banner

Purpose:

- Calls attention to temporary global information.

Supported states:

- information
- success
- warning
- error

Usage rules:

- Use sparingly.
- Must be dismissible when persistent.

### Recommendation Card

Purpose:

- Shows recommended operator action.

Primary information:

- recommendation
- priority
- optional action link

Supported states:

- none
- low
- medium
- high

Usage rules:

- Should remain compact on Operations.
- Full explanation belongs in Analytics or detail pages.

## 12. Navigation Components

### Sidebar Item

Purpose:

- Navigates between major application pages.

States:

- normal
- hover
- focus
- selected
- disabled

Usage rules:

- Selected state must be obvious.
- Icons should support scanning but not replace labels.

### Top Navigation

Purpose:

- Provides global context and high-level actions.

Usage rules:

- Keep compact.
- Do not overload with page-specific actions.

### Breadcrumb

Purpose:

- Shows location within nested views.

Usage rules:

- Use only when depth exists.
- Avoid breadcrumbs on the main Operations page.

### Toolbar Button

Purpose:

- Provides compact actions in dense views.

States:

- normal
- hover
- focus
- selected
- disabled
- loading

Usage rules:

- Use icons with accessible labels.
- Do not use toolbar buttons for unclear commands.

## 13. Input Components

### Search Box

Purpose:

- Filters logs, conversations, events, or settings.

States:

- empty
- focused
- populated
- disabled

Usage rules:

- Include clear placeholder text.
- Support clearing input.

### Filter

Purpose:

- Narrows data by state, type, time, or source.

Usage rules:

- Show active filters clearly.
- Avoid hidden filter state.

### Toggle

Purpose:

- Controls binary settings.

Examples:

- animations enabled
- sound enabled
- logging option

Usage rules:

- Label must describe the enabled state.
- Sound should default to disabled.

### Dropdown

Purpose:

- Selects from a constrained set of options.

Usage rules:

- Use when options are known.
- Avoid dropdowns for primary navigation.

### Action Button

Purpose:

- Triggers a command.

States:

- normal
- hover
- focus
- disabled
- loading
- destructive

Usage rules:

- Label should be specific.
- Destructive actions require confirmation.

## 14. Dialog Components

### Confirmation Dialog

Purpose:

- Confirms significant or destructive actions.

Usage rules:

- Explain the action and consequence.
- Provide clear cancel path.

### Settings Dialog

Purpose:

- Edits configuration without leaving context.

Usage rules:

- Prefer full Settings page for complex configuration.
- Use dialogs for small scoped edits.

### About Dialog

Purpose:

- Shows version, build, runtime, and product information.

Usage rules:

- Keep informational.
- Do not include operational controls.

## 15. Empty States

Purpose:

- Communicate that no data is available yet.

Rules:

- Empty states should be calm.
- Explain what is missing.
- Avoid implying failure unless there is an actual error.

Examples:

- No request activity yet.
- No recommendations queued.
- No recent compression events.

## 16. Loading States

Purpose:

- Hold layout stability while data loads.

Rules:

- Avoid layout shift.
- Use concise loading text.
- Avoid large spinners in Operations.
- Preserve component dimensions where possible.

## 17. Error States

Purpose:

- Explain failures and guide operator action.

Rules:

- State what failed.
- Provide next action when available.
- Avoid exposing sensitive details.
- Preserve compatibility with client-facing proxy behavior.

## 18. Component Rules

- One component answers one question.
- Components should not duplicate nearby information.
- Cards should align consistently.
- Components should scale from full desktop to compact layouts.
- Similar information should use similar component types.
- State behavior should be consistent across pages.
- Loading and empty states should not cause layout shift.
- Error states should be clear without being visually noisy.
- Decorative elements should not compete with operational state.

## 19. Future Components

Reserve patterns for:

- Plugin cards.
- Agent cards.
- Multi-server cards.
- Cloud provider cards.
- Workspace memory cards.

Future components should follow existing card, status, metric, and navigation patterns unless a new pattern is clearly justified.

## 20. Implementation Checklist

Before creating or modifying reusable UI components, verify:

- The component answers one clear question.
- The component has defined normal, hover, focus, selected, disabled, loading, warning, and error behavior where applicable.
- The component does not duplicate nearby information.
- The component scales to compact desktop layouts.
- The component has an empty state when data may be missing.
- The component has a loading state when data is asynchronous.
- The component has an error state when failure is possible.
- Similar information uses the same component type elsewhere.
- The component supports accessibility through labels, focus state, and non-color status cues.
- The component can be reused without page-specific assumptions.
