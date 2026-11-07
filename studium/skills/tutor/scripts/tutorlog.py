"""Evidence log for the tutor: topic records, validation, and understanding levels."""
import json
import os
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from pathlib import Path

KINDS = ("state", "mechanical", "conceptual", "flaw", "invent")
RESULTS = ("correct", "partial", "wrong", "not_answered")
TIERS = ("own_it", "by_hand_then_delegate", "know_exists")
LEVELS = ("moderate", "good", "deep")


class LogError(Exception):
    """A log file is unreadable or has an invalid field. The message names both."""


def home() -> Path:
    env = os.environ.get("TUTOR_HOME")
    return Path(env) if env else Path.home() / "Documents" / "tutor"


@dataclass
class Evidence:
    date: date
    kind: str
    result: str
    confidence: int | None = None
    hinted: bool = False
    surprise: bool = False
    unseen_system: bool = False
    new_variant: bool = False
    exam: bool = False
    note: str = ""


@dataclass
class Topic:
    slug: str
    name: str
    course: str
    section: str
    tier: str
    prereqs: list[str]
    notes: str
    patched: bool
    retest_without_notice: bool
    next_due: date | None
    mistakes: list[str]
    evidence: list[Evidence] = field(default_factory=list)


# ---------- loading and saving ----------

_EVIDENCE_FIELDS = frozenset(f.name for f in fields(Evidence))
_TOPIC_FIELDS = frozenset(f.name for f in fields(Topic))

def _fail(file: Path, name: str, problem: str) -> LogError:
    return LogError(f"{file.name}: field '{name}' {problem}")


def _get(data: dict, name: str, file: Path, prefix: str = ""):
    if name not in data:
        raise _fail(file, prefix + name, "is missing")
    return data[name]


def _typed(value, kind, name: str, file: Path):
    if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
        raise _fail(file, name, f"must be {kind.__name__}, got {value!r}")
    return value


def _choice(value, options: tuple, name: str, file: Path) -> str:
    if value not in options:
        raise _fail(file, name, f"must be one of {', '.join(options)}, got {value!r}")
    return value


def _date(value, name: str, file: Path) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise _fail(file, name, f"must be a YYYY-MM-DD date, got {value!r}") from None


def _str_list(value, name: str, file: Path) -> list[str]:
    _typed(value, list, name, file)
    for i, item in enumerate(value):
        _typed(item, str, f"{name}[{i}]", file)
    return value


def _reject_unknown(data: dict, known, file: Path, prefix: str = "") -> None:
    for key in data:
        if key not in known:
            raise _fail(file, prefix + str(key), "is not a known field")


def _parse_evidence(raw, index: int, file: Path) -> Evidence:
    prefix = f"evidence[{index}]."
    _typed(raw, dict, prefix.rstrip("."), file)
    _reject_unknown(raw, _EVIDENCE_FIELDS, file, prefix)
    confidence = raw.get("confidence")
    if confidence is not None:
        _typed(confidence, int, prefix + "confidence", file)
    flags = {}
    for flag in ("hinted", "surprise", "unseen_system", "new_variant", "exam"):
        flags[flag] = _typed(raw.get(flag, False), bool, prefix + flag, file)
    return Evidence(
        date=_date(_get(raw, "date", file, prefix), prefix + "date", file),
        kind=_choice(_get(raw, "kind", file, prefix), KINDS, prefix + "kind", file),
        result=_choice(_get(raw, "result", file, prefix), RESULTS, prefix + "result", file),
        confidence=confidence,
        note=_typed(raw.get("note", ""), str, prefix + "note", file),
        **flags,
    )


def _parse_topic(data, file: Path) -> Topic:
    if not isinstance(data, dict):
        raise LogError(f"{file.name}: top level must be a JSON object")
    _reject_unknown(data, _TOPIC_FIELDS, file)
    next_due = _get(data, "next_due", file)
    return Topic(
        slug=_typed(_get(data, "slug", file), str, "slug", file),
        name=_typed(_get(data, "name", file), str, "name", file),
        course=_typed(_get(data, "course", file), str, "course", file),
        section=_typed(_get(data, "section", file), str, "section", file),
        tier=_choice(_get(data, "tier", file), TIERS, "tier", file),
        prereqs=_str_list(_get(data, "prereqs", file), "prereqs", file),
        notes=_typed(_get(data, "notes", file), str, "notes", file),
        patched=_typed(_get(data, "patched", file), bool, "patched", file),
        retest_without_notice=_typed(
            _get(data, "retest_without_notice", file), bool, "retest_without_notice", file),
        next_due=None if next_due is None else _date(next_due, "next_due", file),
        mistakes=_str_list(_get(data, "mistakes", file), "mistakes", file),
        evidence=[
            _parse_evidence(raw, i, file)
            for i, raw in enumerate(_typed(_get(data, "evidence", file), list, "evidence", file))
        ],
    )


def load_topics(directory: Path) -> list[Topic]:
    """Load every *.json topic in directory. Raises LogError on the first bad file."""
    topics = []
    for file in sorted(Path(directory).glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise LogError(f"{file.name}: not valid JSON ({exc})") from exc
        topics.append(_parse_topic(data, file))
    return topics


def save_topic(topic: Topic, directory: Path) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    text = json.dumps(asdict(topic), indent=2, ensure_ascii=False, default=lambda d: d.isoformat())
    (directory / f"{topic.slug}.json").write_text(text + "\n", encoding="utf-8")


# ---------- understanding levels ----------

def _earned(item: Evidence) -> bool:
    return item.result == "correct" and not item.hinted


def _lower(level: str | None) -> str | None:
    index = LEVELS.index(level) if level else 0
    return LEVELS[index - 1] if index > 0 else None


def level_from_evidence(evidence: list[Evidence]) -> str | None:
    """Replay evidence by date and return the flag level it supports, or None."""
    level: str | None = None
    since: date | None = None
    for day in sorted({item.date for item in evidence}):
        todays = [item for item in evidence if item.date == day]
        if any(item.surprise and item.result != "correct" for item in todays):
            level, since = _lower(level), day
            continue
        if level is None:
            kinds = {item.kind for item in todays if _earned(item)}
            if {"state", "mechanical"} <= kinds:
                level, since = "moderate", day
        if level == "moderate" and any(
            _earned(item) and item.surprise and item.unseen_system and (day - since).days >= 2
            for item in todays
        ):
            level, since = "good", day
        if level == "good":
            later = [item for item in evidence if item.date > since and item.date <= day and _earned(item)]
            if (any(item.surprise for item in later)
                    and any(item.kind == "flaw" for item in later)
                    and any(item.new_variant for item in later)):
                level, since = "deep", day
    return level


def note_level(levels: list[str | None]) -> str | None:
    """A note shows its weakest topic's level; any unflagged topic means no flag."""
    if not levels or None in levels:
        return None
    return min(levels, key=LEVELS.index)


def confidence_summary(evidence: list[Evidence]) -> str:
    """How often each confidence rating was right, e.g. '5: 1 of 2 correct; not given: 1 of 1 correct'."""
    buckets: dict[int | None, list[bool]] = {}
    for item in evidence:
        buckets.setdefault(item.confidence, []).append(item.result == "correct")
    order = sorted(buckets, key=lambda c: (c is None, c or 0))
    return "; ".join(
        f"{'not given' if c is None else c}: {sum(buckets[c])} of {len(buckets[c])} correct"
        for c in order
    )
