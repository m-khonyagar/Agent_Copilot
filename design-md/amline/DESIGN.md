# Design System Inspiration of Amline (اَملاین)

## 1. Visual Theme & Atmosphere

Amline is an Iranian PropTech platform for smart real estate contract management. Its design system reflects two converging identities: the clarity of a professional enterprise SaaS dashboard and the warmth of an approachable Persian service. The visual language centers on a **teal primary** (`#179A9C`) drawn from calm water and trust — appropriate for a platform handling high-stakes real estate documents — paired with a **terracotta warm accent** (`#A44225`) that carries the earthy tones of traditional Persian architecture.

The canvas is a **mint-tinted off-white** (`#f2f8f6`) rather than pure white, which gives the interface a breathing quality — never sterile, never cold. Cards rest on white (`#ffffff`) against this softly tinted background, creating a clear but gentle layering. The dark mode flips to a deep **dark teal-black** (`#0c1414`), a near-black with a hint of warmth, keeping the teal brand identity alive even in dark contexts.

Being a Persian-language platform, the entire design is **RTL (right-to-left)**. The primary typeface is **Vazirmatn** — the most legible modern Arabic-script font for digital interfaces, designed specifically for Persian and Arabic text. All text flows right-to-left, tab navigation anchors right, and the sidebar sits on the right edge of the screen.

The design is **data-dense but not cluttered**. A 4pt base grid governs every spacing decision. Cards, tables, sidebars, and badges coexist in a system calibrated for administrators who process dozens of contracts, leads, and wallet transactions per session. Hover states and transitions are subtle (0.2s) — fast enough to feel responsive, slow enough to feel polished.

**Key Characteristics:**
- Vazirmatn / Vazir for all Persian text — designed for screen legibility in Arabic script
- RTL layout throughout — sidebar right, text right-aligned, slide-in animations from right
- Mint canvas background (`#f2f8f6`) with white cards — gentle depth without stark contrast
- Teal primary (`#179A9C`) as the single dominant action color; terracotta (`#A44225`) as warm brand accent
- 4pt grid spacing (4px, 8px, 12px, 16px, 20px, 24px, 32px)
- Rounded-corner philosophy: 8px small, 12px standard, 16px card, 20px large panel
- Multi-mode: full light/dark token system with distinct dark surfaces
- Transitions at 0.2s ease for background/color, 0.3s for sidebar transforms

## 2. Color Palette & Roles

### Primary (Teal)
- **Amline Teal** (`#179A9C`): Primary action color — buttons, active sidebar indicator, focus rings, progress steps. Builds trust through its blue-green quality.
- **Teal Hover** (`#126D6F`): Darker teal on hover/active state for primary buttons.
- **Teal Light** (`#5EC4C6`): Legacy lighter teal alias for gradients or secondary highlights.
- **Teal Muted** (`rgba(23, 154, 156, 0.14)`): Background tint for active sidebar items, selected chips, teal badges.

### Brand Warm (Terracotta)
- **Terracotta** (`#A44225`): Secondary brand identity color — used for specific accent moments (warnings, brand highlights, secondary CTAs). Evokes Persian earthenware.
- **Terracotta Muted** (`rgba(164, 66, 37, 0.12)`): Soft background for terracotta-accented components.

### Background & Canvas
- **Page Background** (`#f2f8f6`): The mint-tinted off-white page canvas. Not pure white — has a faint green-teal warmth that ties to the brand.
- **Surface White** (`#ffffff`): Card and panel background — lifts off the canvas cleanly.
- **Surface Elevated** (`#ffffff`): Same as surface, reserved for modals and elevated panels.
- **Surface Muted** (`#EAFAF5`): Deeper mint — used for active sidebar items, table headers, hover states, subtle section backgrounds.

### Foreground & Text
- **Foreground** (`#1E1E1F`): Primary text — almost black with a near-imperceptible warmth.
- **Foreground Muted** (`#565564`): Secondary text, descriptions, card descriptions.
- **Foreground Subtle** (`#9E9EA7`): Tertiary text, placeholders, captions, disabled labels.

### Border & Dividers
- **Border** (`#E7E7E9`): Standard border for cards, inputs, table rows, sidebar dividers.
- **Border Strong** (`#D7D9DE`): Emphasized borders, scrollbar thumbs, heavier dividers.

