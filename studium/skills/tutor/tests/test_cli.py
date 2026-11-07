import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from test_load import make_topic
from tutorlog import Evidence, load_topics, save_topic

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "tutorlog.py"


def write_config(data, target="2027-02-01"):
    data.mkdir(parents=True, exist_ok=True)
    (data / "config.json").write_text(json.dumps({"target_date": target}))


def topics(data):
    return data / "topics"


def run(data, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--data", str(data)],
                          capture_output=True, text=True)


def seed(data, count, **over):
    for i in range(count):
        save_topic(make_topic(slug=f"topic-{i}", name=f"Topic {i}", evidence=[],
                              next_due=date(2026, 11, 1) + timedelta(days=i), **over), topics(data))
    write_config(data)


def test_due_session_lists_at_most_two(tmp_path):
    seed(tmp_path, 5)
    out = run(tmp_path, "due", "--for", "session", "--today", "2026-11-20")
    assert out.returncode == 0
    assert out.stdout.count("Topic ") == 2
    assert "Topic 0" in out.stdout and "Topic 1" in out.stdout


def test_due_block_lists_chosen_and_overflow(tmp_path):
    seed(tmp_path, 8)
    out = run(tmp_path, "due", "--for", "block", "--block-date", "2026-11-20")
    assert out.returncode == 0
    assert out.stdout.count("Topic ") == 6
    assert "overflow: 2" in out.stdout


def test_record_adds_evidence_and_updates_next_due(tmp_path):
    seed(tmp_path, 1)
    ev = {"date": "2026-11-20", "kind": "state", "result": "correct", "surprise": True}
    out = run(tmp_path, "record", "topic-0", "--json", json.dumps(ev))
    assert out.returncode == 0, out.stderr
    topic = load_topics(topics(tmp_path))[0]
    assert len(topic.evidence) == 1
    assert topic.next_due == date(2026, 11, 27)
    ev["date"] = "2026-11-27"
    run(tmp_path, "record", "topic-0", "--json", json.dumps(ev))
    assert load_topics(topics(tmp_path))[0].next_due == date(2026, 12, 18)
    ev.update(date="2026-12-18", result="wrong")
    run(tmp_path, "record", "topic-0", "--json", json.dumps(ev))
    assert load_topics(topics(tmp_path))[0].next_due == date(2026, 12, 20)


def test_record_non_surprise_keeps_next_due(tmp_path):
    seed(tmp_path, 1)
    ev = {"date": "2026-11-20", "kind": "state", "result": "correct"}
    assert run(tmp_path, "record", "topic-0", "--json", json.dumps(ev)).returncode == 0
    assert load_topics(topics(tmp_path))[0].next_due == date(2026, 11, 1)


def test_record_non_surprise_sets_next_due_when_none(tmp_path):
    save_topic(make_topic(slug="x", evidence=[], next_due=None), topics(tmp_path))
    write_config(tmp_path)
    ev = {"date": "2026-11-20", "kind": "state", "result": "correct"}
    assert run(tmp_path, "record", "x", "--json", json.dumps(ev)).returncode == 0
    assert load_topics(topics(tmp_path))[0].next_due == date(2026, 11, 27)


def test_record_rejects_bad_evidence_and_unknown_slug(tmp_path):
    seed(tmp_path, 1)
    bad = run(tmp_path, "record", "topic-0", "--json", json.dumps({"date": "2026-11-20", "kind": "nope", "result": "correct"}))
    assert bad.returncode == 2 and "kind" in bad.stderr
    missing = run(tmp_path, "record", "ghost", "--json", "{}")
    assert missing.returncode == 2 and "ghost" in missing.stderr


def test_level_and_summary(tmp_path):
    seed(tmp_path, 1)
    assert run(tmp_path, "level", "topic-0").stdout.strip() == "none"
    out = run(tmp_path, "summary", "topic-0")
    assert out.returncode == 0


def test_broken_topic_file_exits_2_naming_file(tmp_path):
    topics(tmp_path).mkdir()
    (topics(tmp_path) / "broken.json").write_text("{not json")
    out = run(tmp_path, "due", "--for", "session")
    assert out.returncode == 2
    assert "broken.json" in out.stderr


def test_block_action_without_state_file(tmp_path):
    seed(tmp_path, 1)
    out = run(tmp_path, "block-action", "--block-date", "2026-11-20")
    assert out.returncode == 0
    assert out.stdout.strip() == "create"


def _state(tmp_path, **over):
    state = {"block_date": "2026-11-20", "event_id": "e1", "task_id": "t1",
             "completed": False, "overflow_history": []}
    state.update(over)
    (tmp_path / "review_state.json").write_text(json.dumps(state))


def test_block_action_with_state_and_overflow_warning(tmp_path):
    seed(tmp_path, 8)
    _state(tmp_path, overflow_history=[1, 2])
    out = run(tmp_path, "block-action", "--block-date", "2026-11-20")
    assert out.returncode == 0
    assert out.stdout.splitlines()[0] == "update"
    assert "overflow" in out.stdout.lower() and len(out.stdout.splitlines()) == 2


