---
name: "EduGrade AI — Industrial Academic Precision"
description: "An authoritative, Swiss-brutalist academic intelligence design system inspired by Wastetide.ai, pairing razor-sharp 0px grid geometry with vermilion highlights and IBM Plex Mono telemetry."
---

## Overview

EduGrade AI's design system embodies **Industrial Academic Precision** — a high-contrast, Swiss-brutalist aesthetic inspired by Wastetide.ai. It pairs stark `#FFFFFF` and `#F2F1F1` concrete-gray architectural grids, deep espresso ink (`#1B0401`), and electric vermilion (`#FF3316` / `#C81E06`) signal blocks with **Space Grotesk** uppercase display headings and **IBM Plex Mono** technical telemetry.

The interface uses exposed `1px` hairline grid borders, razor-sharp `0px` corners on cards, buttons, and inputs, and pill-shaped (`9999px`) category tags. Every CGPA figure, credit ratio, and placement cutoff is rendered with tabular precision.

## Colors

The palette pairs high-contrast signal vermilion (`primary: #C81E06`, `primary-container: #FF3316`) for primary CTAs and impact KPI blocks with deep espresso-black (`secondary: #1B0401`, `on-surface: #1B0401`) and matte carbon (`inverse-surface: #111111`) for structural contrast over `#FFFFFF` and `#F2F1F1` surfaces.

```yaml
colors:
  success: "#006A63"
  on-success: "#FFFFFF"
  warning: "#9A4A00"
  on-warning: "#FFFFFF"
  light:
    primary: "#C81E06"
    on-primary: "#FFFFFF"
    primary-container: "#FF3316"
    on-primary-container: "#1B0401"
    secondary: "#1B0401"
    on-secondary: "#FFFFFF"
    secondary-container: "#E6E5E5"
    on-secondary-container: "#1B0401"
    tertiary: "#872D00"
    on-tertiary: "#FFFFFF"
    tertiary-container: "#FFDFD7"
    on-tertiary-container: "#1B0401"
    error: "#BA1A1A"
    on-error: "#FFFFFF"
    error-container: "#FFDAD6"
    on-error-container: "#93000A"
    background: "#FFFFFF"
    on-background: "#1B0401"
    surface: "#FFFFFF"
    surface-dim: "#D4D2D2"
    surface-bright: "#FFFFFF"
    surface-container-lowest: "#FFFFFF"
    surface-container-low: "#F2F1F1"
    surface-container: "#EAE9E9"
    surface-container-high: "#E0DFDF"
    surface-container-highest: "#D4D2D2"
    on-surface: "#1B0401"
    surface-variant: "#EAE9E9"
    on-surface-variant: "#4A3937"
    outline: "#6E5A57"
    outline-variant: "#D4D0CF"
    inverse-surface: "#111111"
    inverse-on-surface: "#FFFFFF"
    inverse-primary: "#FF3316"
  dark:
    primary: "#FF6B54"
    on-primary: "#1B0401"
    primary-container: "#FF3316"
    on-primary-container: "#1B0401"
    secondary: "#EAE9E9"
    on-secondary: "#1B0401"
    secondary-container: "#2A2423"
    on-secondary-container: "#FFFFFF"
    tertiary: "#FFB59A"
    on-tertiary: "#1B0401"
    tertiary-container: "#872D00"
    on-tertiary-container: "#FFFFFF"
    error: "#FFB4AB"
    on-error: "#690005"
    error-container: "#93000A"
    on-error-container: "#FFDAD6"
    background: "#111111"
    on-background: "#FFFFFF"
    surface: "#111111"
    surface-dim: "#0A0A0A"
    surface-bright: "#2A2423"
    surface-container-lowest: "#111111"
    surface-container-low: "#1B0401"
    surface-container: "#241917"
    surface-container-high: "#2E2220"
    surface-container-highest: "#3A2D2B"
    on-surface: "#FFFFFF"
    surface-variant: "#2E2220"
    on-surface-variant: "#D4D0CF"
    outline: "#9E9594"
    outline-variant: "#3A2D2B"
    inverse-surface: "#FFFFFF"
    inverse-on-surface: "#1B0401"
    inverse-primary: "#C81E06"
```

## Typography

A three-role Swiss-industrial pairing: **Space Grotesk** delivers punchy, tight-tracked display headlines and KPI numerals; **Inter** handles clean UI labels and prose; and **IBM Plex Mono** drives all technical metadata, course codes, roll numbers, and uppercase micro-labels.

