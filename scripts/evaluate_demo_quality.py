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


def case_source_text(case: dict) -> str:
    return " ".join(
        part
        for part in [
            str(case.get("dream_text", "")),
            str(case.get("voice_transcript", "")),
            " ".join(str(clue) for clue in case.get("visual_clues", [])),
        ]
        if part.strip()
    )


def evaluate_case(case: dict) -> dict:
    result = evaluate_text(
        case_source_text(case),
        required_terms=case.get("required_terms", []),
        banned_terms=case.get("banned_terms", []),
    )
    return {"id": case.get("id", ""), **result}


def evaluate_cases(cases: list[dict]) -> dict:
    results = [evaluate_case(case) for case in cases]
    failures = [result for result in results if not result["passes"]]
    return {
        "case_count": len(cases),
        "ids": [case["id"] for case in cases],
        "failures": failures,
        "passes": not failures,
    }


def main() -> int:
    cases = load_cases()
    report = evaluate_cases(cases)
    print(json.dumps(report, indent=2))
    return 0 if report["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
