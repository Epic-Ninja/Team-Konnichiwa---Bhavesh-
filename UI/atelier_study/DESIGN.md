---
name: Atelier Study
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c8c7be'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#919189'
  outline-variant: '#474740'
  surface-tint: '#c7c7bb'
  primary: '#fffff1'
  on-primary: '#303128'
  primary-container: '#e2e2d5'
  on-primary-container: '#63645a'
  inverse-primary: '#5e5f55'
  secondary: '#c8c5ca'
  on-secondary: '#303033'
  secondary-container: '#47464a'
  on-secondary-container: '#b6b4b8'
  tertiary: '#fffdff'
  on-tertiary: '#362e33'
  tertiary-container: '#ebdee4'
  on-tertiary-container: '#6a6166'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e3e3d6'
  primary-fixed-dim: '#c7c7bb'
  on-primary-fixed: '#1b1c14'
  on-primary-fixed-variant: '#46483e'
  secondary-fixed: '#e4e1e6'
  secondary-fixed-dim: '#c8c5ca'
  on-secondary-fixed: '#1b1b1e'
  on-secondary-fixed-variant: '#47464a'
  tertiary-fixed: '#ecdfe5'
  tertiary-fixed-dim: '#cfc3c9'
  on-tertiary-fixed: '#201a1e'
  on-tertiary-fixed-variant: '#4d4449'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  surface-card: '#1F1F23'
  accent-indigo: '#6366F1'
  accent-olive: '#848D78'
  accent-clay: '#D97757'
  accent-emerald: '#5E8C7E'
  text-muted: '#666666'
typography:
  display-lg:
    fontFamily: literata
    fontSize: 42px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: literata
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: literata
    fontSize: 28px
    fontWeight: '500'
    lineHeight: '1.2'
  headline-md:
    fontFamily: literata
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: hankenGrotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: hankenGrotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0.01em
  label-caps:
    fontFamily: jetbrainsMono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: '1.0'
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  page-margin: 24px
  section-gap: 48px
  element-gap: 16px
  card-padding: 20px
---

## Brand & Style

This design system is anchored in the concept of a "Digital Sanctuary"—a space that feels less like a productivity tool and more like a high-end stationery shop or a curated editorial journal. The brand personality is human, quiet, and intentional, eschewing the frantic energy of typical study apps for a calm, academic focus.

The design style is a blend of **Minimalism** and **Glassmorphism**, heavily influenced by Japanese design principles (Ma - the beauty of empty space). It utilizes asymmetrical layouts to break the rigid grid of standard SaaS products, creating a more organic, human-centric feel. Visuals are defined by high-contrast typography, expansive whitespace, and a physical sense of layering that mimics paper and glass.

## Colors

The palette is rooted in a warm, sophisticated dark mode. The background (#111111) is a soft off-black that reduces eye strain during long study sessions. The primary color is a Warm Cream (#E2E2D5), used for primary text and high-importance actions to provide a tactile, paper-like contrast.

Accents are strictly muted and earthy—Clay, Olive, and Emerald—evoking natural materials. These should be used sparingly for status indicators, categorization, or subtle highlights. Avoid any high-saturation neons or default system blues to maintain the premium, editorial atmosphere.

## Typography

The typography follows an editorial hierarchy. **Literata** provides a scholarly, rhythmic feel for headings, making even a simple "Good Morning" feel significant. **Hanken Grotesk** is used for body text to maintain modern legibility, while **JetBrains Mono** is used for small labels and metadata to give a subtle "archival" or "notated" feel.

Tracking (letter spacing) is tight on large headings to create a cohesive block of text, while body text and labels use more generous tracking to ensure airiness and breathing room.

## Layout & Spacing

The layout is defined by **Dynamic Asymmetry**. Rather than a strict 12-column grid, use varied horizontal margins to create a "scrapbook" or journal feel. Large blocks of text should often be offset from the center or aligned to different margins than the headings above them.

Whitespace is treated as a functional element, not a void. Large gaps (48px+) are used between major sections to prevent information density. On mobile, use a consistent 24px side margin for the primary container, but allow specific elements—like featured images or carousel cards—to bleed edge-to-edge to create visual rhythm.

## Elevation & Depth

Depth is achieved through **Soft Layering** rather than traditional elevation.
- **Glass Panels:** Surfaces use a subtle backdrop blur with a low-opacity white border (0.5px) to simulate thin glass.
- **Micro-Shadows:** Avoid heavy dropshadows. Instead, use a very soft, diffused ambient shadow (color: #000000, opacity: 0.2, blur: 12px) to lift cards slightly off the background.
- **Depth of Field:** Background elements (like abstract organic shapes) should utilize Gaussian blurs to suggest a shallow depth of field, keeping the user's focus on the sharp, high-contrast foreground cards.

## Shapes

The shape language is generous and welcoming. All primary cards and containers use a **24px (rounded-xl)** corner radius to soften the interface. Buttons are strictly **Pill-Shaped** (fully rounded ends) to make them feel like smooth pebbles.

Dividers must be extremely subtle—0.5px thickness using the Secondary color (#18181B)—serving more as a visual guide than a hard barrier.

## Components

### Buttons
Primary buttons are pill-shaped, using the Warm Cream (#E2E2D5) background with dark text. Secondary buttons are "ghost" style with a thin 1px border and no fill, or a glassmorphic fill with backdrop blur.

### Cards
Cards are the primary structural element. Use the Card color (#1F1F23) with a 24px corner radius. They should feel like "floating plates." For interactive cards, add a 1px inner border of a lighter grey to catch the "light" from the top.

### Input Fields
Inputs should feel like writing on a line in a notebook. Use a simple bottom-border only for the resting state, which glows subtly with the Primary color when focused.

### Icons & Illustrations
Icons must be "thin-stroke" (1px or 1.5px weight) with open paths, appearing elegant and airy. Illustrations are hand-drawn, charcoal-style or fine-liner sketches. They should feel human and slightly imperfect, never using standard flat-vector styles.

### Chips/Labels
Small, pill-shaped labels using the JetBrains Mono font. They should have a neutral background (#18181B) and a colored text label from the accent palette to indicate categories without overwhelming the screen.