def test_block_action_completed_and_delete(tmp_path):
    seed(tmp_path, 1)
    _state(tmp_path, completed=True)
    assert run(tmp_path, "block-action", "--block-date", "2026-11-20").stdout.strip() == "none"
    _state(tmp_path, completed=False)
    empty = tmp_path / "empty"
    (empty).mkdir()
    (empty / "review_state.json").write_text((tmp_path / "review_state.json").read_text())
    assert run(empty, "block-action", "--block-date", "2026-11-20").stdout.strip() == "delete"


def test_block_action_bad_state_file(tmp_path):
    (tmp_path / "review_state.json").write_text('{"block_date": "nope"}')
    out = run(tmp_path, "block-action", "--block-date", "2026-11-20")
    assert out.returncode == 2 and "review_state.json" in out.stderr


def test_clock(tmp_path):
    assert run(tmp_path, "clock", "left").returncode == 2
    assert run(tmp_path, "clock", "start").returncode == 0
    assert (tmp_path / ".session_start").exists()
    out = run(tmp_path, "clock", "left")
    assert out.returncode == 0
    assert 59 <= int(out.stdout.split()[0]) <= 60



def test_config_and_state_in_data_dir_do_not_disturb_due(tmp_path):
    seed(tmp_path, 2)
    _state(tmp_path)
    out = run(tmp_path, "due", "--for", "session", "--today", "2026-11-20")
    assert out.returncode == 0 and out.stdout.count("Topic ") == 2


def test_record_uses_target_date_from_config(tmp_path):
    ev = json.dumps({"date": "2026-12-20", "kind": "state", "result": "correct", "surprise": True})
    passes = [Evidence(date=date(2026, 12, d), kind="state", result="correct", surprise=True)
              for d in (1, 10)]
    for target, expected in (("2027-02-01", date(2027, 1, 18)), ("2027-06-01", date(2027, 2, 18))):
        write_config(tmp_path, target)
        save_topic(make_topic(slug="p", evidence=list(passes)), topics(tmp_path))
        assert run(tmp_path, "record", "p", "--json", ev).returncode == 0
        assert load_topics(topics(tmp_path))[0].next_due == expected


def test_record_needs_valid_config(tmp_path):
    seed(tmp_path, 1)
    ev = json.dumps({"date": "2026-11-20", "kind": "state", "result": "correct"})
    (tmp_path / "config.json").unlink()
    out = run(tmp_path, "record", "topic-0", "--json", ev)
    assert out.returncode == 2 and "config.json" in out.stderr
    write_config(tmp_path, "soon")
    out = run(tmp_path, "record", "topic-0", "--json", ev)
    assert out.returncode == 2 and "target_date" in out.stderr


def _rec(tmp_path, slug, day, result, **extra):
    ev = {"date": day, "kind": "state", "result": result, "surprise": True, **extra}
    out = run(tmp_path, "record", slug, "--json", json.dumps(ev))
    assert out.returncode == 0, out.stderr
    return load_topics(topics(tmp_path))[0].next_due


def test_three_correct_items_one_day_give_seven_days(tmp_path):
    seed(tmp_path, 1)
    assert [_rec(tmp_path, "topic-0", "2026-11-20", "correct") for _ in range(3)] == [date(2026, 11, 27)] * 3


def test_wrong_then_correct_same_day_is_failure(tmp_path):
    seed(tmp_path, 1)
    _rec(tmp_path, "topic-0", "2026-11-20", "wrong")
    assert _rec(tmp_path, "topic-0", "2026-11-20", "correct") == date(2026, 11, 22)


def test_correct_then_wrong_same_day_is_failure(tmp_path):
    seed(tmp_path, 1)
    _rec(tmp_path, "topic-0", "2026-11-20", "correct")
    assert _rec(tmp_path, "topic-0", "2026-11-20", "wrong") == date(2026, 11, 22)


def test_third_passed_day_gets_sixty_days_or_the_own_it_pull(tmp_path):
    seed(tmp_path, 1)
    _rec(tmp_path, "topic-0", "2026-10-01", "correct")
    _rec(tmp_path, "topic-0", "2026-10-10", "correct")
    assert _rec(tmp_path, "topic-0", "2026-10-20", "correct") == date(2026, 12, 19)
    assert _rec(tmp_path, "topic-0", "2026-12-20", "correct") == date(2027, 1, 18)


def test_failure_day_resets_passes(tmp_path):
    seed(tmp_path, 1)
    _rec(tmp_path, "topic-0", "2026-10-01", "correct")
    _rec(tmp_path, "topic-0", "2026-10-10", "wrong")
    assert _rec(tmp_path, "topic-0", "2026-10-20", "correct") == date(2026, 10, 27)


def test_bool_is_not_an_int_for_confidence_or_history(tmp_path):
    seed(tmp_path, 1)
    bad = run(tmp_path, "record", "topic-0", "--json",
              json.dumps({"date": "2026-11-20", "kind": "state", "result": "correct", "confidence": True}))
    assert bad.returncode == 2 and "confidence" in bad.stderr
    _state(tmp_path, overflow_history=[True, 1])
    out = run(tmp_path, "block-action", "--block-date", "2026-11-20")
    assert out.returncode == 2 and "overflow_history" in out.stderr
