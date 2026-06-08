# Model-Led Pact V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Dream Customs generate natural English demo cards by letting MiniCPM5-1B own briefing, drafting, and critique while MiniCPM-V-4.6 contributes richer visual witness evidence.

**Architecture:** Keep the public Hugging Face Space and Modal-hosted MiniCPM endpoints unchanged. Add a model-led generation path that builds a structured `DreamBrief`, drafts a `PactCard`, asks the text model to critique and rewrite weak output, and uses deterministic guards only for schema, safety, grammar, and fallback resilience. Upgrade vision output from flat clues to a witness report that still feeds the existing `DreamIntake.visual_clues` fallback path.

**Tech Stack:** Python, Pydantic, Gradio, pytest, MiniCPM5-1B hosted text route, MiniCPM-V-4.6 hosted vision route, existing Modal/HF Space deployment flow.

---

## File Structure

- Modify `dream_customs/schema.py`: add `VisionWitness`, `DreamBrief`, and `PactCritique` models without breaking existing `DreamIntake`, `PactCard`, or `CustomsSession` serialization.
- Modify `dream_customs/prompts.py`: add prompts for visual witness reports, dream briefs, pact drafts, pact critique, and pact rewrite.
- Modify `dream_customs/models.py`: add generic JSON generation methods and optional model-led methods on `FakeTextClient`, `OllamaTextClient`, `HostedMiniCPMTextClient`, `FakeVisionClient`, `OllamaVisionClient`, and `HostedMiniCPMVisionClient`.
- Modify `dream_customs/pipeline.py`: add the model-led pact flow, English grammar guards, and a fallback path that preserves the current text-only demo behavior.
- Modify `dream_customs/app_logic.py` and `dream_customs/ui/actions.py` only if needed to route richer debug data; do not add visible developer jargon to the public mobile flow.
- Create `tests/test_model_led_pact.py`: focused tests for brief, critique, rewrite, grammar cleanup, and the screenshot elevator regression.
- Create `tests/test_vision_witness.py`: focused tests for MiniCPM-V witness parsing and fallback clues.
- Create `tests/fixtures/demo_eval_cases.json`: ten English-demo quality cases used by a local evaluation script.
- Create `scripts/evaluate_demo_quality.py`: deterministic quality checks for the ten demo cases.
- Create `docs/smoke/2026-06-08-model-led-pact-v2-smoke.md`: record local and live Space acceptance evidence after implementation.

## Task 0: Baseline And Branch Hygiene

**Files:**
- Read: `AGENTS.md`
- Read: `PRODUCT.md`
- Read: `docs/spec.md`
- Read: `docs/handoff.md`
- Read: `docs/superpowers/plans/2026-06-08-dream-customs-story-ux-polish.md`
- Verify: git branch and remotes

- [ ] **Step 1: Confirm repository and branch**

Run:

```bash
pwd
git status --short --branch
git remote -v
```

Expected:

```text
/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon
## feature/dream-customs-ui-voice-settings...origin/feature/dream-customs-ui-voice-settings
origin https://github.com/adjcjh777/dream-customs-build-small.git
space https://huggingface.co/spaces/build-small-hackathon/dream-customs
```

- [ ] **Step 2: Sync latest code**

Run:

```bash
git pull
```

Expected:

```text
Already up to date.
```

- [ ] **Step 3: Run baseline tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all existing tests pass before the model-led changes begin.

## Task 1: Add Model-Led Data Contracts

**Files:**
- Modify: `dream_customs/schema.py`
- Modify: `tests/test_schema.py`

- [ ] **Step 1: Add failing schema tests**

Append to `tests/test_schema.py`:

```python
from dream_customs.schema import DreamBrief, PactCritique, VisionWitness


def test_vision_witness_flattens_report_into_demo_clues():
    witness = VisionWitness(
        scene_summary="A hand-drawn elevator panel is stuck on floor 14.",
        objects=["elevator button", "wax"],
        visible_text=["14"],
        spatial_relations=["button below the frozen number"],
        mood_cues=["stuck", "cold"],
        uncertain_details=["whether the floor is a basement"],
        surprising_detail="The buttons look melted rather than broken.",
    )

    clues = witness.to_visual_clues()

    assert clues[0] == "Scene: A hand-drawn elevator panel is stuck on floor 14."
    assert "Object: elevator button" in clues
    assert "Visible text: 14" in clues
    assert "Surprising detail: The buttons look melted rather than broken." in clues


def test_dream_brief_carries_evidence_and_demo_language():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
        safety_flags=[],
        language="en",
    )

    assert brief.language == "en"
    assert "floor 14" in brief.anchors
    assert brief.visual_evidence == ["Visible text: 14"]


def test_pact_critique_flags_template_and_grammar_failures():
    critique = PactCritique(
        passes=False,
        issues=["repeated article", "template fallback"],
        rewrite_instruction="Rewrite in natural English using elevator, wax, and floor 14.",
    )

    assert not critique.passes
    assert "repeated article" in critique.issues
    assert "natural English" in critique.rewrite_instruction
```

