---
name: Dream Customs
description: A nocturnal dream customs workbench for turning dream evidence into a next-day pact.
colors:
  bg-night: "oklch(0.145 0.030 238)"
  bg-void: "oklch(0.080 0.010 250)"
  surface-ink: "oklch(0.205 0.035 238)"
  surface-raised: "oklch(0.275 0.045 236)"
  primary-cobalt: "oklch(0.690 0.105 232)"
  primary-cobalt-deep: "oklch(0.510 0.115 234)"
  accent-coral-stamp: "oklch(0.705 0.160 28)"
  accent-aurora: "oklch(0.820 0.110 185)"
  ink-main: "oklch(0.965 0.010 235)"
  ink-muted: "oklch(0.760 0.030 232)"
  border-dream: "oklch(0.430 0.055 235)"
  warning: "oklch(0.760 0.150 75)"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 760
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 720
    lineHeight: 1.18
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 680
    lineHeight: 1.3
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 450
    lineHeight: 1.55
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 650
    lineHeight: 1.25
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary-cobalt-deep}"
    textColor: "{colors.ink-main}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  button-accent:
    backgroundColor: "{colors.accent-coral-stamp}"
    textColor: "{colors.bg-void}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  input-composer:
    backgroundColor: "{colors.surface-ink}"
    textColor: "{colors.ink-main}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
---

# Design System: Dream Customs

## 1. Overview

**Creative North Star: "The Night Desk"**

Dream Customs should feel like a working customs desk that appears inside a dream at 4:17 a.m. The surface is dark because the user often arrives from bed or after waking, but it is not a generic terminal. Cobalt, aurora cyan, and coral stamp ink carry the strange color. Familiar controls carry trust.

This is product UI first. The user needs to type, upload, record, answer, and decide what happens next. The dream atmosphere belongs in the background wash, pact inspector, stamps, and evidence chips, while controls stay clear and predictable.

**V3 First-Screen Trust Rule.** A user must be able to understand and start the ritual without scrolling. The dream text field, primary submit action, image/voice/mood evidence controls, and live pact summary belong in the first visible screen. Timeline and examples are supporting context, not the entry point.

**Key Characteristics:**

- Bottom composer as the primary input, modeled after Codex app behavior.
- Conversation timeline for declarations, questions, and pact drafts.
- Evidence tray for text, image, audio, mood, and model status.
- Pact inspector that can be drafted, revised, or sealed.
- Generated bitmap art as atmospheric header and state art, never as unreadable UI chrome.

## 2. Colors

The palette is nocturnal and atmospheric: neutral dark surfaces, cobalt primary actions, aurora hints, and coral stamp moments.

### Primary

- **Cobalt Gate** (`oklch(0.690 0.105 232)`): primary selection, active step, focus accents, and subtle interactive outlines.
- **Deep Cobalt Gate** (`oklch(0.510 0.115 234)`): filled primary buttons and selected composer controls with near-white text.

### Secondary

- **Coral Stamp Ink** (`oklch(0.705 0.160 28)`): final seal action, permit stamp, alert edge for safety notes, and one memorable highlight per screen.
- **Aurora Evidence Light** (`oklch(0.820 0.110 185)`): image/audio evidence status, successful extraction, and soft dream-glow details.

### Neutral

- **Night Background** (`oklch(0.145 0.030 238)`): app body and mobile shell.
- **Void Rail** (`oklch(0.080 0.010 250)`): app outer edge, header underlay, and screenshot-safe negative space.
- **Ink Surface** (`oklch(0.205 0.035 238)`): composer, timeline items, and tool panels.
- **Raised Surface** (`oklch(0.275 0.045 236)`): active inspector panels and output cards.
- **Main Ink** (`oklch(0.965 0.010 235)`): body text on dark surfaces.
- **Muted Ink** (`oklch(0.760 0.030 232)`): secondary labels that still remain readable.

### Named Rules

**The Stamp Rarity Rule.** Coral is used for sealing, warnings, and permit marks only. It must not become a general decoration color.

**The No Parchment Rule.** Do not return to cream, beige, or faux paper backgrounds. Dream color comes from night, ink, and evidence light.

## 3. Typography

**Display Font:** Inter with system fallbacks

**Body Font:** Inter with system fallbacks
**Label/Mono Font:** Use system mono only for permit IDs, debug JSON, and model telemetry.

