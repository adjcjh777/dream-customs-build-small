from dream_customs.models import FakeVisionClient
from dream_customs.prompts import visual_witness_prompt


def test_visual_witness_prompt_requests_structured_report():
    prompt = visual_witness_prompt()

    assert "MiniCPM-V-4.6" in prompt
    assert "scene_summary" in prompt
    assert "objects" in prompt
    assert "visible_text" in prompt
    assert "spatial_relations" in prompt
    assert "mood_cues" in prompt
    assert "uncertain_details" in prompt
    assert "surprising_detail" in prompt
    assert "strict JSON" in prompt
    assert "Do not diagnose" in prompt


def test_fake_vision_client_returns_witness_report():
    witness = FakeVisionClient().extract_witness("demo.png")

    assert witness.scene_summary
    assert "blue hallway" in " ".join(witness.to_visual_clues()).lower()