- [ ] **Step 2: Run schema tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_schema.py::test_vision_witness_flattens_report_into_demo_clues tests/test_schema.py::test_dream_brief_carries_evidence_and_demo_language tests/test_schema.py::test_pact_critique_flags_template_and_grammar_failures -q
```

Expected: FAIL with import errors for `VisionWitness`, `DreamBrief`, and `PactCritique`.

- [ ] **Step 3: Implement schema models**

Add to `dream_customs/schema.py` after `DreamIntake`:

```python
class VisionWitness(BaseModel):
    scene_summary: str = ""
    objects: list[str] = Field(default_factory=list)
    visible_text: list[str] = Field(default_factory=list)
    spatial_relations: list[str] = Field(default_factory=list)
    mood_cues: list[str] = Field(default_factory=list)
    uncertain_details: list[str] = Field(default_factory=list)
    surprising_detail: str = ""

    def to_visual_clues(self) -> list[str]:
        clues: list[str] = []
        if self.scene_summary.strip():
            clues.append(f"Scene: {self.scene_summary.strip()}")
        for label, values in [
            ("Object", self.objects),
            ("Visible text", self.visible_text),
            ("Spatial relation", self.spatial_relations),
            ("Mood cue", self.mood_cues),
            ("Uncertain detail", self.uncertain_details),
        ]:
            clues.extend(f"{label}: {value.strip()}" for value in values if value.strip())
        if self.surprising_detail.strip():
            clues.append(f"Surprising detail: {self.surprising_detail.strip()}")
        return clues[:12]


class DreamBrief(BaseModel):
    anchors: list[str] = Field(default_factory=list)
    emotional_hypothesis: str = ""
    today_bridge: str = ""
    visual_evidence: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    language: str = "en"


class PactCritique(BaseModel):
    passes: bool = True
    issues: list[str] = Field(default_factory=list)
    rewrite_instruction: str = ""
```

- [ ] **Step 4: Run schema tests and verify pass**

Run:

```bash
.venv/bin/python -m pytest tests/test_schema.py::test_vision_witness_flattens_report_into_demo_clues tests/test_schema.py::test_dream_brief_carries_evidence_and_demo_language tests/test_schema.py::test_pact_critique_flags_template_and_grammar_failures -q
```

Expected: PASS.

- [ ] **Step 5: Commit schema contracts**

Run:

```bash
git add dream_customs/schema.py tests/test_schema.py
git commit -m "feat: add model-led pact schemas"
```

Expected: commit succeeds.

## Task 2: Add English Demo Prompt Contracts

**Files:**
- Modify: `dream_customs/prompts.py`
- Create: `tests/test_model_led_pact.py`
- Create: `tests/test_vision_witness.py`

- [ ] **Step 1: Add failing prompt tests**

Create `tests/test_model_led_pact.py` with:

```python
from dream_customs.pipeline import build_intake
from dream_customs.prompts import dream_brief_prompt, pact_critique_prompt, pact_draft_prompt, pact_rewrite_prompt
from dream_customs.schema import DreamBrief, PactCard, PactCritique


def test_dream_brief_prompt_requires_english_demo_brief():
    intake = build_intake(
        dream_text="I kept missing an elevator. The buttons melted like wax, and floor 14 froze.",
        visual_clues=["Visible text: 14", "Object: melted button"],
        mood="Uneasy",
    )

    prompt = dream_brief_prompt(intake)

    assert "English demo" in prompt
    assert "anchors" in prompt
    assert "visual_evidence" in prompt
    assert "Do not diagnose" in prompt


def test_pact_draft_prompt_uses_brief_not_template_fallback():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
    )

    prompt = pact_draft_prompt(brief, "I want to stop freezing before a task.")

    assert "Write natural English" in prompt
    assert "Use at least two anchors" in prompt
    assert "Do not use template phrases" in prompt
    assert "elevator" in prompt


def test_pact_critique_prompt_checks_screenshot_regression():
    card = PactCard(
        visitor_name="An Elevator",
        permit_id="DREAM20260608-015",
        contraband=["melted buttons", "froze at 14"],
        risk_level="medium: handle gently, without treating it as a warning sign",
        alliance_reading="I am safe, but the wax is sticky and the floor is cold.",
        practical_suggestion="Pick one real task that feels like the an elevator.",
        weird_task="I will try to push the floor button with my hand instead of the lever.",
        bedtime_release="Tonight, the an elevator and the the button are logged.",
    )
    brief = DreamBrief(anchors=["elevator", "melted wax", "floor 14"])

    prompt = pact_critique_prompt(brief, card)

    assert "the an" in prompt
    assert "the the" in prompt
    assert "invented details" in prompt
    assert "natural English" in prompt


def test_pact_rewrite_prompt_uses_critique_instruction():
    card = PactCard(
        visitor_name="An Elevator",
        permit_id="DREAM20260608-015",
        contraband=["melted buttons", "froze at 14"],
        risk_level="medium: handle gently, without treating it as a warning sign",
        alliance_reading="I am safe, but the wax is sticky and the floor is cold.",
        practical_suggestion="Pick one real task that feels like the an elevator.",
        weird_task="I will try to push the floor button with my hand instead of the lever.",
        bedtime_release="Tonight, the an elevator and the the button are logged.",
    )
    brief = DreamBrief(anchors=["elevator", "melted wax", "floor 14"])
    critique = PactCritique(
        passes=False,
        issues=["repeated article", "invented lever"],
        rewrite_instruction="Rewrite without repeated articles or invented lever details.",
    )

    prompt = pact_rewrite_prompt(brief, card, critique)

    assert "Rewrite without repeated articles" in prompt
    assert "Return strict JSON" in prompt
    assert "floor 14" in prompt
