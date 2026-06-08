ESCALATION_TERMS = (
    "hurt myself",
    "kill myself",
    "suicide",
    "self-harm",
    "hurt someone",
    "many nights",
    "cannot function",
    "panic attack",
    "想伤害自己",
    "自杀",
    "自残",
    "伤害别人",
    "很多天睡不着",
    "无法正常生活",
    "无法生活",
)


def needs_escalation(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ESCALATION_TERMS)


def safety_note() -> str:
    return (
        "This dream sounds heavier than a playful reflection tool should handle. "
        "If you feel unsafe, cannot sleep for many nights, or worry you may hurt "
        "yourself or someone else, please reach out to a trusted person or professional support now."
    )
