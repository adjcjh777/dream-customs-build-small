# Product

## Register

product

## Users

Dream QA / 梦境问答台 serves people who wake up with vivid, strange, or unsettling dreams and want a small morning conversation before the day takes over. The primary user may still be half asleep, on a phone, and emotionally sticky from the dream. The secondary user is an international hackathon judge or playful AI explorer who needs to understand the loop quickly and see why small multimodal models matter.

## Product Purpose

The product helps a user unpack a dream through a guided, step-by-step Q&A. It accepts text, image, and voice fragments, turns them into one structured dream intake, asks gentle follow-up questions, drafts a grounded interpretation, and ends with one Today Tip.

The hackathon-facing experience is English-first. A visible `English / 中文` language control keeps the Chinese experience available without making judges start from a Chinese-only first screen.

Success means the user receives something more useful than a one-shot interpretation: one clear today tip first, an optional tiny action, and then a non-certain explanation grounded in concrete dream details and the user's answer. The tip can be practical, playful, or simply caring, but it must feel connected to the dream.

## Brand Personality

Gentle, strange, lucid.

The voice is a calm dream companion who asks good questions and takes odd details seriously without becoming mystical or clinical. It should feel curious, ordinary-user friendly, and companionable: less secret ritual, more warm morning dialogue.

## Anti-references

- Do not look like a plain Gradio form with two columns and one submit button.
- Do not look like a beige parchment certificate, generic tarot card, therapy intake form, or purple AI SaaS dashboard.
- Do not sound like generic healing-app advice that could fit any input.
- Do not use medical, diagnostic, frightening, fate-telling, or prophecy language.
- Do not bury the main action below many controls.
- Do not force the user to complete a long questionnaire before seeing value.
- Do not end with multiple competing recommendations; the final result needs one primary today tip.

## Design Principles

1. The AI is a question guide, not an oracle.
2. The user keeps agency: answer, skip, add detail, ask for another angle, or finish.
3. The interface should be dream-colored but product-trustworthy.
4. Every final output should lead to one small next-day reference or action.
5. The final tip must cite a concrete dream anchor.
6. The demo path must survive Space constraints and still have a model-backed route.
7. English mode is the default public path; Chinese mode is a first-class toggle, not a separate product.
8. Recommendation quality is tested with a deterministic Today Tip eval set before deployment.
9. English mode must stay natural English, including translated or paraphrased dream anchors; mixed Chinese helper text is a regression.
10. Tiny actions should feel like a first step the user may choose, not a hard command to solve the real-world problem immediately.
11. The final card prioritizes the Today Tip before interpretation; interpretation is supporting reflection, not the main payoff.

## Accessibility & Inclusion

Target WCAG AA contrast for body text, controls, and placeholder text. Support mobile-first use, keyboard navigation, visible focus states, reduced motion, and English/Chinese text without layout breakage. Avoid flashing effects, fear-based copy, or overconfident claims about dream meaning. Severe distress, self-harm, harm to others, or inability to function must show a clear support note.
