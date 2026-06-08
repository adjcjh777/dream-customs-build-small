# Dream Customs MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Gradio MVP for Dream Customs that accepts text, image, and voice dream declarations and returns a playful, safe "Today's Pact" card powered primarily by MiniCPM5-1B plus MiniCPM-V-4.6.

**Architecture:** The app normalizes all modalities into a `DreamIntake` schema, then runs a two-stage pipeline: dream visitor negotiation and final pact generation. The MVP starts with mocked model clients and deterministic tests, then swaps in MiniCPM inference wrappers after core behavior is stable.

**Tech Stack:** Python, Gradio, pytest, Pydantic or dataclasses, Hugging Face Transformers or compatible inference endpoints, MiniCPM-V-4.6, MiniCPM5-1B, small ASR adapter.

---

## Execution Status 2026-06-05

- [x] Project scaffold, README, package marker, pytest path hook.
- [x] `DreamIntake` and `PactCard` schemas.
- [x] Safety layer with escalation copy for severe distress.
- [x] Prompt templates for visual clue extraction, negotiation, and pact generation.
- [x] HTML pact card renderer.
- [x] Fake model clients and deterministic pipeline.
- [x] Ollama adapters for MiniCPM5 text and MiniCPM-V vision, kept optional.
- [x] Gradio app with text, image, voice inputs and backend selectors.
- [x] Local smoke checks: pytest, app import, `get_api_info`, HTTP 200, `/config`, `/api/predict`.
- [x] Local Ollama pull: `hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0` and `openbmb/minicpm-v4.6`.
- [ ] Submission packaging, demo video script, and final material checklist.

Implementation note: detailed steps below are the original TDD plan. The final code keeps the demo backend as default because local Ollama smoke tests showed MiniCPM5 GGUF returning malformed output and MiniCPM-V failing to load in the current Ollama runner.

---

## File Structure

- Create `app.py`: Gradio UI and event handlers.
- Create `requirements.txt`: Space dependencies.
- Create `README.md`: project overview, model constraints, running instructions.
- Create `dream_customs/__init__.py`: package marker.
- Create `dream_customs/schema.py`: input and output data models.
- Create `dream_customs/prompts.py`: prompt templates and formatting helpers.
- Create `dream_customs/safety.py`: safety checks and escalation copy.
- Create `dream_customs/render.py`: HTML card rendering.
- Create `dream_customs/models.py`: model wrapper interfaces, fake clients, and later real model adapters.
- Create `dream_customs/pipeline.py`: orchestration from inputs to final card.
- Create `tests/test_schema.py`: schema tests.
- Create `tests/test_safety.py`: safety tests.
- Create `tests/test_render.py`: render tests.
- Create `tests/test_pipeline.py`: pipeline tests with fake clients.

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `dream_customs/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create dependency file**

Write `requirements.txt`:

```text
gradio>=5.0
pydantic>=2.7
pytest>=8.0
transformers>=4.56
torch
pillow
soundfile
```

- [ ] **Step 2: Create README**

Write `README.md`:

````markdown
# Dream Customs / 梦境海关

A Build Small Hackathon Gradio app that helps users form a playful alliance with last night's dream.

## Models

- MiniCPM-V-4.6 for image/sketch understanding.
- MiniCPM5-1B for dream negotiation and pact generation.
- A small ASR adapter may be used only for voice transcription.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, small actions, and escalation copy for severe distress.
````

- [ ] **Step 3: Create package marker**

Write `dream_customs/__init__.py`:

```python
"""Dream Customs package."""
```

- [ ] **Step 4: Create pytest config hook**

Write `tests/conftest.py`:

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

- [ ] **Step 5: Run scaffold check**

Run:

```bash
python -m pytest -q
```

Expected:

```text
no tests ran
```

- [ ] **Step 6: Commit scaffold**

```bash
git add requirements.txt README.md dream_customs/__init__.py tests/conftest.py
git commit -m "feat: scaffold dream customs app"
```

## Task 2: Data Schemas

**Files:**
- Create: `dream_customs/schema.py`
- Create: `tests/test_schema.py`

- [ ] **Step 1: Write failing schema tests**

Write `tests/test_schema.py`:

```python
from dream_customs.schema import DreamIntake, PactCard


