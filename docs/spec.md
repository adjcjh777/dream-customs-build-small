# Dream Customs / 梦境海关 Product Spec

Last updated: 2026-06-05

## 1. One-Line Concept

梦境海关帮用户和昨晚的梦结盟：用户用语音、图片或文字申报梦境，系统把不安转成第二天的小建议，把怪梦转成一件 5 分钟能完成的有趣小事。

## 2. Contest Fit

- Event: Build Small Hackathon.
- Build window: 2026-06-05 to 2026-06-15.
- Deployment target: Gradio app on Hugging Face Space.
- Model constraint: total model parameters must be <= 32B.
- Primary track fit: An Adventure in Thousand Token Wood, because the AI is the load-bearing delight of the experience.
- Secondary story: Backyard AI, because the concept comes from a real sleep problem: frequent vivid dreams and poor sleep.
- Model family constraint: prioritize MiniCPM models before considering any unrelated small model.

## 3. Core User Problem

The user wakes up after vivid or unsettling dreams and wants a quick, non-clinical way to make sense of the dream before the day begins. Existing dream tools often feel either too mystical, too diagnostic, or too generic. This product should feel like a playful ritual that gives emotional order without pretending to be therapy.

## 4. Product Principles

1. Do not diagnose.
2. Do not frighten the user.
3. Convert dream residue into a small next-day action.
4. Keep the output weird enough to show a friend.
5. Make the AI the main experience, not a helper hidden behind a form.
6. Keep the MVP stable enough for Gradio Space and demo-video recording.

## 5. User Inputs

All inputs are normalized into one `DreamIntake` object so the app does not become three separate products.

### 5.1 Text Input

The user writes:

- Dream narrative.
- Wake-up mood.
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

## 6. Dream Intake Schema

```json
{
  "dream_text": "我梦见自己一直赶不上电梯，楼层按钮会融化。",
  "voice_transcript": "我梦见我一直赶不上电梯...",
  "visual_clues": ["歪斜电梯门", "蓝色楼道", "融化的数字 14"],
  "mood": "焦虑但有点滑稽",
  "recurring_symbols": ["电梯", "迟到", "融化的按钮"],
  "uncertainty": "梦的后半段记不清",
  "user_context": "最近晚上常做梦，睡醒后想获得第二天建议"
}
```

## 7. Model Responsibilities

### MiniCPM-V-4.6

Role: dream witness.

Responsibilities:

- Read sketches, notes, screenshots, and photos.
- Extract objects, locations, visible text, colors, spatial relationships, and emotional cues.
- Return concise JSON-compatible visual clues.

Non-responsibilities:

- Do not generate the final alliance card.
- Do not provide psychological interpretation.

### MiniCPM5-1B

Role: dream diplomat.

Responsibilities:

- Merge dream text, voice transcript, and visual clues.
- Name the dream visitor.
- Ask 2-3 alliance negotiation questions.
- Generate the final alliance card.
- Keep tone playful, gentle, and non-clinical.

## 8. MVP User Flow

1. User opens Gradio app.
2. User submits any combination of text, image, and voice.
3. App transcribes voice if present.
4. App calls MiniCPM-V-4.6 if image is present.
5. App builds `DreamIntake`.
6. MiniCPM5-1B generates a dream visitor profile and 2-3 follow-up questions.
7. User answers questions or clicks "skip / refuse cooperation".
8. MiniCPM5-1B generates a final alliance card.
9. App renders the card as a shareable visual block and plain text.

## 9. Output Contract

The final card must include:

- Dream visitor name.
- Entry permit number.
- Carried emotional contraband.
- Risk level, phrased playfully.
- Alliance reading: what the dream may be trying to protect.
- One practical next-day suggestion.
- One 5-minute weird task.
- One bedtime release phrase.
- Safety note if the input indicates severe distress.

Example:

```json
{
  "visitor_name": "迟到的电梯",
  "permit_id": "DC-0605-014",
  "contraband": ["未申报的焦虑", "融化的按钮", "一小袋没来得及开始的事"],
  "risk_level": "橙色：需要被安置，但不需要被害怕",
  "alliance_reading": "这个梦像是在提醒你，今天不要把启动一件事和完成一件事混成同一个压力。",
  "practical_suggestion": "提前 10 分钟开始一件最小的任务，只要求打开它。",
  "weird_task": "给电梯写一句道歉信：抱歉总让你替我背迟到的锅。",
  "bedtime_release": "今日电梯已停靠，未完成事项明日再报关。",
  "safety_note": ""
}
```

## 10. UX Structure

### Screen 1: Dream Declaration Desk

Inputs:

- Textbox for dream notes.
- Image upload for dream sketch or bedside note.
- Audio input for spoken dream.
- Optional mood selector.

Primary action:

- "Submit to Customs"

### Screen 2: Alliance Negotiation

Content:

- Dream visitor name.
- 2-3 questions from the customs officer.
- Buttons: answer, skip, refuse cooperation.

### Screen 3: Today's Pact Card

Content:

- Card-style result.
- Copy text button.
- Download/share image target if feasible.
- "Release this dream for tonight" reset action.

## 11. Safety Boundaries

The app must:

- Avoid diagnoses, medical claims, or certainty about dream meaning.
- Avoid telling users that a dream proves trauma, illness, or danger.
- Use language such as "may be", "could be treated as", and "for today, try".
- If the user mentions self-harm, intent to harm others, severe insomnia, panic, or inability to function, show a supportive escalation note.

Escalation copy:

> This dream sounds heavier than a playful customs ritual should handle. If you feel unsafe, unable to sleep for many nights, or worried you may hurt yourself or someone else, please reach out to a trusted person or professional support now.

## 12. Recommended MVP Scope

Included:

- Gradio app.
- Text input.
- Image input through MiniCPM-V-4.6.
- Voice input through small ASR adapter.
- MiniCPM5-1B prompt flow.
- Result card in HTML.
- Example mode for demo stability.
- Basic safety classifier prompt or rule layer.

Excluded from MVP:

- Voice output.
- Long-term account system.
- Medical sleep tracking.
- Dream history database.
- Personalized therapy plans.
- Multi-user social feed.

## 13. Grill Questions And Recommended Answers

1. Is this a therapy tool?
   - Recommended answer: no. It is a playful reflection and next-day ritual tool.

2. Which track should the submission emphasize?
   - Recommended answer: Thousand Token Wood first, Backyard AI second.

3. Should voice be core?
   - Recommended answer: voice input yes, voice output no for MVP.

4. Should the image input be mandatory?
   - Recommended answer: no. Image is a strong MiniCPM-V demo path but text alone must work.

5. What is the winning demo moment?
   - Recommended answer: user speaks a dream, uploads a quick sketch, and receives a strange but useful "Today's Pact" card.

## 14. Open Questions

- Which ASR adapter should be used on Hugging Face Space for the MVP?
- Should the first demo be in Chinese, English, or bilingual?
- Do we want to submit under the same team/repo as the earlier Ordinary Relics MVP, or create a new Space?
- Should the visual card support image download in MVP or only screenshot-friendly HTML?
