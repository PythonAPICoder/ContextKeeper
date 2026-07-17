# ContextKeeper Color System

Status: Current through Phase 6.5F-B5.6.

## 1. Purpose

This document defines the official UI color system for ContextKeeper.

The color system supports a calm, polished, enterprise-grade AI Operations Console. It applies to all current and future browser UI screens, including Operations, Conversations, Context, Analytics, Logs, Settings, and future multi-server or plugin workflows.

## 2. Color Philosophy

Colors in ContextKeeper are semantic, not decorative.

Every color should communicate a clear purpose:

- health
- risk
- activity
- connection state
- context pressure
- compression or memory intelligence
- interaction state
- structure

The UI should avoid gaming, cyberpunk, hacker-terminal, rainbow, neon-heavy, or flashy RGB aesthetics. Color should clarify operations state without making normal operation feel urgent.

Status must always be understandable without relying on color alone. Pair color with labels, icons, text, shape, or position.

## 3. Primary Theme Direction

Dark theme is the primary v1 direction.

The dark theme should use slate and blue-gray surfaces, restrained contrast, and a single primary blue/cyan accent. Backgrounds should never be pure black, and primary text should not be pure white.

Light theme may be supported later, but v1 design and implementation should prioritize the dark operations console.

## 4. Semantic Color Roles

| Role | Meaning | Primary Use |
| --- | --- | --- |
| Background | Application base | App shell and page background |
| Surface | Panels and cards | Cards, sidebars, topbar |
| Border | Structure | Card edges, separators, table rows |
| Text | Readability | Headings, values, labels |
| Muted | Secondary information | Help text, inactive metadata |
| Accent | Live neutral emphasis | Active navigation, flow, selected controls |
| Healthy | Normal connected state | Online services, safe context |
| Warning | Attention required | Elevated latency, context warning |
| Critical | Degraded or failed state | Offline services, critical thresholds |
| Intelligence | Compression and memory | Summaries, compression, memory features |

## 5. Dark Theme Palette

| Token | Name | Hex | Purpose |
| --- | --- | --- | --- |
| `bg.base` | Deep Slate | `#090E1A` | Main application background |
| `bg.shell` | Console Shell | `#0D1424` | Sidebar and persistent chrome |
| `bg.panel` | Panel Slate | `#111827` | Main panel background |
| `bg.card` | Card Slate | `#182132` | Standard cards |
| `bg.card.strong` | Raised Slate | `#1F2937` | Emphasized cards and active surfaces |
| `border.subtle` | Subtle Border | `#263244` | Low-emphasis borders |
| `border.strong` | Strong Border | `#334155` | Active or grouped borders |
| `text.primary` | Soft White | `#E5E7EB` | Primary text |
| `text.secondary` | Soft Slate | `#CBD5E1` | Secondary text |
| `text.muted` | Muted Blue Gray | `#94A3B8` | Metadata and helper text |
| `text.disabled` | Disabled Gray | `#64748B` | Disabled or unavailable text |
| `accent.primary` | Operational Cyan | `#38BDF8` | Live activity and neutral emphasis |
| `accent.secondary` | Soft Indigo | `#818CF8` | Secondary emphasis and selected details |

## 6. Status Colors

| Token | Name | Hex | Meaning |
| --- | --- | --- | --- |
| `status.healthy` | Connected Green | `#22C55E` | Healthy, online, safe |
| `status.success` | Success Blue-Green | `#10B981` | Completed successfully |
| `status.busy` | Activity Cyan | `#38BDF8` | Active, processing, live traffic |
| `status.warning` | Attention Amber | `#F59E0B` | Elevated risk, attention required |
| `status.critical` | Critical Red | `#EF4444` | Degraded, failed, critical |
| `status.offline` | Offline Red | `#DC2626` | Disconnected or unavailable |
| `status.unknown` | Unknown Slate | `#94A3B8` | Unknown, loading, unavailable |

Rules:

- Green means healthy or connected.
- Blue-green means a completed successful operation, such as compression completed, export completed, plugin installed, configuration saved, or another completed operation.
- Amber means warning or attention.
- Red means degraded, critical, failed, or offline.
- Blue means live activity, processing, or neutral emphasis.
- Status colors must be paired with text labels or icons.
- Success is distinct from healthy. Healthy represents ongoing operational health; success represents completed operations.

## 7. Connection Flow Colors

The Connection Flow widget represents:

```text
Client -> ContextKeeper -> Ollama -> Model
```

| State | Color | Hex | Use |
| --- | --- | --- | --- |
| Connected | Connected Green | `#22C55E` | Healthy connected node |
| Idle | Muted Blue Gray | `#94A3B8` | Available but inactive |
| Streaming | Operational Cyan | `#38BDF8` | Live request or streaming traffic |
| Warning | Attention Amber | `#F59E0B` | Slow, delayed, or degraded segment |
| Disconnected | Offline Red | `#DC2626` | Missing or unavailable connection |
| Error | Critical Red | `#EF4444` | Failed request or broken segment |

Rules:

- Flow lines should be muted by default.
- Active flow may use cyan emphasis.
- Degraded segments should use amber or red plus a label.
- Future animation should not depend on color alone.

## 8. Context Pressure Colors

