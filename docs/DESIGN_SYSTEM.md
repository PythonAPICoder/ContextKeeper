# ContextKeeper Design System

## Purpose

This document defines the visual and interaction foundation for the ContextKeeper browser dashboard.

The dashboard is an operations console for a local AI proxy. It should help an operator understand health, traffic, context pressure, and required action quickly without feeling noisy or decorative.

## Design Philosophy

ContextKeeper UI should feel:

- **Professional**: clear, stable, and production-ready.
- **Calm**: avoids unnecessary urgency, clutter, and visual noise.
- **Intelligent**: surfaces meaning, not just raw metrics.
- **Transparent**: shows what the proxy is doing and why.
- **Alive**: uses subtle live state, motion, and flow cues where they improve comprehension.

The interface should behave like a desktop operations application rendered in a browser, not like a marketing site or generic responsive web page.

## Color Palette

The dashboard uses a dark operational palette with restrained accent color.

| Token | Purpose | Value |
| --- | --- | --- |
| `--bg` | Application background | `#090e1a` |
| `--sidebar` | Sidebar surface | `#0d1424` |
| `--panel` | Main panel background | `#111827` |
| `--card` | Card surface | `#182132` |
| `--card-strong` | Emphasized card surface | `#1f2937` |
| `--text` | Primary text | `#e5e7eb` |
| `--soft` | Secondary high-contrast text | `#cbd5e1` |
| `--muted` | Muted text | `#94a3b8` |
| `--line` | Borders and connector lines | `#2d3a4f` |
| `--accent` | Primary operational accent | `#38bdf8` |
| `--accent-2` | Secondary accent | `#818cf8` |
| `--good` | Healthy / online | `#22c55e` |
| `--warn` | Attention / warning | `#f59e0b` |
| `--bad` | Critical / offline | `#ef4444` |

Color usage rules:

- Green, amber, and red are reserved for operational status.
- Blue accents indicate live data, active navigation, and neutral system activity.
- Avoid large single-hue surfaces. Cards should be dark neutral surfaces with restrained accent cues.
- Avoid decorative gradients unless they reinforce hierarchy or state.

## Typography

Preferred font stack:

```css
font-family: "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
```

Typography rules:

- Use compact, scan-friendly headings.
- Avoid oversized hero typography inside operational views.
- Use uppercase only for short status labels, badges, and operational headings.
- Do not use negative letter spacing.
- Do not scale body text directly with viewport width.
- Prefer truncation or detail pages for long operational strings.

## Spacing

Spacing is based on an 8px grid.

| Step | Size | Use |
| --- | --- | --- |
| 0.5 | 4px | Tight internal label spacing |
| 1 | 8px | Compact gaps, badge padding |
| 1.5 | 12px | Dense card padding |
| 2 | 16px | Standard card padding |
| 3 | 24px | Page gutters and major grouping |
| 4 | 32px | Large layout separation |

Operations pages should use dense spacing. Detail pages may use more vertical space.

## Corner Radius

Use restrained radii:

- Cards and panels: `8px`
- Small controls and badges: `999px` only for pills/status badges
- Icons, marks, and compact buttons: `6px` to `8px`
- Avoid large rounded cards unless a later brand system explicitly calls for them.

## Shadows and Elevation

Elevation should be subtle and functional.

- Base cards use low-opacity dark shadows.
- Hover elevation should be slight: border color change and at most a 1px vertical lift.
- Avoid stacked shadows that make the dashboard feel card-heavy.
- Modal/dialog elevation may be stronger than page cards.

## Motion and Animation

Motion should support live operations comprehension.

Allowed:

- subtle value change feedback
- gentle status pulse on live connection dots
- future connection-flow animation showing request movement
- short transitions for hover and state changes

Avoid:

- decorative motion
- looping background animation
- distracting large-scale movement
- motion required to understand critical state

Future animation should respect an `animations_enabled` setting when available.

## Sound Policy

Sound is optional and disabled by default.

Rules:

- No sound should play without explicit user opt-in.
- Sound should be limited to critical state changes or user-requested alerts.
- Sound must have a visible setting and a clear mute/off state.
- No sound should be used for normal request flow.

## Accessibility

Requirements:

- Status must not rely on color alone; use text labels and icons.
- Maintain readable contrast on dark surfaces.
- Keep focus states visible for navigation and controls.
- Avoid tiny click targets in settings and action controls.
- Ensure live regions and animations do not overwhelm assistive technology.
- Respect reduced-motion preferences for nonessential animation.

## Branding Principles

ContextKeeper branding should communicate local control, transparency, and operational trust.

Brand direction:

- Serious but not cold.
- Technical but understandable.
- Local-first and privacy-conscious.
- Visual metaphors should emphasize flow, context, containment, and clarity.

Avoid:

- mascot-driven UI
- consumer social app styling
- decorative AI sparkle patterns
- excessive purple gradients
- marketing hero layouts inside the operations console
