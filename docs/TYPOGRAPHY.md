# ContextKeeper Typography

Status: Current through Phase 6.5F-B5.6.

## 1. Purpose

This document defines the typography system for ContextKeeper.

Typography should support dense operational scanning, clear hierarchy, and calm enterprise-grade presentation.

## 2. Typography Philosophy

Text should be:

- compact
- readable
- consistent
- operational
- restrained

Use typography to clarify hierarchy, not to create decoration.

## 3. Font Recommendations

Primary font stack:

```text
Segoe UI Variable, Segoe UI, Arial, sans-serif
```

Fallbacks should preserve legibility on Windows and browser-rendered desktop UI.

## 4. Display Text

Use display text only for primary health state or major page-level status.

Rules:

- Keep short.
- Avoid wrapping where possible.
- Do not use oversized marketing-style headlines in Operations.

## 5. Headings

Headings identify page regions and major panels.

Rules:

- Use concise labels.
- Prefer sentence case or short title case.
- Avoid multiple competing heading sizes in one view.

## 6. Card Titles

Card titles should be short operational labels.

Examples:

- System Health
- Context Usage
- Request Statistics
- Recommendations
- Resources

Rules:

- Keep card titles compact.
- Do not use explanatory phrases as card titles.

## 7. Metric Values

Metric values should be prominent and easy to scan.

Rules:

- Use consistent numeric formatting.
- Include units where needed.
- Avoid excessive decimal precision.
- Pair values with labels.

## 8. Labels

Labels describe controls, metrics, and statuses.

Rules:

- Keep labels short.
- Use consistent terms across pages.
- Do not replace labels with icons alone.

## 9. Body Text

Body text should explain state or action briefly.

Rules:

- Keep operational copy concise.
- Move long explanations to detail pages.
- Avoid marketing language.

## 10. Captions

Captions support metadata such as timestamps, model names, endpoints, or token detail.

Rules:

- Use muted styling.
- Keep readable at compact sizes.
- Truncate long technical strings when needed.

## 11. Monospace Usage

Use monospace only for:

- ports
- paths
- model identifiers when needed
- request IDs
- code-like values

Do not use monospace as the general dashboard typeface.

## 12. Spacing

Typography spacing should follow the 8px grid.

Rules:

- Tight labels may use 4px spacing.
- Card title to content spacing should be compact.
- Large vertical gaps should be reserved for page grouping, not card interiors.

## 13. Accessibility

Requirements:

- Maintain readable contrast.
- Avoid text smaller than necessary in compact views.
- Do not rely on color alone for status.
- Preserve visible focus labels and control text.

## 14. Implementation Checklist

Before changing typography, verify:

- Text supports quick operational scanning.
- Heading hierarchy is clear.
- Metrics are readable at compact desktop widths.
- Labels are present for icon controls.
- Long text is truncated or moved to detail views.
- Typography remains consistent across similar components.
