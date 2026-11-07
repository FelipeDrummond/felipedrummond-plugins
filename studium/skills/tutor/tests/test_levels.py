from datetime import date

from tutorlog import Evidence, confidence_summary, level_from_evidence, note_level


def ev(day, kind, result="correct", **flags):
    fields = dict(confidence=None, hinted=False, surprise=False, unseen_system=False,
                  new_variant=False, exam=False, note="")
    fields.update(flags)
    return Evidence(date=date(2026, 11, day), kind=kind, result=result, **fields)


def test_no_evidence_means_no_flag():
    assert level_from_evidence([]) is None


def test_moderate_needs_statement_and_standard_problem_same_day():
    assert level_from_evidence([ev(1, "state"), ev(1, "mechanical")]) == "moderate"
    assert level_from_evidence([ev(1, "state"), ev(3, "mechanical")]) is None


def test_hinted_answers_earn_nothing():
    assert level_from_evidence([ev(1, "state", hinted=True), ev(1, "mechanical")]) is None


def test_good_needs_surprise_retest_days_later_on_unseen_system():
    base = [ev(1, "state"), ev(1, "mechanical")]
    assert level_from_evidence(base + [ev(3, "conceptual", surprise=True, unseen_system=True)]) == "good"
    assert level_from_evidence(base + [ev(2, "conceptual", surprise=True, unseen_system=True)]) == "moderate"
    assert level_from_evidence(base + [ev(3, "conceptual", surprise=True)]) == "moderate"


def test_deep_needs_later_pass_flaw_and_variant():
    good = [ev(1, "state"), ev(1, "mechanical"), ev(3, "conceptual", surprise=True, unseen_system=True)]
    assert level_from_evidence(good + [ev(9, "conceptual", surprise=True), ev(9, "flaw"), ev(9, "invent", new_variant=True)]) == "deep"
    assert level_from_evidence(good + [ev(9, "conceptual", surprise=True), ev(9, "flaw")]) == "good"


def test_failed_retest_lowers_one_level_and_below_moderate_removes():
    good = [ev(1, "state"), ev(1, "mechanical"), ev(3, "conceptual", surprise=True, unseen_system=True)]
    assert level_from_evidence(good + [ev(9, "conceptual", "wrong", surprise=True)]) == "moderate"
    assert level_from_evidence(good + [ev(9, "conceptual", "wrong", surprise=True), ev(12, "conceptual", "partial", surprise=True)]) is None


def test_exam_problem_alone_cannot_raise_a_flag():
    assert level_from_evidence([ev(1, "mechanical", exam=True)]) is None


def test_exam_mechanical_counts_with_statement():
    assert level_from_evidence([ev(1, "state"), ev(1, "mechanical", exam=True)]) == "moderate"


def test_evidence_order_does_not_matter():
    shuffled = [ev(3, "conceptual", surprise=True, unseen_system=True), ev(1, "mechanical"), ev(1, "state")]
    assert level_from_evidence(shuffled) == "good"


def test_note_shows_weakest_topic():
    assert note_level(["deep", "moderate"]) == "moderate"
    assert note_level(["good", None]) is None
    assert note_level([]) is None


def test_confidence_summary_is_short():
    text = confidence_summary([ev(1, "mechanical", confidence=5), ev(1, "flaw", "wrong", confidence=5), ev(1, "state", confidence=None)])
    assert "5: 1 of 2 correct" in text and "not given: 1 of 1 correct" in text
