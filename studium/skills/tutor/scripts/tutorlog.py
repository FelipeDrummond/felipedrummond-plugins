"""Evidence log for the tutor: topic records, validation, and understanding levels."""
import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime, timedelta
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


# ---------- retest scheduling and limits ----------

_INTERVAL_DAYS = {0: 7, 1: 21}
_FAILURE_DAYS = 2
_STEADY_DAYS = 60
_FINAL_WINDOW_DAYS = 14


def next_due(today: date, consecutive_passes: int, passed: bool, tier: str, target: date) -> date:
    """Next retest date. consecutive_passes counts the passes before this result."""
    days = _FAILURE_DAYS if not passed else _INTERVAL_DAYS.get(consecutive_passes, _STEADY_DAYS)
    due = today + timedelta(days=days)
    final_window = target - timedelta(days=_FINAL_WINDOW_DAYS)
    if tier == "own_it" and today < final_window and due > target:
        return final_window
    return due


def _failed_last_retest(topic: Topic) -> bool:
    surprises = [item for item in topic.evidence if item.surprise]
    return bool(surprises) and max(surprises, key=lambda item: item.date).result != "correct"


def _due_on(topics: list[Topic], day: date) -> list[Topic]:
    return [t for t in topics if t.next_due is not None and t.next_due <= day]


def session_opening(topics: list[Topic], today: date, limit: int = 2) -> list[Topic]:
    """Due topics: failed last retest first, then tier, then longest overdue."""
    due = _due_on(topics, today)
    due.sort(key=lambda t: (not _failed_last_retest(t), TIERS.index(t.tier), t.next_due))
    return due[:limit]


def plan_block(topics: list[Topic], block_date: date, capacity: int = 6) -> tuple[list[Topic], int]:
    """Topics for the review block by tier then longest overdue, and how many didn't fit."""
    due = _due_on(topics, block_date)
    due.sort(key=lambda t: (TIERS.index(t.tier), t.next_due))
    return due[:capacity], max(0, len(due) - capacity)


def block_action(state: dict | None, due_count: int, block_date: date) -> str:
    """What to do with the calendar event for block_date: create, update, delete or none."""
    if state is not None and state["block_date"] == block_date:
        if state["completed"]:
            return "none"
        return "update" if due_count > 0 else "delete"
    return "create" if due_count > 0 else "none"


def overflowing(history: list[int]) -> bool:
    """True when the last two weeks both had topics that didn't fit the block."""
    return len(history) >= 2 and history[-1] > 0 and history[-2] > 0