def test_dream_intake_defaults_lists():
    intake = DreamIntake(dream_text="I missed an elevator.")
    assert intake.dream_text == "I missed an elevator."
    assert intake.visual_clues == []
    assert intake.recurring_symbols == []


def test_pact_card_requires_core_fields():
    card = PactCard(
        visitor_name="Late Elevator",
        permit_id="DC-0001",
        contraband=["unfiled anxiety"],
        risk_level="orange",
        alliance_reading="The dream asks for a smaller start.",
        practical_suggestion="Open one task ten minutes early.",
        weird_task="Write the elevator an apology note.",
        bedtime_release="Today the elevator has docked.",
    )
    assert card.safety_note == ""
    assert "Late Elevator" in card.to_plain_text()
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
python -m pytest tests/test_schema.py -q
```

Expected: FAIL with `ModuleNotFoundError` or missing model classes.

- [ ] **Step 3: Implement schemas**

Write `dream_customs/schema.py`:

```python
from pydantic import BaseModel, Field


class DreamIntake(BaseModel):
    dream_text: str = ""
    voice_transcript: str = ""
    visual_clues: list[str] = Field(default_factory=list)
    mood: str = ""
    recurring_symbols: list[str] = Field(default_factory=list)
    uncertainty: str = ""
    user_context: str = ""

    def merged_text(self) -> str:
        parts = [
            self.dream_text.strip(),
            self.voice_transcript.strip(),
            "Visual clues: " + ", ".join(self.visual_clues) if self.visual_clues else "",
            "Mood: " + self.mood.strip() if self.mood else "",
            "Recurring symbols: " + ", ".join(self.recurring_symbols) if self.recurring_symbols else "",
            "Uncertainty: " + self.uncertainty.strip() if self.uncertainty else "",
            "Context: " + self.user_context.strip() if self.user_context else "",
        ]
        return "\n".join(part for part in parts if part)


class PactCard(BaseModel):
    visitor_name: str
    permit_id: str
    contraband: list[str]
    risk_level: str
    alliance_reading: str
    practical_suggestion: str
    weird_task: str
    bedtime_release: str
    safety_note: str = ""

    def to_plain_text(self) -> str:
        contraband = ", ".join(self.contraband)
        lines = [
            f"Dream visitor: {self.visitor_name}",
            f"Permit: {self.permit_id}",
            f"Contraband: {contraband}",
            f"Risk level: {self.risk_level}",
            f"Alliance reading: {self.alliance_reading}",
            f"Today's suggestion: {self.practical_suggestion}",
            f"Weird task: {self.weird_task}",
            f"Bedtime release: {self.bedtime_release}",
        ]
        if self.safety_note:
            lines.append(f"Safety note: {self.safety_note}")
        return "\n".join(lines)
```

- [ ] **Step 4: Run schema tests**

Run:

```bash
python -m pytest tests/test_schema.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit schemas**

```bash
git add dream_customs/schema.py tests/test_schema.py
git commit -m "feat: add dream customs schemas"
```

## Task 3: Safety Layer

**Files:**
- Create: `dream_customs/safety.py`
- Create: `tests/test_safety.py`

- [ ] **Step 1: Write failing safety tests**

Write `tests/test_safety.py`:

```python
from dream_customs.safety import needs_escalation, safety_note


def test_ordinary_dream_does_not_escalate():
    assert not needs_escalation("I dreamed about a strange elevator.")


def test_self_harm_text_escalates():
    assert needs_escalation("I might hurt myself if I cannot sleep.")


def test_safety_note_mentions_professional_support():
    assert "professional support" in safety_note().lower()
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
python -m pytest tests/test_safety.py -q
```

