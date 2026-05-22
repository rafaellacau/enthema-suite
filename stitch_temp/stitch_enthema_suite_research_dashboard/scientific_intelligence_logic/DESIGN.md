---
name: Scientific Intelligence Logic
colors:
  surface: '#f7f9ff'
  surface-dim: '#d7dae0'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4fa'
  surface-container: '#ebeef4'
  surface-container-high: '#e5e8ee'
  surface-container-highest: '#dfe3e8'
  on-surface: '#181c20'
  on-surface-variant: '#414754'
  inverse-surface: '#2d3135'
  inverse-on-surface: '#eef1f7'
  outline: '#727785'
  outline-variant: '#c1c6d6'
  surface-tint: '#005bc0'
  primary: '#005bbf'
  on-primary: '#ffffff'
  primary-container: '#1a73e8'
  on-primary-container: '#ffffff'
  inverse-primary: '#adc7ff'
  secondary: '#005ac1'
  on-secondary: '#ffffff'
  secondary-container: '#4d8efe'
  on-secondary-container: '#00285c'
  tertiary: '#9e4300'
  on-tertiary: '#ffffff'
  tertiary-container: '#c55500'
  on-tertiary-container: '#0e0200'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc7ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a41'
  on-secondary-fixed-variant: '#004494'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb691'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#783100'
  background: '#f7f9ff'
  on-background: '#181c20'
  surface-variant: '#f8f9fa'
  success: '#34a853'
  warning: '#f9ab00'
  danger: '#ea4335'
  surface-base: '#ffffff'
  border-subtle: '#dadce0'
  data-viz-purple: '#DFD1FF'
  data-viz-lime: '#E4F222'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 44px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Roboto Flex
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Roboto Flex
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-page: 48px
  margin-mobile: 16px
  container-max-width: 1440px
---

## Brand & Style

The design system is engineered for high-density information environments where clarity, precision, and cognitive ease are paramount. Drawing inspiration from the utility of the Google Cloud Console and the refined efficiency of Linear, the aesthetic is **Corporate Modern** with a focus on institutional reliability. 

The brand personality is academic and sophisticated. It avoids decorative flourishes in favor of structural integrity. The interface serves as a "silent partner" to the researcher—disappearing to allow the data to take center stage while providing a sense of rhythmic calm through purposeful whitespace and a rigid geometric structure.

## Colors

This design system utilizes a high-clarity palette rooted in Google's core semantic colors. 

- **Primary & Secondary:** Google Blue serves as the primary driver for actions and states. 
- **Semantics:** Success (Green), Warning (Amber), and Danger (Red) follow strict functional roles for status reporting and data validation.
- **Neutrals:** The background is anchored in pure white to maximize contrast, while a very light gray (`#f8f9fa`) is reserved for secondary navigation panels and container backgrounds to distinguish depth without using shadows.
- **Accent Palette:** Borrowed from high-performance tools to assist in complex data visualization, including a muted purple and high-vis lime for categorization.

## Typography

The typographic system prioritizes legibility in multi-column layouts. 

- **Headings:** Plus Jakarta Sans provides a contemporary, high-end "Google Sans" feel, offering clean geometric shapes that remain legible even at scale.
- **Body:** Roboto Flex is the workhorse of the system, utilized for all research data, descriptions, and UI controls. Its variable nature allows for precise weight adjustments in data-heavy tables.
- **Labels & Mono:** JetBrains Mono is used for metadata, scientific IDs, and technical values to provide a "lab-spec" feel that distinguishes static text from dynamic data.

## Layout & Spacing

This design system uses a **Fixed-Fluid Hybrid** model. The main content area lives within a 1440px max-width container to prevent line-lengths from becoming unreadable on ultra-wide monitors, while sidebars and navigation panels occupy fixed widths (e.g., 280px for primary nav).

- **Grid:** A 12-column grid system is used for page layouts.
- **Rhythm:** Spacing follows a strict 4px/8px incremental scale. 
- **Mobile Adaptivity:** At the 768px breakpoint, page margins compress to 16px and multi-column research dashboards reflow into single-column vertical stacks. Lateral padding in cards is reduced to maximize horizontal space for data tables.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** rather than heavy shadows. 

1. **Level 0 (Background):** Pure White (#FFFFFF) for the primary workspace.
2. **Level 1 (Subtle Inset):** Very Light Gray (#F8F9FA) for sidebars and header backgrounds.
3. **Level 2 (Cards):** Surfaces with a sharp 1px border (`#DADCE0`) and a minimal "Material 3" shadow (0 1px 3px rgba(60,64,67,0.12)). 

Avoid stacked shadows. If a modal or popover is required, use a scrim (overlay) of 40% opacity black to focus attention, and increase the shadow spread to 12px for the elevated element.

## Shapes

The shape language is **Rounded**, leaning towards the softer side of professional software. 

- **Buttons & Inputs:** Use a standard 8px radius (`0.5rem`).
- **Cards & Primary Containers:** Use a generous 12px or 16px radius to soften the high-density data and make the interface feel modern and approachable.
- **Chips & Tags:** Use a fully rounded pill-shape to distinguish them from interactive buttons.

## Components

- **Buttons:** Primary buttons use solid `#1a73e8` with white text. Secondary buttons use a 1px border of `#dadce0` with blue text. No gradients.
- **Inputs:** Use the "Outlined" Material 3 style. Labels should be small, JetBrains Mono, and positioned above the field. Focus states utilize a 2px blue stroke.
- **Cards:** Always use white backgrounds. Group related research data within cards to create clear visual boundaries.
- **Chips:** Used for metadata (e.g., "Peer Reviewed", "Pending"). Backgrounds should be low-saturation versions of the semantic colors (e.g., light green background with dark green text for "Success").
- **Data Tables:** High-density with 40px row heights. Use alternating row stripes (zebra striping) with `#f8f9fa` for readability in large datasets. Header rows use `label-sm` typography with a subtle bottom border.
- **Navigation:** Vertical sidebar with icons on the left. Active states are indicated by a blue "pill" background behind the icon/text.