```

Create `tests/test_vision_witness.py` with:

```python
from dream_customs.prompts import visual_witness_prompt


def test_visual_witness_prompt_requests_structured_report():
    prompt = visual_witness_prompt()

    assert "MiniCPM-V-4.6" in prompt
    assert "scene_summary" in prompt
    assert "spatial_relations" in prompt
    assert "surprising_detail" in prompt
    assert "Do not diagnose" in prompt
```

- [ ] **Step 2: Run prompt tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py tests/test_vision_witness.py -q
```

Expected: FAIL with import errors for the new prompt functions.

- [ ] **Step 3: Implement new prompt functions**

Add to `dream_customs/prompts.py`:

```python
from dream_customs.schema import DreamBrief, PactCard, PactCritique


def visual_witness_prompt() -> str:
    return """
You are MiniCPM-V-4.6 acting as the witness clerk at Dream Customs.
Read the image as dream evidence: a sketch, bedside note, screenshot, or photo.
Do not diagnose the user. Do not infer a fixed symbolic meaning.
Return strict JSON with:
scene_summary, objects, visible_text, spatial_relations, mood_cues,
uncertain_details, surprising_detail.
Keep each list item short, concrete, and visibly grounded in the image.
""".strip()


def dream_brief_prompt(intake: DreamIntake) -> str:
    return f"""
You are MiniCPM5-1B preparing an English demo brief for Dream Customs.
Do not diagnose. Do not claim the dream has one certain meaning.
Turn the intake into a compact reasoning brief that a later writer can use.
Return strict JSON with:
anchors, emotional_hypothesis, today_bridge, visual_evidence, safety_flags, language.

Rules:
- language must be "en".
- anchors must be concrete dream details, not generic feelings.
- visual_evidence must reuse image clues when present.
- today_bridge must connect the dream to one realistic action for today.
- safety_flags is empty unless the user mentions self-harm, harming others,
  severe distress, severe insomnia, panic, or inability to function.

Dream intake:
{intake.merged_text()}
""".strip()


def pact_draft_prompt(brief: DreamBrief, answers: str) -> str:
    return f"""
You are the Dream Customs diplomat writing an English demo clearance pass.
Write natural English. Keep the tone gentle, playful, and useful.
Do not use template phrases such as "feels like the", "logged and cleared",
or "the dream may be pointing to" unless they fit naturally.
Use at least two anchors from the brief. Use at least one visual_evidence item
when visual evidence is present. Do not invent objects or actions.
Return strict JSON with:
visitor_name, permit_id, contraband, risk_level, alliance_reading,
practical_suggestion, weird_task, bedtime_release, safety_note.

Dream brief:
{brief.model_dump_json()}

User answers:
{answers or "No answers filed."}
""".strip()


def pact_critique_prompt(brief: DreamBrief, card: PactCard) -> str:
    return f"""
You are the Dream Customs quality critic for an English demo card.
Check for repeated articles such as "the an" and "the the", awkward grammar,
template fallback language, invented details, diagnosis, frightening certainty,
generic wellness advice, and missing dream anchors.
Return strict JSON with:
passes, issues, rewrite_instruction.
If the card is already natural, specific, safe, and grounded, passes must be true
and rewrite_instruction must be an empty string.

Dream brief:
{brief.model_dump_json()}

Draft card:
{card.model_dump_json()}
""".strip()


def pact_rewrite_prompt(brief: DreamBrief, card: PactCard, critique: PactCritique) -> str:
    return f"""
You are the Dream Customs diplomat revising an English demo clearance pass.
Follow the critique exactly while preserving safe, playful, non-diagnostic tone.
Use at least two real anchors from the brief. Do not add objects that are not in
the brief or current card. Return strict JSON with:
visitor_name, permit_id, contraband, risk_level, alliance_reading,
practical_suggestion, weird_task, bedtime_release, safety_note.

Dream brief:
{brief.model_dump_json()}

Current card:
{card.model_dump_json()}

Critique:
{critique.model_dump_json()}
""".strip()
```

- [ ] **Step 4: Run prompt tests and verify pass**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py tests/test_vision_witness.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit prompt contracts**

Run:

```bash
git add dream_customs/prompts.py tests/test_model_led_pact.py tests/test_vision_witness.py
git commit -m "feat: add model-led pact prompts"
```

Expected: commit succeeds.

## Task 3: Add Model-Led Client Methods

**Files:**
- Modify: `dream_customs/models.py`
- Modify: `tests/test_ollama_models.py`
- Modify: `tests/test_model_led_pact.py`
- Modify: `tests/test_vision_witness.py`

- [ ] **Step 1: Add failing client tests**

Append to `tests/test_model_led_pact.py`:

```python
from dream_customs.models import FakeTextClient


def test_fake_text_client_supports_model_led_methods():
    client = FakeTextClient()

    brief = client.generate_brief("brief prompt")
    card = client.generate_pact_draft("draft prompt")
    critique = client.critique_pact("critique prompt")

    assert brief.language == "en"
    assert brief.anchors
    assert card.visitor_name
    assert critique.passes
```