### Semantic Colors
- **Success** (`#0D9488`): Positive status badges, completed states, success toasts. Teal-adjacent for brand coherence.
- **Warning** (`#F59E0B`): Caution states, pending contract stages, amber alerts.
- **Error** (`#DC2626`): Destructive actions, failed states, validation errors.
- **Info** (`#0284C7`): Informational notifications, neutral highlights, link anchors.

### Semantic Muted Backgrounds
- **Success Muted** (`rgba(13, 148, 136, 0.12)`)
- **Warning Muted** (`rgba(245, 158, 11, 0.14)`)
- **Error Muted** (`rgba(220, 38, 38, 0.10)`)
- **Info Muted** (`rgba(2, 132, 199, 0.10)`)

### Focus & Ring
- **Ring** (`#179A9C`): Focus ring color for all interactive elements — consistent teal identity.

### Dark Mode Overrides
- **Page Background** (`#0C1414`): Deep teal-black — not neutral dark, has warmth.
- **Surface** (`#111827`): Dark navy-gray panels and cards.
- **Surface Elevated** (`#1E293B`): Modals, elevated layers.
- **Surface Muted** (`#162022`): Table headers, active items in dark.
- **Border** (`#334155`), **Border Strong** (`#475569`): Slate-toned borders for dark mode.
- **Primary Dark** (`#2DD4BF`): Lighter teal for dark mode — maintains contrast ratio.
- **Terracotta Dark** (`#E07A5F`): Lighter terracotta for dark mode legibility.

## 3. Typography Rules

### Font Family
- **Primary**: `Vazirmatn`, `Vazir`, `Tahoma`, `system-ui`, `sans-serif`
- Vazirmatn is a variable-weight Persian typeface with excellent screen rendering. Always loaded via web font. Falls back to Vazir (earlier version), then Tahoma (universally available on Windows/Mac for Persian), then system-ui.
- No separate monospace font — code snippets use system-ui monospace or inherit from browser defaults.

### Type Scale & Hierarchy

| Role | Class | Size | Line Height | Weight | Notes |
|------|-------|------|-------------|--------|-------|
| Display | `.amline-display` | 28px (md: 32px) | 36px | 700 (bold) | Page titles, hero headings |
| Title | `.amline-title` | 18px (md: 20px) | 28px | 600 (semibold) | Section headings, card titles |
| Body | `.amline-body` | 14px (md: 16px) | relaxed | 400 | Standard paragraph text |
| Caption | `.amline-caption` | 12px | default | 400 | Metadata, timestamps, helper text |
| Base HTML | `html, body` | 16px | 1.65 | 400 | Base — slightly loose for Persian legibility |
| Button / Label | `.btn`, `.label` | 14px | — | 500 (medium) | Interactive labels |
| Badge / Tag | `.badge` | 12px | — | 600 (semibold) | Status indicators |
| Table Header | `.table th` | 14px | — | 500 | Column headers |

### Principles
- **Right-to-left always**: All `text-align` defaults are `right`. Persian characters and word-spacing are tuned for RTL reading direction.
- **Loose base line-height (1.65)**: Persian characters are taller and more complex than Latin glyphs. The extra line-height prevents characters from visually crowding across lines.
- **Letter-spacing 0.01em globally**: A very slight positive tracking to improve Persian character separation on small screens — opposite of Latin design systems which typically use negative tracking for headings.
- **Weight range 400–700**: Four weights in use — 400 (body), 500 (interactive/medium), 600 (semibold/title), 700 (bold/display). No ultra-light weights.
- **No italic**: Persian typography does not conventionally use italic. Use weight 600 for emphasis instead.

## 4. Component Stylings

### Buttons

**Primary Button (`.btn.btn-primary`)**
- Background: `#179A9C`
- Text: `white`
- Padding: `0 16px` (px-4)
- Height: min-height `44px` (11 × 4px = 44px — minimum touch target)
- Radius: `0.75rem` (12px — `--amline-radius-md`)
- Hover: background `#126D6F`
- Focus: `ring-2 ring-[#179A9C] ring-offset-2`
- Disabled: `opacity-50`, pointer-events none

