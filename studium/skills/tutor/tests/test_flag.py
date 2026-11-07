import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import flag
from flag import FlagError, find_note, new_bytes, set_flag

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "flag.py"

FM = b"---\ntype: concept\nconfidence: 0\n---\n\n# Title\nBody \xff bytes\n"


def test_adds_property_before_closing_fence():
    assert new_bytes(FM, "good") == b"---\ntype: concept\nconfidence: 0\nunderstanding: good\n---\n\n# Title\nBody \xff bytes\n"


def test_replaces_in_place():
    with_flag = new_bytes(FM, "good")
    assert new_bytes(with_flag, "deep") == with_flag.replace(b"good", b"deep")


def test_round_trip_restores_exact_bytes():
    assert new_bytes(new_bytes(FM, "good"), None) == FM


def test_no_frontmatter_round_trip():
    body = b"# Note\ntext\n"
    assert new_bytes(body, "moderate") == b"---\nunderstanding: moderate\n---\n" + body
    assert new_bytes(new_bytes(body, "moderate"), None) == body


def test_crlf_is_preserved():
    crlf = FM.replace(b"\n", b"\r\n")
    assert b"understanding: good\r\n---\r\n" in new_bytes(crlf, "good")
    assert new_bytes(new_bytes(crlf, "good"), None) == crlf


def test_refuses_unclosed_frontmatter_and_bom():
    for bad in (b"---\ntype: x\nno close\n", b"\xef\xbb\xbf---\na: b\n---\n"):
        with pytest.raises(FlagError):
            new_bytes(bad, "good")


def test_body_containing_a_fence_or_the_word_is_untouched():
    note = b"---\na: b\n---\nunderstanding: keep me\n---\n"
    assert new_bytes(note, "good") == b"---\na: b\nunderstanding: good\n---\nunderstanding: keep me\n---\n"


def test_removing_absent_flag_returns_input_unchanged():
    assert new_bytes(FM, None) == FM
    assert new_bytes(b"# plain\n", None) == b"# plain\n"
    assert new_bytes(b"---\n---\nx", None) == b"---\n---\nx"


def test_closing_fence_at_end_of_file_without_newline():
    assert new_bytes(b"---\na: b\n---", "good") == b"---\na: b\nunderstanding: good\n---"


def test_removal_deletes_only_a_preexisting_flag_line():
    note = b"---\na: b\nunderstanding: 3\nc: d\n---\nbody\n"
    assert new_bytes(note, None) == b"---\na: b\nc: d\n---\nbody\n"


def test_refuses_duplicate_or_multiline_flag():
    for bad in (b"---\nunderstanding: a\nunderstanding: b\n---\n",
                b"---\nunderstanding:\n  - a\n---\n"):
        with pytest.raises(FlagError):
            new_bytes(bad, "good")


def test_rejects_unknown_level():
    for bad in ("great", "", "None", "GOOD"):
        with pytest.raises(FlagError):
            new_bytes(FM, bad)


def test_refuses_setting_on_empty_or_whitespace_note():
    for empty in (b"", b"  \n\t\n"):
        with pytest.raises(FlagError):
            new_bytes(empty, "good")
        assert new_bytes(empty, None) == empty


# ---- set_flag on real files ----

def make_vault(tmp_path):
    vault = tmp_path / "vault"
    (vault / "sub").mkdir(parents=True)
    (vault / ".obsidian").mkdir()
    (vault / "a.md").write_bytes(FM)
    (vault / "sub" / "b.md").write_bytes(b"# no fm\r\n")
    (vault / "empty.md").write_bytes(b"")
    (vault / "notes.txt").write_bytes(b"text")
    (vault / ".obsidian" / "x.md").write_bytes(b"x")
    return vault, tmp_path / "backups"


