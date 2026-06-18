---
name: shinen-design
description: SHIN-EN 深淵 design system — dark Japanese minimal monochrome for tool dashboards and local web UIs. Use when the user asks for a "dark dashboard", "monochrome UI", "SHIN-EN style", "minimal dark design system", or wants a consistent premium look across internal tools. Vanilla HTML/CSS/JS only — no frameworks, works inline in Python stdlib http.server.
---

# SHIN-EN 深淵 — Design System

Dark Japanese minimal luxury, monochrome absolute. One stylesheet (`shinen.css`, bundled next to this file) + one signature move (ghosted step numerals). Designed for internal tool dashboards: forms, logs, step-by-step pipelines.

**Constraint:** Vanilla HTML/CSS/JS only. No frameworks, no build step. The CSS can be linked, inlined in a `<style>` tag, or served from a stdlib HTTP server.

## When to apply

- User asks for a dashboard / control panel / local tool UI with a dark, minimal, premium look
- User says "SHIN-EN", "monochrome UI", "dark Japanese minimal"
- A project already uses `.sn-*` classes — extend it, never restyle it

## 1. Design Principles

1. **Monochrome by choice.** No color accents. Hierarchy via weight, size, opacity, whitespace.
2. **Numerals are architecture.** Giant ghosted step numbers (01, 02) act as watermarks behind content blocks — the signature move.
3. **Whitespace is premium.** Negative space > density. One idea per screen-height.
4. **Strict ink tiers.** 3 text brightness levels only. Never 5.
5. **Motion is meaning.** Reveal animations trigger on scroll; micro-interactions confirm user action.
6. **Mobile-first always.** `clamp()` for fluid type. Safe-area for notch. ≥48px touch targets.

## 2. Tokens

### Surfaces (5-step scale, darkest → lightest)

| Token | Hex | Usage |
|---|---|---|
| `--sumi` | `#0a0a0a` | Page background (primary) |
| `--kuro` | `#141414` | Elevated card / section bg |
| `--hair` | `#1f1f1f` | Input background |
| `--line` | `#2a2a2a` | Borders, hairline separators |
| `--ghost` | `#2e2e2e` | Ghosted numerals, placeholders |

### Ink (3-tier — NEVER more)

| Token | Hex | Usage |
|---|---|---|
| `--ink` | `#f5f5f5` | PRIMARY — headings, values, CTA labels |
| `--fog` | `#a8a8a8` | SECONDARY — body copy, metadata |
| `--silt` | `#6e6e6e` | TERTIARY — labels, captions, eyebrows |

**Status rule:** never convey status by color alone (there is no color). Pair with icon + text — `--ink` + ✓ for success, `--ink` + ✗ for error, `--fog` for pending.

### Typography (font stack LOCKED)

```css
--font-display: 'Space Grotesk', system-ui, sans-serif;   /* 700 ONLY */
--font-body:    'Inter', system-ui, sans-serif;           /* 400/500 — NEVER 300 */
--font-mono:    'JetBrains Mono', ui-monospace, monospace;/* 400 only */
```

Type scale (1.25 modular): `--t-xs` 0.72rem · `--t-sm` 0.85rem · `--t-base` 1rem · `--t-md` 1.25rem · `--t-lg` 1.5rem · `--t-xl` 2rem · `--t-2xl` 3rem · `--t-mega` `clamp(6rem, 18vw, 11rem)` (ghosted numerals).

Letter spacing: `--ls-tight` -0.02em (display) · `--ls-wide` 0.08em (eyebrow uppercase) · `--ls-mega` 0.18em (mono labels).

### Spacing (4pt linear — use ONLY these)

`--s-1` 4 · `--s-2` 8 · `--s-3` 12 · `--s-4` 16 · `--s-6` 24 · `--s-8` 32 · `--s-12` 48 · `--s-16` 64 · `--s-24` 96 · `--s-32` 128px.

### Radii

`--r-sm` 4px (chip) · `--r-md` 8px (input) · `--r-lg` 16px (card) · `--r-pill` 999px (**all CTA buttons are pills**).

### Motion

`--d-fast` 150ms (hover/press) · `--d-base` 240ms (state) · `--d-slow` 400ms (scroll reveal) · `--d-hero` 800ms (numeral scale-in). Easings: `--e-out` `cubic-bezier(0.16,1,0.3,1)`, `--e-in-out`, `--e-spring`. All motion respects `prefers-reduced-motion: reduce`. Animate only transform/opacity — never width/height.

## 3. Signature Move — Ghosted Numerals

Every step-block has a giant `01`, `02`, ... numeral as architectural watermark:

