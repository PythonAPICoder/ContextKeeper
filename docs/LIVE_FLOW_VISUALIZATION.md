# ContextKeeper Live Flow Visualization

## 1. Purpose

The Live Flow Visualization is the signature operational widget in ContextKeeper. It shows whether AI requests can move through the active path:

```text
Client
  |
ContextKeeper
  |
Ollama
  |
Model
```

The widget should make request flow, connection health, and failure location understandable at a glance. It must remain calm during normal operation and become more explicit only when user attention is required.

## 2. Visualization Goals

- Show whether the request path is connected.
- Show whether traffic is flowing.
- Identify the segment responsible for delays or failures.
- Reserve space for future packet animation.
- Scale from full desktop to compact desktop layouts.
- Support future multi-server and cloud-provider routing.

The visualization should communicate system state, not decorate the page.

## 3. Node Types

### Client Node

Purpose:

- Represents connected applications or users sending requests.

Primary information:

- client state
- number of recent clients
- last observed activity when available

States:

- waiting
- connected
- active
- warning
- disconnected

### ContextKeeper Node

Purpose:

- Represents the local proxy and orchestration layer.

Primary information:

- proxy status
- listening address or port
- routing/compression activity when relevant

States:

- online
- active
- warning
- error

### Ollama Node

Purpose:

- Represents the upstream Ollama service.

Primary information:

- reachability
- version when available
- latency when available

States:

- checking
- online
- slow
- warning
- offline
- error

### Model Node

Purpose:

- Represents the active or most recently used model.

Primary information:

- model name
- active/waiting state
- optional load or response state

States:

- waiting
- active
- streaming
- warning
- unavailable

## 4. Connection Types

### Client to ContextKeeper

Shows whether clients are reaching the proxy.

### ContextKeeper to Ollama

Shows whether the proxy can reach the upstream AI runtime.

### Ollama to Model

Shows whether a model is active or selected.

Rules:

- Connection lines should be muted when idle.
- Active lines may use restrained live-activity emphasis.
- Degraded lines must pair visual state with text.

## 5. Connection States

| State | Meaning |
| --- | --- |
| Connected | Segment is available and healthy |
| Idle | Segment is available but inactive |
| Streaming | Request or response stream is active |
| Warning | Segment is slow, unstable, or elevated risk |
| Disconnected | Segment is unavailable |
| Error | Segment has failed or returned an error |

Connection state must not rely on color alone. Use labels, icons, line style, node state, or supporting text.

## 6. Packet Animation Concepts

Flow packets are future animation placeholders.

Purpose:

- represent request movement
- represent streaming response movement
- show direction and activity

Rules:

- Packets should map to real request activity.
- Packet speed may reflect request rate or streaming state.
- Packets should be subtle during normal operation.
- Packet animation must pause or simplify when reduced motion is enabled.
- Do not animate packets for decoration.

## 7. Streaming Visualization

Streaming should be visible without becoming noisy.

Recommended behavior:

- show directional packet movement along active segments
- use a subtle pulse on the active node or connector
- display streaming state text where space allows
- avoid rapid flashing

Streaming should distinguish request direction from response direction when the interaction model supports it.

## 8. Error Visualization

Errors should identify the failing segment.

Rules:

- Mark the affected node or connector.
- Provide concise text explaining the failure.
- Do not make the entire flow appear failed if only one segment is degraded.
- Keep healthy segments visually distinct from failed segments.

Examples:

- Ollama offline: mark ContextKeeper to Ollama segment and Ollama node.
- No active model: mark Model node as waiting, not critical.
- Client not connected: mark Client node as waiting, not failed.

## 9. Reconnection Behavior

Reconnection should communicate recovery clearly.

Behavior:

- transition from offline to checking
- transition from checking to online or warning
- clear stale error emphasis after recovery
- optionally show a success event outside the flow widget

Do not use celebratory animation for recovery. Recovery should feel stable and factual.

## 10. Idle Behavior

Idle is a normal state.

Rules:

- Idle should look calm and available.
- Do not imply a failure when no client or model is active.
- Idle connectors should remain visible but low-emphasis.
- Empty text should explain the state, such as "No clients seen recently."

## 11. Future Multi-Server Support

The visualization must eventually support:

- multiple ContextKeeper instances
- multiple Ollama endpoints
- remote model providers
- cloud providers
- routed model paths
- fallback paths

Future layout options:

- stacked server lanes
- grouped provider clusters
- expandable routes
- selected route focus with secondary routes muted

The default Operations view should still focus on the active route.

## 12. Accessibility

Requirements:

- Every node has a text label.
- Every state has a text equivalent.
- Color is never the only state cue.
- Animation is optional and respects reduced-motion preferences.
- The flow path remains understandable when animation is disabled.

## 13. Layout Rules

- Full desktop: flow may be the largest visual element.
- Medium desktop: flow may become a two-row topology.
- Compact desktop: flow should remain readable with smaller nodes.
- Narrow width: flow may stack vertically.
- Node labels should remain visible at all sizes.
- Long details should truncate or move to tooltips/detail pages.
- Flow should not push all operational metrics below the fold.

## 14. Implementation Checklist

Before implementing or modifying the Live Flow Visualization, verify:

- The path Client -> ContextKeeper -> Ollama -> Model is clear.
- Every node has a purpose, label, and state.
- Every connector has a state.
- Idle, streaming, warning, disconnected, and error states are represented.
- Reduced-motion behavior is defined.
- Error state identifies the affected segment.
- Compact desktop layout remains readable.
- Multi-server expansion is not blocked by the layout.
