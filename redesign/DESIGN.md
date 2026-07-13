---
name: Spatial Minimalism
colors:
  surface: '#141314'
  surface-dim: '#141314'
  surface-bright: '#3a393a'
  surface-container-lowest: '#0e0e0f'
  surface-container-low: '#1c1b1c'
  surface-container: '#201f20'
  surface-container-high: '#2b2a2b'
  surface-container-highest: '#363435'
  on-surface: '#e5e1e2'
  on-surface-variant: '#c9c5cc'
  inverse-surface: '#e5e1e2'
  inverse-on-surface: '#313031'
  outline: '#938f96'
  outline-variant: '#48464c'
  surface-tint: '#c9c4d5'
  primary: '#c9c4d5'
  on-primary: '#312f3c'
  primary-container: '#12101c'
  on-primary-container: '#7f7b8b'
  inverse-primary: '#605c6b'
  secondary: '#ffb783'
  on-secondary: '#4f2500'
  secondary-container: '#d97722'
  on-secondary-container: '#451f00'
  tertiary: '#d2c5aa'
  on-tertiary: '#37301d'
  tertiary-container: '#171103'
  on-tertiary-container: '#877c65'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e6e0f2'
  primary-fixed-dim: '#c9c4d5'
  on-primary-fixed: '#1c1a26'
  on-primary-fixed-variant: '#484553'
  secondary-fixed: '#ffdcc5'
  secondary-fixed-dim: '#ffb783'
  on-secondary-fixed: '#301400'
  on-secondary-fixed-variant: '#713700'
  tertiary-fixed: '#efe1c5'
  tertiary-fixed-dim: '#d2c5aa'
  on-tertiary-fixed: '#211b0a'
  on-tertiary-fixed-variant: '#4f4632'
  background: '#141314'
  on-background: '#e5e1e2'
  surface-variant: '#363435'
  deep-ink: '#0A0910'
  sanitized-white: '#F8FAFC'
  apricot: '#FB923C'
  teal: '#2DD4BF'
  violet: '#A78BFA'
  edge-light: rgba(255, 255, 255, 0.12)
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  technical-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  technical-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is built on the philosophy of **Tactile Digitalism**. It creates a high-performance environment that feels like a physical object—specifically high-end hardware like an iPad chassis—translated into a digital interface. The goal is to evoke a sense of "elite utility": tools that are powerful enough for professionals but polished enough for luxury consumers.

The visual direction combines **Spatial Minimalism** with high-information density. It avoids the clinical coldness of traditional flat design by using depth, environmental lighting, and organic G2 squircle geometry. The experience should feel immersive, responsive, and heavy—as if every UI element has physical mass and is hovering mere millimeters beneath the glass surface.

**Key Stylistic Pillars:**
- **Physicality:** Use of micro-depth and multi-layered shadows to give elements weight.
- **Environmentalism:** Surfaces react to the content behind or beneath them through intelligent edge lighting and glassmorphism.
- **Efficiency:** A "pro-tool" layout density inspired by high-productivity software, prioritizing information over decorative white space.

## Colors

The palette is anchored by **Deep Ink**, a sophisticated, purple-tinted black that provides more depth and "room" for shadows than pure hex #000000. In light mode, **Sanitized White** offers a crisp, clinical base that remains soft on the eyes.

**Functional Color Application:**
- **Base Surfaces:** Use `deep-ink` as the primary canvas. It acts as the "chassis" of the application.
- **Accents:** Apricot, Teal, and Violet are never used as flat fills for large areas. Instead, they are applied as vibrant **mesh gradients** to indicate brand presence, state changes, or high-priority calls to action.
- **Intelligent Edge Lighting:** This is a dynamic border color. It should be a semi-transparent white or a hue-shifted version of the underlying content, simulating light catching the "bevel" of a squircle.

## Typography

