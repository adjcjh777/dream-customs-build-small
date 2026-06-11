from typing import Literal, Optional

from pydantic import BaseModel, Field


class DreamQuestionIntake(BaseModel):
    dream_text: str = ""
    voice_transcript: str = ""
    visual_clues: list[str] = Field(default_factory=list)
    mood: str = ""
    main_question: str = ""
    recurring_symbols: list[str] = Field(default_factory=list)
    uncertainty: str = ""
    user_context: str = ""

    def merged_text(self) -> str:
        parts = [
            self.dream_text.strip(),
            self.voice_transcript.strip(),
            "Visual clues: " + ", ".join(self.visual_clues) if self.visual_clues else "",
            "Mood: " + self.mood.strip() if self.mood else "",
            "Main question: " + self.main_question.strip() if self.main_question else "",
            "Recurring symbols: " + ", ".join(self.recurring_symbols) if self.recurring_symbols else "",
            "Uncertainty: " + self.uncertainty.strip() if self.uncertainty else "",
            "Context: " + self.user_context.strip() if self.user_context else "",
        ]
        return "\n".join(part for part in parts if part)


class DreamIntake(DreamQuestionIntake):
    """Backward-compatible name for older integration code."""


class DreamQAState(BaseModel):
    dream_summary: str = ""
    main_question: str = ""
    dream_anchors: list[str] = Field(default_factory=list)
    followup_questions: list[str] = Field(default_factory=list)
    user_answers: list[str] = Field(default_factory=list)
    current_step: Literal["record", "ask", "interpret", "tip"] = "record"

    @classmethod
    def from_intake(
        cls,
        intake: DreamQuestionIntake,
        dream_summary: str = "",
        dream_anchors: Optional[list[str]] = None,
        followup_questions: Optional[list[str]] = None,
    ) -> "DreamQAState":
        return cls(
            dream_summary=dream_summary,
            main_question=intake.main_question,
            dream_anchors=dream_anchors or [],
            followup_questions=followup_questions or [],
            current_step="ask" if followup_questions else "record",
        )


class TodayTipCard(BaseModel):
    dream_summary: str
    main_question: str = ""
    dream_anchors: list[str] = Field(default_factory=list)
    followup_questions: list[str] = Field(default_factory=list)
    user_answers: list[str] = Field(default_factory=list)
    interpretation: str
    today_tip: str
    tiny_action: str = ""
    caring_note: str = ""
    safety_note: str = ""

    def _combined_public_text(self) -> str:
        return "\n".join(
            [
                self.dream_summary,
                self.main_question,
                self.interpretation,
                self.today_tip,
                self.tiny_action,
                self.caring_note,
            ]
        ).lower()

    def references_dream_anchor(self) -> bool:
        text = self._combined_public_text()
        for anchor in self.dream_anchors:
            clean = anchor.strip().lower()
            if not clean:
                continue
            if clean in text:
                return True
            tokens = [part for part in clean.replace("：", " ").replace(":", " ").split() if len(part) >= 2]
            if any(token in text for token in tokens):
                return True
            for marker in ("电梯", "按钮", "楼", "桥", "水", "14", "melted", "elevator", "button", "floor"):
                if marker in clean and marker in text:
                    return True
        return False

    def to_plain_text(self) -> str:
        lines = [
            "今日小 Tips",
            f"梦境摘要: {self.dream_summary}",
            f"想理解的问题: {self.main_question}",
            f"梦境线索: {', '.join(self.dream_anchors)}",
            f"解读草稿: {self.interpretation}",
            f"今日小 Tips: {self.today_tip}",
        ]
        if self.tiny_action:
            lines.append(f"没试过的小事: {self.tiny_action}")
        if self.caring_note:
            lines.append(f"关心一句: {self.caring_note}")
        if self.safety_note:
            lines.append(f"安全提示: {self.safety_note}")
        return "\n".join(lines)


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


SessionPhase = Literal[
    "empty",
    "record",
    "ask",
    "interpret",
    "tip",
    "declaring",
    "negotiating",
    "drafting",
    "sealed",
    "error",
]
EvidenceType = Literal["text", "image", "audio", "mood"]
EvidenceStatus = Literal["queued", "extracting", "extracted", "failed", "selected"]
TimelineRole = Literal["system", "user", "assistant", "interpretation", "tip", "customs", "pact", "error"]


class EvidenceItem(BaseModel):
    type: EvidenceType
    label: str
    status: EvidenceStatus = "queued"
    content: str = ""
    source_path: str = ""
    error: str = ""


class TimelineEvent(BaseModel):
    role: TimelineRole
    title: str
    body: str = ""
    meta: str = ""
    status: str = ""


class CustomsSession(BaseModel):
    phase: SessionPhase = "empty"
    language: str = "en"
    intake: DreamQuestionIntake = Field(default_factory=DreamQuestionIntake)
    qa_state: DreamQAState = Field(default_factory=DreamQAState)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    question_history: list[str] = Field(default_factory=list)
    answer_history: list[str] = Field(default_factory=list)
    draft_tip: Optional[TodayTipCard] = None
    sealed_tip: Optional[TodayTipCard] = None
    draft_pact: Optional[PactCard] = None
    sealed_pact: Optional[PactCard] = None
    safety_flags: list[str] = Field(default_factory=list)
    events: list[TimelineEvent] = Field(default_factory=list)

    def answers_text(self) -> str:
        return "\n".join(answer.strip() for answer in self.answer_history if answer.strip())

    def evidence_count(self) -> int:
        return len([item for item in self.evidence_items if item.status != "failed"])

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)
