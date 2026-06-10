import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dream_customs.ui.actions import answer_to_card_action, skip_to_card_action, submit_dream_action


FIXTURE_PATH = Path("tests/fixtures/today_tip_eval_cases.json")
OLD_CUSTOMS_TERMS = ["permit", "contraband", "clearance", "sealed", "pact"]
FRIGHTENING_TERMS = ["you will fail", "prophecy says", "fate says", "must mean", "mental illness"]
CHINESE_UI_LABELS = ["今日小", "梦境摘要", "想理解的问题", "解读草稿", "没试过的小事", "关心一句"]
CHINESE_LEAKAGE_TERMS = ["数字", "电梯", "按钮", "楼层", "融化", "梦境"]
HARD_COMMAND_PHRASES = ["address it immediately", "fix it immediately", "solve it immediately"]


def _load_cases(path: Path = FIXTURE_PATH) -> List[Dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text_for_case(case: Dict[str, Any]) -> Dict[str, Any]:
    state, _view_json = submit_dream_action(
        dream_text=case["dream_text"],
        mood=case.get("mood", "Neutral"),
        text_backend="demo",
        vision_backend="demo",
        language=case.get("language", "en"),
    )
    if case.get("answer"):
        _state, view_json = answer_to_card_action(
            state,
            case["answer"],
            text_backend="demo",
            vision_backend="demo",
            language=case.get("language", "en"),
        )
    else:
        _state, view_json = skip_to_card_action(
            state,
            text_backend="demo",
            vision_backend="demo",
            language=case.get("language", "en"),
        )
    return json.loads(view_json)


def evaluate_case(case: Dict[str, Any]) -> List[str]:
    view = _text_for_case(case)
    combined = "\n".join([view.get("card_title", ""), view.get("card_text", ""), view.get("card_html", "")])
    lowered = combined.lower()
    interpretation = (
        view.get("debug", {})
        .get("session", {})
        .get("draft_tip", {})
        .get("interpretation", "")
        .lower()
    )
    failures: List[str] = []

    if view.get("status") != "tip":
        failures.append("did_not_reach_tip")

    if not any(anchor.lower() in lowered for anchor in case.get("required_anchors", [])):
        failures.append("missing_required_anchor")

    missing_answer_terms = [term for term in case.get("required_answer_terms", []) if term.lower() not in lowered]
    if missing_answer_terms:
        failures.append("missing_answer_terms:" + ",".join(missing_answer_terms))

    missing_interpretation_terms = [
        term for term in case.get("required_interpretation_terms", []) if term.lower() not in interpretation
    ]
    if missing_interpretation_terms:
        failures.append("missing_interpretation_terms:" + ",".join(missing_interpretation_terms))

    old_terms = [term for term in OLD_CUSTOMS_TERMS if term in lowered]
    if old_terms:
        failures.append("old_customs_terms:" + ",".join(old_terms))

    frightening = [term for term in FRIGHTENING_TERMS if term in lowered]
    if frightening:
        failures.append("unsafe_or_overcertain_terms:" + ",".join(frightening))

    if case.get("language", "en") == "en":
        chinese_labels = [label for label in CHINESE_UI_LABELS if label in combined]
        if chinese_labels:
            failures.append("chinese_ui_labels:" + ",".join(chinese_labels))
        chinese_terms = [term for term in CHINESE_LEAKAGE_TERMS if term in combined]
        if chinese_terms:
            failures.append("chinese_anchor_leakage:" + ",".join(chinese_terms))
        hard_commands = [phrase for phrase in HARD_COMMAND_PHRASES if phrase in lowered]
        if hard_commands:
            failures.append("hard_command:" + ",".join(hard_commands))

    if case.get("requires_safety_note") and "trusted person or professional support" not in lowered:
        failures.append("missing_support_note")

    return failures


def evaluate_cases(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    failures = {case["id"]: evaluate_case(case) for case in cases}
    failures = {case_id: issues for case_id, issues in failures.items() if issues}
    return {"case_count": len(cases), "failures": failures, "passes": not failures}


def main() -> int:
    result = evaluate_cases(_load_cases())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
