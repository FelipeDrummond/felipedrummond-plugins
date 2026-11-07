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


def test_unknown_topic_key_names_file_and_field(tmp_path):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["pachted"] = True
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match=r"fourier-series\.json.*'pachted'.*not a known field"):
        load_topics(tmp_path)


def test_unknown_evidence_key_names_file_index_and_field(tmp_path):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["evidence"][0]["hintd"] = True
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match=r"fourier-series\.json.*'evidence\[0\]\.hintd'.*not a known field"):
        load_topics(tmp_path)


def test_file_name_not_matching_slug_names_file_and_field(tmp_path):
    save_topic(make_topic(slug="lyapunov_direct"), tmp_path)
    (tmp_path / "lyapunov_direct.json").rename(tmp_path / "lyapunov-direct.json")
    with pytest.raises(LogError, match=r"lyapunov-direct\.json: field 'slug'"):
        load_topics(tmp_path)


@pytest.mark.parametrize("slug", ["Fourier", "fourier series", "-lead", "a.b", ""])
def test_slug_with_bad_characters_is_rejected_on_load(tmp_path, slug):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["slug"] = slug
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match=r"fourier-series\.json: field 'slug'"):
        load_topics(tmp_path)


@pytest.mark.parametrize("slug", ["../escape", "sub/topic", "Bad", ""])
def test_save_refuses_bad_slug_and_writes_nothing(tmp_path, slug):
    target = tmp_path / "topics"
    with pytest.raises(LogError, match="slug"):
        save_topic(make_topic(slug=slug), target)
    assert not any(tmp_path.rglob("*.json"))


@pytest.mark.parametrize("confidence", [0, 6, -1])
def test_confidence_outside_one_to_five_names_the_field(tmp_path, confidence):
    save_topic(make_topic(), tmp_path)
    path = tmp_path / "fourier-series.json"
    data = json.loads(path.read_text())
    data["evidence"][0]["confidence"] = confidence
    path.write_text(json.dumps(data))
    with pytest.raises(LogError, match=r"evidence\[0\]\.confidence"):
        load_topics(tmp_path)


def test_confidence_null_and_bounds_are_allowed(tmp_path):
    ev = make_topic().evidence[0]
    for confidence in (None, 1, 5):
        topic = make_topic(evidence=[Evidence(**{**ev.__dict__, "confidence": confidence})])
        save_topic(topic, tmp_path)
        assert load_topics(tmp_path) == [topic]