**Character:** The interface uses one sans family so the product feels controlled. Personality comes from naming, layout, stamps, and generated imagery rather than decorative fonts.

### Hierarchy

- **Display** (760, 2.25rem, 1.05): app title and sealed pact headline only.
- **Headline** (720, 1.5rem, 1.18): step titles and pact section names.
- **Title** (680, 1rem, 1.3): timeline item headers, buttons, inspector labels.
- **Body** (450, 1rem, 1.55): dream text, questions, pact explanations, max 70ch for prose.
- **Label** (650, 0.8125rem, 1.25): compact field labels, evidence chips, status text.

### Named Rules

**The Low-Light Readability Rule.** Muted text must remain legible on dark surfaces. Never use low-contrast gray for field labels or placeholders.

## 4. Elevation

Depth is mostly tonal, not shadow-heavy. The app should feel layered like a dark desk under soft light, not like floating cards on a SaaS page. Shadows appear only for the active composer, a hovered evidence item, or a sealed pact.

### Shadow Vocabulary

- **composer-focus** (`0 0 0 1px oklch(0.690 0.105 232), 0 12px 32px rgba(0, 0, 0, 0.28)`): focused bottom composer.
- **pact-lift** (`0 10px 28px rgba(0, 0, 0, 0.24)`): sealed pact card only.
- **stamp-glow** (`0 0 20px rgba(255, 107, 84, 0.24)`): coral seal hover or success state.

### Named Rules

**The State First Rule.** Shadows communicate focus, hover, or completion. They are not default decoration.

## 5. Components

### Buttons

- **Shape:** medium rectangle, 10px radius.
- **Primary:** Deep Cobalt Gate fill, Main Ink text, 12px 16px padding.
- **Accent:** Coral Stamp Ink for `Seal today's pact` only.
- **Hover / Focus:** tonal lift plus visible cobalt focus ring.
- **Secondary:** transparent or Ink Surface fill with full border, never ghost text alone.

### Chips

- **Style:** small rounded pills with icon, label, and state dot.
- **State:** queued, extracted, failed, or selected. Evidence type uses icon and color, not long explanatory text.

### Cards / Containers

- **Corner Style:** 10px to 14px. No 32px rounded cards.
- **Background:** Ink Surface for timeline items, Raised Surface for active inspector.
- **Shadow Strategy:** flat by default, lifted only when active or sealed.
- **Border:** full border using Border Dream, not a side stripe.
- **Internal Padding:** 16px mobile, 24px desktop.

### Inputs / Fields

- **Style:** Codex-like bottom composer with large multiline input, attachment controls, model selector menu, and primary action clustered on the right.
- **Focus:** cobalt ring, slightly raised surface, no layout shift.
- **Error / Disabled:** inline message below composer, disabled actions stay readable and explain why.

### Navigation

- **Style:** compact status rail with current phase: Declare, Inspect, Negotiate, Draft, Seal.
- **Mobile:** phase rail collapses to segmented steps above the composer.

### Signature Component: Pact Inspector

The pact inspector is a live customs file, not just a final HTML card. It shows visitor, permit ID, evidence count, risk, suggested action, weird task, and whether the pact is draft or sealed. It gives the user three choices: add material, ask another question, or seal today's pact.

## 6. Do's and Don'ts

### Do:

- **Do** make the bottom composer the most obvious control on mobile and desktop.
- **Do** keep the first declaration controls above the timeline so a tired user can start immediately.
- **Do** keep every phase actionable with one clear next step.
- **Do** use generated raster imagery for the dream atmosphere, header state, or empty state.
- **Do** verify dark-mode contrast for body text, labels, placeholders, chips, and disabled controls.
- **Do** preserve a deterministic demo backend while adding a model-backed route.

### Don't:

- **Don't** ship a plain Gradio two-column form as the primary experience.
- **Don't** use beige parchment, tarot, faux therapy, or generic purple AI visuals.
- **Don't** use one-shot generation as the whole flow.
- **Don't** hide `Add material`, `Continue negotiation`, or `Seal pact` below the fold.
- **Don't** render navigation-looking text that cannot be clicked.
- **Don't** reserve tall empty panels for future content on the first screen.
- **Don't** pair a 1px border with a large soft shadow on every card.
- **Don't** use side-stripe borders, gradient text, or decorative glass panels.
