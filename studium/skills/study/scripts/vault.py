#!/usr/bin/env python3
"""What the student knows, read from the concept notes in the Obsidian vault.

A concept note's `confidence` is its Leitner box (0 = never tested, 1-5 = earned by
review results) and `last_tested` is the date of its last review. Both live in the
note's frontmatter, so the schedule is readable and editable in Obsidian itself.

    vault.py profile [--topic NAME]
    vault.py status [--topic NAME]
    vault.py record NOTE {solid,partial,miss} [--predicted GRADE] [--comment TEXT]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_VAULT = Path.home() / "Documents" / "Obsidian Vault"
INTERVAL_DAYS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
GRADES = ("solid", "partial", "miss")
LOG_HEADING = "## Review log"
QUESTIONS_HEADING = "## Open questions"
GAP_TAG = "s/gap"


@dataclass
class Note:
    path: Path
    confidence: int
    last_tested: dt.date | None
    topics: list[str]
    tags: list[str]
    prereqs: list[str]
    log: list[str]
    questions: list[str]

    @property
    def title(self) -> str:
        return self.path.stem

    @property
    def level(self) -> str:
        """How well the note is known, in a word or two."""
        if GAP_TAG in self.tags:
            return "stub"
        return f"box {self.confidence}" if self.last_tested else "untested"

    @property
    def due(self) -> dt.date | None:
        if self.last_tested is None:
            return None
        box = min(max(self.confidence, 1), 5)
        return self.last_tested + dt.timedelta(days=INTERVAL_DAYS[box])


@dataclass
class Status:
    due: list[Note]
    untested: list[Note]
    gaps: list[Note]
    next_due: dt.date | None


def split_note(text: str) -> tuple[list[str], list[str]]:
    """Split a note into frontmatter lines and body lines (delimiters dropped)."""
    lines = text.split("\n")
    if lines[0].strip() != "---" or "---" not in (line.strip() for line in lines[1:]):
        raise ValueError("note has no frontmatter")
    end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    return lines[1:end], lines[end + 1 :]


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Parse the flat YAML that Obsidian writes into (scalar fields, block-list fields)."""
    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {}
    key = None
    for line in lines:
        if match := re.match(r"^([\w-]+):\s*(.*)$", line):
            key = match.group(1)
            scalars[key] = match.group(2).strip()
        elif key and (item := re.match(r"^\s+-\s+(.*)$", line)):
            lists.setdefault(key, []).append(item.group(1).strip())
    return scalars, lists


def link_name(value: str) -> str:
    """'"[[Math|maths]]"' -> 'Math'."""
    return value.strip("\"'").removeprefix("[[").removesuffix("]]").split("|")[0]


def section_items(body: list[str], heading: str) -> list[str]:
    """The list items under a heading, without their leading dash."""
    if heading not in body:
        return []
    start = body.index(heading) + 1
    end = next((i for i in range(start, len(body)) if body[i].startswith("#")), len(body))
    return [line[2:].strip() for line in body[start:end] if line.startswith("- ")]


def load_note(path: Path) -> Note | None:
    """Return the note if it is a concept note, else None."""
    try:
        frontmatter, body = split_note(path.read_text())
    except ValueError:
        return None
    scalars, lists = parse_frontmatter(frontmatter)
    if scalars.get("type") != "concept":
        return None
    tested = scalars.get("last_tested")
    return Note(
        path=path,
        confidence=int(scalars.get("confidence") or 0),
        last_tested=dt.date.fromisoformat(tested) if tested else None,
        topics=[link_name(t) for t in lists.get("topics", [])],
        tags=lists.get("tags", []),
        prereqs=[link_name(p) for p in lists.get("prereqs", [])],
        log=section_items(body, LOG_HEADING),
        questions=section_items(body, QUESTIONS_HEADING),
    )


def load_notes(vault: Path, topic: str | None = None) -> list[Note]:
    notes = [n for p in sorted((vault / "concepts").rglob("*.md")) if (n := load_note(p))]
    if topic:
        notes = [n for n in notes if topic.lower() in (t.lower() for t in n.topics)]
    return notes


def format_profile(notes: list[Note], all_notes: list[Note], today: dt.date) -> str:
    """A snapshot of what the student knows: weakest notes first, with the evidence."""
    by_title = {n.title.lower(): n for n in all_notes}
    weakness = {"stub": -2, "untested": -1}

    out = [f"Knowledge profile on {today.isoformat()} ({len(notes)} concept notes)"]
    for note in sorted(notes, key=lambda n: (weakness.get(n.level, n.confidence), n.title)):
        if note.level == "stub":
            state = "stub, not written"
        elif note.level == "untested":
            state = "written, never tested"
        else:
            due = " · due" if (d := note.due) and d <= today else ""
            state = f"{note.level} · tested {note.last_tested}{due}"
        out.append(f"{note.title} · {state}")
        if note.prereqs:
            levels = (
                f"{p} ({known.level if (known := by_title.get(p.lower())) else 'no note'})"
                for p in note.prereqs
            )
            out.append(f"    prereqs: {', '.join(levels)}")
        out += [f"    open: {question}" for question in note.questions]
        out += [f"    log: {entry}" for entry in note.log[-2:]]
    return "\n".join(out)


