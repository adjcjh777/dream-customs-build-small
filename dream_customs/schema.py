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