def minutes_left(start: datetime, now: datetime, length: int = 60) -> int:
    return max(0, length - int((now - start).total_seconds() // 60))


# ---------- command line ----------

_CONFIG_FILE = "config.json"
_TOPICS_DIR = "topics"
_STATE_FILE = "review_state.json"
_CLOCK_FILE = ".session_start"


def _target_date(directory: Path) -> date:
    file = directory / _CONFIG_FILE
    if not file.exists():
        raise LogError(f"{file.name}: file not found in {directory}")
    try:
        raw = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LogError(f"{file.name}: not valid JSON ({exc})") from exc
    _typed(raw, dict, "(top level)", file)
    return _date(_get(raw, "target_date", file), "target_date", file)


def _find(topics: list[Topic], slug: str) -> Topic:
    for topic in topics:
        if topic.slug == slug:
            return topic
    raise LogError(f"no topic with slug '{slug}'")


def _consecutive_passes(evidence: list[Evidence]) -> int:
    count = 0
    for item in sorted((e for e in evidence if e.surprise), key=lambda e: e.date, reverse=True):
        if item.result != "correct":
            break
        count += 1
    return count


def _print_topics(topics: list[Topic]) -> None:
    for topic in topics:
        due = topic.next_due.isoformat() if topic.next_due else "none"
        print(f"{topic.name} ({topic.slug}) tier={topic.tier} due={due}")


def _read_state(directory: Path) -> dict | None:
    file = directory / _STATE_FILE
    if not file.exists():
        return None
    try:
        raw = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LogError(f"{file.name}: not valid JSON ({exc})") from exc
    _typed(raw, dict, "(top level)", file)
    history = _typed(_get(raw, "overflow_history", file), list, "overflow_history", file)
    for i, item in enumerate(history):
        _typed(item, int, f"overflow_history[{i}]", file)
    return {
        "block_date": _date(_get(raw, "block_date", file), "block_date", file),
        "completed": _typed(_get(raw, "completed", file), bool, "completed", file),
        "overflow_history": history,
    }


def _cmd_due(args, directory: Path) -> None:
    topics = load_topics(directory / _TOPICS_DIR)
    today = args.today or date.today()
    if args.target == "session":
        _print_topics(session_opening(topics, today))
        return
    chosen, overflow = plan_block(topics, args.block_date or today)
    _print_topics(chosen)
    print(f"overflow: {overflow}")


def _cmd_record(args, directory: Path) -> None:
    topics_dir = directory / _TOPICS_DIR
    topic = _find(load_topics(topics_dir), args.slug)
    target = _target_date(directory)
    try:
        raw = json.loads(args.json)
    except json.JSONDecodeError as exc:
        raise LogError(f"--json: not valid JSON ({exc})") from exc
    item = _parse_evidence(raw, len(topic.evidence), Path("--json"))
    prior_passes = _consecutive_passes(topic.evidence)
    topic.evidence.append(item)
    passed = item.result == "correct"
    if item.surprise:
        topic.next_due = next_due(item.date, prior_passes, passed, topic.tier, target)
    elif topic.next_due is None:
        topic.next_due = next_due(item.date, 0, True, topic.tier, target)
    save_topic(topic, topics_dir)
    print(f"recorded; next due {topic.next_due}")


def _cmd_block_action(args, directory: Path) -> None:
    state = _read_state(directory)
    chosen, overflow = plan_block(load_topics(directory / _TOPICS_DIR), args.block_date)
    print(block_action(state, len(chosen) + overflow, args.block_date))
    if state is not None and overflowing(state["overflow_history"]):
        print("warning: overflow two weeks running, more topics are due than the block holds")


def _cmd_clock(args, directory: Path) -> None:
    file = directory / _CLOCK_FILE
    if args.action == "start":
        directory.mkdir(parents=True, exist_ok=True)
        file.write_text(datetime.now().isoformat(), encoding="utf-8")
        print("session clock started")
        return
    if not file.exists():
        raise LogError(f"{file.name}: session clock was never started")
    try:
        start = datetime.fromisoformat(file.read_text(encoding="utf-8").strip())
    except ValueError as exc:
        raise LogError(f"{file.name}: not a valid timestamp ({exc})") from exc
    print(f"{minutes_left(start, datetime.now())} minutes left")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tutor evidence log")
    sub = parser.add_subparsers(dest="command", required=True)

    def command(name: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name)
        p.add_argument("--data", type=Path, default=None, help="log directory (default: HOME/data)")
        return p

    due = command("due")
    due.add_argument("--for", dest="target", choices=("session", "block"), required=True)
    due.add_argument("--today", type=date.fromisoformat)
    due.add_argument("--block-date", type=date.fromisoformat)
    command("level").add_argument("slug")
    command("summary").add_argument("slug")
    record = command("record")
    record.add_argument("slug")
    record.add_argument("--json", required=True)
    command("block-action").add_argument("--block-date", type=date.fromisoformat, required=True)
    command("clock").add_argument("action", choices=("start", "left"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    directory = args.data or home() / "data"
    try:
        if args.command == "due":
            _cmd_due(args, directory)
        elif args.command == "level":
            print(level_from_evidence(_find(load_topics(directory / _TOPICS_DIR), args.slug).evidence) or "none")
        elif args.command == "summary":
            print(confidence_summary(_find(load_topics(directory / _TOPICS_DIR), args.slug).evidence) or "no evidence")
        elif args.command == "record":
            _cmd_record(args, directory)
        elif args.command == "block-action":
            _cmd_block_action(args, directory)
        else:
            _cmd_clock(args, directory)
    except LogError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
