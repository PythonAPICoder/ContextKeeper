# ContextKeeper Live Flow Visualization

Status: Current through Phase 6.5F-B5.4.2.

The Connection Flow visualization is the signature operational widget in ContextKeeper. It shows whether requests can move through the active path:

```text
Client -> ContextKeeper -> Ollama -> Model
```

It is part of the System Activity row beside Context Trend.

## Goals

- Show whether the request path is available.
- Show whether traffic is actively flowing.
- Identify which segment is waiting, active, warning, offline, or failed.
- Keep the visualization calm during normal operation.
- Preserve reduced-motion support.
- Scale from wide desktop to compact layouts.

The visualization should communicate system state, not decorate the page.

## Nodes

### Client

Represents connected applications or users sending requests.

Primary information:

- client state;
- recent client count;
- last observed activity when available.

### ContextKeeper

Represents the local proxy and orchestration layer.

Primary information:

- proxy status;
- listening port;
- activity state.

### Ollama

Represents the configured upstream Ollama runtime.

Primary information:

- reachability;
- version when available;
- latency when available.

### Model

Represents the active or most recently observed model.

Primary information:

- model name;
- waiting/active/observed state;
- model warmup or unavailable state when known.

## Connection segments

- Client to ContextKeeper.
- ContextKeeper to Ollama.
- Ollama to Model.

Rules:

- Idle connections are muted.
- Active connections receive restrained emphasis.
- Degraded connections pair visual state with text and badges.
- Status is never communicated by color alone.

## Moving marker

The current implementation includes a restrained moving marker on the SVG connection path during active traffic.

Requirements:

- The marker represents real request/stream activity.
- The marker must be visible enough to distinguish from the static connector path.
- The marker uses a moderately larger dot and subtle halo after the B5.4.2 visibility polish.
- The marker must not resemble a flashing alert.
- Animation speed and direction should remain stable unless a future phase explicitly changes behavior.
- Inactive state must not imply active traffic.

Reduced-motion behavior:

- Continuous marker animation is disabled or hidden under `prefers-reduced-motion`.
- State labels, badges, and node text remain the source of truth when motion is reduced.

## Error and degraded states

Errors should identify the failing segment.

Examples:

- No client activity: Client node waits while proxy and Ollama may remain healthy.
- Ollama offline: ContextKeeper-to-Ollama segment and Ollama node indicate the failure.
- No model observed: Model node waits without implying proxy failure.
- Request failure: activity and recent request diagnostics show failure state.

## Responsive behavior

The full horizontal topology is preferred on desktop. At narrower widths, the layout may stack while preserving node order and status readability.

Manual review should confirm:

- no clipping;
- no horizontal overflow;
- labels and badges remain readable;
- active marker remains visible on desktop;
- reduced-motion mode remains calm.

## Future considerations

Future versions may extend Connection Flow for:

- multiple Ollama backends;
- cloud-provider routing;
- model routing;
- validation traffic;
- richer bidirectional streaming visualization.

These are not current Version 1 implementation commitments unless promoted in `ROADMAP.md`.