**Secondary Button (`.btn.btn-secondary`)**
- Background: `#64748B` (slate-600)
- Text: `white`
- Hover: `#475569` (slate-700)
- Same radius, padding, and min-height as primary

**Outline Button (`.btn.btn-outline`)**
- Background: `white` (`--amline-surface`)
- Border: `1px solid #E7E7E9` (`--amline-border`)
- Hover: Background shifts to `#EAFAF5` (`--amline-surface-muted`)
- Text: inherits foreground

**Ghost Button (`.btn.btn-ghost`)**
- Background: transparent
- Hover: `#EAFAF5` muted surface
- No border, no shadow

### Cards (`.card`)
- Background: `#ffffff` (`--amline-surface`)
- Border: `1px solid #E7E7E9`
- Radius: `1rem` (16px — `--amline-radius-lg`)
- Shadow: `0 1px 2px rgba(30, 30, 31, 0.06)` (sm)
- Header: `border-bottom: 1px solid #E7E7E9`, padding `20px`
- Content padding: `20px`
- Title: 18px semibold, tracking-tight
- Description: 14px `#565564`

### Inputs (`.input`)
- Height: min-height `44px`
- Border: `1px solid #E7E7E9`
- Radius: `0.75rem` (12px)
- Background: `#ffffff`
- Padding: `8px 14px` (py-2 px-3.5)
- Text size: 14px
- Placeholder: `#9E9EA7`
- Focus: `ring-2 ring-[#179A9C]`
- Full width by default

### Badges (`.badge`)
- Shape: pill (`rounded-full`)
- Padding: `0 10px` (px-2.5), `2px` vertical (py-0.5)
- Font: 12px semibold
- **Success**: background `#0D9488`, text white
- **Warning**: background `#F59E0B`, text white
- **Error**: background `#DC2626`, text white
- **Info**: background `#0284C7`, text white

### Sidebar (`.sidebar`)
- Width: `288px` (72 × 4px)
- Position: fixed right (RTL), full height, z-50
- Background: `#ffffff`
- Border-left: `1px solid #E7E7E9` (right edge in LTR terms, left edge in RTL terms)
- Shadow: `0 4px 16px rgba(30,30,31,0.08)`
- Transition: `transform 300ms`
- Mobile: slides in/out; Desktop lg+: static

**Sidebar Item (`.sidebar-item`)**
- Padding: `10px 24px` (py-2.5 px-6)
- Font: 14px, `#565564`
- Hover: background `#EAFAF5`, text `#1E1E1F`
- Active: `border-right: 4px solid #179A9C`, background `rgba(23,154,156,0.14)`, text `#179A9C`, weight 500

### Tables (`.table-container`)
- Container: full width, `overflow-auto`, `rounded-lg`, `border`, white background
- Header cells (`th`): height 48px, background `#EAFAF5`, padding `0 16px`, text `#565564`, `font-medium`, `text-right`
- Data cells (`td`): `border-top: 1px solid #E7E7E9`, padding `16px`, text `#1E1E1F`
- Row hover: background `#F1F5F9` (slate-100 light), `#1E293B` (dark)

### Labels (`.label`)
- 14px, `font-medium` (weight 500)
- Color: `#1E1E1F` (foreground)

## 5. Layout Principles

### Spacing System (4pt Grid)
| Token | Value | Tailwind |
|-------|-------|---------|
| `--amline-space-1` | 4px | `p-1` |
| `--amline-space-2` | 8px | `p-2` |
| `--amline-space-3` | 12px | `p-3` |
| `--amline-space-4` | 16px | `p-4` |
| `--amline-space-5` | 20px | `p-5` |
| `--amline-space-6` | 24px | `p-6` |
| `--amline-space-8` | 32px | `p-8` |

### Container
- Max width: `1400px` (`.container-amline`)
- Horizontal padding: `16px` (xs), `24px` (sm), `32px` (lg)
- Centered with `mx-auto`

### Grid & Layout
- Primary layout: sidebar (right) + main content (left) — RTL-native
- Sidebar width: 288px fixed; content fills remaining width
- Dashboard grids: 1 column mobile → 2 columns tablet → 3–4 columns desktop
- KPI cards: equal-width grid, responsive columns
- Table sections: full width with horizontal scroll on small screens