- Space Grotesk 700, `--t-mega`, color `--ghost`, `position: absolute; top: -0.2em; right: 0; z-index: 0;`
- Content sits at `z-index: 1`
- Reveal: IntersectionObserver (threshold 0.2) adds `.revealed` → scale 0.85→1, opacity 0→1, 800ms `--e-out`

```html
<section class="sn-step" data-step="01">
  <span class="sn-numeral" aria-hidden="true">01</span>
  <div class="sn-step-body">
    <span class="sn-eyebrow">Setup</span>
    <h2 class="sn-h2">Configure the source</h2>
    <!-- content -->
  </div>
</section>
```

```js
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('revealed'); io.unobserve(e.target); }
  });
}, { threshold: 0.2 });
document.querySelectorAll('.sn-step').forEach(el => io.observe(el));
```

## 4. Component Classes (all in `shinen.css`)

| Class | Component |
|---|---|
| `.sn-container` | 880px centered page container |
| `.sn-brand` | Top-left brand header (dot + uppercase name) |
| `.sn-h1` `.sn-h2` `.sn-h3` `.sn-sub` | Headings + lead paragraph |
| `.sn-eyebrow` | Uppercase label with preceding 24px hairline |
| `.sn-step` `.sn-numeral` `.sn-step-body` | Signature step-block |
| `.sn-card` | `--kuro` bg, `--line` border, 16px radius |
| `.sn-field` `.sn-label` `.sn-input` `.sn-select` `.sn-field-row` | Forms — inputs 52px tall, **16px font (prevents iOS zoom)** |
| `.sn-btn` (+ `--secondary`, `--block`) | Pill CTA, 48/52px, primary = `--ink` on `--sumi` |
| `.sn-log` (+ `.sn-log-ts`, `.sn-log-ok`) | Mono log panel, scrollable, subtle scrollbar |
| `.sn-chip` | Uppercase status chip |
| `.sn-divider` | 1px hairline `hr` |

## 5. Page Shell Pattern

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{TOOL_NAME}</title>
  <!-- Fonts: load via <link> (more reliable than CSS @import, esp. when inlined). -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@400&family=Space+Grotesk:wght@700&display=swap">
  <link rel="stylesheet" href="shinen.css">
</head>
<body>
  <div class="sn-container">
    <header class="sn-brand"><strong>{BRAND}</strong>&nbsp;· {TOOL_NAME}</header>
    <h1 class="sn-h1">{One-line tool purpose}</h1>
    <p class="sn-sub">{Subtitle in --fog}</p>
    <section class="sn-step" data-step="01">…</section>
    <section class="sn-step" data-step="02">…</section>
  </div>
  <script>/* IntersectionObserver helper from §3 */</script>
</body>
</html>
```

Per-tool differentiator = the step *count* and *content*, never the visual language.

## 6. Non-Negotiable Rules

1. Monochrome only — never add a brand/accent color
2. 3 ink tiers strictly — never collapse label + value to same brightness
3. Space Grotesk 700 only; Inter 400/500 only (never 300); JetBrains Mono 400 only
4. All CTAs pill-shaped (`--r-pill`)
5. Numerals `aria-hidden="true"`, zero-padded (`01` not `1`)
6. Inputs 16px font (iOS zoom), ≥48px touch targets everywhere
7. `prefers-reduced-motion` always handled (already in the CSS)
8. Status = icon + text, never color alone
9. SVG icons only (Heroicons/Lucide) — no emoji icons
10. Test at 375px viewport first; headlines may be centered, body text never

## 7. Accessibility (built in — keep it)

- Contrast: `--ink`/`--sumi` 17.5:1 (AAA) · `--fog`/`--sumi` 8.9:1 (AAA) · `--silt`/`--sumi` AA for labels/captions only — never body copy
- `:focus-visible` 2px outline + 3px offset on every focusable element
- Semantic heading order h1→h2→h3; labels associated via `for`/`id`
- Safe-area insets on body padding (notch devices)
- `aria-live="polite"` on log/status regions that update dynamically

## 8. Adoption Checklist

1. Copy `shinen.css` next to your HTML (or inline it in a `<style>` tag for single-file servers)
2. Use the page shell from §5; fill `{BRAND}` / `{TOOL_NAME}`. **Keep the font `<link>` tags in `<head>`** — the CSS `@import` is only a fallback and gets dropped when the CSS is inlined or concatenated non-first, so without the `<link>` the page silently falls back to system fonts. Needs network access (Google Fonts CDN); for offline/air-gapped, self-host the 3 woff2 files and swap the URL.
3. Wrap each pipeline phase in a `.sn-step` with zero-padded `data-step`
4. Paste the IntersectionObserver helper in a `<script>`
5. Run through §6 rules before shipping
