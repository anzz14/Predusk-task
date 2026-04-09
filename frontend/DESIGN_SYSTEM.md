# Minimalist Black & White Design System

This document outlines the design conventions for the SEO Analyzer frontend application. Follow these rules when building any new components.

## Color Palette

Restricted to a minimalist black & white palette with a single accent red for errors only:

- **Background**: White (#ffffff) and near-black (#0a0a0a)
- **Text**: Black (#000000), muted gray (#6b7280), light gray (#f5f5f5)
- **Borders**: Light (#e5e5e5), medium (#d4d4d8)
- **Accent**: Black (used for primary buttons, focus rings, active states)
- **Destructive/Error**: Red (#ef4444) — used only for errors and destructive actions

**No blues, purples, or brand colors anywhere.**

## Component Patterns

### Buttons

**Primary Button (CTA)**
- Background: black
- Text: white
- Border: none
- Hover: slightly darker/opaque
- Focus: 2px black ring with 2px offset
- Padding: `px-4 py-2`
- Use class: `.btn-primary`

**Secondary/Outline Button**
- Background: white
- Text: black
- Border: 1px black
- Hover: light gray background
- Focus: 2px black ring with 2px offset
- Padding: `px-4 py-2`
- Use class: `.btn-secondary`

**Destructive Button** (rarely used)
- Background: #ef4444 (red)
- Text: white
- Same behavior as primary but with red

### Badges

**Active/Processing Badge**
- Background: black
- Text: white
- Border: none
- Padding: `px-2 py-1`
- Font size: `text-xs` with `font-medium`
- Use class: `.badge-active`

**Inactive/Status Badge** (e.g., "queued", "completed")
- Background: white
- Text: black
- Border: 1px #e5e5e5
- Padding: `px-2 py-1`
- Font size: `text-xs` with `font-medium`
- Use class: `.badge-inactive`

### Cards

- Background: white
- Border: 1px #e5e5e5
- Padding: `p-6`
- Border radius: `rounded-lg` (0.5rem)
- Shadow: subtle (`shadow-xs` — 0 1px 2px 0 rgba(0,0,0,0.05))
- Use class: `.card`
- No drop shadows except the minimal shadow-xs

### Tables

- Background: white
- No zebra striping
- Row separator: 1px bottom border (#e5e5e5) only
- No cell borders
- Use class: `.table-row` for `<tr>` elements
- Header background: light gray (#f5f5f5)
- Header text: black, bold

### Inputs

- Background: white
- Border: 1px #d4d4d8 (medium gray)
- Text: black
- Placeholder: #6b7280 (muted gray)
- Padding: `px-3 py-2`
- Border radius: `rounded-md` (0.375rem)
- Focus state:
  - Border changes to black
  - 2px black ring with opacity (focus:ring-black/10)
  - No fill color change
- Use class: `.input-clean`

### Progress Bars

- Track background: #f5f5f5 (light gray)
- Bar fill: black (#000000)
- Height: `h-2` or `h-1` depending on context
- Border radius: fully rounded (for visual softness)

### Form Labels

- Color: black
- Font weight: `font-medium` or `font-semibold`
- No special styling needed

## Typography

- **Font Stack**: System fonts only
  ```
  -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
  "Helvetica Neue", Arial, sans-serif
  ```
- **No custom fonts** — keep it simple and performant
- **Font sizes**: Use Tailwind defaults (`text-sm`, `text-base`, `text-lg`, etc.)
- **Font weights**: Regular (400), medium (500), semibold (600), bold (700)

## Spacing

- **Generous whitespace** — don't cram elements
- **Base unit**: 0.25rem (Tailwind default spacing scale)
- **Common spacings**:
  - Small sections: `gap-2` or `gap-3`
  - Medium sections: `gap-4` or `gap-6`
  - Large sections: `gap-8` or `gap-12`

## Layout Principles

1. **Clean alignment** — use CSS Grid or Flexbox consistently
2. **No clutter** — remove visual noise
3. **Clear hierarchy** — use spacing and typography weight to establish importance
4. **Generous padding** — especially in cards and containers
5. **Minimal visual elements** — borders only when necessary for separation

## Focus & Accessibility

- All interactive elements must have visible focus state
- Use `.focus-ring` for standard 2px offset ring
- Use `.focus-ring-black` for tighter 0 offset ring (when needed)
- Always maintain sufficient contrast (black on white = WCAG AAA)

## Component Examples

### Card with Content
```tsx
<div className="card">
  <h3 className="text-lg font-semibold mb-4">Title</h3>
  <p className="text-sm text-foreground-muted mb-6">Description</p>
  <button className="btn-primary">Action</button>
</div>
```

### Status Badge List
```tsx
<div className="flex gap-2">
  <span className="badge-active">processing</span>
  <span className="badge-inactive">completed</span>
</div>
```

### Input with Label
```tsx
<label className="block mb-2">
  <span className="text-sm font-medium text-black mb-1 block">Label</span>
  <input className="input-clean w-full" type="text" placeholder="Enter value..." />
</label>
```

## What NOT to Do

- ❌ Do not add brand colors (blues, purples, etc.)
- ❌ Do not use background gradients
- ❌ Do not add decorative elements
- ❌ Do not use custom fonts
- ❌ Do not use color to indicate state—use badges or text labels
- ❌ Do not add drop shadows (except shadow-xs on cards)
- ❌ Do not use zebra striping in tables
- ❌ Do not add animations unless they serve purpose (e.g., loading state)