### Whitespace Philosophy
- Cards have `20px` padding on all sides — breathing room for data-dense views
- Section separation by card boundaries, not large vertical gaps
- Compact density: professional admin tool, not a marketing site. Information is primary, decoration is secondary.

### Border Radius Scale
| Size | Value | Use |
|------|-------|-----|
| Small (sm) | 8px (0.5rem) | Small chips, scrollbar thumbs |
| Medium (md) | 12px (0.75rem) | Buttons, inputs, most interactive elements |
| Large (lg) | 16px (1rem) | Cards, panels, table containers, sidebar |
| XL | 20px (1.25rem) | Large modal panels, hero elements |
| Full pill | 9999px | Badges, status tags |

## 6. Depth & Elevation

| Level | Shadow | Use |
|-------|--------|-----|
| Flat (0) | none | Page background, plain text blocks |
| Subtle (sm) | `0 1px 2px rgba(30,30,31,0.06)` | Cards at rest |
| Standard (md) | `0 4px 16px rgba(30,30,31,0.08)` | Sidebar, modals, dropdowns |
| Prominent (lg) | `0 12px 40px rgba(30,30,31,0.10)` | Elevated sheets, fullscreen overlays |

**Shadow Philosophy**: Amline uses three purposeful shadow levels — not decorative, not heavy. The background canvas (`#f2f8f6`) creates natural depth against white (`#ffffff`) cards without needing strong shadows. Shadows are used mainly for floating elements (sidebar, modals) rather than static cards. In dark mode, shadow opacity increases dramatically (0.35–0.45) because dark surfaces don't create the natural background/foreground contrast that the light canvas does.

### Animation & Transition
- Color/background transitions: `0.2s ease`
- Sidebar slide: `0.3s` transform
- Fade in: `0.28s ease-out` (opacity 0→1 + translateY -8px→0)
- Slide in (RTL): `0.28s ease-out` (opacity 0→1 + translateX -12px→0 — inverted for LTR equivalent in RTL context)

## 7. Do's and Don'ts

### Do
- Use `#179A9C` teal as the single dominant action color — buttons, active states, focus rings, selected items
- Always use the mint canvas (`#f2f8f6`) as the page background, not white
- Use white (`#ffffff`) for card/panel backgrounds to lift them off the canvas
- Use `#EAFAF5` (surface-muted) for hover backgrounds, table headers, and active sidebar items
- Apply RTL direction (`dir="rtl"`) at the HTML root — Vazirmatn needs RTL context for correct rendering
- Maintain minimum touch target of `44px` height for all buttons and inputs
- Use the 4pt spacing grid — all spacing should be multiples of 4px
- Apply `0.75rem` (12px) radius to buttons and inputs; `1rem` (16px) to cards
- Use badge variants (success/warning/error/info) to communicate contract and lead statuses
- Apply the terracotta (`#A44225`) only for secondary brand moments, never as an action color

### Don't
- Don't use pure `#ffffff` as the page background — it removes the brand warmth of the mint canvas
- Don't use italic — Persian typography doesn't conventionally use italic; use weight 600 for emphasis
- Don't apply negative letter-spacing — Vazirmatn is optimized for slight positive tracking (0.01em)
- Don't create UI that assumes LTR reading — icons, arrows, progress indicators must all be RTL-aware
- Don't use the primary teal for destructive or warning states — use semantic error (`#DC2626`) and warning (`#F59E0B`)
- Don't use heavy shadows (> 0.12 opacity) on static cards — keep elevation whisper-level for clean SaaS aesthetic
- Don't use weight 300 (light) — minimum text weight is 400 for Persian legibility at screen sizes
- Don't place the sidebar on the left — in RTL layout, the sidebar belongs on the right

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile (xs) | ≥ 380px | Extra-small mobile baseline |
| Mobile | < 640px | Single column, sidebar hidden (slide-in on toggle) |
| Tablet (sm) | 640px | Two-column grids begin, slightly larger type |
| Tablet (md) | 768px | Dashboard KPI grid expands |
| Desktop (lg) | 1024px | Sidebar becomes static/persistent |
| Desktop (xl) | 1280px | Full three/four-column dashboards |
| Wide (2xl) | 1400px | Container max-width — content stays centered |

