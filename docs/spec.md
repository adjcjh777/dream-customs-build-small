# Dream QA / 梦境问答台 Product Spec

Last updated: 2026-06-08

## 1. One-Line Concept

Dream QA helps users unpack last night's dream step by step: they record a dream with text, image, or voice; the system asks one grounded follow-up question; then it gives a non-diagnostic, non-fatalistic interpretation draft and one gentle Today Tip.

The public hackathon demo is English-first because the event is international. Chinese remains available through the in-app `English / 中文` toggle.

## 2. Contest Fit

- Event: Build Small Hackathon.
- Build window: 2026-06-05 to 2026-06-15.
- Deployment target: Gradio app on Hugging Face Space.
- Model constraint: total model parameters must be <= 32B.
- Primary track fit: An Adventure in Thousand Token Wood, because the AI-driven conversation is the main experience.
- Secondary story: Backyard AI, because the concept comes from a real sleep problem: frequent vivid dreams and morning confusion.
- Model family constraint: prioritize MiniCPM models before considering any unrelated small model.

## 3. Core User Problem

The user wakes up after a vivid or unsettling dream and wants help making sense of it without receiving mystical certainty, therapy language, or generic advice. They may not know the right question yet, so the app should help them gradually clarify what they are curious or worried about.

## 4. Product Principles

1. Do not diagnose.
2. Do not frighten the user.
3. Do not claim the dream has one fixed meaning.
4. Ask before interpreting.
5. Ground every final answer in concrete dream details.
6. End with one small today tip, not a pile of advice.
7. Keep the MVP stable enough for Gradio Space and demo-video recording.
8. Default to English for public judging; keep Chinese as a first-class toggle.

## 5. User Inputs

All inputs are normalized into one dream intake object so the app does not become three separate products.

### 5.1 Text Input

The user writes:

- Dream narrative.
- Wake-up mood.
- What feels confusing or important.
- Repeated symbols.
- Any second-day concern or wish.

### 5.2 Image Input

The user uploads:

- A dream sketch.
- A bedside note.
- A screenshot or photo related to the dream.
- A quick doodle drawn after waking.

MiniCPM-V-4.6 extracts visual clues and returns structured text.

### 5.3 Voice Input

The user speaks the dream immediately after waking.

Implementation note: MiniCPM-V-4.6 and MiniCPM5-1B are not raw audio ASR models. Voice input needs a small transcription adapter. The adapter only converts audio to text; dream understanding remains MiniCPM-driven.

### 5.4 Language Input

The app defaults to English. A visible language toggle allows `中文`. The same `DreamQuestionIntake -> DreamQAState -> TodayTipCard` pipeline is used for both languages; only prompt instructions, UI labels, and rendered output labels change.

## 6. Data Model

The refactor should move from `DreamIntake -> PactCard` toward:

```text
DreamQuestionIntake -> DreamQAState -> TodayTipCard
```

### 6.1 DreamQuestionIntake

```json
{
  "dream_text": "我梦见自己一直赶不上电梯，楼层按钮会融化。",
  "voice_transcript": "我梦见我一直赶不上电梯...",
  "visual_clues": ["歪斜电梯门", "蓝色楼道", "融化的数字 14"],
  "mood": "焦虑但有点滑稽",
  "main_question": "这个梦是不是和我最近拖延有关？",
  "recurring_symbols": ["电梯", "迟到", "融化的按钮"],
  "uncertainty": "梦的后半段记不清",
  "user_context": "最近晚上常做梦，睡醒后想获得第二天建议"
}
```

### 6.2 DreamQAState

```json
{
  "dream_summary": "你梦见自己赶不上电梯，楼层按钮像蜡一样融化。",
  "dream_anchors": ["赶不上电梯", "融化的按钮", "焦虑但滑稽"],
  "main_question": "这个梦和最近拖延有关吗？",
  "followup_questions": [
    "梦里最强烈的感受是着急、害怕，还是荒诞？",
    "最近有没有一件事让你觉得还没开始就已经迟到？"
  ],
  "user_answers": ["更像是还没开始就觉得迟到。"],
  "current_step": "interpret"
}
```

### 6.3 TodayTipCard

```json
{
  "dream_summary": "你梦见赶不上电梯，按钮融化，醒来有点焦虑。",
  "main_question": "它是否和最近拖延有关？",
  "interpretation": "也许这个梦不是在证明你真的迟到了，而是在把“还没开始就担心来不及”的感觉演成了电梯。",
  "today_tip": "今天先选一件小事，只做打开它的第一步，别要求自己马上抵达。",
  "tiny_action": "用 5 分钟写下：如果电梯只停一层，我今天先停在哪一层？",
  "caring_note": "你不需要一醒来就解决所有问题，先把节奏找回来就很好。",
  "safety_note": ""
}
```