def review_status(vault: Path, today: dt.date, topic: str | None = None) -> Status:
    notes = load_notes(vault, topic)

    gaps = [n for n in notes if GAP_TAG in n.tags]
    written = [n for n in notes if GAP_TAG not in n.tags]
    untested = [n for n in written if n.due is None]
    scheduled = sorted(
        ((due, n) for n in written if (due := n.due) is not None), key=lambda pair: pair[0]
    )
    due_now = [n for due, n in scheduled if due <= today]
    upcoming = [due for due, _ in scheduled if due > today]
    return Status(due_now, untested, gaps, min(upcoming, default=None))


def next_confidence(confidence: int, grade: str) -> int:
    if grade == "solid":
        return min(confidence + 1, 5)
    if grade == "partial":
        return max(confidence, 1)
    return 1


def set_field(frontmatter: list[str], key: str, value: str) -> None:
    for i, line in enumerate(frontmatter):
        if re.match(rf"^{key}:", line):
            frontmatter[i] = f"{key}: {value}"
            return
    raise ValueError(f"frontmatter has no `{key}` field; is this a concept note?")


def append_log(body: list[str], entry: str) -> None:
    """Add an entry to the note's review log, creating the section at the end if needed."""
    if LOG_HEADING not in body:
        while body and not body[-1].strip():
            body.pop()
        body += ["", LOG_HEADING, "", entry, ""]
        return
    start = body.index(LOG_HEADING)
    end = next(
        (i for i in range(start + 1, len(body)) if body[i].startswith("#")), len(body)
    )
    while not body[end - 1].strip():
        end -= 1
    body.insert(end, entry)


def record(
    path: Path,
    grade: str,
    today: dt.date,
    predicted: str | None = None,
    comment: str = "",
) -> dt.date:
    """Write a review result into the note and return its next due date."""
    frontmatter, body = split_note(path.read_text())
    scalars, _ = parse_frontmatter(frontmatter)
    confidence = next_confidence(int(scalars.get("confidence") or 0), grade)

    set_field(frontmatter, "confidence", str(confidence))
    set_field(frontmatter, "last_tested", today.isoformat())
    prediction = f" (predicted {predicted})" if predicted else ""
    entry = f"- {today.isoformat()}: {grade}{prediction} → confidence {confidence}. {comment}"
    append_log(body, entry.rstrip())

    path.write_text("\n".join(["---", *frontmatter, "---", *body]))
    return today + dt.timedelta(days=INTERVAL_DAYS[confidence])


def format_status(status: Status, vault: Path, today: dt.date) -> str:
    def row(note: Note, prefix: str = "") -> str:
        topics = ", ".join(note.topics) or "no topic"
        return f"  {prefix}{note.title}  [{topics}]  {note.path.relative_to(vault)}"

    out = [f"Review status on {today.isoformat()}", "", f"DUE ({len(status.due)})"]
    out += [
        row(n, f"{(today - due).days}d overdue · box {n.confidence} · ")
        for n in status.due
        if (due := n.due)
    ]
    out += ["", f"UNTESTED: written, never examined ({len(status.untested)})"]
    out += [row(n) for n in status.untested]
    out += ["", f"GAPS: stubs still to write ({len(status.gaps)})"]
    out += [row(n) for n in status.gaps]
    if status.next_due:
        out += ["", f"Next scheduled review falls due on {status.next_due.isoformat()}"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="What the student knows, from the vault.")
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    commands = parser.add_subparsers(dest="command", required=True)

    # The same two options again, so they also work after the subcommand.
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--vault", type=Path, default=argparse.SUPPRESS)
    shared.add_argument("--today", type=dt.date.fromisoformat, default=argparse.SUPPRESS)

    for name, text in [
        ("profile", "what the student knows: every note's level, prereqs and recent results"),
        ("status", "list due, untested and stub notes"),
    ]:
        command = commands.add_parser(name, help=text, parents=[shared])
        command.add_argument("--topic", help="only notes whose topics include this name")

    rec = commands.add_parser("record", help="write a review result into a note", parents=[shared])
    rec.add_argument("note", type=Path)
    rec.add_argument("grade", choices=GRADES)
    rec.add_argument("--predicted", choices=GRADES)
    rec.add_argument("--comment", default="")

    args = parser.parse_args(argv)
    if args.command == "profile":
        notes = load_notes(args.vault, args.topic)
        print(format_profile(notes, load_notes(args.vault), args.today))
    elif args.command == "status":
        print(format_status(review_status(args.vault, args.today, args.topic), args.vault, args.today))
    else:
        note = args.note if args.note.is_absolute() else args.vault / args.note
        next_due = record(note, args.grade, args.today, args.predicted, args.comment)
        print(f"Recorded {args.grade} for {note.stem}; next review due {next_due.isoformat()}")


if __name__ == "__main__":
    main()