def snapshot(root):
    return {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def test_set_flag_changes_only_that_file(tmp_path):
    vault, backups = make_vault(tmp_path)
    before = snapshot(vault)
    msg = set_flag(vault / "a.md", "good", vault, backups)
    after = snapshot(vault)
    assert "good" in msg
    assert [k for k in before if before[k] != after[k]] == [Path("a.md")]
    assert set(before) == set(after)
    assert (vault / "a.md").read_bytes() == new_bytes(FM, "good")
    files = list(backups.iterdir())
    assert len(files) == 1 and files[0].read_bytes() == FM


def test_two_writes_to_same_note_keep_two_backups(tmp_path):
    vault, backups = make_vault(tmp_path)
    set_flag(vault / "a.md", "good", vault, backups)
    set_flag(vault / "a.md", "deep", vault, backups)
    assert len(list(backups.iterdir())) == 2


def test_set_flag_then_none_restores_file(tmp_path):
    vault, backups = make_vault(tmp_path)
    before = snapshot(vault)
    set_flag(vault / "sub" / "b.md", "deep", vault, backups)
    set_flag(vault / "sub" / "b.md", None, vault, backups)
    assert snapshot(vault) == before


def test_set_flag_unchanged_writes_no_backup(tmp_path):
    vault, backups = make_vault(tmp_path)
    assert "unchanged" in set_flag(vault / "a.md", None, vault, backups)
    assert not backups.exists()
    set_flag(vault / "a.md", "good", vault, backups)
    n = len(list(backups.iterdir()))
    assert "unchanged" in set_flag(vault / "a.md", "good", vault, backups)
    assert len(list(backups.iterdir())) == n


def test_set_flag_refuses_empty_note(tmp_path):
    vault, backups = make_vault(tmp_path)
    (vault / "ws.md").write_bytes(b" \n\n")
    for name in ("empty.md", "ws.md"):
        with pytest.raises(FlagError):
            set_flag(vault / name, "good", vault, backups)
    assert (vault / "empty.md").read_bytes() == b""
    assert "unchanged" in set_flag(vault / "empty.md", None, vault, backups)
    assert not backups.exists()


def test_set_flag_refuses_outside_vault(tmp_path):
    vault, backups = make_vault(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_bytes(b"secret\n")
    (vault / "link.md").symlink_to(outside)
    for target in (outside, vault / "link.md", vault / ".." / "outside.md",
                   vault / "sub" / ".." / ".." / "outside.md"):
        with pytest.raises(FlagError):
            set_flag(target, "good", vault, backups)
    assert outside.read_bytes() == b"secret\n"
    assert not backups.exists()


def test_set_flag_refuses_non_markdown_and_dot_obsidian(tmp_path):
    vault, backups = make_vault(tmp_path)
    (vault / ".trash").mkdir()
    (vault / ".trash" / "t.md").write_bytes(b"t")
    for name in ("notes.txt", ".obsidian/x.md", ".trash/t.md"):
        with pytest.raises(FlagError):
            set_flag(vault / name, "good", vault, backups)
    assert not backups.exists()


def test_set_flag_refuses_missing_note_and_creates_nothing(tmp_path):
    vault, backups = make_vault(tmp_path)
    before = snapshot(vault)
    with pytest.raises(FlagError):
        set_flag(vault / "nope.md", "good", vault, backups)
    with pytest.raises(FlagError):
        set_flag(vault / "sub", "good", vault, backups)
    assert snapshot(vault) == before
    assert not backups.exists()


def test_set_flag_refuses_backup_dir_inside_vault(tmp_path):
    vault, _ = make_vault(tmp_path)
    with pytest.raises(FlagError):
        set_flag(vault / "a.md", "good", vault, vault / "backups")
    assert (vault / "a.md").read_bytes() == FM


def test_set_flag_refuses_if_file_changed_since_read(tmp_path, monkeypatch):
    vault, backups = make_vault(tmp_path)
    note = vault / "a.md"
    real_read = flag._read
    calls = []

    def racing_read(path):
        data = real_read(path)
        calls.append(1)
        if len(calls) == 1:
            path.write_bytes(data + b"edited meanwhile\n")
        return data

    monkeypatch.setattr(flag, "_read", racing_read)
    with pytest.raises(FlagError, match="changed"):
        set_flag(note, "good", vault, backups)
    assert note.read_bytes() == FM + b"edited meanwhile\n"


def test_set_flag_refuses_malformed_note_untouched(tmp_path):
    vault, backups = make_vault(tmp_path)
    (vault / "bad.md").write_bytes(b"---\nunclosed\n")
    with pytest.raises(FlagError):
        set_flag(vault / "bad.md", "good", vault, backups)
    assert (vault / "bad.md").read_bytes() == b"---\nunclosed\n"
    assert not backups.exists()


# ---- find_note ----

def test_find_note_recorded_path_wins(tmp_path):
    vault, _ = make_vault(tmp_path)
    (vault / "other").mkdir()
    (vault / "other" / "a.md").write_bytes(b"dup")
    assert find_note(vault, "a.md", "a") == [vault / "a.md"]


def test_find_note_by_title_after_move(tmp_path):
    vault, _ = make_vault(tmp_path)
    (vault / "moved").mkdir()
    (vault / "moved" / "Gradient Descent.md").write_bytes(b"x")
    assert find_note(vault, "old/place.md", "gradient descent") == [vault / "moved" / "Gradient Descent.md"]


def test_find_note_returns_all_matches_when_ambiguous(tmp_path):
    vault, _ = make_vault(tmp_path)
    (vault / "x").mkdir()
    (vault / "y").mkdir()
    (vault / "x" / "Topic.md").write_bytes(b"1")
    (vault / "y" / "topic.md").write_bytes(b"2")
    assert find_note(vault, "gone.md", "TOPIC") == [vault / "x" / "Topic.md", vault / "y" / "topic.md"]


def test_find_note_not_found_and_excluded_dirs(tmp_path):
    vault, _ = make_vault(tmp_path)
    assert find_note(vault, "gone.md", "x") == []
    assert find_note(vault, ".obsidian/x.md", "x") == []
    assert find_note(vault, "", "nothing") == []


# ---- CLI ----

def run_cli(home, *args):
    env = {**os.environ, "TUTOR_HOME": str(home)}
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


def write_config(home, vault):
    (home / "data").mkdir(parents=True, exist_ok=True)
    (home / "data" / "config.json").write_text(json.dumps({"vault": str(vault)}))


def test_cli_set_and_remove(tmp_path):
    vault, _ = make_vault(tmp_path)
    home = tmp_path / "home"
    write_config(home, vault)
    r = run_cli(home, "set", str(vault / "a.md"), "good")
    assert r.returncode == 0, r.stderr
    assert (vault / "a.md").read_bytes() == new_bytes(FM, "good")
    assert len(list((home / "data" / "flag_backups").iterdir())) == 1
    r = run_cli(home, "set", "a.md", "none")
    assert r.returncode == 0, r.stderr
    assert (vault / "a.md").read_bytes() == FM


def test_cli_find(tmp_path):
    vault, _ = make_vault(tmp_path)
    home = tmp_path / "home"
    write_config(home, vault)
    r = run_cli(home, "find", "gone.md", "b")
    assert r.returncode == 0
    assert r.stdout.split() == [str(vault / "sub" / "b.md")]
    assert run_cli(home, "find", "gone.md", "zzz").stdout == ""


def test_cli_missing_or_invalid_config_names_the_file(tmp_path):
    home = tmp_path / "home"
    r = run_cli(home, "find", "a.md", "a")
    assert r.returncode == 2 and "config.json" in r.stderr
    (home / "data").mkdir(parents=True)
    (home / "data" / "config.json").write_text("{not json")
    r = run_cli(home, "find", "a.md", "a")
    assert r.returncode == 2 and "config.json" in r.stderr
    write_config(home, tmp_path / "does-not-exist")
    r = run_cli(home, "find", "a.md", "a")
    assert r.returncode == 2 and "config.json" in r.stderr
    (home / "data" / "config.json").write_text("{}")
    r = run_cli(home, "find", "a.md", "a")
    assert r.returncode == 2 and "vault" in r.stderr


def test_cli_rejects_bad_level(tmp_path):
    vault, _ = make_vault(tmp_path)
    home = tmp_path / "home"
    write_config(home, vault)
    r = run_cli(home, "set", "a.md", "great")
    assert r.returncode != 0
    assert (vault / "a.md").read_bytes() == FM