```yaml
typography:
  display-lg:
    fontFamily: "Space Grotesk"
    fontSize: 40px
    fontWeight: 700
    lineHeight: 46px
    letterSpacing: -0.75px
  display-lg-mobile:
    fontFamily: "Space Grotesk"
    fontSize: 30px
    fontWeight: 700
    lineHeight: 36px
    letterSpacing: -0.5px
  headline-lg:
    fontFamily: "Space Grotesk"
    fontSize: 28px
    fontWeight: 700
    lineHeight: 34px
    letterSpacing: -0.5px
  headline-md:
    fontFamily: "Space Grotesk"
    fontSize: 22px
    fontWeight: 700
    lineHeight: 28px
    letterSpacing: -0.25px
  title-lg:
    fontFamily: "Inter"
    fontSize: 18px
    fontWeight: 600
    lineHeight: 24px
    letterSpacing: -0.1px
  title-md:
    fontFamily: "Inter"
    fontSize: 15px
    fontWeight: 600
    lineHeight: 22px
    letterSpacing: 0px
  body-lg:
    fontFamily: "Inter"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 22px
    letterSpacing: 0px
  body-md:
    fontFamily: "Inter"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
    letterSpacing: 0px
  body-sm:
    fontFamily: "Inter"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 18px
    letterSpacing: 0.1px
  label-lg:
    fontFamily: "Inter"
    fontSize: 14px
    fontWeight: 600
    lineHeight: 20px
    letterSpacing: 0.1px
  label-md:
    fontFamily: "Inter"
    fontSize: 12px
    fontWeight: 600
    lineHeight: 16px
    letterSpacing: 0.2px
  label-sm:
    fontFamily: "Inter"
    fontSize: 11px
    fontWeight: 500
    lineHeight: 14px
    letterSpacing: 0.3px
  mono-md:
    fontFamily: "IBM Plex Mono"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 18px
    letterSpacing: 0px
  mono-sm:
    fontFamily: "IBM Plex Mono"
    fontSize: 11px
    fontWeight: 500
    lineHeight: 14px
    letterSpacing: 0.2px
```

## Layout & Spacing

The desktop web application uses a persistent `256px` left navigation rail paired with a fluid 12-column content canvas (`max-w-[1440px]`), `24px` outer page padding, and `20px`–`24px` grid gutters. Exposed `1px` architectural grid borders and vermilion accent blocks anchor visual hierarchy.

```yaml
spacing:
  gutter-xs: 4px
  gutter-sm: 8px
  gutter-md: 16px
  gutter-lg: 24px
  gutter-xl: 32px
  section: 40px
  page-margin: 24px
```

## Elevation & Depth

Hierarchy is established strictly through **flat architectural contrast blocks** (`#FFFFFF`, `#F2F1F1`, `#FF3316`, `#1B0401`, `#111111`) and **1px hairline borders** (`outline-variant`) rather than soft drop shadows.

## Shapes

The system uses **razor-sharp `0px` corners** across all cards, buttons, inputs, and containers, with `9999px` (`full`) reserved strictly for pill tags and circular status dots.

```yaml
rounded:
  sm: 0px
  DEFAULT: 0px
  md: 0px
  lg: 0px
  xl: 0px
  full: 9999px
```

## Motion & Micro-interaction

Motion is crisp, purposeful, and understated. Hover and active state transitions on navigation items, buttons, and table rows resolve within `120ms` using `ease-out`. Panel transitions and chart bar reveals decelerate smoothly over `240ms`. All animations respect `prefers-reduced-motion` and animate only `transform`, `opacity`, and color properties.

```yaml
motion:
  state-change:
    duration: 120ms
    delay: 0ms
    timingFunction: ease-out
  surface-enter:
    duration: 240ms
    delay: 0ms
    timingFunction: cubic-bezier(0.2, 0, 0, 1)
  surface-exit:
    duration: 160ms
    delay: 0ms
    timingFunction: cubic-bezier(0.3, 0, 1, 1)
```

## Voice & Content Strategy

- **Tone of voice:** Clear, encouraging, and academically rigorous. Avoids hype or vague motivational filler; grounds every insight in real credits, SGPA/CGPA numbers, and degree requirements.
- **Capitalisation:** Sentence case for headings, navigation labels, and button actions (e.g., "Simulate Target CGPA", "Ask AI Advisor"); uppercase only for official course codes (`CS3401`) and letter grades (`A+`, `O`).
- **Terminology:** Consistently use **SGPA** (Semester GPA), **CGPA** (Cumulative GPA), **Credits Earned**, **Standing Arrears** (or **Active Backlogs**), and **Placement Eligibility**.
- **Numbers & Formatting:** Always format GPA values to two decimal places (`8.64`, `9.12`) using `tabular-nums`, and display credit ratios clearly (`112 / 160 Credits`).

## Components

Component implementations live as individual HTML sticker sheet files in
`components/`. Each file contains the canonical, styled HTML components with
`<!-- COMPONENT: name -->` comment markers. Read each file before use.

- **Badge** → `@components/badge.html`: `badge-numeric`, `badge-dot`
- **Button** → `@components/button.html`: `button-primary`, `button-icon`, `button-with-icon`
- **Card** → `@components/card.html`: `card-elevated`, `card-action`, `card-interactive`, `card-interactive-2`
- **Typography** → `@components/typography.html`: `typography-display`, `typography-body`, `typography-label`
