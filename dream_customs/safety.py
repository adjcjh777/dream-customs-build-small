ESCALATION_TERMS = (
    "hurt myself",
    "kill myself",
    "do not want to wake up",
    "don't want to wake up",
    "didn't want to wake up",
    "hopeless",
    "can't go on",
    "cannot go on",
    "suicide",
    "self-harm",
    "hurt someone",
    "many nights",
    "three nights",
    "3 nights",
    "can't sleep",
    "cannot sleep",
    "cannot function",
    "panic attack",
    "想伤害自己",
    "自杀",
    "自残",
    "不想醒来",
    "不想活",
    "活不下去",
    "轻生",
    "绝望",
    "撑不住",
    "崩溃",
    "伤害别人",
    "很多天睡不着",
    "连续3晚",
    "连续 3 晚",
    "连续三晚",
    "连续很多天",
    "无法正常生活",
    "无法生活",
)


def needs_escalation(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ESCALATION_TERMS)


def safety_note(language: str = "en") -> str:
    if language == "zh":
        return (
            "这段梦和醒来后的感受听起来已经超过了一个轻量梦境反思工具适合独自处理的范围。"
            "如果你感到不安全、连续很多天睡不着，或担心自己可能伤害自己或别人，请现在联系一个可信任的人，"
            "或寻求专业支持。"
        )
    return (
        "This dream sounds heavier than a playful reflection tool should handle. "
        "If you feel unsafe, cannot sleep for many nights, or worry you may hurt "
        "yourself or someone else, please reach out to a trusted person or professional support now."
    )
