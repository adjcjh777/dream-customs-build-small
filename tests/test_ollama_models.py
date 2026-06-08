from dream_customs.models import (
    HostedMiniCPMTextClient,
    HostedMiniCPMVisionClient,
    OllamaTextClient,
    OllamaVisionClient,
    _extract_json_object,
)
from dream_customs.schema import DreamBrief, PactCritique, VisionWitness


class StubOllamaTextClient(OllamaTextClient):
    def __init__(self, response_text: str):
        super().__init__()
        self.response_text = response_text

    def _post_generate(self, prompt: str, num_predict: int = 512):
        return {"response": self.response_text}


class StubOllamaVisionClient(OllamaVisionClient):
    def __init__(self, response_text: str):
        super().__init__()
        self.response_text = response_text

    def _post_generate(self, prompt: str, image_b64: str, num_predict: int = 256):
        return {"response": self.response_text}


class StubHostedTextClient(HostedMiniCPMTextClient):
    def __init__(self, payload):
        super().__init__(endpoint="https://example.invalid")
        self.payload = payload

    def _post_json(self, prompt: str, max_tokens: int = 700):
        return self.payload


def test_extract_json_object_handles_code_fence():
    parsed = _extract_json_object('```json\n{"visitor_name": "Gate 14"}\n```')
    assert parsed == {"visitor_name": "Gate 14"}


def test_ollama_text_client_parses_negotiation_json():
    client = StubOllamaTextClient(
        '{"visitor_name":"迟到的电梯","questions":["它要什么？","你要什么？"],"tone_note":"温和一点"}'
    )
    negotiation = client.generate_negotiation("梦见电梯")
    assert negotiation["visitor_name"] == "迟到的电梯"
    assert negotiation["questions"] == ["它要什么？", "你要什么？"]


def test_ollama_text_client_falls_back_on_empty_json():
    client = StubOllamaTextClient("{}")
    negotiation = client.generate_negotiation("梦见电梯")
    assert negotiation["visitor_name"]
    assert len(negotiation["questions"]) == 3


def test_ollama_text_client_parses_pact_card():
    client = StubOllamaTextClient(
        """
        {
          "visitor_name":"迟到的电梯",
          "permit_id":"DC-42",
          "contraband":["未申报的焦虑"],
          "risk_level":"yellow",
          "alliance_reading":"先开始，不急着完成。",
          "practical_suggestion":"打开一个 5 分钟任务。",
          "weird_task":"给电梯盖章。",
          "bedtime_release":"今日放行。",
          "safety_note":""
        }
        """
    )
    card = client.generate_pact("梦见电梯")
    assert card.permit_id == "DC-42"
    assert card.contraband == ["未申报的焦虑"]


def test_ollama_vision_client_parses_visual_clues(tmp_path):
    image_path = tmp_path / "dream.png"
    image_path.write_bytes(b"not a real png but enough for adapter encoding")
    client = StubOllamaVisionClient(
        '{"objects":["passport stamp"],"places":["customs desk"],"colors":["blue"],"mood_cues":["foggy"]}'
    )
    clues = client.extract_clues(str(image_path))
    assert clues == ["passport stamp", "customs desk", "blue", "foggy"]


def test_hosted_text_client_parses_common_response_shape():
    client = StubHostedTextClient(
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"visitor_name":"Gate 14","questions":["What does it ask?"],'
                            '"tone_note":"Keep it small."}'
                        )
                    }
                }
            ]
        }
    )
    negotiation = client.generate_negotiation("dream")
    assert negotiation["visitor_name"] == "Gate 14"
    assert negotiation["questions"] == ["What does it ask?"]


def test_hosted_text_client_parses_model_led_brief():
    class StubHostedBriefClient(HostedMiniCPMTextClient):
        def _post_json(self, prompt, max_tokens=700):
            return {
                "response": (
                    '{"anchors":["elevator","melted wax","floor 14"],'
                    '"emotional_hypothesis":"The dream may be protecting a stuck feeling.",'
                    '"today_bridge":"Name one next movement.",'
                    '"visual_evidence":["Visible text: 14"],'
                    '"safety_flags":[],"language":"en"}'
                )
            }

    brief = StubHostedBriefClient(endpoint="https://example.test").generate_brief("prompt")

    assert isinstance(brief, DreamBrief)
    assert brief.anchors == ["elevator", "melted wax", "floor 14"]
    assert brief.language == "en"


def test_hosted_text_client_parses_pact_critique():
    class StubHostedCritiqueClient(HostedMiniCPMTextClient):
        def _post_json(self, prompt, max_tokens=700):
            return {
                "response": (
                    '{"passes":false,'
                    '"issues":["repeated article","missing floor 14"],'
                    '"rewrite_instruction":"Rewrite with elevator, wax, and floor 14."}'
                )
            }

    critique = StubHostedCritiqueClient(endpoint="https://example.test").critique_pact("prompt")

    assert isinstance(critique, PactCritique)
    assert not critique.passes
    assert critique.issues == ["repeated article", "missing floor 14"]
    assert "floor 14" in critique.rewrite_instruction


def test_hosted_vision_client_parses_witness_report():
    class StubHostedVisionWitnessClient(HostedMiniCPMVisionClient):
        def _post_image(self, image_path):
            return {
                "response": (
                    '{"scene_summary":"A blue hallway ends at a stuck elevator.",'
                    '"objects":["elevator button","melted wax"],'
                    '"visible_text":["14"],'
                    '"spatial_relations":["button below frozen floor number"],'
                    '"mood_cues":["stuck","cold"],'
                    '"uncertain_details":["whether the wax is real"],'
                    '"surprising_detail":"The button looks melted rather than broken."}'
                )
            }

    witness = StubHostedVisionWitnessClient(endpoint="https://example.test").extract_witness("demo.png")

    assert isinstance(witness, VisionWitness)
    assert witness.scene_summary == "A blue hallway ends at a stuck elevator."
    assert "Visible text: 14" in witness.to_visual_clues()