| State | Color | Hex | Meaning |
| --- | --- | --- | --- |
| Safe | Connected Green | `#22C55E` | Context usage is comfortably below thresholds |
| Elevated | Activity Cyan | `#38BDF8` | Context is active but not risky |
| Warning | Attention Amber | `#F59E0B` | Context is approaching compression |
| Compression Threshold | Intelligence Purple | `#A78BFA` | Compression is likely or recommended |
| Critical | Critical Red | `#EF4444` | Context pressure may disrupt continuity |

Rules:

- Context pressure should be displayed as both percentage and state.
- Compression threshold should be visually distinct from generic warning.
- Critical context pressure should include an action or explanation.

## 9. Compression Colors

Purple is reserved for compression, memory, and intelligence-related features.

| Token | Name | Hex | Use |
| --- | --- | --- | --- |
| `intelligence.base` | Intelligence Purple | `#A78BFA` | Compression and memory indicators |
| `intelligence.soft` | Soft Purple Surface | `#2E2550` | Low-emphasis compression background |
| `intelligence.border` | Purple Border | `#6D5BD0` | Compression timeline and badges |

Rules:

- Do not use purple as the main dashboard accent.
- Use purple only when the feature relates to compression, memory, summarization, or intelligence.
- Compression colors must be paired with timestamps, labels, or summaries.

## 10. Chart and Metric Colors

Charts should use limited, purposeful colors.

Recommended chart colors:

| Series | Hex | Use |
| --- | --- | --- |
| Primary series | `#38BDF8` | Main request or latency trend |
| Healthy series | `#22C55E` | Success or healthy capacity |
| Warning series | `#F59E0B` | Elevated risk or threshold |
| Critical series | `#EF4444` | Errors or critical thresholds |
| Intelligence series | `#A78BFA` | Compression or memory events |
| Neutral series | `#94A3B8` | Baseline or comparison |

Rules:

- Use muted gridlines such as `#263244`.
- Use clear axis or inline labels.
- Avoid more than three strong series colors in one chart.
- Use semantic emphasis for thresholds and incidents.
- Do not use rainbow palettes.

## 11. Interaction Colors

| Interaction | Color | Hex | Notes |
| --- | --- | --- | --- |
| Hover border | Operational Cyan | `#38BDF8` | Low-opacity border or glow |
| Active navigation | Cyan over slate | `#38BDF8` | Active state plus label |
| Focus ring | Soft Cyan | `#7DD3FC` | Must be visible on dark surfaces |
| Disabled | Disabled Gray | `#64748B` | Pair with disabled cursor/state |
| Selected | Soft Indigo | `#818CF8` | Secondary selection or mode |

Rules:

- Avoid using more than one strong accent in the same component.
- Focus states must remain visible.
- Hover states should be subtle and should not look like alerts.

## Reserved Accent

| Name | Hex | Purpose |
| --- | --- | --- |
| Gold | `#EAB308` | Reserved for rare, high-value visual emphasis |

Gold may be used for:

- version highlights
- featured badges
- release announcements
- future premium features, if ever introduced

Gold should never be used for routine operational dashboard elements.

## 12. Accessibility Rules

- Do not rely on color alone for status.
- Pair status colors with labels, icons, shape, or text.
- Avoid pure black backgrounds and pure white text.
- Maintain readable contrast for text on card surfaces.
- Keep warning and critical states distinguishable by text and iconography.
- Respect reduced-motion preferences for animated color transitions.
- Do not use color-only alerts in logs, charts, or recommendations.

## 13. Usage Rules

- Use green only for healthy or connected states.
- Use amber only for warning, attention, or elevated risk.
- Use red only for degraded, critical, failed, or offline states.
- Use blue/cyan for live activity, processing, active controls, and neutral emphasis.
- Use purple only for compression, memory, summarization, or intelligence features.
- Use gray/slate for structure, disabled states, inactive states, and muted metadata.
- Avoid multiple competing accent colors inside one component.
- Keep normal operation calm and low-noise.

## 14. Future Light Theme Notes

Light theme may be supported after the dark v1 console is stable.

Future light theme requirements:

- preserve semantic roles and token names
- maintain status color meaning
- avoid pure white backgrounds
- use subtle warm-gray or cool-slate surfaces
- test chart and status contrast separately from dark theme

Light theme should not change the product personality. It should still feel calm, operational, and enterprise-grade.

## Colors to Avoid

The ContextKeeper interface should avoid:

- rainbow palettes
- pure black (`#000000`) backgrounds
- pure white (`#FFFFFF`) text
- neon cyan or neon green
- animated rainbow gradients
- flashing status colors
- multiple competing accent colors
- decorative color changes without semantic meaning

These restrictions preserve ContextKeeper's calm, professional, enterprise-grade visual identity.

## 15. Implementation Checklist

Before implementing color changes, verify:

- Every color has a semantic purpose.
- Status is understandable without color alone.
- Dark theme remains the primary v1 target.
- The palette avoids neon, rainbow, gaming, cyberpunk, and hacker-terminal aesthetics.
- Green, amber, red, blue, purple, and slate are used only for their defined roles.
- Charts use limited series colors and muted gridlines.
- Focus states are visible.
- Disabled states are visibly distinct.
- Normal operation remains visually calm.
- Future light theme can reuse the same semantic token structure.
