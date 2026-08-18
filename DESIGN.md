---
version: alpha
name: Phonos.ai
description: >
  A precision intelligence surface — warm off-white paper grain under
  deep-charcoal ink, with a single charged Vermilion accent that fires only
  on primary moments. Display type is set in a condensed grotesque at extreme
  sizes with tight tracking; body copy stays in a high-legibility proportional
  sans. Depth comes from paper texture and hairline borders, never from drop
  shadows or gradients. The three recommendation modes (Easy / Medium / Deep)
  share this base language but each carry their own micro-character: Easy is
  warm and conversational, Medium is precise and architectural, Deep is
  focused and minimal. Nothing in this system is decorative; every element
  exists because a user decision requires it.

colors:
  vermilion:   "#E8420A"
  ink:         "#1A1916"
  body:        "#3C3A35"
  muted:       "#7A7669"
  hairline:    "#D8D3C8"
  canvas:      "#F0EDE6"
  surface:     "#F7F4EF"
  surface-elevated: "#FDFCFA"
  on-vermilion: "#FFFFFF"
  success:     "#1A7A4A"
  warning:     "#C47A0A"
  error:       "#C42A1A"
  india-verified: "#1A7A4A"

typography:
  display-hero:
    fontFamily: "'Barlow Condensed', 'Arial Narrow', sans-serif"
    fontSize: "clamp(72px, 10vw, 140px)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-2px"
  display-xl:
    fontFamily: "'Barlow Condensed', 'Arial Narrow', sans-serif"
    fontSize: "clamp(48px, 7vw, 96px)"
    fontWeight: 700
    lineHeight: 0.95
    letterSpacing: "-1.5px"
  display-lg:
    fontFamily: "'Barlow Condensed', 'Arial Narrow', sans-serif"
    fontSize: "clamp(32px, 5vw, 56px)"
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: "-0.8px"
  display-md:
    fontFamily: "'Barlow Condensed', 'Arial Narrow', sans-serif"
    fontSize: "clamp(24px, 3vw, 40px)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.5px"
  label-caps:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.12em"
    textTransform: "uppercase"
  label-sm:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "11px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.08em"
    textTransform: "uppercase"
  body-lg:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "-0.01em"
  body-md:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "-0.01em"
  body-sm:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  mono:
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  button:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.04em"
    textTransform: "uppercase"
  nav:
    fontFamily: "'DM Sans', Inter, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "0.06em"
    textTransform: "uppercase"

rounded:
  none: "0px"
  xs:   "2px"
  sm:   "4px"
  md:   "6px"
  lg:   "10px"
  xl:   "16px"
  full: "9999px"

spacing:
  xs:      "4px"
  sm:      "8px"
  md:      "12px"
  base:    "16px"
  lg:      "24px"
  xl:      "40px"
  xxl:     "64px"
  section: "96px"
  hero:    "160px"