Expected: FAIL with missing module or functions.

- [ ] **Step 3: Implement safety functions**

Write `dream_customs/safety.py`:

```python
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
    "伤害别人",
    "很多天睡不着",
    "无法正常生活",
)


def needs_escalation(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ESCALATION_TERMS)


def safety_note() -> str:
    return (
        "This dream sounds heavier than a playful customs ritual should handle. "
        "If you feel unsafe, cannot sleep for many nights, or worry you may hurt "
        "yourself or someone else, please reach out to a trusted person or professional support now."
    )
```

- [ ] **Step 4: Run safety tests**

Run:

```bash
python -m pytest tests/test_safety.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit safety layer**

```bash
git add dream_customs/safety.py tests/test_safety.py
git commit -m "feat: add dream customs safety layer"
```

## Task 4: Prompt Templates

**Files:**
- Create: `dream_customs/prompts.py`

- [ ] **Step 1: Create prompt module**

Write `dream_customs/prompts.py`:

```python
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

Dream intake:
{intake.merged_text()}

User answers:
{answers}

Return strict JSON with:
visitor_name, permit_id, contraband, risk_level, alliance_reading,
practical_suggestion, weird_task, bedtime_release, safety_note.
""".strip()
```

- [ ] **Step 2: Commit prompts**

```bash
git add dream_customs/prompts.py
git commit -m "feat: add dream customs prompts"
```

## Task 5: HTML Renderer

**Files:**
- Create: `dream_customs/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write failing render tests**

Write `tests/test_render.py`:

```python
from dream_customs.render import render_pact_card
from dream_customs.schema import PactCard


def test_render_pact_card_contains_core_fields():
    html = render_pact_card(
        PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-1",
            contraband=["unfiled anxiety"],
            risk_level="orange",
            alliance_reading="The dream asks for a smaller start.",
            practical_suggestion="Open one task ten minutes early.",
            weird_task="Write the elevator an apology note.",
            bedtime_release="Today the elevator has docked.",
        )
    )
    assert "Late Elevator" in html
    assert "Today's Pact" in html
    assert "<script" not in html.lower()
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
python -m pytest tests/test_render.py -q
```

Expected: FAIL with missing renderer.

- [ ] **Step 3: Implement renderer**

Write `dream_customs/render.py`:

```python
from html import escape

from dream_customs.schema import PactCard


def render_pact_card(card: PactCard) -> str:
    contraband = "".join(f"<li>{escape(item)}</li>" for item in card.contraband)
    safety = f"<p class='safety'>{escape(card.safety_note)}</p>" if card.safety_note else ""
    return f"""
<section class="pact-card">
  <div class="pact-header">
    <span>Dream Customs</span>
    <span>{escape(card.permit_id)}</span>
  </div>
  <h2>Today's Pact</h2>
  <h3>{escape(card.visitor_name)}</h3>
  <p><strong>Risk:</strong> {escape(card.risk_level)}</p>
  <p><strong>Alliance:</strong> {escape(card.alliance_reading)}</p>
  <p><strong>Suggestion:</strong> {escape(card.practical_suggestion)}</p>
  <p><strong>Weird task:</strong> {escape(card.weird_task)}</p>
  <p><strong>Bedtime release:</strong> {escape(card.bedtime_release)}</p>
  <div><strong>Contraband</strong><ul>{contraband}</ul></div>
  {safety}
