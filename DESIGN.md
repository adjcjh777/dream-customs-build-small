---
name: Dream Customs
description: A nocturnal dream customs workbench for turning dream evidence into a next-day pact.
colors:
  bg-night: "oklch(0.185 0.018 55)"
  bg-void: "oklch(0.130 0.012 55)"
  surface-ink: "oklch(0.235 0.018 58)"
  surface-raised: "oklch(0.295 0.020 62)"
  primary-sage: "oklch(0.690 0.105 150)"
  primary-sage-deep: "oklch(0.455 0.090 155)"
  accent-coral-stamp: "oklch(0.700 0.140 32)"
  accent-amber-lamp: "oklch(0.830 0.120 76)"
  accent-aurora: "oklch(0.745 0.080 185)"
  ink-main: "oklch(0.960 0.010 78)"
  ink-muted: "oklch(0.760 0.018 78)"
  border-dream: "oklch(0.465 0.024 70)"
  warning: "oklch(0.760 0.150 75)"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 760
    lineHeight: 1.05
    letterSpacing: "0"
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
    backgroundColor: "{colors.primary-sage-deep}"
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

**Creative North Star: "The Morning Customs Desk"**

Dream Customs should feel like a small warm customs desk that appears after waking: quiet, slightly strange, and easy enough to use before the day fully starts. The surface can stay dark like Codex, but it should read as warm charcoal and lamplight rather than a cold technical dashboard. Sage action color, amber light, muted coral seal ink, and a little aurora evidence color carry the identity.

This is product UI first. The user needs to type, attach, optionally add voice, answer, and decide what happens next. The dream atmosphere belongs in the background wash, pact inspector, stamps, and evidence chips, while controls stay clear and predictable.

**V4 Unified Composer Rule.** The dream input should behave like a Codex-style multimodal composer, not like a Gradio form. Text, image upload, voice upload, mood, add-material, and send belong visually inside one rounded input surface. Technical model routes and advanced workflow shortcuts should be collapsed by default.

**Key Characteristics:**

- Unified composer as the primary input, modeled after Codex app behavior.
- Conversation timeline for declarations, questions, and pact drafts.
- Evidence tray for text, image, audio, mood, and model status.
- Pact inspector that can be drafted, revised, or sealed.
- Generated bitmap art as atmospheric header and state art, never as unreadable UI chrome.

## 2. Colors

The palette is nocturnal and atmospheric: neutral dark surfaces, cobalt primary actions, aurora hints, and coral stamp moments.

### Primary

- **Sage Gate** (`oklch(0.690 0.105 150)`): primary selection, active step, focus accents, and subtle interactive outlines.
- **Deep Sage Gate** (`oklch(0.455 0.090 155)`): filled primary buttons and selected composer controls with near-white text.

### Secondary

- **Coral Stamp Ink** (`oklch(0.700 0.140 32)`): final seal action, permit stamp, alert edge for safety notes, and one memorable highlight per screen.
- **Amber Lamp** (`oklch(0.830 0.120 76)`): warmth, trust cue, and section highlights.
- **Aurora Evidence Light** (`oklch(0.745 0.080 185)`): image/audio evidence status, successful extraction, and soft dream-glow details.

### Neutral

- **Warm Night Background** (`oklch(0.185 0.018 55)`): app body and mobile shell.
- **Soft Void Rail** (`oklch(0.130 0.012 55)`): app outer edge, header underlay, and screenshot-safe negative space.
- **Charcoal Ink Surface** (`oklch(0.235 0.018 58)`): composer, timeline items, and tool panels.
- **Raised Warm Surface** (`oklch(0.295 0.020 62)`): active inspector panels and output cards.
- **Main Ink** (`oklch(0.960 0.010 78)`): body text on dark surfaces.
- **Muted Ink** (`oklch(0.760 0.018 78)`): secondary labels that still remain readable.

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

- **Do** make the unified composer the most obvious control on mobile and desktop.
- **Do** keep the first declaration controls above the timeline so a tired user can start immediately.
- **Do** keep every phase actionable with one clear next step.
- **Do** use generated raster imagery for the dream atmosphere, header state, or empty state.
- **Do** verify dark-mode contrast for body text, labels, placeholders, chips, and disabled controls.
- **Do** preserve a deterministic demo backend while adding a model-backed route.

### Don't:

- **Don't** ship a plain Gradio two-column form as the primary experience.
- **Don't** use beige parchment, tarot, faux therapy, or generic purple AI visuals.
- **Don't** use one-shot generation as the whole flow.
- **Don't** expose technical model routes as first-level controls unless the user opens model settings.
- **Don't** render navigation-looking text that cannot be clicked.
- **Don't** reserve tall empty panels for future content on the first screen.
- **Don't** pair a 1px border with a large soft shadow on every card.
- **Don't** use side-stripe borders, gradient text, or decorative glass panels.
