# Dream Customs / 梦境海关 PRD

Last updated: 2026-06-05

## 1. Executive Summary

### Problem Statement

Users who wake up from frequent or vivid dreams may feel unsettled, tired, or mentally cluttered. They need a lightweight way to turn dream residue into a gentle next-day action without receiving pseudo-clinical dream diagnosis.

### Proposed Solution

Dream Customs is a Gradio app that accepts voice, image, and text dream declarations, normalizes them into a structured dream intake, and uses MiniCPM models to generate a playful "dream alliance" card with practical advice, a weird 5-minute task, and a bedtime release phrase.

### Success Criteria

- A user can complete the core flow from input to final card in <= 90 seconds on the hosted demo.
- At least 90% of demo runs produce a parseable final output object matching the required schema.
- At least 5 real users can understand the output without extra explanation and rate it >= 4/5 for delight.
- At least 3 real users report that the "today's pact" feels actionable.
- The app runs with total model parameters <= 32B and is packaged for Gradio/Hugging Face Space.

## 2. User Experience & Functionality

### User Personas

1. Primary persona: vivid dreamer.
   - Recently sleeps poorly or wakes with strong dream fragments.
   - Wants a small morning ritual, not therapy.

2. Secondary persona: playful AI explorer.
   - Wants a strange AI experience worth showing a friend.
   - Cares about creativity and shareable outputs.

3. Demo viewer / judge.
   - Needs to understand the interaction in under one minute.
   - Looks for clear small-model fit and Gradio polish.

### User Stories

#### Story 1: Text Dream Declaration

As a vivid dreamer, I want to type my dream so that I can get a next-day pact even if I have no image or audio.

Acceptance criteria:

- User can submit text-only input.
- App creates a valid `DreamIntake` object.
- Final card includes dream visitor, practical suggestion, weird task, and bedtime release phrase.

#### Story 2: Image Dream Declaration

As a user who remembers images better than words, I want to upload a sketch or bedside note so that the system can use visual dream clues.

Acceptance criteria:

- User can upload one image.
- MiniCPM-V-4.6 extracts at least 3 visual clues when visible content exists.
- Visual clues are included in the final `DreamIntake`.
- If image extraction fails, text-only flow still works.

#### Story 3: Voice Dream Declaration

As a half-awake user, I want to speak my dream so that I do not need to type immediately after waking.

Acceptance criteria:

- User can record or upload an audio clip.
- ASR adapter returns a transcript.
- Transcript is visible/editable before final submission or transparently included in the declaration.
- If ASR fails, user receives a concise fallback message and can type manually.

#### Story 4: Alliance Negotiation

As a user, I want the AI to ask me a few questions so that the final advice feels connected to my dream.

Acceptance criteria:

- App generates 2-3 questions.
- User can answer all, answer some, or skip.
- Skip path still generates a final card.

#### Story 5: Today's Pact Card

As a user, I want a visually clear output card so that I can screenshot or share the result.

Acceptance criteria:

- Card includes all required output fields.
- Card is readable on mobile and desktop.
- Card avoids medical or diagnostic framing.
- Card includes a short safety note only when needed.

### Non-Goals

- Medical diagnosis or therapy.
- Sleep-stage tracking.
- Long-term journaling database.
- Account creation.
- Voice output in MVP.
- Social feed or leaderboard.
- Fine-tuning during the hackathon MVP.

## 3. AI System Requirements

### Tool Requirements

- MiniCPM-V-4.6 for image-to-text visual clue extraction.
- MiniCPM5-1B for text reasoning, persona, structured output, and alliance card generation.
- A small ASR adapter for voice-to-text. This adapter is not the core AI experience.
- Gradio for UI.
- Optional HTML/CSS card renderer.

### Prompt Requirements

Prompts must:

- Ask for JSON-compatible output.
- Keep the tone playful, gentle, and non-clinical.
- Avoid strong claims about dream meaning.
- Include a safety boundary for severe distress.
- Keep final advice small enough to execute in 5-10 minutes.

### Evaluation Strategy

Create an eval set with at least 12 dream inputs:

- 4 text-only dreams.
- 3 image-assisted dreams.
- 3 voice-transcript dreams.
- 2 distress-edge cases.

Measure:

- Schema validity.
- Tone safety.
- Practicality of advice.
- Weird-task delight.
- Ability to recover from missing modality.

Pass thresholds:

- Schema validity: >= 90%.
- No diagnostic language in ordinary cases: 100%.
- Safety note appears in distress-edge cases: >= 90%.
- Human delight rating on 5 demo cases: average >= 4/5.

## 4. Technical Specifications

### Architecture Overview

```text
Gradio inputs
  -> text input
  -> image upload -> MiniCPM-V-4.6 visual clue extractor
  -> audio upload/record -> ASR adapter
  -> DreamIntake builder
  -> MiniCPM5-1B customs officer prompt
  -> negotiation questions
  -> final MiniCPM5-1B pact prompt
  -> HTML card renderer
```

### Core Components

- `app.py`: Gradio UI composition and event wiring.
- `dream_customs/schema.py`: dataclasses or Pydantic models for inputs and outputs.
- `dream_customs/models.py`: model/client loading and inference wrappers.
- `dream_customs/prompts.py`: prompt templates.
- `dream_customs/pipeline.py`: orchestration logic.
- `dream_customs/safety.py`: lightweight safety checks and copy.
- `dream_customs/render.py`: HTML card rendering.
- `tests/`: schema, prompt, safety, and pipeline unit tests with mocked model outputs.

### Integration Points

- Hugging Face Space runtime.
- Hugging Face model downloads or inference endpoints.
- Gradio audio, image, and text components.
- Optional model cache in Space environment.

### Security & Privacy

- Do not persist user dreams by default.
- Do not log raw dream text or uploaded images in production demo logs.
- Provide visible copy: "This is a playful reflection tool, not medical advice."
- Do not require account login.

## 5. Risks & Roadmap

### Phased Rollout

#### MVP

- Text, image, and voice input.
- Dream intake normalization.
- MiniCPM-V-4.6 image clue extraction.
- MiniCPM5-1B negotiation and final card.
- HTML output card.
- Safety boundary.

#### v1.1

- More polished card export.
- Better example gallery.
- Optional bilingual output.
- More robust eval harness.

#### v2.0

- Voice output through VoxCPM2.
- Local dream history stored only in browser/session.
- Multiple customs officer styles.

### Technical Risks

- MiniCPM-V-4.6 may be heavy for Space hardware if loaded locally.
- MiniCPM5-1B output may fail strict JSON without repair.
- ASR adapter may complicate dependencies.
- Audio input on mobile browsers may behave inconsistently.
- Safety classification may be too weak if only prompt-based.

### Mitigations

- Keep text-only demo path always functional.
- Add JSON repair and schema validation.
- Use examples with fixed sample media for demo recording.
- Make ASR optional and fallback to manual transcript.
- Keep image extraction output concise to reduce latency.