</section>
""".strip()
```

- [ ] **Step 4: Run render tests**

Run:

```bash
python -m pytest tests/test_render.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit renderer**

```bash
git add dream_customs/render.py tests/test_render.py
git commit -m "feat: render dream pact card"
```

## Task 6: Fake Model Clients And Pipeline

**Files:**
- Create: `dream_customs/models.py`
- Create: `dream_customs/pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing pipeline tests**

Write `tests/test_pipeline.py`:

```python
from dream_customs.models import FakeTextClient, FakeVisionClient
from dream_customs.pipeline import build_intake, generate_pact


def test_build_intake_merges_modalities():
    intake = build_intake(
        dream_text="I missed an elevator.",
        voice_transcript="The buttons melted.",
        visual_clues=["blue hallway"],
        mood="anxious",
    )
    assert "elevator" in intake.merged_text()
    assert "blue hallway" in intake.merged_text()


def test_generate_pact_returns_card_and_html():
    intake = build_intake(dream_text="I missed an elevator.", mood="anxious")
    card, html = generate_pact(intake, "I want a small start.", FakeTextClient())
    assert card.visitor_name
    assert "Today's Pact" in html
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
python -m pytest tests/test_pipeline.py -q
```

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement fake model clients**

Write `dream_customs/models.py`:

```python
from dream_customs.schema import PactCard


class FakeVisionClient:
    def extract_clues(self, image_path: str | None) -> list[str]:
        if not image_path:
            return []
        return ["blue hallway", "melted elevator buttons", "number 14"]


class FakeTextClient:
    def generate_pact(self, prompt: str) -> PactCard:
        return PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-DEMO-014",
            contraband=["unfiled anxiety", "melted buttons"],
            risk_level="orange: needs placement, not fear",
            alliance_reading="This visitor asks you to separate starting from finishing.",
            practical_suggestion="Open one small task ten minutes early.",
            weird_task="Write the elevator a one-sentence apology note.",
            bedtime_release="Today the elevator has docked; unfinished floors report tomorrow.",
        )
```

- [ ] **Step 4: Implement pipeline**

Write `dream_customs/pipeline.py`:

```python
from dream_customs.prompts import pact_prompt
from dream_customs.render import render_pact_card
from dream_customs.safety import needs_escalation, safety_note
from dream_customs.schema import DreamIntake, PactCard


def build_intake(
    dream_text: str = "",
    voice_transcript: str = "",
    visual_clues: list[str] | None = None,
    mood: str = "",
    recurring_symbols: list[str] | None = None,
    uncertainty: str = "",
    user_context: str = "",
) -> DreamIntake:
    return DreamIntake(
        dream_text=dream_text,
        voice_transcript=voice_transcript,
        visual_clues=visual_clues or [],
        mood=mood,
        recurring_symbols=recurring_symbols or [],
        uncertainty=uncertainty,
        user_context=user_context,
    )


def generate_pact(intake: DreamIntake, answers: str, text_client) -> tuple[PactCard, str]:
    prompt = pact_prompt(intake, answers)
    card = text_client.generate_pact(prompt)
    merged = intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    return card, render_pact_card(card)
```

- [ ] **Step 5: Run pipeline tests**

Run:

```bash
python -m pytest tests/test_pipeline.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit pipeline**

```bash
git add dream_customs/models.py dream_customs/pipeline.py tests/test_pipeline.py
git commit -m "feat: add dream customs pipeline"
```

## Task 7: Gradio App

**Files:**
- Create: `app.py`

- [ ] **Step 1: Implement Gradio UI with fake clients**

Write `app.py`:

```python
import gradio as gr

from dream_customs.models import FakeTextClient, FakeVisionClient
from dream_customs.pipeline import build_intake, generate_pact


vision_client = FakeVisionClient()
text_client = FakeTextClient()


def run_customs(dream_text, image, audio, mood):
    visual_clues = vision_client.extract_clues(image)
    voice_transcript = ""
    if audio:
        voice_transcript = "Audio received. ASR adapter will transcribe this in the next implementation pass."
    intake = build_intake(
        dream_text=dream_text or "",
        voice_transcript=voice_transcript,
        visual_clues=visual_clues,
        mood=mood or "",
        user_context="User wants a gentle next-day suggestion after vivid dreams.",
    )
    card, html = generate_pact(intake, "User accepted a small pact.", text_client)
    return intake.model_dump(), card.to_plain_text(), html


with gr.Blocks(title="Dream Customs") as demo:
    gr.Markdown("# Dream Customs / 梦境海关")
    gr.Markdown("Declare last night's dream by text, image, or voice. Get a playful pact for today.")
    with gr.Row():
        dream_text = gr.Textbox(label="Dream text", lines=6)
        image = gr.Image(label="Dream sketch or bedside note", type="filepath")
        audio = gr.Audio(label="Voice note", type="filepath")
    mood = gr.Textbox(label="Wake-up mood", placeholder="anxious, amused, foggy...")
    submit = gr.Button("Submit to Customs")
    intake_json = gr.JSON(label="Dream Intake")
    plain = gr.Textbox(label="Plain text result", lines=10)
    card = gr.HTML(label="Today's Pact Card")
    submit.click(run_customs, [dream_text, image, audio, mood], [intake_json, plain, card])


if __name__ == "__main__":
    demo.launch()
```

- [ ] **Step 2: Run app smoke test**

Run:

```bash
python app.py
```

Expected: local Gradio URL appears and the app loads.

- [ ] **Step 3: Commit Gradio app**

```bash
git add app.py
git commit -m "feat: add dream customs gradio app"
```

## Task 8: Real Model Adapter Pass

**Files:**
- Modify: `dream_customs/models.py`
- Modify: `requirements.txt`
- Add tests only if wrappers can be mocked without downloading models.

- [ ] **Step 1: Add interface classes without loading models at import time**

Modify `dream_customs/models.py` to add lazy classes:

```python
class MiniCPMVisionClient:
    def __init__(self, model_name: str = "openbmb/MiniCPM-V-4.6"):
        self.model_name = model_name
        self._pipe = None

    def _load(self):
        if self._pipe is None:
            from transformers import pipeline
            self._pipe = pipeline("image-text-to-text", model=self.model_name)
        return self._pipe

    def extract_clues(self, image_path: str | None) -> list[str]:
        if not image_path:
            return []
        pipe = self._load()
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "path": image_path},
                {"type": "text", "text": "Extract concise dream-like visual clues as a comma-separated list. Do not diagnose."},
            ],
        }]
        result = pipe(text=messages)
        text = str(result)
        return [part.strip() for part in text.replace("\n", ",").split(",") if part.strip()][:8]
```

- [ ] **Step 2: Keep fake clients as default for tests**

Do not make real models load during pytest. The Gradio app may keep fake clients until model runtime is validated.

- [ ] **Step 3: Commit adapters**

```bash
git add dream_customs/models.py requirements.txt
git commit -m "feat: add minicpm model adapter skeleton"
```

## Task 9: Space Packaging And Final Checks

**Files:**
- Modify: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: Add `.gitignore`**

Write `.gitignore`:

```text
.venv/
__pycache__/
.pytest_cache/
*.pyc
.DS_Store
.superpowers/
```

- [ ] **Step 2: Run all tests**

Run:

```bash
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Run app**

Run:

```bash
python app.py
```

Expected: app launches; submit sample dream; final card renders.

- [ ] **Step 4: Commit final packaging**

```bash
git add .gitignore README.md
git commit -m "chore: prepare dream customs space packaging"
```

## Self-Review

- Spec coverage: text, image, voice, DreamIntake, MiniCPM roles, safety, card output, and Gradio are covered.
- Placeholder scan: no planned step uses unresolved placeholder tokens as an implementation substitute.
- Type consistency: `DreamIntake`, `PactCard`, `FakeTextClient`, and `FakeVisionClient` are defined before use.

## Execution Choice

Plan complete and saved to `docs/superpowers/plans/2026-06-05-dream-customs-mvp.md`.

Recommended execution option: Subagent-Driven. Use one fresh worker per task, review between tasks, and keep commits small.
