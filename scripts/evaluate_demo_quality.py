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
