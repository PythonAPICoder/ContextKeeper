# ContextKeeper Dashboard Layout

## 1. Purpose

This document defines the visual layout and information architecture for the ContextKeeper Operations Dashboard.

The Operations Dashboard is the primary AI Operations Console surface. It should help users understand system health, request flow, context pressure, compression activity, and required action without reading a report.

This document defines layout, hierarchy, spacing, and user flow. It does not define colors, typography, backend contracts, or implementation code.

## 2. Dashboard Design Goals

- Communicate overall system health within three seconds.
- Present status before configuration.
- Make live request flow visually central.
- Show only the information needed for operational awareness.
- Avoid duplicate information.
- Avoid clutter and dense report-style layouts.
- Keep critical information above the fold during normal desktop operation.
- Provide clear paths to detail pages for deeper investigation.

The dashboard should feel like a live operations console, not a static reporting screen.

## 3. Information Hierarchy

The dashboard should prioritize information in this order:

1. Overall Health
2. User Action Required
3. Live Request Flow
4. Operational Metrics
5. Context Pressure
6. Compression Activity
7. Timeline
8. Events
9. Detailed Logs

Detailed logs and long history should not compete with the main Operations view. They belong in secondary views or expandable detail areas.

## 4. Overall Page Structure

The dashboard uses a 12-column responsive grid inside the main content area.

Recommended desktop structure:

```text
Header
Primary Status Row
Live Connection Flow Area
Operational Metrics + Context & Compression
Activity Timeline + Event Feed
Footer / Status Bar
```

Recommended grid:

- Page max width: fluid, fills available browser width.
- Grid columns: 12.
- Desktop gutter: 16px.
- Compact desktop gutter: 12px.
- Narrow gutter: 8px.
- Outer page margin: 16px to 24px on desktop.
- Compact desktop page margin: 12px to 16px.

The page should scan naturally from top to bottom. Users should not need to inspect side panels before understanding primary health and flow.

## 5. Header Layout

The header provides persistent application context and global access.

Required content:

- Application title: ContextKeeper.
- Connection summary: proxy port and Ollama endpoint.
- Global status: concise health state.
- Settings access: link or button to Settings.

Recommended layout:

- Header spans all 12 columns.
- Application title aligns left.
- Connection summary and Settings access align right.
- Header height should remain compact.
- Header should not compete visually with the Primary Status Row.

Header sizing:

- Full desktop height: 56px to 72px.
- Compact desktop height: 44px to 56px.
- Avoid multiline header content unless width is narrow.

## 6. Primary Status Row

The Primary Status Row provides the fastest answer to system state.

Required components:

- Overall Health card.
- User Action Required / Recommendations card.
- Ollama status.
- ContextKeeper status.
- Active Model status.
- Connected Clients status.

Recommended full desktop layout:

- Overall Health spans 3 to 4 columns.
- Recommendations spans 3 to 4 columns.
- Service status cards use remaining columns.
- Cards align to a shared height.

Recommended compact desktop layout:

- Overall Health and Recommendations may stack in a left column.
- Service status cards may form a 2-column or 3-column compact grid.
- Cards should reduce height before pushing Live Connection Flow too far down.

Rules:

- Each card answers one question.
- Recommendations should remain compact when no action is required.
- Long explanatory text should move to detail pages.
- Empty states must remain visually balanced.

## 7. Live Connection Flow Area

The Live Connection Flow is the dashboard centerpiece.

Required topology:

```text
Client -> ContextKeeper -> Ollama -> Model
```

Purpose:

- Show whether the request path is connected.
- Show where traffic is flowing.
- Show degraded or disconnected segments.
- Reserve space for future animated request flow.

Recommended layout:

- Full desktop: spans all 12 columns.
- Compact desktop: spans all available width below the Primary Status Row.
- Minimum supported width: may become a two-row or vertical topology.

Sizing:

- Full desktop height: 240px to 320px.
- Compact desktop height: 140px to 220px.
- Narrow layout: height determined by stacked node cards.

Rules:

- The flow area should be the largest visual element on full desktop.
- Do not make it so tall that operational metrics disappear below the fold.
- Connection nodes should remain readable at every supported width.
- Animation space should be reserved but not required for static layout.

## 8. Operational Metrics Area

Operational Metrics show whether traffic is healthy.

Required metrics:

- Requests.
- Latency.
- Throughput.
- Tokens.
- Errors.

Recommended layout:

- Full desktop: metric cards span 6 to 8 columns total.
- Compact desktop: use a 2-column grid.
- Narrow layout: stack cards vertically.

Each metric card should include:

- label
- primary value
- short supporting text or trend
- optional compact visualization

Rules:

- Metrics should not duplicate the Primary Status Row unless they add detail.
- Charts should remain compact on Operations.
- Detailed trend analysis belongs in Analytics.

