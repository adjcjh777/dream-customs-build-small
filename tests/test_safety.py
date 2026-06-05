from dream_customs.safety import needs_escalation, safety_note


def test_ordinary_dream_does_not_escalate():
    assert not needs_escalation("I dreamed about a strange elevator.")


def test_self_harm_text_escalates():
    assert needs_escalation("I might hurt myself if I cannot sleep.")


def test_chinese_severe_insomnia_escalates():
    assert needs_escalation("我已经很多天睡不着，感觉无法正常生活。")


def test_safety_note_mentions_professional_support():
    assert "professional support" in safety_note().lower()
