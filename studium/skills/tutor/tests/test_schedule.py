from datetime import date, datetime, timedelta

from test_load import make_topic
from tutorlog import (Evidence, block_action, minutes_left, next_due, overflowing,
                      plan_block, session_opening)

T = date(2027, 2, 1)


def test_intervals():
    assert next_due(date(2026, 11, 6), 0, True, "own_it", T) == date(2026, 11, 13)
    assert next_due(date(2026, 11, 6), 1, True, "own_it", T) == date(2026, 11, 27)
    assert next_due(date(2026, 11, 6), 2, True, "own_it", T) == date(2027, 1, 5)
    assert next_due(date(2026, 11, 6), 5, True, "own_it", T) == date(2027, 1, 5)


def test_failure_comes_back_in_two_days():
    assert next_due(date(2026, 11, 6), 3, False, "own_it", T) == date(2026, 11, 8)


def test_own_it_is_pulled_into_final_two_weeks():
    assert next_due(date(2026, 12, 20), 2, True, "own_it", T) == date(2027, 1, 18)
    assert next_due(date(2026, 12, 20), 2, True, "know_exists", T) == date(2027, 2, 18)


def test_dates_at_and_after_target_still_compute():
    assert next_due(date(2027, 1, 25), 2, True, "own_it", T) == date(2027, 3, 26)
    assert next_due(date(2027, 6, 1), 0, True, "own_it", T) == date(2027, 6, 8)


def _ev(day, result, surprise=True):
    return Evidence(date=day, kind="state", result=result, surprise=surprise)


def test_session_opening_limit_and_order():
    today = date(2026, 12, 1)
    old = date(2026, 10, 1)
    topics = [
        make_topic(slug=f"t{i}", name=f"t{i}", tier="own_it", next_due=old + timedelta(days=i),
                   evidence=[_ev(old, "correct")])
        for i in range(30)
    ]
    topics.append(make_topic(slug="know", name="know", tier="know_exists", next_due=date(2026, 9, 1),
                             evidence=[]))
    topics.append(make_topic(slug="failed", name="failed", tier="know_exists",
                             next_due=date(2026, 11, 30), evidence=[_ev(old, "wrong")]))
    topics.append(make_topic(slug="future", name="future", next_due=date(2026, 12, 2)))
    topics.append(make_topic(slug="never", name="never", next_due=None))
    chosen = session_opening(topics, today)
    assert [t.slug for t in chosen] == ["failed", "t0"]
    assert len(session_opening(topics, today, limit=5)) == 5


def test_non_surprise_failure_does_not_count_as_failed():
    today = date(2026, 12, 1)
    a = make_topic(slug="a", tier="know_exists", next_due=date(2026, 11, 1),
                   evidence=[_ev(date(2026, 10, 1), "wrong", surprise=False)])
    b = make_topic(slug="b", tier="own_it", next_due=date(2026, 11, 20), evidence=[])
    assert [t.slug for t in session_opening([a, b], today)] == ["b", "a"]


def _eight():
    topics = [
        make_topic(slug=f"k{i}", tier="know_exists", next_due=date(2026, 11, 1) + timedelta(days=i))
        for i in range(4)
    ]
    topics += [
        make_topic(slug=f"o{i}", tier="own_it", next_due=date(2026, 11, 10) + timedelta(days=i))
        for i in range(4)
    ]
    return topics


def test_block_chooses_by_tier_then_overdue_and_counts_overflow():
    chosen, overflow = plan_block(_eight(), date(2026, 11, 15))
    assert len(chosen) == 6 and overflow == 2
    assert chosen[0].tier == "own_it"
    assert [t.slug for t in chosen] == ["o0", "o1", "o2", "o3", "k0", "k1"]


def test_items_not_yet_due_stay_out():
    topics = [make_topic(slug="soon", next_due=date(2026, 11, 16)),
              make_topic(slug="never", next_due=None),
              make_topic(slug="due", next_due=date(2026, 11, 15))]
    chosen, overflow = plan_block(topics, date(2026, 11, 15))
    assert [t.slug for t in chosen] == ["due"] and overflow == 0


def test_block_action_never_duplicates():
    d = date(2026, 11, 15)
    assert block_action(None, 3, d) == "create"
    assert block_action(None, 0, d) == "none"
    assert block_action({"block_date": d, "completed": False}, 3, d) == "update"
    assert block_action({"block_date": d, "completed": False}, 0, d) == "delete"
    assert block_action({"block_date": d, "completed": True}, 3, d) == "none"
    assert block_action({"block_date": d, "completed": True}, 0, d) == "none"
    assert block_action({"block_date": date(2026, 11, 8), "completed": True}, 3, d) == "create"
    assert block_action({"block_date": date(2026, 11, 8), "completed": False}, 0, d) == "none"


def test_overflow_warning_needs_two_weeks_running():
    assert overflowing([0, 2, 1]) and not overflowing([2, 0, 1]) and not overflowing([3])
    assert not overflowing([])


def test_minutes_left():
    start = datetime(2026, 11, 6, 10, 0)
    assert minutes_left(start, start + timedelta(minutes=50)) == 10
    assert minutes_left(start, start + timedelta(minutes=75)) == 0
    assert minutes_left(start, start + timedelta(minutes=30), length=45) == 15
