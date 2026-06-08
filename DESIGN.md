---
name: Dream QA
description: A guided dream Q&A interface for turning dream fragments into one grounded today tip.
colors:
  morning-mist: "oklch(0.965 0.014 210)"
  warm-paper: "oklch(0.985 0.010 82)"
  soft-ink: "oklch(0.205 0.020 70)"
  muted-ink: "oklch(0.500 0.030 82)"
  surface-card: "oklch(0.995 0.006 82)"
  surface-sage: "oklch(0.930 0.035 145)"
  primary-sage: "oklch(0.555 0.105 145)"
  primary-sage-deep: "oklch(0.390 0.095 145)"
  accent-amber: "oklch(0.820 0.120 78)"
  accent-coral: "oklch(0.710 0.135 32)"
  border-soft: "oklch(0.825 0.020 85)"
  warning: "oklch(0.760 0.150 75)"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "2rem"
    fontWeight: 760
    lineHeight: 1.08
    letterSpacing: "0"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 720
    lineHeight: 1.2
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
  md: "8px"
  lg: "12px"
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
    textColor: "{colors.warm-paper}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  button-secondary:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.primary-sage-deep}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  input-composer:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.soft-ink}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
---

# Design System: Dream QA

## 1. Overview

**Creative North Star: "The Morning Question Desk"**

Dream QA should feel like a calm morning workspace for unpacking a dream while it is still fresh. The surface is light, readable, and ordinary-user friendly, with enough dream atmosphere to feel memorable. The interface is a product experience first: the user needs to record, answer, skip, add detail, and receive one today tip without decoding a metaphor-heavy ritual.

The old customs/pact visual language is deprecated for new work. A small `Dream Customs` label may remain for repo/Space continuity, but the primary visible experience should be `梦境问答台 / Dream QA`.

**Key Characteristics:**

- Stepper with four phases: Record, Ask, Interpret, Tip.
- Conversation timeline for dream fragments, follow-up questions, answers, and interpretation draft.
- Unified multimodal composer for text, image, voice, mood, and primary action.
- Right-side desktop panel for interpretation draft and Today Tip preview.
- Mobile final screen that prioritizes the Today Tip before optional explanation.

## 2. Colors

The palette is soft morning product UI: warm white surfaces, charcoal text, sage actions, amber note highlights, and coral used sparingly for warmth or safety.

### Primary

- **Sage Guide** (`oklch(0.555 0.105 145)`): stepper progress, selected chips, focus accents.
- **Deep Sage Guide** (`oklch(0.390 0.095 145)`): primary buttons and active controls.

### Secondary

- **Amber Note** (`oklch(0.820 0.120 78)`): follow-up question highlight, Today Tip accent, gentle attention.
- **Coral Care** (`oklch(0.710 0.135 32)`): caring note, safety edge, and one small emotional highlight per result.

### Neutral

- **Morning Mist** (`oklch(0.965 0.014 210)`): app background.
- **Warm Paper** (`oklch(0.985 0.010 82)`): main reading surface.
- **Soft Ink** (`oklch(0.205 0.020 70)`): primary text.
- **Muted Ink** (`oklch(0.500 0.030 82)`): secondary labels with readable contrast.
- **Soft Border** (`oklch(0.825 0.020 85)`): panel and input borders.

### Named Rules

**The One Tip Rule.** Visual emphasis should guide the eye to one primary Today Tip. Do not create multiple equally loud recommendation blocks.

**The No Oracle Rule.** Avoid tarot, prophecy, mystic symbols, parchment certificates, and theatrical stamps.

## 3. Typography

**Display Font:** Inter with system fallbacks.

**Body Font:** Inter with system fallbacks.

**Label/Mono Font:** Use system mono only for debug JSON, model telemetry, or structured IDs.

### Hierarchy

- **Display** (760, 2rem, 1.08): app title and final Today Tip headline.
- **Headline** (720, 1.375rem, 1.2): step titles and result section names.
- **Title** (680, 1rem, 1.3): timeline item headers, buttons, and compact panel labels.
- **Body** (450, 1rem, 1.55): dream text, questions, interpretations, max 70ch for prose.
- **Label** (650, 0.8125rem, 1.25): chips, status text, and small metadata.

### Named Rules

**The Morning Readability Rule.** The user may be half-awake. Body text, buttons, placeholders, and chips must stay readable on mobile.

## 4. Elevation

Depth is subtle and functional. Panels should feel placed on a calm desk, not floating in a SaaS layout.

### Shadow Vocabulary

- **composer-focus** (`0 0 0 1px rgba(65, 115, 78, 0.35), 0 12px 28px rgba(45, 56, 42, 0.14)`): focused composer.
- **tip-lift** (`0 10px 24px rgba(45, 56, 42, 0.16)`): final Today Tip card only.
- **question-glow** (`0 0 18px rgba(230, 178, 75, 0.22)`): active follow-up question.

### Named Rules

**The State First Rule.** Shadows communicate focus, hover, or completion. They are not default decoration.

## 5. Components

### Buttons

- **Shape:** 8px radius.
- **Primary:** Deep Sage Guide fill, Warm Paper text, 12px 16px padding.
- **Secondary:** Warm Paper fill, Deep Sage text, full border.
- **Care / Safety:** Coral Care only for safety/support actions or caring note markers.
- **Hover / Focus:** tonal lift plus visible focus ring.

### Chips

- **Style:** small rounded pills with icon, label, and state dot.
- **Use:** mood, image clue status, voice transcript status, answer/skip choices, and alternate angle request.
- **Text:** short labels only. Long explanatory text belongs in timeline or result body.

### Cards / Containers

- **Corner Style:** 8px to 12px. No oversized rounded blobs.
- **Background:** Warm Paper or Surface Card.
- **Shadow Strategy:** flat by default, lifted only when active or final.
- **Border:** full soft border.
- **Internal Padding:** 16px mobile, 24px desktop.

### Inputs / Fields

- **Style:** unified composer with multiline dream input, attachment controls, mood, and primary action.
- **Focus:** sage ring, slightly raised surface, no layout shift.
- **Error / Disabled:** inline message below composer, disabled actions stay readable and explain why.

### Navigation

- **Style:** visible stepper with current phase: Record, Ask, Interpret, Tip.
- **Mobile:** stepper collapses to compact segmented steps above the conversation.
- **Desktop:** left rail or top rail is acceptable, but it must map to real states.

### Signature Component: Today Tip Panel

The Today Tip Panel is the final surface. It shows:

- Dream summary.
- Main question.
- Grounded interpretation.
- One primary Today Tip.
- Optional tiny action.
- Optional caring note.
- Safety note only when needed.

The tip should be first-class and easy to screenshot, but it must not look like a diagnosis card or mystical certificate.

## 6. Do's and Don'ts

### Do:

- **Do** make the first action obvious on mobile and desktop.
- **Do** show the gradual Q&A flow so users understand why the final tip is grounded.
- **Do** keep every phase actionable with one clear next step.
- **Do** cite concrete dream anchors in the final result.
- **Do** preserve a deterministic demo backend while adding a model-backed route.
- **Do** verify text fits inside controls at 390px mobile width.

### Don't:

- **Don't** ship a plain Gradio two-column form as the primary experience.
- **Don't** use tarot, parchment, prophecy, medical intake, or generic healing-app aesthetics.
- **Don't** expose technical model routes as first-level controls unless the user opens model settings.
- **Don't** render navigation-looking text that cannot be clicked.
- **Don't** create several competing tips in the final result.
- **Don't** let the final advice become generic wellness copy unrelated to the dream.