components:
  nav-link:
    typography: "{typography.nav}"
    color: "{colors.muted}"
    color-hover: "{colors.ink}"
    color-active: "{colors.vermilion}"
    transition: "color 200ms ease"

  wordmark:
    typography: "{typography.label-caps}"
    fontWeight: 700
    fontSize: "14px"
    color: "{colors.ink}"
    letterSpacing: "0.06em"

  button-primary:
    backgroundColor: "{colors.vermilion}"
    textColor: "{colors.on-vermilion}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "14px 28px"
    height: "48px"
    hover-opacity: 0.88
    transition: "background-color 200ms ease, opacity 200ms ease"

  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    border: "1px solid {colors.hairline}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "14px 28px"
    height: "48px"
    hover-background: "{colors.canvas}"
    transition: "background-color 200ms ease, border-color 200ms ease"

  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "14px 28px"
    height: "48px"
    hover-color: "{colors.ink}"
    transition: "color 200ms ease"

  card-recommendation:
    backgroundColor: "{colors.surface-elevated}"
    border: "1px solid {colors.hairline}"
    rounded: "{rounded.none}"
    padding: "{spacing.xl}"
    hover-border-color: "{colors.ink}"
    transition: "border-color 240ms ease"

  badge-verified:
    backgroundColor: "transparent"
    textColor: "{colors.india-verified}"
    border: "1px solid {colors.india-verified}"
    typography: "{typography.label-sm}"
    fontSize: "10px"
    rounded: "{rounded.none}"
    padding: "2px 6px"

  badge-rank:
    fontFamily: "'Barlow Condensed', sans-serif"
    fontSize: "11px"
    fontWeight: 700
    letterSpacing: "0.08em"
    textColor: "{colors.muted}"

  score-bar:
    trackColor: "{colors.hairline}"
    fillColor: "{colors.vermilion}"
    height: "2px"
    rounded: "{rounded.none}"

  slider-input:
    trackColor: "{colors.hairline}"
    thumbColor: "{colors.ink}"
    fillColor: "{colors.ink}"
    height: "1px"
    thumbSize: "16px"

  persona-row:
    borderBottom: "1px solid {colors.hairline}"
    padding: "20px 0"
    typography-index: "{typography.label-caps}"
    typography-name: "{typography.display-md}"
    color-index: "{colors.muted}"
    color-name: "{colors.ink}"
    hover-background: "transparent"
    hover-border-bottom-color: "{colors.vermilion}"
    transition: "border-color 220ms ease, color 220ms ease"

  mode-tile:
    backgroundColor: "{colors.surface}"
    border: "1px solid {colors.hairline}"
    rounded: "{rounded.none}"
    padding: "{spacing.xl}"
    hover-border: "1px solid {colors.ink}"
    transition: "border-color 220ms ease"

  accordion-row:
    borderBottom: "1px solid {colors.hairline}"
    padding: "20px {spacing.base}"
    expanded-background: "{colors.surface}"
    transition: "background-color 200ms ease"

  input-text:
    backgroundColor: "transparent"
    border: "none"
    borderBottom: "1px solid {colors.hairline}"
    typography: "{typography.body-lg}"
    color: "{colors.ink}"
    focus-border-bottom-color: "{colors.ink}"
    padding: "{spacing.md} 0"
    placeholder-color: "{colors.muted}"

  nav-bar:
    backgroundColor: "{colors.canvas}"
    borderBottom: "1px solid {colors.hairline}"
    height: "52px"
    padding: "0 {spacing.xl}"
    position: "sticky"
    top: "0"
    zIndex: 100

  loading-state:
    typography: "{typography.label-caps}"
    color: "{colors.muted}"
    progressColor: "{colors.vermilion}"
    backgroundColor: "{colors.canvas}"

---

## Overview

Phonos.ai is a decision-support tool, not a storefront. Its visual language must answer one implicit user question at every moment: **"Is this system trustworthy enough to help me spend Rs 20,000 to Rs 1,50,000?"**

