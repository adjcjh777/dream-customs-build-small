# Dream QA / 梦境问答台 PRD

Last updated: 2026-06-08

## 1. Executive Summary

### Problem Statement

Users who wake up from vivid dreams may feel unsettled, curious, or mentally cluttered. They often do not need a definitive "meaning"; they need a short, safe conversation that helps them identify what question the dream left behind and what tiny thing they can do today.

### Proposed Solution

Dream QA is a Gradio app that accepts voice, image, and text dream fragments, normalizes them into a structured dream intake, asks one gentle follow-up question, drafts a grounded interpretation, and ends with a Morning Ticket whose first payload is one Today Tip.

The repository and Space may continue to use `Dream Customs` as the deployed project name, but the product experience should no longer be built around permits, contraband, or sealed pact cards.

The public demo defaults to English for the international hackathon audience. A visible language toggle preserves the Chinese experience.

### Success Criteria

- A user can complete the core text-only Q&A flow in <= 90 seconds on the hosted demo.
- At least one follow-up question feels related to the dream in >= 90% of demo runs.
- Final output references at least one concrete dream detail.
- Final output gives exactly one primary today tip.
- Ordinary cases contain no diagnostic, prophetic, or frightening language.
- Distress-edge cases show a support note.
- English is the default public language; Chinese remains available through one visible toggle.
- `python scripts/evaluate_today_tip_quality.py` passes before deployment.
- The app runs with total model parameters <= 32B and is packaged for Gradio/Hugging Face Space.

## 2. User Experience & Functionality

### User Personas

1. Primary persona: vivid dreamer.
   - Recently sleeps poorly or wakes with strong dream fragments.
   - Wants a small morning reflection, not therapy or fortune-telling.

2. Secondary persona: playful AI explorer.
   - Wants a strange AI experience worth showing a friend.
   - Cares about creativity and shareable outputs.

3. Demo viewer / judge.
   - Needs to understand the interaction in under one minute.
   - Looks for clear small-model fit and Gradio polish.
   - Should land on an English first screen without needing translation.

### User Stories

#### Story 1: Text Dream Q&A

As a vivid dreamer, I want to type my dream so that the app can help me figure out what I am actually wondering about.

Acceptance criteria:

- User can submit text-only input.
- App creates a valid dream intake object.
- App asks at least one relevant follow-up question.
- User can answer or skip.
- Final output includes a grounded today tip.

#### Story 2: Image-Assisted Dream Clues

As a user who remembers images better than words, I want to upload a sketch or bedside note so that the system can use visual dream clues.

Acceptance criteria:

- User can upload one image.
- MiniCPM-V-4.6 extracts visible clues when content exists.
- Visual clues are included in the dream intake and final interpretation.
- If image extraction fails, text-only flow still works.

#### Story 3: Voice Dream Capture

As a half-awake user, I want to speak my dream so that I do not need to type immediately after waking.

Acceptance criteria:

- User can record or upload an audio clip.
- ASR adapter returns a transcript.
- Transcript is visible/editable or transparently included in the dream intake.
- If ASR fails, user receives a concise fallback message and can type manually.

#### Story 4: Follow-Up Question Flow

As a user, I want the AI to ask me a few questions so that the final interpretation feels connected to my dream rather than generic.

Acceptance criteria:

- App generates 1-3 follow-up questions.
- User can answer all, answer some, skip, or ask for another angle.
- Skip path still generates a final tip.
- Questions avoid clinical or diagnostic phrasing.

#### Story 5: Morning Ticket

As a user, I want a clear final result so that I leave with one small thing for today.

Acceptance criteria:

- Result includes dream summary, main question, today tip, optional tiny 5-minute action, supporting interpretation, optional caring note, and safety note when needed.
- Result presents the Today Tip before supporting interpretation.
- Result is readable on mobile and desktop.
- Result avoids medical, prophetic, or deterministic framing.
- Today tip references a concrete dream anchor.
- Optional tiny action is a five-minute first step, not a command to solve the whole issue immediately.
- Supporting interpretation uses the user's answer when the answer names a concrete waking-life task.

#### Story 6: Bilingual Demo

As an international judge, I want the app to open in English, while Chinese users can still switch to 中文.

Acceptance criteria:

