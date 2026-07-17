# ContextKeeper Animation Guidelines

Status: Current through Phase 6.5F-B5.6.

## 1. Purpose

This document defines animation behavior for ContextKeeper.

Animation must communicate operational information. It should never be decorative, distracting, or required to understand system state.

## 2. Motion Philosophy

Motion in ContextKeeper should:

- clarify state changes
- show live request flow
- confirm user interaction
- support real-time observability
- remain calm during normal operation

Avoid:

- decorative loops
- flashy transitions
- bouncing or playful motion
- animation that implies urgency when none exists
- motion that hides or delays important information

## 3. Timing

Recommended durations:

- Hover feedback: 120ms to 180ms.
- Focus feedback: immediate to 120ms.
- Card state transition: 160ms to 240ms.
- Status transition: 180ms to 300ms.
- Notification entrance: 180ms to 260ms.
- Flow packet movement: based on request/stream state, generally slow and readable.

Critical state changes should be prompt, not dramatic.

## 4. Easing

Recommended easing:

- Standard UI transitions: `ease-out`.
- State transitions: `cubic-bezier(0.2, 0, 0, 1)`.
- Hover transitions: `ease`.
- Flow movement: linear or near-linear when representing real traffic.

Avoid elastic, bounce, or exaggerated easing.

## 5. Hover Animations

Allowed hover behavior:

- subtle border emphasis
- slight surface shift
- low-opacity accent highlight
- small icon opacity change

Rules:

- Hover must not look like warning or error state.
- Avoid large movement.
- Do not animate layout dimensions on hover.

## 6. Card Transitions

Cards may transition:

- border color
- background surface
- elevation
- status accent

Rules:

- Keep card transitions subtle.
- Avoid expanding cards on hover.
- Avoid transitions that cause layout shift.

## 7. Status Transitions

Status transitions should help users notice state changes.

Allowed:

- status dot pulse for live/checking state
- brief value update feedback
- smooth gauge transition
- badge state transition

Rules:

- Warning and critical states should be clear but not flashing.
- Recovery should feel stable and factual.
- Never use rapid flashing status colors.

## 8. Flow Animation

Flow animation is reserved for real request movement.

Allowed:

- packet movement from Client to ContextKeeper to Ollama to Model
- subtle streaming pulse on active connector
- low-intensity activity shimmer on active path

Rules:

- No flow animation without related activity.
- Do not animate idle flow.
- Animation must pause or simplify when reduced motion is enabled.
- Flow animation should not obscure node labels.

## 9. Timeline Animation

Timeline entries may use light entrance animation when new items arrive.

Rules:

- New event movement should be subtle.
- Do not animate every refresh if data is unchanged.
- Avoid reordering animations that make chronology hard to follow.

## 10. Notification Animation

Notifications may enter and exit with short transitions.

Rules:

- Entrance should not cover critical content.
- Persistent alerts must not pulse continuously.
- Dismissal should be immediate and predictable.

## 11. Loading Animation

Loading should preserve layout stability.

Allowed:

- static skeleton area
- subtle shimmer for longer loading states
- checking text
- low-intensity progress indicator

Rules:

- Avoid large spinners in Operations.
- Loading states should not shift layout.
- Loading animation should not look like live traffic.

## 12. Reduced-Motion Behavior

When reduced motion is enabled:

- disable decorative transitions
- replace flow packets with static active state
- disable continuous pulse unless essential
- preserve all state labels and values

The UI must remain fully understandable without animation.

## 13. Performance Guidelines

Animation should:

- use opacity and transform when possible
- avoid layout-triggering animation
- avoid animating large blurred surfaces
- avoid excessive simultaneous animations
- remain smooth on local desktop hardware

Operations should prioritize real-time data clarity over visual effects.

## 14. Animation Rules

- Animation communicates information.
- Idle state remains quiet.
- Critical state is explicit, not flashy.
- Motion must not delay user action.
- Motion must respect accessibility preferences.
- Animation should be consistent for similar components.

## 15. Implementation Checklist

Before adding animation, verify:

- The animation has an operational purpose.
- The state remains clear without animation.
- Reduced-motion behavior is defined.
- The animation does not cause layout shift.
- The animation does not obscure labels or values.
- The animation does not compete with health or action state.
- The timing and easing match ContextKeeper standards.