## 9. Context & Compression Area

This area explains context pressure and compression state.

Required content:

- Context usage.
- Compression status.
- Memory indicators.

Recommended layout:

- Full desktop: sits beside Operational Metrics.
- Compact desktop: may share a row with Resources or Active Conversation.
- Narrow layout: stack below Traffic.

Rules:

- Context usage must show pressure state and value.
- Compression status should distinguish normal, recommended, completed, and critical states.
- Memory indicators should remain concise.
- Detailed compression history belongs on the Context page.

## 10. Activity Timeline

The Activity Timeline shows chronological operational history.

Content:

- request summaries
- compression events
- warnings
- health transitions

Recommended layout:

- Full desktop: lower section, 6 to 8 columns.
- Compact desktop: below core metrics or behind a detail link if space is constrained.
- Narrow layout: stack below metrics.

Rules:

- Timeline items should be concise.
- Use timestamps consistently.
- Do not show full logs in the Operations timeline.

## 11. Event Feed

The Event Feed shows recent operational events.

Content:

- informational messages
- errors
- notifications
- service state changes

Recommended layout:

- Full desktop: beside Activity Timeline.
- Compact desktop: below Traffic and Resources.
- Narrow layout: stack or link to Logs.

Rules:

- Events should be scannable.
- Errors must be clear and actionable.
- Informational events should not look urgent.
- Detailed logs belong on the Logs page.

## 12. Footer / Status Bar

The Footer or Status Bar provides runtime metadata.

Required content:

- Version.
- Build.
- Runtime.
- Uptime.

Recommended layout:

- Full desktop: compact horizontal bar at bottom.
- Compact desktop: single-line metadata where possible.
- Narrow layout: wrap metadata or move to Settings/About.

Rules:

- Footer content must not compete with operational status.
- Footer may be omitted from the above-the-fold area if space is constrained.

## 13. Responsive Layout Behavior

### Full-Screen Desktop

Target examples:

- 2560x1440.
- 3440x1440.

Behavior:

- Use rich 12-column layout.
- Primary Status Row and Live Connection Flow appear above the fold.
- Operational Metrics and Context & Compression should begin above the fold.
- No scrolling should be required for normal operational awareness.

### 75% Desktop Width

Target example:

- Browser window around 1400px to 1900px wide.

Behavior:

- Use compact desktop layout.
- Primary status cards may reorganize into a denser grid.
- Recommendations should remain compact.
- Connection Flow may become a two-row topology.
- Traffic, Resources, and Active Conversation should remain visible or begin above the fold.

### Minimum Supported Width

Target example:

- Browser window around 1100px to 1350px wide.

Behavior:

- Use compact desktop mode before switching to mobile stacking.
- Reduce card padding, gaps, and min-heights.
- Keep top metrics, full Connection Flow, and at least Traffic and Resources reachable with minimal scrolling.
- Below this range, vertical stacking and scrolling are acceptable.

## 14. Expansion Strategy

Reserve layout capacity for future features without crowding Operations.

Future expansion areas:

- Multi-server monitoring.
- Plugin panels.
- Agent monitoring.
- Cloud providers.
- Workspace memory.

Rules:

- New features should not be added directly to Operations unless they affect health, flow, or immediate action.
- Detail-heavy features should receive dedicated pages or drill-down panels.
- Operations should remain the launch pad.

## 15. Layout Rules

- One component should answer one question.
- No scrolling should be required during normal desktop operation.
- Critical information should always remain above the fold.
- Cards should align consistently.
- Similar information should use similar sizing.
- Empty states should remain visually balanced.
- Avoid duplicate information across adjacent cards.
- Long text should be truncated, summarized, or moved to detail pages.
- Compact layouts should feel intentional, not squeezed.
- Connection Flow should remain readable before decorative details are preserved.

## 16. Future Expansion

The dashboard layout must support future growth toward:

- multi-server operations
- plugin lifecycle monitoring
- agent execution monitoring
- model routing visibility
- workspace memory observability
- cloud provider status

Future dashboard extensions should preserve the primary hierarchy:

1. Health.
2. Action.
3. Flow.
4. Metrics.
5. Context.
6. Events.
7. Details.

## 17. Implementation Checklist

Before implementing or modifying dashboard layouts, verify:

- The layout communicates overall health within three seconds.
- The page reads naturally from top to bottom.
- The Primary Status Row appears above the Live Connection Flow.
- Live Connection Flow is visually central.
- Critical information remains above the fold on full desktop.
- Compact desktop widths remain usable at 100% zoom.
- Cards align to the 12-column grid.
- Similar components use similar sizing.
- Each component answers one clear question.
- Empty states are balanced and not visually broken.
- Detailed logs and long history are not shown directly in Operations.
- Future multi-server, plugin, agent, cloud, and memory areas have an expansion path.