- Default UI title is `Dream QA`.
- A visible `English / 中文` control exists.
- English mode renders English labels and card headings.
- English mode translates or paraphrases non-English anchors into English unless preserving a deliberate user quote.
- Chinese mode renders `梦境问答台` and Chinese Today Tip labels.
- Both modes use the same model/pipeline route.

### Non-Goals

- Medical diagnosis or therapy.
- Dream prophecy or symbolic certainty.
- Sleep-stage tracking.
- Long-term journaling database.
- Account creation.
- Voice output in MVP.
- Social feed or leaderboard.
- Fine-tuning during the hackathon MVP.

## 3. AI System Requirements

### Tool Requirements

- MiniCPM-V-4.6 for image-to-text visual clue extraction.
- MiniCPM5-1B for text reasoning, follow-up questions, interpretation, and Today Tip generation.
- A small ASR adapter for voice-to-text. This adapter is not the core AI experience.
- Gradio for UI.
- Optional HTML/CSS result renderer.

### Prompt Requirements

Prompts must:

- Ask for JSON-compatible output.
- Keep the tone playful, gentle, and non-clinical.
- Avoid strong claims about dream meaning.
- Include a safety boundary for severe distress.
- Keep final advice small enough to execute today.
- Require at least one dream anchor in the final tip.
- Follow selected language: English by default, Chinese when selected.
- Avoid mixed-language leakage in English output.
- Avoid hard commands such as "address it immediately"; prefer optional first-step language.

### Evaluation Strategy

Create an eval set with at least 12 dream inputs:

- 4 text-only dreams.
- 3 image-assisted dreams.
- 3 voice-transcript dreams.
- 2 distress-edge cases.

Measure:

- Schema validity.
- Follow-up relevance.
- Tone safety.
- Dream-anchor grounding.
- Practicality of today tip.
- Ability to recover from missing modality.
- Old customs words do not appear in the Dream QA result: permit, contraband, clearance, sealed, pact.
- English default output does not contain Chinese UI labels.

Pass thresholds:

- Schema validity: >= 90%.
- No diagnostic language in ordinary cases: 100%.
- Safety note appears in distress-edge cases: >= 90%.
- At least one concrete dream anchor in final result: >= 90%.
- Human usefulness/delight rating on 5 demo cases: average >= 4/5.

Current deterministic gate:

```bash
python scripts/evaluate_today_tip_quality.py
```

This gate covers 10 representative cases and should be expanded toward the 12-case target as image/voice remote smoke matures.

## 4. Technical Specifications

### Architecture Overview

```text
Gradio inputs
  -> text input
  -> image upload -> MiniCPM-V-4.6 visual clue extractor
  -> audio upload/record -> ASR adapter
  -> DreamQuestionIntake builder
  -> MiniCPM5-1B summary/main-question prompt
  -> follow-up question flow
  -> user answer/skip/another-angle
  -> MiniCPM5-1B interpretation prompt
  -> TodayTipCard prompt
  -> HTML result renderer
```

### Core Components

- `app.py`: thin Gradio entrypoint.
- `dream_customs/schema.py`: Pydantic models for dream intake, Q&A state, and Today Tip output.
- `dream_customs/models.py`: model/client loading and inference wrappers.
- `dream_customs/prompts.py`: prompt templates.
- `dream_customs/pipeline.py`: orchestration logic.
- `dream_customs/safety.py`: lightweight safety checks and copy.
- `dream_customs/render.py`: HTML result rendering.
- `dream_customs/ui/`: Gradio UI shell, copy, actions, and styles.
- `tests/`: schema, prompt, safety, pipeline, render, and UI action unit tests with mocked model outputs.

### Integration Points

- Hugging Face Space runtime.
- Hugging Face model downloads or private Modal endpoints.
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
- MiniCPM5-1B follow-up and final Today Tip.
- HTML output card.
- Safety boundary.

#### v1.1

- Better example gallery.
- Optional bilingual output.
- More robust eval harness.
- Better result export.

#### v2.0

- Voice output through VoxCPM2.
- Local dream history stored only in browser/session.
- Multiple question-guide styles.

### Technical Risks

- MiniCPM-V-4.6 may be heavy for Space hardware if loaded locally.
- MiniCPM5-1B output may fail strict JSON without repair.
- ASR adapter may complicate dependencies.
- Audio input on mobile browsers may behave inconsistently.
- Final tips may become generic unless prompts and repair logic enforce dream anchors.
