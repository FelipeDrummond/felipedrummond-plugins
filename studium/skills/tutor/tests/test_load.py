import json
from datetime import date

import pytest

from tutorlog import Evidence, LogError, Topic, home, load_topics, save_topic


def make_topic(**over):
    fields = dict(
        slug="fourier-series", name="Fourier series", course="Math", section="2",
        tier="own_it", prereqs=["integration"], notes="n", patched=False,
        retest_without_notice=True, next_due=date(2026, 11, 8), mistakes=["sign slip"],
        evidence=[Evidence(date=date(2026, 11, 1), kind="state", result="correct", confidence=4,
                           hinted=False, surprise=False, unseen_system=False,
                           new_variant=False, exam=False, note="ok")],
    )
    fields.update(over)
    return Topic(**fields)


def test_round_trip(tmp_path):
    topic = make_topic()
    save_topic(topic, tmp_path)
    assert load_topics(tmp_path) == [topic]


def test_round_trip_without_next_due(tmp_path):
    topic = make_topic(next_due=None, evidence=[])
    save_topic(topic, tmp_path)
    assert load_topics(tmp_path) == [topic]


def test_saved_file_is_indented_json_with_iso_dates(tmp_path):
    save_topic(make_topic(), tmp_path)
    text = (tmp_path / "fourier-series.json").read_text()
    assert '\n  "slug"' in text and '"2026-11-08"' in text
    assert json.loads(text)["evidence"][0]["date"] == "2026-11-01"


def test_bad_json_names_the_file(tmp_path):
    (tmp_path / "broken.json").write_text('{"name": ')
    with pytest.raises(LogError, match="broken.json"):
        load_topics(tmp_path)


def test_unknown_tier_names_the_field(tmp_path):
    save_topic(make_topic(tier="whatever"), tmp_path)
    with pytest.raises(LogError, match="tier"):
        load_topics(tmp_path)


def test_bad_date_names_the_field(tmp_path):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["next_due"] = "tomorrow"
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match="next_due"):
        load_topics(tmp_path)


def test_unknown_evidence_kind_names_the_field(tmp_path):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["evidence"][0]["kind"] = "vibes"
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match="kind"):
        load_topics(tmp_path)


def test_missing_field_names_the_field(tmp_path):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    del data["course"]
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match="course"):
        load_topics(tmp_path)


def test_one_bad_file_is_never_skipped(tmp_path):
    save_topic(make_topic(), tmp_path)
    (tmp_path / "broken.json").write_text("[]")
    with pytest.raises(LogError, match="broken.json"):
        load_topics(tmp_path)


def test_home_respects_env(monkeypatch, tmp_path):
    monkeypatch.setenv("TUTOR_HOME", str(tmp_path))
    assert home() == tmp_path


def test_home_default(monkeypatch):
    monkeypatch.delenv("TUTOR_HOME", raising=False)
    assert home().name == "tutor" and home().parent.name == "Documents"