Append to `tests/test_vision_witness.py`:

```python
from dream_customs.models import FakeVisionClient


def test_fake_vision_client_returns_witness_report():
    witness = FakeVisionClient().extract_witness("demo.png")

    assert witness.scene_summary
    assert "blue hallway" in " ".join(witness.to_visual_clues()).lower()
```

Append to `tests/test_ollama_models.py`:

```python
from dream_customs.schema import DreamBrief, PactCritique, VisionWitness


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


def test_hosted_text_client_parses_pact_critique():
    class StubHostedCritiqueClient(HostedMiniCPMTextClient):
        def _post_json(self, prompt, max_tokens=700):
            return {
                "response": (
                    '{"passes":false,'
                    '"issues":["repeated article"],'
                    '"rewrite_instruction":"Fix repeated articles."}'
                )
            }

    critique = StubHostedCritiqueClient(endpoint="https://example.test").critique_pact("prompt")

    assert isinstance(critique, PactCritique)
    assert not critique.passes


def test_hosted_vision_client_parses_witness_report():
    class StubHostedVisionWitnessClient(HostedMiniCPMVisionClient):
        def _post_image(self, image_path):
            return {
                "response": (
                    '{"scene_summary":"A blue hallway with a frozen elevator panel.",'
                    '"objects":["elevator button"],'
                    '"visible_text":["14"],'
                    '"spatial_relations":["button below number"],'
                    '"mood_cues":["cold"],'
                    '"uncertain_details":[],' 
                    '"surprising_detail":"The button looks waxy."}'
                )
            }

    witness = StubHostedVisionWitnessClient(endpoint="https://example.test").extract_witness("demo.png")

    assert isinstance(witness, VisionWitness)
    assert "Visible text: 14" in witness.to_visual_clues()
```

- [ ] **Step 2: Run client tests and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py::test_fake_text_client_supports_model_led_methods tests/test_vision_witness.py::test_fake_vision_client_returns_witness_report tests/test_ollama_models.py::test_hosted_text_client_parses_model_led_brief tests/test_ollama_models.py::test_hosted_text_client_parses_pact_critique tests/test_ollama_models.py::test_hosted_vision_client_parses_witness_report -q
```

Expected: FAIL because the client methods are not implemented.

- [ ] **Step 3: Implement fake client methods**

In `dream_customs/models.py`, import the new schemas:

```python
from dream_customs.schema import DreamBrief, PactCard, PactCritique, VisionWitness
```

Add to `FakeTextClient`:

```python
    def generate_brief(self, prompt: str) -> DreamBrief:
        return DreamBrief(
            anchors=["elevator", "melted buttons", "floor 14"],
            emotional_hypothesis="The dream may be protecting the user from freezing at the start of a task.",
            today_bridge="Choose one stalled task and name the next small movement.",
            visual_evidence=["Visible text: 14"],
            safety_flags=[],
            language="en",
        )

    def generate_pact_draft(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)

    def critique_pact(self, prompt: str) -> PactCritique:
        return PactCritique(passes=True, issues=[], rewrite_instruction="")

    def rewrite_pact(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)
```

Add to `FakeVisionClient`:

```python
    def extract_witness(self, image_path: Optional[str]) -> VisionWitness:
        if not image_path:
            return VisionWitness()
        return VisionWitness(
            scene_summary="A blue hallway with a melted elevator button.",
            objects=["elevator button", "blue hallway"],
            visible_text=["14"],
            spatial_relations=["button near the frozen floor number"],
            mood_cues=["stuck", "uncertain"],
            uncertain_details=[],
            surprising_detail="The button looks soft, almost waxy.",
        )
```

- [ ] **Step 4: Implement hosted and Ollama model-led text parsing**

Add helper methods to `HostedMiniCPMTextClient` and mirror the same signatures in `OllamaTextClient`:

```python
    def generate_brief(self, prompt: str) -> DreamBrief:
        parsed = self._generate_json(
            prompt,
            (
                '{"anchors":["string"],"emotional_hypothesis":"string",'
                '"today_bridge":"string","visual_evidence":["string"],'
                '"safety_flags":["string"],"language":"en"}'
            ),
            max_tokens=520,
        )
        if not parsed:
            return self.fallback.generate_brief(prompt)
        try:
            return DreamBrief(
                anchors=_as_string_list(parsed.get("anchors")),
                emotional_hypothesis=str(parsed.get("emotional_hypothesis", "")).strip(),
                today_bridge=str(parsed.get("today_bridge", "")).strip(),
                visual_evidence=_as_string_list(parsed.get("visual_evidence")),
                safety_flags=_as_string_list(parsed.get("safety_flags")),
                language=str(parsed.get("language", "en")).strip() or "en",
            )
        except (TypeError, ValueError):
            return self.fallback.generate_brief(prompt)

    def generate_pact_draft(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)

    def critique_pact(self, prompt: str) -> PactCritique:
        parsed = self._generate_json(
            prompt,
            '{"passes":true,"issues":["string"],"rewrite_instruction":"string"}',
            max_tokens=360,
        )
        if not parsed:
            return self.fallback.critique_pact(prompt)
        return PactCritique(
            passes=bool(parsed.get("passes", True)),
            issues=_as_string_list(parsed.get("issues")),
            rewrite_instruction=str(parsed.get("rewrite_instruction", "")).strip(),
        )

    def rewrite_pact(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)