### Touch Targets
- All buttons and inputs: minimum `44px` height (enforced via CSS on `button` and `.btn` under 1024px breakpoint)
- Sidebar items: `10px` vertical padding, naturally exceeds 44px with 14px text

### Collapsing Strategy
- Sidebar: fixed overlay (with toggle button) on mobile/tablet → static panel at `lg` breakpoint
- Dashboard grids: 1 → 2 → 3–4 columns based on screen width
- Tables: horizontal scroll with `overflow-auto` wrapper — column count stays consistent
- Cards: full width on mobile → proportional grid on tablet+
- Display text: scales down from 32px to 28px (base → md breakpoint flipped for RTL responsive order)

### RTL-Specific Responsive Notes
- Slide-in animations use `translateX(-12px)` in RTL context (content enters from right)
- Active sidebar indicator uses `border-right` (right border in RTL = visual left edge of sidebar item)
- Text alignment: `text-right` is the baseline, `text-left` only for numbers and code
- Icon orientation: directional icons (arrows, chevrons) must be flipped for RTL — use CSS `transform: scaleX(-1)` or RTL-aware icon variants

## 9. Agent Prompt Guide

### Quick Color Reference
- Page background: `#f2f8f6`
- Card/surface: `#ffffff`
- Surface hover/active: `#EAFAF5`
- Primary CTA: `#179A9C`
- Primary hover: `#126D6F`
- Primary ring: `#179A9C`
- Heading text: `#1E1E1F`
- Body text: `#565564`
- Subtle/placeholder: `#9E9EA7`
- Border: `#E7E7E9`
- Success: `#0D9488`
- Warning: `#F59E0B`
- Error: `#DC2626`
- Info: `#0284C7`

### Example Component Prompts
- "Create a Persian/RTL admin dashboard card. Direction: RTL. Background: `#ffffff`, border: `1px solid #E7E7E9`, radius: 16px, shadow: `0 1px 2px rgba(30,30,31,0.06)`. Title at 18px Vazirmatn weight 600, color `#1E1E1F`, text-right. Description at 14px weight 400, color `#565564`. Card sits on a `#f2f8f6` page background."
- "Build an RTL sidebar. Position: fixed right. Width: 288px. Background: `#ffffff`. Border-left: `1px solid #E7E7E9`. Active item: background `rgba(23,154,156,0.14)`, border-right `4px solid #179A9C`, text `#179A9C`, weight 500. Inactive item: text `#565564`, hover background `#EAFAF5`. Font: Vazirmatn 14px, text-right."
- "Design a status badge row for contract states. Use pill shape (9999px radius, px-2.5 py-0.5, 12px semibold, white text): success `#0D9488` (تأیید شده / Approved), warning `#F59E0B` (در انتظار / Pending), error `#DC2626` (رد شده / Rejected), info `#0284C7` (در بررسی / Under Review)."
- "Create a primary button: background `#179A9C`, text white, radius 12px, height 44px, px-4, Vazirmatn 14px medium. Hover background `#126D6F`. Focus ring: `2px solid #179A9C` with 2px offset."
- "Build a data table for contract listings. RTL direction. Table container: white background, border `1px solid #E7E7E9`, radius 16px, overflow-auto. Header row: background `#EAFAF5`, height 48px, px-4, text-right, `#565564` medium 500. Data rows: border-top `1px solid #E7E7E9`, p-4, `#1E1E1F`, hover background `#F1F5F9`."

### Iteration Guide
1. The mint canvas (`#f2f8f6`) is not white — ensure your component renders on this background to see the correct card lift
2. RTL is structural, not cosmetic — set `dir="rtl"` on the container or `html` element, not just `text-align: right`
3. Teal `#179A9C` is the single primary action color; never use terracotta for CTAs
4. Font loading: always include Vazirmatn via Google Fonts or a local font face — `font-family: 'Vazirmatn', 'Vazir', Tahoma, sans-serif`
5. All button/input heights must be at least 44px — this is enforced via CSS for mobile, but maintain it across all breakpoints
6. In dark mode, switch `--amline-primary` to `#2DD4BF` (lighter teal) — pure `#179A9C` becomes too low-contrast on dark surfaces
7. Sidebar active state uses `border-right` in RTL (not `border-left`) — this places the accent line on the visual left of the item (the reading-start side in RTL)
