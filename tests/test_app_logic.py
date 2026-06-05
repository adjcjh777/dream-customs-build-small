import json

from dream_customs.app_logic import run_customs_once


def test_run_customs_once_generates_demo_outputs():
    negotiation, pact_text, html, debug_json = run_customs_once(
        dream_text="我梦见迟到的电梯。",
        mood="foggy",
        answers="我想先完成一件小事。",
    )
    debug = json.loads(debug_json)
    assert "Visitor:" in negotiation
    assert "Dream visitor:" in pact_text
    assert "Today's Pact" in html
    assert debug["status"] == "ok"
    assert debug["intake"]["dream_text"] == "我梦见迟到的电梯。"


def test_run_customs_once_requires_one_modality():
    negotiation, pact_text, html, debug_json = run_customs_once(dream_text="")
    assert negotiation == "No declaration received."
    assert "Please add text" in pact_text
    assert html == ""
    assert json.loads(debug_json) == {"status": "empty"}