```

For `OllamaTextClient`, use the same body but pass `num_predict` instead of `max_tokens` in `_generate_json()` calls.

- [ ] **Step 5: Implement hosted and Ollama vision witness parsing**

Add to `HostedMiniCPMVisionClient` and mirror the same method in `OllamaVisionClient`:

```python
    def extract_witness(self, image_path: Optional[str]) -> VisionWitness:
        if not image_path:
            return VisionWitness()
        payload = self._post_image(image_path)
        if not payload:
            return self.fallback.extract_witness(image_path)
        parsed = _extract_json_object(_hosted_text_from_response(payload))
        if not parsed:
            text = _hosted_text_from_response(payload)
            clues = [part.strip() for part in re.split(r"[,，\n]", _strip_markdown_and_thinking(text)) if part.strip()]
            return VisionWitness(scene_summary="; ".join(clues[:2]), objects=clues[2:6])
        return VisionWitness(
            scene_summary=str(parsed.get("scene_summary", "")).strip(),
            objects=_as_string_list(parsed.get("objects")),
            visible_text=_as_string_list(parsed.get("visible_text")),
            spatial_relations=_as_string_list(parsed.get("spatial_relations")),
            mood_cues=_as_string_list(parsed.get("mood_cues")),
            uncertain_details=_as_string_list(parsed.get("uncertain_details")),
            surprising_detail=str(parsed.get("surprising_detail", "")).strip(),
        )
```

Update `extract_clues()` to call `extract_witness(image_path).to_visual_clues()` first, then fall back to the old flat parsing if the witness is empty.

- [ ] **Step 6: Run client tests and verify pass**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py::test_fake_text_client_supports_model_led_methods tests/test_vision_witness.py::test_fake_vision_client_returns_witness_report tests/test_ollama_models.py::test_hosted_text_client_parses_model_led_brief tests/test_ollama_models.py::test_hosted_text_client_parses_pact_critique tests/test_ollama_models.py::test_hosted_vision_client_parses_witness_report -q
```

Expected: PASS.

- [ ] **Step 7: Commit client methods**

Run:

```bash
git add dream_customs/models.py tests/test_model_led_pact.py tests/test_vision_witness.py tests/test_ollama_models.py
git commit -m "feat: add model-led MiniCPM clients"
```

Expected: commit succeeds.

## Task 4: Route The Model-Led Pact Flow

**Files:**
- Modify: `dream_customs/pipeline.py`
- Modify: `tests/test_model_led_pact.py`
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Add failing model-led flow regression**

Append to `tests/test_model_led_pact.py`:

```python
from dream_customs.pipeline import build_intake, generate_model_led_pact


def test_model_led_pact_rewrites_screenshot_elevator_regression():
    class CriticTextClient(FakeTextClient):
        def generate_pact_draft(self, prompt):
            return PactCard(
                visitor_name="An Elevator",
                permit_id="DREAM20260608-015",
                contraband=["melted buttons", "froze at 14"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading="I am safe, but the wax is sticky and the floor is cold.",
                practical_suggestion="Pick one real task that feels like the an elevator.",
                weird_task="I will try to push the floor button with my hand instead of the lever.",
                bedtime_release="Tonight, the an elevator and the the button are logged.",
            )

        def critique_pact(self, prompt):
            return PactCritique(
                passes=False,
                issues=["repeated article", "invented lever"],
                rewrite_instruction="Rewrite without repeated articles or the invented lever.",
            )

        def rewrite_pact(self, prompt):
            return PactCard(
                visitor_name="The Elevator Stuck at 14",
                permit_id="DREAM20260608-015",
                contraband=["melted buttons", "floor 14", "the urge to freeze before starting"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading=(
                    "The elevator, wax-soft buttons, and frozen 14 can be treated as a small scene "
                    "about getting stuck before the first move."
                ),
                practical_suggestion="Choose one stalled task and write only the next button-sized action.",
                weird_task="Draw floor 14 on a sticky note, tap it once, and spend five minutes on the first step.",
                bedtime_release="Tonight, the elevator can stay on floor 14 while tomorrow's first button waits quietly.",
            )

    intake = build_intake(
        dream_text="I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.",
        visual_clues=["Visible text: 14", "Object: melted elevator button"],
        mood="Uneasy",
    )

    card, html = generate_model_led_pact(intake, "", CriticTextClient())
    joined = card.to_plain_text().lower()

    assert "the an" not in joined
    assert "the the" not in joined
    assert "lever" not in joined
    assert "floor 14" in joined
    assert "melted" in joined or "wax" in joined
    assert "Today's Clearance Pass" in html or "Today's Pact" in html
```

