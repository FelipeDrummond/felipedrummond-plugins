import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from test_load import make_topic
from tutorlog import load_topics, save_topic

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "tutorlog.py"


def run(data, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--data", str(data)],
                          capture_output=True, text=True)


def seed(data, count, **over):
    for i in range(count):
        save_topic(make_topic(slug=f"topic-{i}", name=f"Topic {i}", evidence=[],
                              next_due=date(2026, 11, 1) + timedelta(days=i), **over), data)


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
    topic = load_topics(tmp_path)[0]
    assert len(topic.evidence) == 1
    assert topic.next_due == date(2026, 11, 27)
    ev["date"] = "2026-11-27"
    run(tmp_path, "record", "topic-0", "--json", json.dumps(ev))
    assert load_topics(tmp_path)[0].next_due == date(2026, 12, 18)
    ev.update(date="2026-12-18", result="wrong")
    run(tmp_path, "record", "topic-0", "--json", json.dumps(ev))
    assert load_topics(tmp_path)[0].next_due == date(2026, 12, 20)


def test_record_non_surprise_keeps_next_due(tmp_path):
    seed(tmp_path, 1)
    ev = {"date": "2026-11-20", "kind": "state", "result": "correct"}
    assert run(tmp_path, "record", "topic-0", "--json", json.dumps(ev)).returncode == 0
    assert load_topics(tmp_path)[0].next_due == date(2026, 11, 1)


def test_record_non_surprise_sets_next_due_when_none(tmp_path):
    save_topic(make_topic(slug="x", evidence=[], next_due=None), tmp_path)
    ev = {"date": "2026-11-20", "kind": "state", "result": "correct"}
    assert run(tmp_path, "record", "x", "--json", json.dumps(ev)).returncode == 0
    assert load_topics(tmp_path)[0].next_due == date(2026, 11, 27)


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
    (tmp_path / "broken.json").write_text("{not json")
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


def test_state_and_config_files_are_not_topics(tmp_path):
    seed(tmp_path, 1)
    _state(tmp_path)
    (tmp_path / "config.json").write_text("{}")
    assert [t.slug for t in load_topics(tmp_path)] == ["topic-0"]
