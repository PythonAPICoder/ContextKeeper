# ContextKeeper Dashboard Mockups

Status: Superseded historical planning document. These text mockups preserve earlier design direction, but they are not the current dashboard contract. The current dashboard includes the grouped system instrument panel, System Activity row with Context Trend and Connection Flow, Request Traffic, Live Conversation Timeline, and Conversation Inspector drawer. Use `DASHBOARD_LAYOUT.md`, `CONVERSATION_INSPECTOR.md`, `PROJECT_HISTORY.md`, and source code for current behavior.

## 1. Purpose

This document provides textual dashboard mockups for ContextKeeper. These mockups define the intended structure for full desktop, 75% desktop, and compact layouts.

The mockups describe layout and information placement only. They do not define implementation code.

## 2. Full Desktop Layout

Target:

- 2560x1440
- 3440x1440

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Header: ContextKeeper        Proxy / Ollama / Global Status / Settings       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Overall Health │ Recommendations │ Ollama │ ContextKeeper │ Model │ Clients │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│        Live Connection Flow: Client -> ContextKeeper -> Ollama -> Model       │
│                                                                              │
├───────────────────────────────┬──────────────────────────┬───────────────────┤
│ Operational Metrics           │ Context & Compression    │ Resources         │
│ Requests / Latency / Errors   │ Context / Memory / Comp. │ CPU / RAM / VRAM  │
├───────────────────────────────┴──────────────────────────┬───────────────────┤
│ Activity Timeline                                         │ Event Feed        │
├────────────────────────────────────────────────────────────┴───────────────────┤
│ Footer: Version / Build / Runtime / Uptime                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

Region contents:

- Header: application title, connection summary, global status, Settings access.
- Primary Status Row: overall health, required action, service status.
- Live Connection Flow: centerpiece path and future animation space.
- Operational Metrics: requests, latency, throughput, tokens, errors.
- Context & Compression: context pressure, compression status, memory indicators.
- Timeline: request summaries, compression events, warnings.
- Event Feed: recent events, notifications, errors.
- Footer: version, build, runtime, uptime.

## 3. 75% Desktop Layout

Target:

- Browser width around 1400px to 1900px.

```text
┌────────────────────────────────────────────────────────────┐
│ Header: ContextKeeper        Connection Summary / Settings │
├───────────────────────┬────────────────────────────────────┤
│ Overall Health         │ Health / Context / Request Metrics │
│ Recommendations        │ Service Status Cards               │
├───────────────────────┴────────────────────────────────────┤
│ Live Connection Flow: compact horizontal or two-row topology│
├──────────────────────────────┬──────────────────────────────┤
│ Traffic                      │ Resources                    │
├──────────────────────────────┼──────────────────────────────┤
│ Active Conversation          │ Context & Compression         │
├──────────────────────────────┴──────────────────────────────┤
│ Timeline / Events                                            │
└──────────────────────────────────────────────────────────────┘
```

Behavior:

- Primary status compresses before pushing flow down.
- Recommendations stays compact.
- Connection Flow remains fully visible.
- Traffic and Resources should begin above the fold.

## 4. Compact Layout

Target:

- Browser width around 1100px to 1350px.

```text
┌──────────────────────────────────────────────┐
│ Header: compact title / status / settings    │
├───────────────┬───────────────┬──────────────┤
│ Health Hero   │ System Health │ Context      │
│ Actions       │ Requests      │ Status       │
├───────────────┴───────────────┴──────────────┤
│ Live Flow: 2x2 compact topology              │
│ Client -> ContextKeeper                      │
│ Model  <- Ollama                             │
├───────────────────────┬──────────────────────┤
│ Traffic               │ Resources            │
├───────────────────────┴──────────────────────┤
│ Active Conversation / Context Summary         │
├──────────────────────────────────────────────┤
│ Timeline / Events / Logs links                │
└──────────────────────────────────────────────┘
```

Behavior:

- Cards use compact padding and reduced min-heights.
- Top metrics stay visible at 100% zoom.
- Full Connection Flow is visible with minimal scrolling.
- Traffic and Resources remain visible or begin immediately after flow.
- Narrower widths may stack vertically.

## 5. Header

Contains:

- ContextKeeper title.
- connection summary.
- global status.
- Settings access.

Rules:

- Keep compact.
- Do not add detailed controls.
- Status remains visible before configuration.

## 6. Primary Status Row

Contains:

- overall health.
- recommendations.
- Ollama.
- ContextKeeper.
- active model.
- connected clients.

Rules:

- Answer health and action first.
- Do not duplicate detailed metrics.
- Empty recommendations should be calm and compact.

## 7. Live Connection Flow

Contains:

- Client node.
- ContextKeeper node.
- Ollama node.
- Model node.
- connection lines.
- future packet animation space.

Rules:

- Full desktop: largest visual element.
- 75% desktop: compact horizontal or two-row layout.
- Compact: 2x2 topology.
- Motion is reserved for actual request flow.

## 8. Operational Metrics

Contains:

- requests.
- latency.
- throughput.
- tokens.
- errors.

Rules:

- Use compact cards.
- Show primary value first.
- Move deeper trends to Analytics.

## 9. Context & Compression

Contains:

- context pressure.
- compression status.
- memory indicators.

Rules:

- Show state and value.
- Explain compression action when it occurs.
- Move history to Context page.

## 10. Timeline

Contains:

- chronological operational history.
- request summaries.
- compression events.
- warnings.

Rules:

- Keep entries concise.
- Avoid full logs.

## 11. Events

Contains:

- recent operational events.
- notifications.
- errors.

Rules:

- Errors must be clear.
- Informational events should not look urgent.

## 12. Footer

Contains:

- version.
- build.
- runtime.
- uptime.

Rules:

- Keep compact.
- May move to Settings/About when width is constrained.

## 13. Mockup Approval Rule

High-fidelity visual mockups should be approved before major UI implementation changes. Implementation should follow the design language, color system, layout guide, component library, and animation guidelines.