The answer is embedded in restraint. The base canvas is warm paper `{colors.canvas}` (#F0EDE6) not white-white, because cold white reads as template. Not cream-yellow, because that reads as dated. This is the off-white of a premium printed document, under `{colors.ink}` (#1A1916) text. Vermilion `{colors.vermilion}` (#E8420A) is the single charged color: it fires on the primary CTA, on the active nav item, on the rank #1 badge, on the "India Verified" callout. Nowhere else.

Display typography uses Barlow Condensed, a grotesque with extreme vertical compression at heavy weight. At clamp(72px, 10vw, 140px) with 800 weight and -2px tracking, one word fills a viewport. This is intentional. The AI has a point of view; it is allowed to be large about it. Body text is DM Sans: slightly rounded, highly legible at small sizes, warm without being playful.

Depth comes from paper texture (CSS noise filter on `{colors.canvas}`) and 1px `{colors.hairline}` borders. There are no drop shadows, no card elevations created by blur. Surfaces separate by being slightly different values of the same warm neutral.

**Key Characteristics:**
- Single accent: `{colors.vermilion}` carries every primary action. Used in at most 3 places per viewport.
- No drop shadows. Elevation is expressed through border contrast and background value shift.
- Display type in Barlow Condensed 700-800; body in DM Sans 400; mono in JetBrains Mono.
- Border radius is 0 on all interactive surfaces (cards, buttons, rows, inputs). The system is architectural, not bubbly.
- Three recommendation modes share the same design language. Their character is expressed through copy, pacing, and interaction model, not through color differentiation.
- `{typography.label-caps}` governs all section labels, navigation, and meta-text. 11px, 0.12em tracking, 600 weight. This creates a secondary typographic tier that reads as "system annotation" rather than content.
- The three mode names are exactly: Easy, Medium, Deep. Never prefixed, never shortened, never renamed.

---

## Colors

### Brand & Accent
- **Vermilion** (`{colors.vermilion}` #E8420A): The sole brand color. Fires on: the primary CTA button, the active navigation item underline, the recommendation #1 rank badge, the "India Verified" success state, the score bar fill on the top-ranked phone. Used at most 3 times per viewport. Never used as a background wash. Never used for decorative purposes.

### Surface
- **Canvas** (`{colors.canvas}` #F0EDE6): The default page floor. Warm off-white. Receives a subtle CSS noise texture to simulate paper grain. All pages render on this.
- **Surface** (`{colors.surface}` #F7F4EF): One half-step above canvas. Used for expanded accordion state, mode selection background wash, and secondary content areas.
- **Surface Elevated** (`{colors.surface-elevated}` #FDFCFA): The lightest surface tier. Used for cards and panels. Separated from canvas only by a `{colors.hairline}` border.

### Hairlines & Structure
- **Hairline** (`{colors.hairline}` #D8D3C8): The single border color. Used at 1px for every structural separator: nav bottom border, card borders, accordion row separators, input underlines, table dividers. Never used thicker than 1px.

### Text
- **Ink** (`{colors.ink}` #1A1916): Primary text and all interactive hover states.
- **Body** (`{colors.body}` #3C3A35): Secondary text, specification values, body copy.
- **Muted** (`{colors.muted}` #7A7669): Tertiary text, labels, placeholders, disabled states, rank indices.

### Semantic
- **India Verified** (`{colors.india-verified}` #1A7A4A): Used only for the India availability badge and verified checkmark. This color carries trust; never use it decoratively.
- **Warning** (`{colors.warning}` #C47A0A): Trade-off indicators.
- **Error** (`{colors.error}` #C42A1A): Hard failures, empty states.

---

## Typography

**Primary Display Face:** Barlow Condensed (Google Fonts, weights 600-800)
**Body & UI Face:** DM Sans (Google Fonts, weights 400-600)
**Monospace:** JetBrains Mono (Google Fonts, weight 400)

### Hierarchy

| Token | Family | Size | Weight | Line-height | Tracking |
|---|---|---|---|---|---|
| display-hero | Barlow Condensed | clamp(72-140px) | 800 | 0.92 | -2px |
| display-xl | Barlow Condensed | clamp(48-96px) | 700 | 0.95 | -1.5px |
| display-lg | Barlow Condensed | clamp(32-56px) | 700 | 1.0 | -0.8px |
| display-md | Barlow Condensed | clamp(24-40px) | 600 | 1.05 | -0.5px |
| label-caps | DM Sans | 11px | 600 | 1.2 | +0.12em |
| label-sm | DM Sans | 11px | 500 | 1.2 | +0.08em |
| body-lg | DM Sans | 18px | 400 | 1.6 | -0.01em |
| body-md | DM Sans | 15px | 400 | 1.6 | -0.01em |
| body-sm | DM Sans | 13px | 400 | 1.5 | 0 |
| mono | JetBrains Mono | 13px | 400 | 1.5 | 0 |
| button | DM Sans | 13px | 600 | 1 | +0.04em |
| nav | DM Sans | 12px | 500 | 1 | +0.06em |

### Principles
Display type at extreme scale communicates the weight of the AI's judgment. A recommendation engine that whispers is not trustworthy. One that declares in condensed grotesque with negative tracking reads like a verdict. The display size is always clamped fluid: no breakpoints for headings, just a linear interpolation from mobile minimum to desktop maximum.

`{typography.label-caps}` is used consistently for every "annotation": section titles like "AI EXPERT PITCH", column headers like "RANK / MODEL / MATCH", and mode labels. The uppercase with wide tracking separates annotation text from content.

Monospace is used in exactly two places: the budget readout number in Medium mode (gives it a "readout" character), and inline specification values in the detail spec table.

---

## Layout

### Grid & Container
- Max content width: 1320px, centered
- Page gutter: clamp(24px, 5vw, 80px) — fluid
- Section gap: `{spacing.section}` (96px) between major page sections
- Column grid: 12 columns, 20px gutter (for expanded results panel and phone detail)

### Whitespace Philosophy
The page breathes. The home hero section is full-viewport-height with content vertically centered. The mode pages (Easy, Medium, Deep) are intentionally stripped: no header during the active flow, no footer. The user came here to make a decision; everything that does not serve that decision is removed.

### Spacing Scale
- xs: 4px (icon-to-label gaps)
- sm: 8px (inline element spacing)
- md: 12px (compact padding)
- base: 16px (default padding unit)
- lg: 24px (card internal padding)
- xl: 40px (section internal padding)
- xxl: 64px (between major content groups)
- section: 96px (between page sections)
- hero: 160px (hero top/bottom padding)

---

## Elevation

This system has zero drop shadows. Elevation is expressed through:

1. Background value shift: Surface-elevated (#FDFCFA) sits visually above Canvas (#F0EDE6) without a shadow.
2. Border contrast: Cards use a `{colors.hairline}` 1px border. On hover, the border shifts to `{colors.ink}`.
3. Paper texture: A subtle CSS noise filter on the canvas creates depth impression without structural shadow.

The nav bar uses `border-bottom: 1px solid {colors.hairline}` only. No blur, no shadow.

---

## Components

**nav-bar** — Sticky, 52px height. Background `{colors.canvas}`. `border-bottom: 1px solid {colors.hairline}`. Contains: left-aligned wordmark (label-caps, 14px, 700 weight, `{colors.ink}`), right-aligned mode selector links in `{typography.nav}`. Mode selector items are `{colors.muted}` at rest, `{colors.ink}` on hover, with a 1px `{colors.vermilion}` bottom underline on the active mode. Removed on Easy / Medium / Deep mode entry pages during the selection flow.

**button-primary** — `{colors.vermilion}` background, white text. `{typography.button}`. No border radius. Padding 14px x 28px, min-height 48px. On hover: opacity 0.88. No box shadow. No gradient. This is the only element allowed to be Vermilion.

**button-secondary** — Transparent background, `{colors.ink}` text. 1px `{colors.hairline}` border. Same size spec as primary. On hover: `{colors.canvas}` background. Used for secondary actions (Compare, See All Specs).

**button-ghost** — Transparent, `{colors.muted}` text, no border. Used for tertiary actions (Back, Reject).

**card-recommendation** — The result accordion expanded panel. `{colors.surface-elevated}` background, 1px `{colors.hairline}` border, zero border radius, `{spacing.xl}` padding. Three-section layout: AI Explanation (full width), Key Strengths + Compromises (2-col), Spec Table (full width). Buy button (button-primary) and Reject (button-ghost) in an action bar at the bottom.

**badge-verified** — 10px label-sm, `{colors.india-verified}` text and border, transparent background, no radius. Text: "INDIA VERIFIED". Appears inline next to brand name.

**score-bar** — 2px high, `{colors.hairline}` track, `{colors.vermilion}` fill. Width represents AI match score. No animation on mount. Used in Results accordion and phone detail sidebar.

**slider-input** — Custom-styled range input. 1px `{colors.hairline}` track, `{colors.ink}` thumb (16px square, no radius). Fill from min to thumb is `{colors.ink}`. Used in Medium mode for budget and weight sliders.

**persona-row** — Full-width click target in Easy mode. `border-bottom: 1px solid {colors.hairline}`. Left: index in label-caps, muted. Center: persona name in display-md, ink. On hover: border-bottom shifts to `{colors.vermilion}`. No background fill change, no icon, no emoji.

**mode-tile** — On home page "Choose Your Path" section. `{colors.surface}` background, 1px `{colors.hairline}` border, zero radius. Contains: mode name in display-md, description in body-sm, action label in label-caps. On hover: border becomes 1px `{colors.ink}`.

**accordion-row** — Each phone result. `border-bottom: 1px solid {colors.hairline}`. Collapsed height: 72px. Columns: rank (8ch), brand+model (flex-1), AI match % (8ch), price (12ch), chevron (24px). On hover: background shifts to `{colors.surface}`. On expand: content slides open below.

**input-text** — Deep mode. No border, no background, no radius. Only border-bottom. body-lg text. On focus: border-bottom shifts to `{colors.ink}`. Placeholder in `{colors.muted}`. Full-width.

**loading-state** — Centered on `{colors.canvas}`. A single 240px `{colors.vermilion}` progress bar (2px tall, animated width) with a label-caps label that cycles: "Searching database...", "Scoring candidates...", "Verifying India availability...". No spinner, no percentage counter.

---

## Motion

All transitions are ease at 200-240ms. No spring physics, no bounce.

- Color/border hover transitions: 200ms ease
- Accordion expand/collapse: CSS grid-template-rows trick (0fr to 1fr), 280ms ease
- Page transitions: opacity fade, 240ms ease via Framer Motion AnimatePresence
- Loading bar: CSS width animation, 3s ease-in-out, loops until data arrives
- Persona hover underline: border-bottom color transition, 220ms ease

**Forbidden motion patterns:**
- No parallax scrolling
- No scroll-triggered number counters
- No text shimmer / skeleton loaders (use loading-state component)
- No entrance animations on result rows after data loads
- No cursor follower or magnetic button effects

---

## Responsive Behavior

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Nav: wordmark + hamburger; hero: display-hero to display-xl; mode tiles: 1-up; accordion: hide score column |
| Tablet | 640-1024px | Nav shows all links; mode tiles 2-up; all accordion columns visible |
| Desktop | 1024-1440px | Full layout; expanded card 2-column; phone detail 2-column hero |
| Wide | > 1440px | Content capped at 1320px; gutters absorb remainder |

### Touch Targets
- All interactive rows and buttons: minimum 44 x 44px (WCAG AA)
- Slider thumbs: 40px x 40px click target despite 16px visual size

### Collapsing Strategy
- Nav: hamburger below 640px, drawer slides from right on canvas background with hairline borders
- Mode tiles: 3-up to 2-up to 1-up, never reflow mid-row
- Results accordion: rank and score columns collapse on mobile; only brand/model and price remain
- Deep mode input: full-viewport-height on all breakpoints

---

## Known Gaps

- Dark mode is not a documented variant. The system renders in one canvas mode only.
- Phone image handling: when imageUrl is null, the component must render a brand-logotype text treatment in Barlow Condensed large weight, muted color. Never a broken img tag.
- The Medium mode slider fill requires JavaScript to set a CSS custom property for the track fill, because native range input styling is inconsistent across browsers.
- Animation easing for accordion height on Safari may need adjustment due to CSS grid animation support quirks.
- PostHog event taxonomy is defined in the implementation plan, not in this file.
