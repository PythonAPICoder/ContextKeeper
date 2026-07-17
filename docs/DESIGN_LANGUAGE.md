# ContextKeeper Design Language

Status: Current through Phase 6.5F-B5.6.

## 1. Vision

ContextKeeper is an AI Operations Console for local and distributed AI systems.

The interface should help users understand system health, request flow, context pressure, and required action within three seconds. It should feel calm, polished, enterprise-grade, and built for real-time observability.

ContextKeeper is not a generic dashboard. It is an operations surface for monitoring and controlling AI infrastructure.

## 2. Design Goals

- Make system health immediately understandable.
- Put status before configuration.
- Show traffic flow clearly and continuously.
- Surface operator action only when action is needed.
- Keep normal operation quiet and stable.
- Preserve trust through transparency and predictable behavior.
- Support future growth without redesigning the visual foundation.

The UI should scale from a single local proxy to multi-server monitoring, routing, plugins, memory, agents, and cloud providers.

## 3. Core Principles

### Health First

The first question the UI answers is: "Is everything healthy?"

Health state should be visible before logs, settings, configuration, or detailed analytics.

### Flow Second

The second question is: "Is traffic flowing?"

Connection and request flow should be visible as a system path, not just as numbers.

### Action Third

The third question is: "Do I need to act?"

Recommendations and alerts should be concise. If no action is required, the UI should say so calmly.

### One Component, One Question

Every component should answer one clear question. If a component needs to answer multiple questions, split it or move details to another page.

### Semantic Color

Color must have meaning.

- Green means healthy or online.
- Amber means attention or elevated risk.
- Red means degraded, critical, or offline.
- Blue means live system activity or neutral emphasis.
- Gray and slate tones provide structure.

Do not use color only for decoration.

## 4. Brand Personality

ContextKeeper should feel:

- Professional
- Calm
- Intelligent
- Transparent
- Reliable
- Real-time
- Local-first

Avoid:

- gaming aesthetics
- cyberpunk styling
- cartoonish visuals
- hacker-terminal clichés
- flashy RGB effects
- decorative AI sparkle patterns
- marketing-page hero layouts inside the product

The product should look like serious infrastructure software that happens to be approachable.

## 5. User Experience Principles

Every interaction within ContextKeeper should reinforce the following principles:

### Information at a Glance

Users should understand the overall health of the system within three seconds of opening the application.

### Progressive Disclosure

Present only the information needed for the current task. Detailed information should be available without overwhelming the primary interface.

### Calm by Default

Normal operation should feel stable and quiet. Visual emphasis should increase only when user attention is required.

### Motion with Purpose

Animations communicate state changes, request flow, streaming activity, or health transitions. Decorative animation should be avoided.

### Consistency

Components with similar purposes should behave consistently throughout the application.

### Efficiency

Common operational tasks should require the fewest possible interactions while remaining discoverable.

### Trust Through Transparency

Whenever ContextKeeper performs an automated action, such as context compression, the user should be able to understand what occurred and why.

## 6. Dashboard Philosophy

The Operations page is a launch pad, not a report.

It should answer:

1. Is everything healthy?
2. Is traffic flowing?
3. Do I need to act?

Detailed information belongs on focused pages:

- Conversations
- Context
- Analytics
- Logs
- Settings

The dashboard should not require users to inspect every metric. It should interpret system state and make the next step obvious.

## 7. Visual Hierarchy

Priority order:

1. Overall health
2. Required action
3. Connection flow
4. Traffic state
5. Context pressure
6. Resource pressure
7. Detailed history
8. Configuration

Layout should reinforce this order. Configuration and secondary details should not compete visually with health or action state.

Typography should be compact, readable, and operational. Large type is reserved for primary health state and major values.

## 8. Motion Philosophy

Motion should communicate information, not decoration.

Allowed motion:

- subtle live status pulse
- value-change feedback
- connection-flow animation showing request movement
- small hover/focus transitions
- state transitions that clarify health changes

Avoid motion that:

- distracts from status
- loops without meaning
- looks decorative
- implies urgency during normal operation
- conflicts with reduced-motion preferences

Motion must remain optional where possible. Future animation settings should allow users to reduce or disable nonessential motion.

## 9. Component Philosophy

Components should be reusable, compact, and purpose-driven.

Each component should define:

- the question it answers
- the states it supports
- the minimum information required
- where detailed information lives

Examples:

- Hero health card: "Is the system healthy?"
- Connection flow: "Is the AI request path connected?"
- Context ring: "How much context pressure exists?"
- Request widget: "Is traffic flowing?"
- Recommendation panel: "Do I need to act?"
- Resource gauge: "Is local capacity constrained?"

Components should support dense desktop layouts and readable compact layouts without feeling squeezed.

## 10. Accessibility

Accessibility is part of operational trust.

Requirements:

- Do not rely on color alone for status.
- Use readable contrast on dark surfaces.
- Preserve visible focus states.
- Keep status text concise and explicit.
- Respect reduced-motion preferences.
- Avoid tiny controls in settings or action areas.
- Ensure empty, loading, and error states are understandable.

Status indicators should pair color with labels, icons, or text.

## 11. Future Expansion

The design language must support future ContextKeeper capabilities:

- multi-server monitoring
- plugin management
- model routing
- workspace memory
- agent coordination
- cloud provider connections
- multi-model observability
- local and remote execution environments

The UI should scale through pages, tabs, filters, and drill-downs rather than by adding more information to Operations.

Future expansion should preserve the same hierarchy:

1. health
2. flow
3. action
4. details
5. configuration

## 12. Design Checklist

Before implementing UI changes, verify:

- The change supports ContextKeeper as an AI Operations Console.
- The user can understand health within three seconds.
- Status appears before configuration.
- Every component answers one clear question.
- Color has semantic meaning.
- Normal operation remains calm.
- Motion communicates information, not decoration.
- The layout works at 100% browser zoom.
- Medium desktop windows remain usable.
- Details are moved to secondary pages when they crowd Operations.
- Existing backend contracts and JavaScript IDs are preserved unless a migration is approved.
- The design can grow toward multi-server, plugin, routing, memory, agent, and cloud-provider workflows.