This design system uses a dual-font strategy to balance elegance with technical precision. **Inter** (as a proxy for SF Pro) handles all primary communication, providing a neutral, high-legibility foundation. **JetBrains Mono** is reserved for technical metadata, keyboard shortcuts, and "pro-level" data points.

**Usage Guidelines:**
- **Headings:** Keep tracking tight (`-0.01em` to `-0.02em`) to mimic the premium feel of editorial design.
- **Technical Metadata:** Use JetBrains Mono for status codes, ⌘K badges, and secondary data strings to signal the "high-performance" nature of the tool.
- **Caps:** Small caps should only be used with JetBrains Mono for section headers or tertiary labels, always with increased letter spacing.

## Layout & Spacing

The layout philosophy is defined by **Functional Density**. It rejects excessive whitespace, opting instead for an organized "Bento Box" grid system where information is compartmentalized into distinct, physical-looking modules.

**Grid & Structure:**
- **Bento Grid:** Use an asymmetrical grid where elements are grouped into containers of varying sizes. This creates a rhythmic, modular appearance.
- **Breakpoints:**
  - **Mobile:** Single column, 16px margins, fluid containers.
  - **Tablet:** 6-column grid, 24px margins, vertical sidebar collapses to an icon-only dock.
  - **Desktop:** 12-column grid, 32px margins, persistent vertical sidebar (Arc-inspired).
- **Rhythm:** All spacing is derived from a 4px base unit. Use tighter gaps (8px–16px) between related modules to maintain the sense of a cohesive "dashboard."

## Elevation & Depth

Elevation is the primary driver of hierarchy in this design system. We use **Micro-Depth**, which avoids large, blurry shadows in favor of crisp, stacked layers that suggest a tight physical tolerance.

**Shadow Architecture:**
Every elevated element (cards, buttons, popovers) must use a minimum of three shadow layers:
1. **The Ambient Occlusion:** A very dark, narrow blur (2px) with high opacity to ground the object.
2. **The Mid-Cast:** A medium blur (8px-12px) with low opacity to define the height.
3. **The Diffusion:** A wide, very faint blur (24px+) that softens the object into the background.

**Glassmorphism:**
Use backdrop blurs (20px - 40px) on overlays and the Dynamic Island-inspired navigation bars. Apply a 1px "Intelligent Edge" border that is slightly lighter than the surface itself to simulate light catching the squircle edge.

## Shapes

The shape language is strictly governed by the **G2 Squircle**. This curvature is more organic than a standard rounded rectangle, with a smoother transition from the straight edge to the curve.

- **Primary Containers:** 24px to 32px radius (G2 Squircle).
- **Inner Components:** Buttons and inputs nested inside containers should have a slightly smaller radius (12px to 16px) to maintain visual nesting harmony.
- **Pill Shapes:** Used exclusively for the "Dynamic Island" navigation bars and status chips to distinguish them from functional containers.

## Components

**Buttons & Interaction:**
Primary buttons use a subtle **shimmer shader** that reacts to the cursor's position, mimicking light catching a metallic surface. They should feel tactile and "pressable," using a 1% scale-down transition on active states.

**Bento Cards:**
The core structural unit. Each card features:
- A background of `deep-ink` or frosted glass.
- A 1px intelligent edge border.
- 3-layer micro-depth shadows.
- Content-driven lighting: the border color should subtly shift toward the primary color of the image or icon inside the card.

**Dynamic Island Bars:**
Pill-shaped, floating navigation elements. These should be positioned at the bottom (for reachability) or top (for status). They utilize high-density glassmorphism and contain ⌘K shortcut hints in JetBrains Mono.

**Input Fields:**
Fields are inset rather than outlined, using a slight inner shadow to appear "carved" into the surface. The focus state is indicated by an Intelligent Edge glow in `apricot` or `violet`.

**Technical Badges:**
Small, high-contrast badges using JetBrains Mono. These are used for keyboard shortcuts (e.g., [ ⌘ ] [ K ]) and are styled with a slight metallic gradient to look like physical keycaps.