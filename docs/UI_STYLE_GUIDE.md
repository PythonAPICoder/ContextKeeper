# ContextKeeper UI Style Guide

## 1. Purpose

This guide defines global UI consistency rules for ContextKeeper.

It covers spacing, radius, elevation, borders, icons, panels, alignment, and consistency expectations for the AI Operations Console.

## 2. Spacing System

Use an 8px spacing grid.

Recommended steps:

- 4px: tight label spacing
- 8px: compact internal gaps
- 12px: dense card padding
- 16px: standard card padding
- 24px: page grouping
- 32px: large section separation

Operations should prefer compact spacing. Detail pages may use more space.

## 3. Border Radius

Recommended radius:

- Cards: 8px.
- Panels: 8px.
- Compact controls: 6px to 8px.
- Badges: pill radius.
- Dialogs: 8px to 10px.

Avoid large rounded surfaces unless approved by the design system.

## 4. Shadows

Shadows should be subtle.

Rules:

- Use shadows to separate surfaces, not decorate.
- Avoid heavy floating cards.
- Hover elevation should be minimal.

## 5. Elevation

Elevation levels:

- Level 0: page background.
- Level 1: cards and panels.
- Level 2: active panels, dropdowns, popovers.
- Level 3: dialogs and modals.

Do not stack multiple high-elevation surfaces in one region.

## 6. Borders

Borders define structure and state.

Rules:

- Use subtle borders for cards and table rows.
- Use stronger borders for active or focused elements.
- Error borders must pair with labels or messages.

## 7. Icons

Icons support scanning but do not replace labels.

Rules:

- Use simple, familiar icons.
- Keep icon size consistent within component groups.
- Avoid decorative icon sets.
- Provide accessible labels for icon-only controls.

## 8. Dividers

Dividers separate related groups.

Rules:

- Use sparingly.
- Prefer spacing and alignment before adding dividers.
- Dividers should be low contrast.

## 9. Panels

Panels group related operational content.

Rules:

- Each panel should have a clear purpose.
- Avoid panels inside panels unless the inner element is a repeated item or dialog.
- Panel headings should be concise.

## 10. Card Spacing

Card spacing should be consistent across similar cards.

Rules:

- Align cards to the grid.
- Keep internal padding compact in Operations.
- Use matching heights for peer cards where practical.
- Compact layouts may reduce padding and height.

## 11. Alignment

Alignment supports scan speed.

Rules:

- Align card edges consistently.
- Align metric labels and values within component groups.
- Avoid irregular card placement unless it clarifies hierarchy.

## 12. White Space

White space should create clarity, not emptiness.

Rules:

- Operations uses dense but readable spacing.
- Detail pages may use more breathing room.
- Avoid unused vertical space above critical content.

## 13. Consistency Rules

- Similar information uses similar components.
- Similar components use similar sizing.
- Status placement should be predictable.
- Empty/loading/error states should use consistent structure.
- Do not introduce one-off visual patterns without a reason.

## 14. Accessibility Reminders

- Preserve focus states.
- Keep labels visible.
- Do not rely on color alone.
- Avoid tiny click targets.
- Respect reduced-motion preferences.

## 15. Implementation Checklist

Before changing UI styling, verify:

- Spacing follows the 8px grid.
- Radius is consistent.
- Borders and elevation support hierarchy.
- Icons are meaningful and labeled.
- Cards align to the layout grid.
- Compact layouts remain readable.
- Accessibility cues remain visible.
