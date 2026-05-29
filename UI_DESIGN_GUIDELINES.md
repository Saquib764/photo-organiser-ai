# TheFluxTrain UI Design Guidelines

Visual design system for **Dashboard**, **App UI** (generation & workflow pages), and **Flow Studio** (node editor). Extracted from the mission-pluto frontend.

**Stack:** Nuxt UI 3 + Tailwind CSS · **Primary:** `pink` (`frontend/app/app.config.ts`) · **Neutral:** `slate` · **Icons:** Heroicons + Iconify (`heroicons:`, `ph:`)

---

## Table of contents

1. [Three UI surfaces](#1-three-ui-surfaces)
2. [Shared foundation](#2-shared-foundation)
3. [Dashboard UI](#3-dashboard-ui)
4. [App UI (normal pages)](#4-app-ui-normal-pages)
5. [Flow Studio (node editor)](#5-flow-studio-node-editor)
6. [Cross-surface mapping](#6-cross-surface-mapping)
7. [Portable CSS variables](#7-portable-css-variables)
8. [Source files](#8-source-files)

---

## 1. Three UI surfaces

| Surface | Layout | Theme default | Density | Primary use |
|---------|--------|---------------|---------|-------------|
| **Dashboard** | `dashboard` — sidebar + scrollable main | Light (`bg-slate-50`) | Comfortable | Home, nav hub, project cards, flow list |
| **App UI** | `app` — header + main (+ optional folder panel) | Light preferred; dark supported | Comfortable → compact in tool areas | Image/video/voice generation, collections, characters |
| **Flow Studio** | Full-screen custom shell (no layout) | **Always dark** | Dense | Node canvas editor `flow-studio/[id]` |

```text
Dashboard / App          Flow Studio
─────────────────        ─────────────────
Light surfaces           gray-950 canvas
Pink nav accents         Pink = selection + CTA
Readable body text       9–12px micro type
Cards & gradients        Nodes & wires
```

**Rule:** Do not use Flow Studio’s near-black palette on dashboard or generation pages. Do use the same **pink primary**, **Heroicons**, and **Nuxt UI** component patterns across all three.

---

## 2. Shared foundation

### Brand

| Token | Value | Usage |
|-------|--------|--------|
| Primary | Tailwind `pink` / `primary-*` | CTAs, active nav, links on hover, badges, credits |
| Neutral | `slate` (app config) | Page backgrounds on dashboard |
| Logo | `/logo.webp`, `h-6`–`h-10`, `rounded` / `rounded-lg` | Header, Flow Studio toolbar |

### Interactive text (light UI)

```
Default:  text-gray-700 dark:text-gray-300
Muted:    text-gray-500 dark:text-gray-400
Heading:  text-gray-900 dark:text-white
Hover link: hover:text-pink-600 dark:hover:text-pink-400
```

### Buttons (Nuxt UI conventions)

| Context | Variant | Size | Notes |
|---------|---------|------|-------|
| Primary CTA | `solid` `color="primary"` | `sm`–`lg` | Main actions; optional `shadow-lg shadow-primary-500/20` on hero CTAs |
| Secondary | `ghost` or `soft` `color="neutral"` | `xs`–`sm` | Toolbar, refresh, cancel |
| Destructive | `color="error"` | `xs`–`sm` | Delete; often `variant="ghost"` or `soft` |
| Icon-only | `ghost` `square` | `xs`–`sm` | Inspector, gallery overlays |

### Credits display (shared pattern)

```
Pulse dot: w-2 h-2 bg-pink-500 rounded-full animate-pulse
Text: font-bold text-pink-600 dark:text-pink-400
Pill: bg-primary-50 dark:bg-primary-900/20 border border-primary-100 + bolt icon
```

### Toasts

Nuxt UI notifications, `position: 'top-0'` (app config). Colors: `success`, `error`, `warning`, `primary`.

### Cards (light UI default)

```
Surface: bg-white or bg-white/70 backdrop-blur
Border: border border-gray-200/70 or border-gray-200
Radius: rounded-lg (tiles) · rounded-xl / rounded-3xl (marketing-style cards)
Shadow: shadow-sm → hover:shadow-md / hover:shadow-xl
Hover border: hover:border-primary-200
```

### Semantic colors (feature accents)

Use **sparingly** for category pills, action card icons, or section icons — not for global chrome:

| Color | Example use |
|-------|-------------|
| `indigo` | Train model, collection page icons |
| `purple` | Image generator, gallery section |
| `violet` | Similar-gallery headings |
| `emerald` / `amber` / `sky` | Project type pills (`ProjectCard`) |
| `red` | Delete, errors |
| `amber` | Dev / public-collection toggles |

### Icons

- **Heroicons** in Nuxt UI: `i-heroicons-*`
- **Sidebar / legacy:** `heroicons:*-solid`, `ph:*-duotone` via `<Icon name="..." />`
- **Flow Studio chrome:** `i-heroicons-*` consistently

---

## 3. Dashboard UI

**Layout:** `frontend/app/layouts/dashboard.vue`  
**Navigation:** `frontend/app/components/dashboard/NavigationSidebar.vue`  
**Typical pages:** `/dashboard`, `/flow-studio` (list), pages with `layout: 'dashboard'`

### Shell

```html
<div class="flex flex-col h-[100dvh] max-h-[100dvh] overflow-hidden bg-slate-50">
  <AnnouncementBar />
  <AppHeader />
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside><!-- NavigationSidebar w-64 --></aside>
    <main class="flex-1 min-h-0 overflow-y-auto"><!-- page --></main>
    <aside><!-- optional FolderSelector w-80 --></aside>
  </div>
</div>
```

- **Page background:** `bg-slate-50` (layout), main content often `bg-transparent`
- **Folder panel:** `w-80`, `bg-white dark:bg-gray-900`, `border-l border-gray-200 dark:border-gray-800`

### Navigation sidebar

| Property | Value |
|----------|--------|
| Width | `w-64` |
| Background | `bg-gradient-to-br from-pink-50 to-rose-100` |
| Dark | `dark:from-pink-900/20 dark:to-rose-900/20` |
| Shape | `rounded-r-xl`, height `h-[calc(100vh-100px)]` |

**Nav item (default):**

```
UButton variant="ghost" color="primary"
px-2 py-2.5 (main) · py-1.5 (compact footer)
hover:bg-pink-100/60 dark:hover:bg-pink-900/30
border-pink-200/20 dark:border-pink-700/20
hover:border-pink-300 dark:hover:border-pink-600
```

**Nav item (active):**

```
bg-pink-100/60 dark:bg-pink-900/30
border-pink-300 dark:border-pink-600
```

**Labels:** `text-sm font-semibold` (main) · `text-xs font-medium` (compact)  
**Hover label:** `group-hover:text-pink-600 dark:group-hover:text-pink-400`  
**Icons:** `size-5` + `group-hover:scale-110 transition-transform duration-300`

**Section label (Experimental):**

```
text-[10px] font-semibold uppercase tracking-wide
text-pink-600/70 dark:text-pink-400/70
```

**Mobile:** `UDrawer` left, same gradient background; hamburger `fixed top-18 left-2` with white/dark card shadow.

### Page content patterns

**Section heading (dashboard home):**

```
h2: text-xl font-bold text-gray-800
subtitle: text-sm text-gray-500 mt-1 max-w-2xl
```

**Count badge:**

```
inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary
```

**Content width:** Often unconstrained in main; flow list uses `max-w-6xl mx-auto px-6 lg:px-12 py-12`.

### Action cards & starter tiles

**Thumbnail card** (`ActionCard`, `FlowAppStarterCard`):

```
Container: rounded-xl border border-gray-200/90 bg-white shadow-sm
Hover: hover:border-gray-300 hover:shadow-md
Image: aspect-[16/10], object-cover, group-hover:scale-[1.03]
Overlay: gradient-to-t from-black/20
Icon badge: size-9 rounded-lg bg-white/90 shadow-sm ring-1 ring-black/5
Title: text-sm font-semibold text-gray-900 group-hover:text-primary-600
Description: text-xs text-gray-600 line-clamp-2
Width: sm:w-56 or min(100%, 220px)
```

**Icon-only card (UCard fallback):**

```
bg-white shadow-md border-0 hover:bg-gray-50 hover:shadow-lg
Header icon: p-2 rounded-full text-white + bg-{color}-500 (indigo, purple, etc.)
Title: text-base font-semibold text-gray-900
Body: text-sm text-gray-600
```

### Project cards

- Grid: `grid-cols-2 lg:grid-cols-3 gap-3`
- Hover: `hover:scale-[1.02] transition-all duration-300`
- **Type pills:** soft colored rings, e.g. `bg-indigo-50 text-indigo-700 ring-1 ring-indigo-100`
- Loading/error: gradient `UCard` (`from-gray-50 to-gray-100`, `from-red-50 to-red-100`)

### Flow Studio list (within dashboard)

Marketing-style cards on light background:

```
Card: bg-white/70 backdrop-blur border border-gray-200/70 rounded-3xl
Hover: hover:shadow-xl hover:shadow-primary-500/5 hover:border-primary-200
Title: text-xl font-bold text-gray-900 group-hover:text-primary-600
Empty state: primary-50 icon box, text-2xl title
CTA: size="lg" shadow-lg shadow-primary-500/20
```

### Dashboard typography scale

| Element | Classes |
|---------|---------|
| Page title (marketing) | `text-3xl md:text-5xl font-bold text-gray-900` |
| Section title | `text-xl font-bold text-gray-800` |
| Card title | `text-sm`–`text-base font-semibold` |
| Meta / dates | `text-xs text-gray-500` |
| Loading hint | `text-xs text-blue-500 animate-pulse` |

### Dashboard do / don’t

**Do:** Keep sidebar pink gradient; use light gray page backgrounds; use `primary` for CTAs only.  
**Don’t:** Use `gray-950` page backgrounds; use Flow Studio micro-type (`text-[9px]`); force dark mode on dashboard home (dashboard index sets `colorMode.preference = 'light'`).

---

## 4. App UI (normal pages)

**Layout:** `frontend/app/layouts/app.vue` — `AppHeader` + scrollable main + optional folder column (`w-80`).  
**Typical pages:** `/image/*`, `/video/*`, `/voice/*`, `/collections/*`, `/characters/*`, `/project/*` — `definePageMeta({ layout: 'app' })`.

### Shell

```html
<div class="flex flex-col min-h-screen">
  <AnnouncementBar />
  <AppHeader />  <!-- UHeader, border-b border-gray-200 dark:border-gray-700 -->
  <main class="flex-1 overflow-y-auto"><!-- page --></main>
</div>
```

**Header (`AppHeader`):**

- Logo `h-10`, breadcrumb `text-gray-700 dark:text-gray-300`
- Nav links: `hover:text-pink-600 dark:hover:text-pink-400`
- Credits in menu with pink pulse dot
- Folder toggle: hidden on `/dashboard`, `/collections`, `/characters`

### Page layouts

**A. Generation workspace (split view)** — e.g. `image/from-image.vue`

```
Root: h-[calc(100vh-65px)] flex flex-col bg-gray-50 dark:bg-gray-900 overflow-hidden
Main: flex-1 flex lg:flex-row
  - Center: GenerationWorkspace (gallery + tabs) p-4
  - Bottom overlay: FloatingPromptInput (absolute, z-[100])
```

**B. Collection / workflow editor** — e.g. `collections/[id].vue`

```
Root: bg-gradient-to-br from-slate-50 to-indigo-50/40
      dark:from-gray-900 dark:to-gray-800
Grid: lg:grid-cols-12 — sidebar col-span-3, gallery col-span-9
Max width: max-w-[1920px] mx-auto
```

**C. Simple content pages**

- Padding: `px-3 lg:px-4`, `py-4`–`py-12`
- Prefer light gradients or `bg-gray-50` over flat white for large workspaces

### Generation workspace tabs

```
Tab bar: border-b border-gray-200 dark:border-gray-700
Tab: text-sm font-medium border-b-2 -mb-px
  Active: text-gray-900 dark:text-white border-primary-500
  Inactive: text-gray-500 hover:text-gray-700 border-transparent
Icon: size-4, label hidden on xs (hidden sm:inline)
```

### Floating prompt bar

Primary input pattern for generation pages:

```
Container: fixed bottom-4 lg:bottom-6, max-w-3xl, z-[100]
Shell: bg-pink-50/90 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl
       border border-pink-200 dark:border-gray-700/50
       shadow-lg shadow-pink-100/50
Textarea: bg-white/70 dark:bg-gray-700/50 border-pink-200 rounded-xl
          text-xs lg:text-sm, min-h-[40px], max-h-[150px]
Generate: UButton color="primary" rounded-xl, paper-airplane icon
Credits footer: bg-primary-50 rounded-lg border border-primary-100, text-[10px] font-bold
```

### Gallery & asset overlays

**Grid thumbnails:**

```
aspect-[3/4] or masonry columns
rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600
Hover overlay: bg-black/40 opacity-0 group-hover:opacity-100
```

**Overlay action buttons (on images):**

```
UButton size="xs" variant="solid" color="neutral"
class="!bg-white/90 hover:!bg-white text-gray-900"
```

### Forms & controls (app pages)

| Control | Pattern |
|---------|---------|
| Page title | `text-lg font-semibold text-gray-900 dark:text-white` |
| Section title | `text-base font-semibold` + optional colored icon |
| Helper text | `text-xs text-gray-600 dark:text-gray-400 leading-relaxed` |
| Labels | `text-xs` or `UFormField` defaults |
| Inputs | Nuxt UI default sizes (`md` in app config) or `size="xs"` in dense sidebars |
| Dropdowns | `GenericDropdown` with full width in side panels |

**Light mode:** Many pages set `colorMode.preference = 'light'` explicitly.

### Feature page accents

Collection workflow uses **indigo** for collection icon (`text-indigo-600`) and **violet** for gallery heading (`text-violet-500`) — secondary accents on top of neutral/pink base.

### App UI typography scale

| Element | Classes |
|---------|---------|
| Page title | `text-lg`–`text-3xl font-semibold` / `font-bold` |
| Section | `text-base font-semibold` |
| Body | `text-sm` / `text-base` |
| Helper | `text-xs text-gray-500`–`text-gray-600` |
| Tab | `text-sm font-medium` |

### App UI do / don’t

**Do:** Support `dark:` variants on borders and text; use pink for primary actions; use floating prompt pattern for generation.  
**Don’t:** Use Flow Studio density (`text-[9px]` labels everywhere); use dark-only gray-950 backgrounds on full pages unless building an editor.

---

## 5. Flow Studio (node editor)

**Page:** `frontend/app/pages/flow-studio/[id].vue` — full viewport, **always dark**, no app/dashboard layout.

### Design intent

| Principle | Implementation |
|-----------|----------------|
| **Tool-first, not marketing** | Near-black canvas, dense UI, small type, uppercase section labels |
| **Hierarchy via surface elevation** | `gray-950` (deepest) → `gray-900` (panels) → `gray-800` (borders, chips) |
| **Accent = action & selection** | `primary-*` (pink) for selection, ports (outputs), generate, credits |
| **Semantic color on icons only** | Red = delete, blue = import, green = export, amber = dev tools, pink = folder |
| **Glass on floating controls** | `bg-gray-900/80 backdrop-blur` for zoom toolbar |

### Layout architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Header (h-12, bg-gray-900, border-b gray-800)               │
├──────────┬──────────────────────────────────┬───────────────┤
│ Library  │ Canvas (flex-1, bg-gray-950)     │ Inspector /   │
│ w-64     │                                  │ UI Viewer /   │
│          │                                  │ Gallery w-56  │
├──────────┴──────────────────────────────────┴───────────────┤
│ Footer (h-6, bg-gray-900)                                   │
└─────────────────────────────────────────────────────────────┘
```

| Region | Width | Background |
|--------|-------|------------|
| Node library (left) | `w-64` (256px) | `bg-gray-900` |
| Canvas (center) | `flex-1` | `bg-gray-950` |
| Inspector / UI viewer (right) | `w-64` | `bg-gray-900` |
| Asset gallery (optional) | `w-56` | `bg-gray-900` |
| Header | `h-12` (48px) | `bg-gray-900` |
| Footer | `h-6` (24px) | `bg-gray-900` |

Panel headers inside sidebars: `h-10` with `border-b border-gray-800 px-4`.

### Color system (Flow Studio)

| Token | Class | Hex (approx.) | Use |
|-------|--------|---------------|-----|
| Canvas / deepest | `bg-gray-950` | `#030712` | Main canvas, node headers, media wells, inputs |
| Panel | `bg-gray-900` | `#111827` | Sidebars, header, footer, node body |
| Border | `border-gray-800` | `#1f2937` | Panel splits, node borders, dividers |
| Elevated chip | `bg-gray-800` | `#1f2937` | Toolbar buttons, port idle, hover targets |
| Subtle border | `border-gray-700` | `#374151` | Button borders, meta nodes |

**Text (dark UI):**

| Role | Classes |
|------|---------|
| Primary body | `text-white` |
| Node title | `text-gray-200` `text-[10px] font-bold` |
| Secondary | `text-gray-300` `text-xs` |
| Muted | `text-gray-500` `text-[10px]` |
| Section labels | `text-gray-400` or `text-gray-600` + `uppercase tracking-widest` |
| Footer hints | `text-gray-600` `text-[9px]` italic |

**Primary (pink):** selection ring `border-primary-500 ring-2 ring-primary-500/20`, icons `text-primary-400`, active toolbar `bg-primary-600/25 border-primary-500/40`, credits badge `bg-primary-500/10 border-primary-500/20 text-primary-400`.

**Graph / wires (not primary):**

| State | Stroke |
|-------|--------|
| Default | `#4f46e5` (indigo-600), 2px |
| Hover | `group-hover:stroke-indigo-400` |
| Selected | `#fbbf24` (amber-400), 3px + glow 30% opacity |
| Dragging | `#6366f1` (indigo-500), dashed |
| Marquee | `border: 1px solid #4f46e5`, `rgba(79, 70, 229, 0.1)` fill |

**Header toolbar icon accents:** gallery `text-primary-400`, clear `text-red-400`, load `text-blue-400`, download `text-green-400`, folder `text-pink-500`, MCP `text-emerald-500/90`.

### Typography (Flow Studio)

**Font:** `font-sans` on page shell.

| Size | Usage |
|------|--------|
| `text-[9px]` | Port labels, footer stats, micro labels, “Connected” |
| `text-[10px]` | Section headers, node titles, inspector labels, zoom % |
| `text-[11px]` | Textareas inside nodes |
| `text-xs` (12px) | Panel titles, library items, buttons |

```
Section title:     text-xs font-bold uppercase tracking-widest text-gray-400
Category label:    text-[10px] font-bold uppercase tracking-widest text-gray-600
Micro label:       text-[10px] font-bold uppercase tracking-tight text-gray-400
Toggle chip:       text-[10px] font-bold uppercase tracking-tight text-gray-400
Footer stat:       text-[9px] uppercase font-bold tracking-tighter text-gray-500
```

**Monospace:** zoom %, credits (`font-mono text-[10px]`).

### Spacing & radii (Flow Studio)

| Element | Value |
|---------|--------|
| Panel padding | `p-4` (headers/inspector), `p-2` (library list) |
| Section gap | `space-y-4` / `space-y-6` in inspector |
| UI viewer groups | `gap-8` top-level, `gap-4` nested |
| Panel / node radius | `rounded-lg` |
| Chips / toolbar | `rounded-md` |
| Carousel arrows | `rounded-full` |
| Default node size | 200×150px; min width 200px, min height 100px on resize |
| Port spacing | `space-y-3`, row height 12px |

### Canvas

**Dot grid:** `radial-gradient(circle, #1f2937 1px, transparent 1px)`, spacing `20px × zoom`, position follows viewport pan.

**Cursors:** canvas `cursor-grab` / `active:cursor-grabbing`; ports `cursor-crosshair`.

**Zoom control (bottom-left):**

```
bg-gray-900/80 backdrop-blur border border-gray-800 rounded-lg p-1 shadow-xl
Label: text-[10px] font-mono text-gray-400
Select active: bg-primary-500/10, color primary
```

**Footer hint:** `Middle-click or Alt+Drag to pan • Scroll to zoom`

### Nodes

**Structure:**

1. Shell — `border-2 rounded-lg shadow-xl`
2. Header — `px-2 py-1 border-b border-gray-800 bg-gray-950 rounded-t-lg`
3. Body — `bg-gray-900 flex-1`
4. Resize handle — bottom-right `border-gray-700` → hover `border-primary-500`

**States:**

| State | Classes |
|-------|---------|
| Default | `border-gray-800 hover:border-gray-700` |
| Selected | `border-primary-500 ring-2 ring-primary-500/20` z-index 10 |
| Tab-group meta | `border-gray-700/50`, transparent body, no shadow |
| Locked | `i-heroicons-lock-closed text-gray-500` |
| Loading | `i-heroicons-arrow-path text-primary-400 animate-spin` |

**Ports:**

- Input: `rounded-l-full bg-gray-700`, hover `bg-primary-500`
- Output: `rounded-r-full bg-primary-500`
- Labels: `text-[9px] font-bold text-gray-400`, visible on `group-hover/node`

**Header:** `i-heroicons-cpu-chip text-primary-400`, title `text-[10px] font-bold text-gray-200`, credits pill `text-[8px]` + bolt.

**Media wells:** `bg-gray-950 rounded`, `object-contain`; empty state `text-[9px] text-gray-500`.

**Generate button:** `UButton color="primary" size="xs"`, `i-heroicons-sparkles`, label “Generate” / “Generating…”.

**Notes node exception:** user `backgroundColor` / `textColor` (default `#ec4899` / `#ffffff`).

### Side panels (library & inspector)

```html
<div class="w-64 border-{l|r} border-gray-800 bg-gray-900 flex flex-col overflow-hidden">
  <div class="h-10 border-b border-gray-800 px-4">...</div>
  <div class="flex-1 overflow-y-auto custom-scrollbar p-4">...</div>
</div>
```

**Library item:** `p-2 rounded-lg hover:bg-gray-800`, icon box `w-6 h-6 bg-gray-800 border-gray-700` hover `border-primary-500`, name `text-xs font-semibold text-gray-300 group-hover:text-white`.

**Inspector inputs:**

```
UInput / UTextarea size="xs"
:ui="{ base: 'bg-gray-950 border-gray-800 text-white disabled:opacity-50' }"
```

Sticky footer: `UButton block color="primary" size="sm"` + sparkles.

### Header toolbar (Flow Studio)

```html
<header class="h-12 border-b border-gray-800 bg-gray-900 px-4 flex items-center justify-between shrink-0">
```

**Toggle chips:** `bg-gray-800/50 rounded-md border border-gray-700/50`, label `text-[10px] font-bold text-gray-400 uppercase`, `USwitch size="xs"`.

**Icon buttons:** `variant="ghost" size="xs" px-2 bg-gray-800 hover:bg-gray-700 border border-gray-700`.

**Save:** `variant="solid" color="primary" size="xs"`.

**Dividers:** `w-px h-4 bg-gray-800`.

### Connections

- Bézier paths; hit stroke 30px transparent
- Double-click to remove
- Marquee: indigo border + 10% fill

### Scrollbars

```css
.custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #374151; }
```

### Flow Studio icons

| Context | Icon |
|---------|------|
| Node / library | `cpu-chip` |
| Generate | `sparkles` |
| Credits | `bolt` |
| UI viewer | `presentation-chart-bar` |
| Zoom | `minus`, `plus`, `arrows-pointing-out` |

Sizes: `w-3`–`w-4` in chrome.

### Flow Studio do / don’t

**Do:** Always dark on `flow-studio/[id]`; uppercase section titles; media on `gray-950` inside `gray-900` cards; `size="xs"` controls.

**Don’t:** Use light dashboard backgrounds; use `text-base` in canvas UI; use `rounded-xl` on nodes; omit `custom-scrollbar` on panels.

### Key differences from Dashboard / App

| Aspect | Flow Studio | Dashboard / App |
|--------|---------------|-----------------|
| Background | `gray-950` | `slate-50`, `gray-50`, gradients |
| Type size | 9–12px dominant | 12–16px+ for reading |
| Section labels | `uppercase tracking-widest` | Sentence case or title case |
| Primary use | Selection, wires, generate | CTAs, nav hover |
| Buttons | Almost always `size="xs"` | `sm`–`lg` |
| Inputs | `bg-gray-950 border-gray-800` override | White / pink-tinted |

---

## 6. Cross-surface mapping

| Concept | Dashboard / App | Flow Studio |
|---------|-----------------|-------------|
| Primary CTA | `UButton color="primary" size="sm"`+ | `size="xs"` + sparkles |
| Secondary | `ghost` / `soft` neutral | `ghost` neutral, `bg-gray-800` chips |
| Panel width | 256px (nav) · 320px (folders) | 256px (library/inspector) |
| Card radius | `rounded-xl`–`rounded-3xl` | `rounded-lg` |
| Empty state | Large icon + `text-sm` copy | Small icon + `text-xs` italic |
| Credits | Pink text / primary-50 pill | `text-[8px]` badge on node |
| Delete | `color="error"` | Red icon `text-red-400` in toolbar |
| Gallery “use asset” | White overlay button | Same pattern in flow gallery panel |

**Bridging a new feature:**

1. Build in **App UI** patterns (readable, light-friendly).
2. If exposed on canvas, add a **Flow Studio** node using dark input overrides from §5.
3. Link from **Dashboard** via thumbnail `ActionCard` or flow list card.

---

## 7. Portable CSS variables

```css
:root {
  /* Brand */
  --tf-primary: #ec4899;
  --tf-primary-muted: rgba(236, 72, 153, 0.15);

  /* App / Dashboard (light) */
  --tf-bg-page: #f8fafc;        /* slate-50 */
  --tf-bg-surface: #ffffff;
  --tf-bg-muted: #f9fafb;       /* gray-50 */
  --tf-border: #e5e7eb;         /* gray-200 */
  --tf-text: #111827;           /* gray-900 */
  --tf-text-muted: #6b7280;     /* gray-500 */
  --tf-nav-gradient-from: #fdf2f8;  /* pink-50 */
  --tf-nav-gradient-to: #ffe4e6;    /* rose-100 */

  /* Flow Studio (dark) */
  --fs-bg-canvas: #030712;
  --fs-bg-panel: #111827;
  --fs-border: #1f2937;
  --fs-wire: #4f46e5;
  --fs-wire-selected: #fbbf24;

  /* Layout */
  --tf-sidebar-width: 256px;
  --tf-folder-panel-width: 320px;
  --tf-header-height: 64px;
}
```

---

## 8. Source files

### Shared

| File | Role |
|------|------|
| `frontend/app/app.config.ts` | `primary: pink`, `neutral: slate` |
| `frontend/app/components/AppHeader.vue` | Global header, credits, mobile nav |

### Dashboard

| File | Role |
|------|------|
| `frontend/app/layouts/dashboard.vue` | Dashboard shell |
| `frontend/app/components/dashboard/NavigationSidebar.vue` | Pink gradient nav |
| `frontend/app/pages/dashboard/index.vue` | Home, action cards, projects |
| `frontend/app/components/dashboard/ActionCard.vue` | Quick action tiles |
| `frontend/app/components/dashboard/ProjectCard.vue` | Project grid cards |
| `frontend/app/pages/flow-studio/index.vue` | Flow list (marketing cards) |

### App UI

| File | Role |
|------|------|
| `frontend/app/layouts/app.vue` | App shell + folder panel |
| `frontend/app/pages/image/from-image.vue` | Workspace + floating prompt |
| `frontend/app/pages/collections/[id].vue` | Gradient workflow layout |
| `frontend/app/components/generations/workspace/GenerationWorkspace.vue` | Tabbed gallery shell |
| `frontend/app/components/generations/FloatingPromptInput.vue` | Pink prompt bar |

### Flow Studio

| File | Role |
|------|------|
| `frontend/app/pages/flow-studio/[id].vue` | Editor chrome |
| `frontend/app/components/flow-studio/FlowStudioCanvas.vue` | Canvas & grid |
| `frontend/app/components/flow-studio/FlowStudioNode.vue` | Node shell |
| `frontend/app/components/flow-studio/NodeLibraryPanel.vue` | Left library |
| `frontend/app/components/flow-studio/NodeInspectorPanel.vue` | Right inspector |