## 7. Model Responsibilities

### MiniCPM-V-4.6

Role: dream witness.

Responsibilities:

- Read sketches, notes, screenshots, and photos.
- Extract objects, locations, visible text, colors, spatial relationships, and emotional cues.
- Return concise JSON-compatible visual witness reports.

Non-responsibilities:

- Do not generate the final TodayTipCard.
- Do not provide psychological diagnosis.

### MiniCPM5-1B

Role: dream question guide.

Responsibilities:

- Merge dream text, voice transcript, and visual clues.
- Summarize the dream without overexplaining.
- Infer or ask the user's main question.
- Ask 1-3 gentle follow-up questions.
- Prefer exactly one visible follow-up question in the public MVP, with another-angle actions available after the first result.
- Draft a non-certain interpretation grounded in dream anchors.
- Generate exactly one primary today tip, with optional tiny action and caring note.
- Keep tone playful, gentle, and non-clinical.
- Follow the selected language: English by default, Chinese when selected.

## 8. MVP User Flow

1. User opens Gradio app.
2. User submits any combination of text, image, and voice.
3. App transcribes voice if present.
4. App calls MiniCPM-V-4.6 if image is present.
5. App builds `DreamQuestionIntake`.
6. MiniCPM5-1B summarizes the dream and identifies the likely `main_question`.
7. App asks 1-3 follow-up questions.
8. User answers, skips, adds detail, or asks for another angle.
9. MiniCPM5-1B drafts a grounded interpretation.
10. MiniCPM5-1B generates a final `TodayTipCard`.
11. Gradio renders a mobile-readable result block and plain text.

## 9. Output Contract

The final result must include:

- Dream summary.
- Main question.
- Grounded interpretation.
- One primary today tip.
- Optional tiny action.
- Optional caring note.
- Safety note if the input indicates severe distress.

The final result must:

- Reference at least one concrete dream anchor.
- Avoid diagnosis, prophecy, or frightening certainty.
- Avoid generic advice that could fit any dream.
- Keep the today tip small enough to try today.
- Use English UI/output labels by default and Chinese labels only when `中文` is selected.

## 10. UX Structure

### Screen 1: Record

Inputs:

- Textbox for dream notes.
- Image upload for dream sketch or bedside note.
- Audio input for spoken dream.
- Optional mood selector.
- Optional field: "你最想理解什么？"

Primary action:

- "Continue"

### Screen 2: Ask

Content:

- Short dream summary.
- Main question guess.
- 1-3 follow-up questions.
- Buttons: answer, skip, ask another angle.

### Screen 3: Interpret

Content:

- Dream anchors detected.
- Draft interpretation using "也许 / 可以把它当作 / 今天先试试" language.
- Controls: add detail, regenerate angle, finish.

### Screen 4: Today Tip

Content:

- One primary today tip.
- Optional tiny action.
- Optional caring note.

### Screen 0: Language

Default: `English`.

Secondary option: `中文`.

The toggle should be visible but not distract from the dream composer.
- Copy text button.
- Reset action.

## 11. Safety Boundaries

The app must:

- Avoid diagnoses, medical claims, or certainty about dream meaning.
- Avoid telling users that a dream proves trauma, illness, danger, fate, or prophecy.
- Use language such as "may be", "could be treated as", and "for today, try".
- If the user mentions self-harm, intent to harm others, severe insomnia, panic, or inability to function, show a supportive escalation note.

Escalation copy:

> This dream sounds heavier than a playful reflection tool should handle. If you feel unsafe, unable to sleep for many nights, or worried you may hurt yourself or someone else, please reach out to a trusted person or professional support now.

## 12. Recommended MVP Scope

Included:

- Gradio app.
- Text input.
- Image input through MiniCPM-V-4.6.
- Voice input through small ASR adapter.
- Dream intake normalization.
- Progressive follow-up questions.
- Today Tip result in HTML.
- Example mode for demo stability.
- Basic safety classifier prompt or rule layer.

Excluded from MVP:

- Voice output.
- Long-term account system.
- Medical sleep tracking.
- Dream history database.
- Personalized therapy plans.
- Multi-user social feed.
- Fine-tuning during the hackathon MVP.

## 13. Grill Questions And Recommended Answers

1. Is this a therapy tool?
   - Recommended answer: no. It is a playful reflection and next-day tip tool.

2. Which track should the submission emphasize?
   - Recommended answer: Thousand Token Wood first, Backyard AI second.

3. What should the demo show?
   - Recommended answer: user enters a dream, answers or skips one follow-up question, and receives a grounded today tip.
