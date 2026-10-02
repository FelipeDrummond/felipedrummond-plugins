import datetime as dt
from pathlib import Path

import pytest

import vault

TODAY = dt.date(2026, 10, 20)


def write_note(
    root: Path,
    name: str,
    confidence: int = 0,
    last_tested: str = "",
    topics: tuple[str, ...] = ("Math",),
    tag: str = "s/draft",
    body: str = "# Title\n\nMy explanation.\n",
) -> Path:
    topic_lines = "".join(f'  - "[[{t}]]"\n' for t in topics)
    path = root / "concepts" / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        "---\n"
        "type: concept\n"
        "created: 2026-10-01\n"
        f"topics:\n{topic_lines}"
        "aliases: []\n"
        f"confidence: {confidence}\n"
        f"last_tested: {last_tested}\n".replace(": \n", ":\n")
        + "prereqs: []\n"
        "sources: []\n"
        "tags:\n"
        f"  - {tag}\n"
        "---\n\n" + body
    )
    return path


def test_status_sorts_notes_into_buckets(tmp_path: Path) -> None:
    write_note(tmp_path, "Overdue", confidence=2, last_tested="2026-10-10")
    write_note(tmp_path, "Due today", confidence=3, last_tested="2026-10-13")
    write_note(tmp_path, "Not yet", confidence=4, last_tested="2026-10-10")
    write_note(tmp_path, "Never examined")
    write_note(tmp_path, "Stub", tag="s/gap", body="# Stub\n")

    status = vault.review_status(tmp_path, TODAY)

    assert [n.title for n in status.due] == ["Overdue", "Due today"]
    assert [n.title for n in status.untested] == ["Never examined"]
    assert [n.title for n in status.gaps] == ["Stub"]
    assert status.next_due == dt.date(2026, 10, 26)


def test_status_filters_by_topic(tmp_path: Path) -> None:
    write_note(tmp_path, "Jacobian", 1, "2026-10-01", topics=("Robot Dynamics", "Math"))
    write_note(tmp_path, "Subspaces", 1, "2026-10-01", topics=("Math",))

    status = vault.review_status(tmp_path, TODAY, topic="robot dynamics")

    assert [n.title for n in status.due] == ["Jacobian"]


@pytest.mark.parametrize(
    ("before", "grade", "after"),
    [
        (0, "solid", 1),
        (0, "miss", 1),
        (2, "solid", 3),
        (5, "solid", 5),
        (3, "partial", 3),
        (0, "partial", 1),
        (4, "miss", 1),
    ],
)
def test_next_confidence(before: int, grade: str, after: int) -> None:
    assert vault.next_confidence(before, grade) == after


def test_record_updates_frontmatter_and_leaves_body_alone(tmp_path: Path) -> None:
    body = "# Subspaces\n\nA subset that is itself a vector space.\n\n## Connections\n\n- [[Vector Spaces]]\n"
    path = write_note(tmp_path, "Subspaces", confidence=2, last_tested="2026-10-10", body=body)

    next_due = vault.record(path, "solid", TODAY, predicted="partial", comment="clean proof")

    text = path.read_text()
    assert "confidence: 3\n" in text
    assert "last_tested: 2026-10-20\n" in text
    assert body.rstrip("\n") in text
    assert text.endswith(
        "## Review log\n\n- 2026-10-20: solid (predicted partial) → confidence 3. clean proof\n"
    )
    assert next_due == dt.date(2026, 10, 27)


def test_record_appends_to_existing_log_before_later_sections(tmp_path: Path) -> None:
    body = "# T\n\nText.\n\n## Review log\n\n- 2026-10-10: miss → confidence 1.\n\n## References\n\n- [[src]]\n"
    path = write_note(tmp_path, "T", confidence=1, last_tested="2026-10-10", body=body)

    vault.record(path, "partial", TODAY)

    text = path.read_text()
    assert (
        "- 2026-10-10: miss → confidence 1.\n"
        "- 2026-10-20: partial → confidence 1.\n\n"
        "## References\n"
    ) in text
    assert text.count("## Review log") == 1


def test_profile_shows_what_the_student_knows_weakest_first(tmp_path: Path) -> None:
    write_note(tmp_path, "Vector Spaces", confidence=4, last_tested="2026-10-15")
    write_note(tmp_path, "Basis", tag="s/gap", body="# Basis\n")
    subspaces = write_note(
        tmp_path,
        "Subspaces",
        confidence=2,
        last_tested="2026-10-10",
        body=(
            "# Subspaces\n\nMy explanation.\n\n"
            "## Open questions\n\n- Does the empty set pass the test?\n\n"
            "## Review log\n\n"
            "- 2026-09-20: solid → confidence 2.\n"
            "- 2026-10-01: miss (predicted solid) → confidence 1. said any line is a subspace\n"
            "- 2026-10-10: solid → confidence 2. clean\n"
        ),
    )
    subspaces.write_text(
        subspaces.read_text().replace(
            "prereqs: []", 'prereqs:\n  - "[[Vector Spaces]]"\n  - "[[Basis]]"\n  - "[[Fields]]"'
        )
    )

    profile = vault.format_profile(vault.load_notes(tmp_path), vault.load_notes(tmp_path), TODAY)

    lines = profile.split("\n")
    titles = [line.split(" · ")[0] for line in lines if line and not line.startswith(" ")]
    assert titles[1:] == ["Basis", "Subspaces", "Vector Spaces"]
    assert "Subspaces · box 2 · tested 2026-10-10 · due" in profile
    assert "Vector Spaces · box 4 · tested 2026-10-15" in profile
    assert "Basis · stub, not written" in profile
    assert "    prereqs: Vector Spaces (box 4), Basis (stub), Fields (no note)" in profile
    assert "    open: Does the empty set pass the test?" in profile
    assert "said any line is a subspace" in profile
    assert "2026-09-20" not in profile  # only the two most recent log entries


@pytest.mark.parametrize("vault_first", [True, False])
def test_vault_option_works_before_or_after_the_subcommand(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], vault_first: bool
) -> None:
    write_note(tmp_path, "Subspaces", confidence=2, last_tested="2026-10-10")
    option = ["--vault", str(tmp_path), "--today", "2026-10-20"]

    vault.main(option + ["profile"] if vault_first else ["profile"] + option)

    assert "Subspaces · box 2 · tested 2026-10-10 · due" in capsys.readouterr().out


def test_record_fails_loudly_on_note_without_schedule_fields(tmp_path: Path) -> None:
    path = tmp_path / "plain.md"
    path.write_text("---\ntype: map\n---\n\n# Map\n")

    with pytest.raises(ValueError, match="confidence"):
        vault.record(path, "solid", TODAY)
