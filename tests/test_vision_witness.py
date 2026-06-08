from dream_customs.prompts import visual_witness_prompt


def test_visual_witness_prompt_requests_structured_report():
    prompt = visual_witness_prompt()

    assert "MiniCPM-V-4.6" in prompt
    assert "scene_summary" in prompt
    assert "spatial_relations" in prompt
    assert "surprising_detail" in prompt
    assert "Do not diagnose" in prompt
