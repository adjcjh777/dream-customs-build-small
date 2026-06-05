import re
from typing import Any, Dict, List, Optional

from dream_customs.schema import PactCard


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


class FakeVisionClient:
    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        return ["blue hallway", "melted elevator buttons", "number 14"]


class FakeASRClient:
    def transcribe(self, audio_path: Optional[str]) -> str:
        if not audio_path:
            return ""
        return "The buttons melted and I could not catch the elevator."


class FakeTextClient:
    def generate_negotiation(self, prompt: str) -> Dict[str, Any]:
        if _contains_cjk(prompt):
            return {
                "visitor_name": "迟到的电梯",
                "questions": [
                    "这部电梯是在阻止你，还是在替你争取一点慢下来的时间？",
                    "如果它今天只允许你带走一件东西，你会选择哪件未完成的小事？",
                    "你愿意用一个 5 分钟动作和它交换放行章吗？",
                ],
                "tone_note": "这个来访者也许不是敌人，而是在提醒你把开始和完成分开。",
            }
        return {
            "visitor_name": "Late Elevator",
            "questions": [
                "Was the elevator blocking you, or buying you a slower morning?",
                "If it lets you carry one unfinished thing into today, which one is smallest?",
                "Would you trade it a five-minute action for a release stamp?",
            ],
            "tone_note": "This visitor may be asking you to separate starting from finishing.",
        }

    def generate_pact(self, prompt: str) -> PactCard:
        if _contains_cjk(prompt):
            return PactCard(
                visitor_name="迟到的电梯",
                permit_id="DC-DEMO-014",
                contraband=["未申报的焦虑", "融化的按钮", "一小袋没来得及开始的事"],
                risk_level="橙色：需要被安置，但不需要被害怕",
                alliance_reading="这个梦也许在提醒你，今天先把启动一件事和完成一件事分开。",
                practical_suggestion="提前 10 分钟打开一个最小任务，只要求开始，不要求完成。",
                weird_task="给电梯写一句道歉信：抱歉总让你替我背迟到的锅。",
                bedtime_release="今日电梯已停靠，未完成事项明日再报关。",
            )
        return PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-DEMO-014",
            contraband=["unfiled anxiety", "melted buttons", "one pouch of unstarted tasks"],
            risk_level="orange: needs placement, not fear",
            alliance_reading="This visitor asks you to separate starting from finishing.",
            practical_suggestion="Open one small task ten minutes early. You only need to start it.",
            weird_task="Write the elevator a one-sentence apology note.",
            bedtime_release="Today the elevator has docked; unfinished floors report tomorrow.",
        )


class MiniCPMVisionClient:
    def __init__(self, model_name: str = "openbmb/MiniCPM-V-4.6"):
        self.model_name = model_name
        self._pipe = None

    def _load(self):
        if self._pipe is None:
            from transformers import pipeline

            self._pipe = pipeline("image-text-to-text", model=self.model_name)
        return self._pipe

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        pipe = self._load()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "path": image_path},
                    {
                        "type": "text",
                        "text": (
                            "Extract concise dream-like visual clues from this image. "
                            "Return a comma-separated list. Do not diagnose."
                        ),
                    },
                ],
            }
        ]
        result = pipe(text=messages)
        text = str(result)
        return [part.strip() for part in text.replace("\n", ",").split(",") if part.strip()][:8]
