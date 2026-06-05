from dream_customs.schema import DreamIntake


def visual_clue_prompt() -> str:
    return (
        "You are the witness clerk at Dream Customs. Extract concise visual clues "
        "from this dream sketch, note, screenshot, or photo. Return JSON with keys: "
        "objects, places, visible_text, colors, mood_cues, uncertain_details. "
        "Do not diagnose the user."
    )


def negotiation_prompt(intake: DreamIntake) -> str:
    return f"""
You are the Dream Customs diplomat. The user is not asking for diagnosis.
Treat the dream as a strange visitor that can form a small pact with the user.
The tone should be gentle, playful, and specific. Do not make medical claims.

Dream intake:
{intake.merged_text()}

Return JSON with:
- visitor_name: short vivid name
- questions: 2 or 3 gentle, specific, slightly weird questions
- tone_note: one sentence explaining the visitor without certainty
""".strip()


def pact_prompt(intake: DreamIntake, answers: str) -> str:
    return f"""
You are the Dream Customs diplomat. Generate a final Today's Pact card.
Do not diagnose. Do not claim the dream has one certain meaning.
Give one practical next-day suggestion and one weird task doable in 5 minutes.
Use warm, non-clinical language. If the user wrote in Chinese, answer in Chinese.

Dream intake:
{intake.merged_text()}

User answers:
{answers}

Return strict JSON with:
visitor_name, permit_id, contraband, risk_level, alliance_reading,
practical_suggestion, weird_task, bedtime_release, safety_note.
""".strip()
