from scripts.evaluate_demo_quality import evaluate_cases, evaluate_text, load_cases


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


def test_load_cases_returns_ten_demo_eval_cases():
    cases = load_cases()

    assert len(cases) == 10
    assert {case["id"] for case in cases} >= {"elevator_wax_floor14"}


def test_evaluate_cases_fails_when_case_required_terms_are_missing():
    report = evaluate_cases(
        [
            {
                "id": "bad_case",
                "dream_text": "I saw a door.",
                "visual_clues": [],
                "mood": "Uneasy",
                "required_terms": ["elevator"],
                "banned_terms": [],
            }
        ]
    )

    assert not report["passes"]
    assert report["failures"][0]["id"] == "bad_case"
    assert "missing required term: elevator" in report["failures"][0]["issues"]
