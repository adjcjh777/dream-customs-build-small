from scripts.evaluate_today_tip_quality import _load_cases, evaluate_case, evaluate_cases


def test_today_tip_quality_eval_passes_fixture_cases():
    result = evaluate_cases(_load_cases())

    assert result["case_count"] == 10
    assert result["failures"] == {}
    assert result["passes"] is True


def test_today_tip_quality_eval_fails_missing_anchor():
    case = {
        "id": "impossible_anchor",
        "dream_text": "I dreamed of an elevator button melting.",
        "mood": "Uneasy",
        "answer": "It felt hard to start.",
        "required_anchors": ["volcano"],
    }

    assert "missing_required_anchor" in evaluate_case(case)