- [ ] **Step 2: Run model-led flow test and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py::test_model_led_pact_rewrites_screenshot_elevator_regression -q
```

Expected: FAIL because `generate_model_led_pact` does not exist.

- [ ] **Step 3: Implement grammar guard helpers**

Add to `dream_customs/pipeline.py`:

```python
def _clean_repeated_articles(text: str) -> str:
    clean = re.sub(r"\bthe\s+an\s+", "an ", text, flags=re.IGNORECASE)
    clean = re.sub(r"\bthe\s+the\s+", "the ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ban\s+an\s+", "an ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ba\s+a\s+", "a ", clean, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", clean).strip()


def _clean_card_grammar(card: PactCard) -> PactCard:
    cleaned = card.model_copy(deep=True)
    cleaned.visitor_name = _clean_repeated_articles(cleaned.visitor_name)
    cleaned.risk_level = _clean_repeated_articles(cleaned.risk_level)
    cleaned.alliance_reading = _clean_repeated_articles(cleaned.alliance_reading)
    cleaned.practical_suggestion = _clean_repeated_articles(cleaned.practical_suggestion)
    cleaned.weird_task = _clean_repeated_articles(cleaned.weird_task)
    cleaned.bedtime_release = _clean_repeated_articles(cleaned.bedtime_release)
    cleaned.contraband = [_clean_repeated_articles(item) for item in cleaned.contraband]
    return cleaned
```

- [ ] **Step 4: Implement `generate_model_led_pact`**

Add imports to `dream_customs/pipeline.py`:

```python
from dream_customs.prompts import (
    dream_brief_prompt,
    followup_question_prompt,
    negotiation_prompt,
    pact_critique_prompt,
    pact_draft_prompt,
    pact_prompt,
    pact_revision_prompt,
    pact_rewrite_prompt,
)
```

Add the function:

```python
def generate_model_led_pact(intake: DreamIntake, answers: str, text_client) -> Tuple[PactCard, str]:
    brief = text_client.generate_brief(dream_brief_prompt(intake))
    card = text_client.generate_pact_draft(pact_draft_prompt(brief, answers))
    critique = text_client.critique_pact(pact_critique_prompt(brief, card))
    if not critique.passes and critique.rewrite_instruction.strip():
        card = text_client.rewrite_pact(pact_rewrite_prompt(brief, card, critique))
    card = _clean_card_grammar(card)
    card = _polish_card_for_daily_use(card, intake, answers)
    merged = intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    elif not needs_escalation(merged):
        card.safety_note = ""
    card = _stamp_card_for_today(card)
    return card, render_pact_card(card)
```

- [ ] **Step 5: Route draft generation through model-led flow with fallback**

Find the existing `draft_pact()` code path in `dream_customs/pipeline.py`. Replace its direct `generate_pact()` call with:

```python
    try:
        card, _html = generate_model_led_pact(next_session.intake, next_session.answers_text(), text_client)
    except AttributeError:
        card, _html = generate_pact(next_session.intake, next_session.answers_text(), text_client)
```

Keep the existing session phase, events, and safety behavior unchanged around this block.

- [ ] **Step 6: Run focused flow tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_model_led_pact.py::test_model_led_pact_rewrites_screenshot_elevator_regression tests/test_pipeline.py::test_ask_answer_skip_draft_revise_and_seal_actions -q
```

Expected: PASS.

- [ ] **Step 7: Run all pipeline tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_pipeline.py tests/test_model_led_pact.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit model-led flow**

Run:

```bash
git add dream_customs/pipeline.py tests/test_model_led_pact.py tests/test_pipeline.py
git commit -m "feat: route model-led pact generation"
```

Expected: commit succeeds.

## Task 5: Upgrade Vision Intake To Witness Reports

**Files:**
- Modify: `dream_customs/pipeline.py`
- Modify: `dream_customs/models.py`
- Modify: `tests/test_vision_witness.py`
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Add failing intake witness test**

Append to `tests/test_vision_witness.py`:

```python
from dream_customs.models import FakeASRClient, FakeVisionClient
from dream_customs.pipeline import intake_from_modalities


def test_intake_from_modalities_uses_vision_witness_clues():
    intake = intake_from_modalities(
        dream_text="I was waiting for an elevator.",
        image_path="demo.png",
        audio_path=None,
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    merged = intake.merged_text().lower()

    assert "scene:" in merged
    assert "visible text: 14" in merged
    assert "surprising detail" in merged
```

- [ ] **Step 2: Run witness intake test and verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_vision_witness.py::test_intake_from_modalities_uses_vision_witness_clues -q
```

Expected: FAIL if `intake_from_modalities()` still calls only `extract_clues()`.

- [ ] **Step 3: Add witness extraction helper**

Add to `dream_customs/pipeline.py`:

```python
def _extract_visual_clues(vision_client, image_path: Optional[str]) -> List[str]:
    if not image_path:
        return []
    try:
        if hasattr(vision_client, "extract_witness"):
            witness = vision_client.extract_witness(image_path)
            clues = witness.to_visual_clues()
            if clues:
                return clues
    except Exception:
        pass
    try:
        return vision_client.extract_clues(image_path)
    except Exception:
        return []
```

Update `intake_from_modalities()`:

```python
    return build_intake(
        dream_text=dream_text or "",
        voice_transcript=asr_client.transcribe(audio_path),
        visual_clues=_extract_visual_clues(vision_client, image_path),
        mood=mood or "",
        user_context=user_context,
    )
```

- [ ] **Step 4: Keep text path alive when witness extraction fails**

Append to `tests/test_pipeline.py`:

```python
def test_witness_failure_keeps_text_path_alive():
    class BrokenWitnessVision:
        def extract_witness(self, image_path):
            raise RuntimeError("vision offline")

        def extract_clues(self, image_path):
            return ["fallback clue"]

    intake = intake_from_modalities(
        dream_text="Text still works.",
        image_path="demo.png",
        audio_path=None,
        mood="Foggy",
        vision_client=BrokenWitnessVision(),
        asr_client=FakeASRClient(),
    )

    assert "Text still works." in intake.merged_text()
    assert "fallback clue" in intake.merged_text()
```

- [ ] **Step 5: Run vision tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_vision_witness.py tests/test_pipeline.py::test_witness_failure_keeps_text_path_alive -q
```

Expected: PASS.

- [ ] **Step 6: Commit witness routing**

Run:

```bash
git add dream_customs/pipeline.py dream_customs/models.py tests/test_vision_witness.py tests/test_pipeline.py
git commit -m "feat: use MiniCPM vision witness reports"
```

Expected: commit succeeds.

## Task 6: Add English Demo Quality Evaluation

**Files:**
- Create: `tests/fixtures/demo_eval_cases.json`
- Create: `scripts/evaluate_demo_quality.py`
- Create: `tests/test_demo_quality_eval.py`

- [ ] **Step 1: Add demo fixture cases**

Create `tests/fixtures/demo_eval_cases.json`:

```json
[
  {
    "id": "elevator_wax_floor14",
    "dream_text": "I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.",
    "visual_clues": ["Visible text: 14", "Object: melted elevator button"],
    "mood": "Uneasy",
    "required_terms": ["elevator", "14"],
    "banned_terms": ["the an", "the the", "lever", "diagnosis"]
  },
  {
    "id": "customs_wet_paper",
    "dream_text": "I was at a customs window carrying a suitcase full of wet paper. The clerk asked me to declare every unfinished promise before sunrise.",
    "visual_clues": [],
    "mood": "Foggy",
    "required_terms": ["customs", "paper"],
    "banned_terms": ["hydrate", "fruit", "prophecy", "diagnosis"]
  },
  {
    "id": "exam_without_pencil",
    "dream_text": "I arrived at an exam with no pencil, but everyone else was already writing.",
    "visual_clues": [],
    "mood": "Restless",
    "required_terms": ["exam", "pencil"],
    "banned_terms": ["medical", "fate", "the an"]
  },
  {
    "id": "locked_green_room",
    "dream_text": "I found a small green room behind my kitchen, but the door kept locking itself.",
    "visual_clues": ["Color: green", "Object: small door"],
    "mood": "Curious",
    "required_terms": ["green", "door"],
    "banned_terms": ["diagnosis", "warning sign", "the the"]
  },
  {
    "id": "train_arrives_silent",
    "dream_text": "A silent train arrived with my name written on a ticket, but I could not read the destination.",
    "visual_clues": ["Visible text: user name on ticket"],
    "mood": "Uneasy",
    "required_terms": ["train", "ticket"],
    "banned_terms": ["destiny", "prophecy", "the an"]
  },
  {
    "id": "phone_full_of_water",
    "dream_text": "My phone was full of water, but it kept ringing from inside a drawer.",
    "visual_clues": [],
    "mood": "Tired",
    "required_terms": ["phone", "water"],
    "banned_terms": ["hydration", "diagnosis", "the the"]
  },
  {
    "id": "missing_shoes_stairwell",
    "dream_text": "I was in a stairwell without shoes, holding a map that only showed blank squares.",
    "visual_clues": ["Object: blank map", "Place: stairwell"],
    "mood": "Foggy",
    "required_terms": ["stairwell", "map"],
    "banned_terms": ["fate", "medical", "the an"]
  },
  {
    "id": "bedside_note_rain",
    "dream_text": "A note on my bedside table said 'bring the rain inside', and the window was already open.",
    "visual_clues": ["Visible text: bring the rain inside", "Object: open window"],
    "mood": "Calm",
    "required_terms": ["rain", "window"],
    "banned_terms": ["diagnosis", "prophecy", "the the"]
  },
  {
    "id": "voice_fragment_buttons",
    "dream_text": "",
    "voice_transcript": "The hallway was blue, and the elevator buttons were warm.",
    "visual_clues": ["Color: blue"],
    "mood": "Uneasy",
    "required_terms": ["hallway", "buttons"],
    "banned_terms": ["the an", "the the", "diagnosis"]
  },
  {
    "id": "abstract_sketch_moon_key",
    "dream_text": "I drew the dream because I only remember a moon-shaped key and a red square.",
    "visual_clues": ["Object: moon-shaped key", "Color: red square"],
    "mood": "Curious",
    "required_terms": ["key", "red"],
    "banned_terms": ["medical", "fate", "the an"]
  }
]
```

- [ ] **Step 2: Add evaluator tests**

Create `tests/test_demo_quality_eval.py`:

```python
from scripts.evaluate_demo_quality import evaluate_text


def test_evaluate_text_passes_grounded_english_card():
    text = (
        "The Elevator Stuck at 14. The melted buttons and frozen floor 14 can stand for "
        "one stalled beginning. Choose one task and write the next button-sized action."
    )

    result = evaluate_text(text, required_terms=["elevator", "14"], banned_terms=["the an", "the the"])

    assert result["passes"]
    assert result["issues"] == []


def test_evaluate_text_fails_repeated_articles_and_missing_anchor():
    text = "Pick one real task that feels like the an elevator."

    result = evaluate_text(text, required_terms=["floor 14"], banned_terms=["the an"])

    assert not result["passes"]
    assert "banned term: the an" in result["issues"]
    assert "missing required term: floor 14" in result["issues"]
```

- [ ] **Step 3: Implement evaluator script**

Create `scripts/evaluate_demo_quality.py`:

```python
import json
from pathlib import Path
from typing import Iterable


def evaluate_text(text: str, required_terms: Iterable[str], banned_terms: Iterable[str]) -> dict:
    lowered = text.lower()
    issues: list[str] = []
    for term in required_terms:
        if term.lower() not in lowered:
            issues.append(f"missing required term: {term}")
    for term in banned_terms:
        if term.lower() in lowered:
            issues.append(f"banned term: {term}")
    if any(marker in lowered for marker in ["you have depression", "this means you will", "certainly predicts"]):
        issues.append("unsafe certainty or diagnosis")
    return {"passes": not issues, "issues": issues}


def load_cases(path: str = "tests/fixtures/demo_eval_cases.json") -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    cases = load_cases()
    print(json.dumps({"case_count": len(cases), "ids": [case["id"] for case in cases]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run evaluator tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_demo_quality_eval.py -q
.venv/bin/python scripts/evaluate_demo_quality.py
```

Expected: pytest PASS; script prints `case_count` as `10`.

- [ ] **Step 5: Commit evaluator**

Run:

```bash
git add tests/fixtures/demo_eval_cases.json scripts/evaluate_demo_quality.py tests/test_demo_quality_eval.py
git commit -m "test: add english demo quality eval cases"
```

Expected: commit succeeds.

## Task 7: Full Verification, Local Smoke, And HF Space Sync

**Files:**
- Verify: all modified files
- Create: `docs/smoke/2026-06-08-model-led-pact-v2-smoke.md`

- [ ] **Step 1: Run full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 3: Run local app smoke**

Run:

```bash
GRADIO_SERVER_PORT=7862 .venv/bin/python app.py
```

Open `http://127.0.0.1:7862` and submit:

```text
I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.
```

Attach an image only if a local sketch is available. Seal the pass and verify:

- The card is in polished English.
- The card does not contain `the an`, `the the`, or invented `lever`.
- The card mentions at least two of `elevator`, `melted buttons`, `wax`, and `floor 14`.
- The practical suggestion is one real next step for today.
- The weird task is playful, harmless, and grounded in the elevator or floor-14 image.
- Mobile width remains readable.

- [ ] **Step 4: Record smoke evidence**

Create `docs/smoke/2026-06-08-model-led-pact-v2-smoke.md`:

```markdown
# Model-Led Pact V2 Smoke

Date: 2026-06-08
Branch: feature/dream-customs-ui-voice-settings

## Local

- Command: `.venv/bin/python -m pytest -q`
- Result: PASS
- Command: `git diff --check`
- Result: PASS
- Command: `GRADIO_SERVER_PORT=7862 .venv/bin/python app.py`
- Result: PASS

## Manual Demo Case

Input:

```text
I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.
```

Acceptance:

- Natural English card: PASS
- No repeated article regression: PASS
- No invented lever detail: PASS
- Uses at least two dream details: PASS
- Practical suggestion is actionable: PASS
- Weird task is harmless and dream-grounded: PASS
- Mobile readable: PASS

## Hugging Face Space

- Push target checked: `space https://huggingface.co/spaces/build-small-hackathon/dream-customs`
- Live Space config checked:
- Live Space manual case checked:
- Notes:
```

- [ ] **Step 5: Commit smoke doc**

Run:

```bash
git add docs/smoke/2026-06-08-model-led-pact-v2-smoke.md
git commit -m "docs: record model-led pact smoke"
```

Expected: commit succeeds.

- [ ] **Step 6: Push GitHub branch**

Run:

```bash
git push origin feature/dream-customs-ui-voice-settings
```

Expected: push succeeds.

- [ ] **Step 7: Sync Hugging Face Space**

Before pushing, verify the remote:

```bash
git remote -v | grep '^space'
```

Expected:

```text
space https://huggingface.co/spaces/build-small-hackathon/dream-customs (fetch)
space https://huggingface.co/spaces/build-small-hackathon/dream-customs (push)
```

Then push or create a Space PR according to the current auth state. If the operation requires a token, secret value, billing confirmation, force push to public `main`, or manual PR merge, stop and ask the user with the exact blocker. Do not print or save tokens.

## Self-Review

- Spec coverage: The plan covers English demo quality, MiniCPM5 brief/draft/critique/rewrite, MiniCPM-V witness reports, screenshot elevator regression, fallback resilience, local tests, local smoke, and HF Space sync.
- Placeholder scan: No unresolved placeholder strings are present in the task instructions.
- Type consistency: `VisionWitness`, `DreamBrief`, `PactCritique`, and `PactCard` names are used consistently across schema, prompts, clients, pipeline, and tests.
- Scope check: The plan is one coherent generation-quality pass. It does not redesign the UI, change Modal deployment architecture, or broaden beyond the MiniCPM family.
