"""Vault flag writer: the only code that writes to the vault, and only the `understanding` property.

Works in bytes throughout. Any doubt about a note's shape raises FlagError and leaves it untouched.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from tutorlog import home

LEVELS = ("moderate", "good", "deep")
EXCLUDED_DIRS = (".obsidian", ".trash", ".git")
_BOM = b"\xef\xbb\xbf"
_FLAG_LINE = re.compile(rb"understanding[ \t]*:")


class FlagError(Exception):
    """A flag change was refused or failed verification. The note is left as it was."""


def _eol(line: bytes) -> bytes:
    for eol in (b"\r\n", b"\n", b"\r"):
        if line.endswith(eol):
            return eol
    return b""


def _is_fence(line: bytes) -> bool:
    return line.rstrip(b"\r\n \t") == b"---"


def new_bytes(original: bytes, level: str | None) -> bytes:
    """Return `original` with the understanding property set to `level`, or removed if None."""
    if level is not None and level not in LEVELS:
        raise FlagError(f"unknown level {level!r}; expected one of {', '.join(LEVELS)} or none")
    if not original.strip():
        if level is not None:
            raise FlagError("note is empty; refusing to set a flag on it")
        return original
    if original.startswith(_BOM):
        raise FlagError("note starts with a byte-order mark; refusing to edit it")

    lines = original.splitlines(keepends=True)
    if not _is_fence(lines[0]):
        if level is None:
            return original
        eol = _eol(lines[0]) or b"\n"
        return b"---" + eol + b"understanding: " + level.encode() + eol + b"---" + eol + original

    eol = _eol(lines[0]) or b"\n"
    close = next((i for i in range(1, len(lines)) if _is_fence(lines[i])), None)
    if close is None:
        raise FlagError("frontmatter is never closed; refusing to edit the note")

    hits = [i for i in range(1, close) if _FLAG_LINE.match(lines[i])]
    if len(hits) > 1:
        raise FlagError("frontmatter has more than one understanding property; refusing to edit the note")
    if hits:
        nxt = lines[hits[0] + 1]
        if nxt[:1] in (b" ", b"\t") or nxt.startswith(b"- "):
            raise FlagError("the existing understanding property spans several lines; refusing to edit the note")

    if level is None:
        if not hits:
            return original
        kept = lines[:hits[0]] + lines[hits[0] + 1:]
        if close == 2:  # the flag was the only property, so the block was ours: drop the whole thing
            return b"".join(lines[close + 1:])
        return b"".join(kept)

    new_line = b"understanding: " + level.encode() + (_eol(lines[hits[0]]) if hits else eol)
    if hits:
        lines[hits[0]] = new_line
    else:
        lines.insert(close, new_line)
    return b"".join(lines)


def _only_flag_changed(original: bytes, result: bytes) -> bool:
    """True if the two differ by exactly one understanding line (added, removed or replaced),
    or by the fence/flag/fence block added to or removed from the top of a note without frontmatter."""
    a, b = original.splitlines(keepends=True), result.splitlines(keepends=True)
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        return len(diff) == 1 and bool(_FLAG_LINE.match(a[diff[0]])) and bool(_FLAG_LINE.match(b[diff[0]]))
    longer, shorter = (a, b) if len(a) > len(b) else (b, a)
    if len(longer) - len(shorter) == 1:
        i = next((i for i in range(len(shorter)) if longer[i] != shorter[i]), len(shorter))
        return bool(_FLAG_LINE.match(longer[i])) and longer[i + 1:] == shorter[i:]
    if len(longer) - len(shorter) == 3:
        return (_is_fence(longer[0]) and bool(_FLAG_LINE.match(longer[1])) and _is_fence(longer[2])
                and longer[3:] == shorter and not (shorter and _is_fence(shorter[0])))
    return False


def _read(path: Path) -> bytes:
    return path.read_bytes()


def _rel(note: Path, vault: Path) -> Path:
    """Resolve `note` and return its path relative to `vault`, or raise FlagError."""
    vault_real = vault.resolve()
    real = note.resolve()
    try:
        rel = real.relative_to(vault_real)
    except ValueError:
        raise FlagError(f"{note} is outside the vault; refusing to edit it") from None
    if real.suffix.lower() != ".md":
        raise FlagError(f"{note} is not a markdown file; refusing to edit it")
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        raise FlagError(f"{note} is inside a reserved vault folder; refusing to edit it")
    return rel


def _backup(original: bytes, rel: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    flat = "__".join(rel.parts)
    for n in range(1000):
        target = backup_dir / f"{stamp}{'' if n == 0 else f'-{n}'}__{flat}"
        try:
            with open(target, "xb") as fh:
                fh.write(original)
            break
        except FileExistsError:
            continue
    else:
        raise FlagError(f"could not find a free backup name in {backup_dir}")
    if target.read_bytes() != original:
        raise FlagError(f"backup {target} does not match the note; nothing was changed")
    return target


def set_flag(note: Path, level: str | None, vault: Path, backup_dir: Path) -> str:
    """Set or remove the understanding property on one note. Returns what changed."""
    rel = _rel(note, vault)
    if backup_dir.resolve().is_relative_to(vault.resolve()):
        raise FlagError(f"backup folder {backup_dir} is inside the vault; refusing to write")
    real = note.resolve()
    if not real.is_file():
        raise FlagError(f"{note} does not exist; nothing was changed")

    original = _read(real)
    result = new_bytes(original, level)
    if result == original:
        return "unchanged"

    expected_without_flag = new_bytes(original, None)
    if new_bytes(result, None) != expected_without_flag:
        raise FlagError(f"{note}: removing the flag from the new content would not give back the original; nothing was changed")
    if not _only_flag_changed(original, result):
        raise FlagError(f"{note}: the new content changes more than the understanding line; nothing was changed")

    backup = _backup(original, rel, backup_dir)
    if _read(real) != original:
        raise FlagError(f"{note} changed since it was read; nothing was written (backup: {backup})")

    with open(real, "r+b") as fh:
        fh.write(result)
        fh.truncate()
    if _read(real) != result:
        with open(real, "r+b") as fh:
            fh.write(original)
            fh.truncate()
        raise FlagError(f"{note}: read-back did not match what was written; original restored from memory (backup: {backup})")

    old = new_bytes(original, None) != original
    if level is None:
        return "removed understanding"
    return f"{'changed' if old else 'added'} understanding: {level}"


def find_note(vault: Path, recorded: str, title: str) -> list[Path]:
    """The recorded path if it exists, else every .md whose stem equals `title` (case-insensitive)."""
    if recorded:
        candidate = vault / recorded
        if candidate.is_file() and not any(p in EXCLUDED_DIRS for p in Path(recorded).parts):
            return [candidate]
    wanted = title.lower()
    found = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in sorted(files):
            path = Path(name)
            if path.suffix.lower() == ".md" and path.stem.lower() == wanted:
                found.append(Path(root) / name)
    return sorted(found)


def _vault_from_config() -> Path:
    config = home() / "data" / "config.json"
    try:
        data = json.loads(config.read_text())
    except FileNotFoundError:
        raise FlagError(f"{config}: file not found") from None
    except (OSError, ValueError) as exc:
        raise FlagError(f"{config}: unreadable ({exc})") from exc
    value = data.get("vault") if isinstance(data, dict) else None
    if not isinstance(value, str) or not value:
        raise FlagError(f"{config}: field 'vault' must be a non-empty path string")
    vault = Path(value).expanduser()
    if not vault.is_dir():
        raise FlagError(f"{config}: field 'vault' is not a folder: {vault}")
    return vault


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vault flag writer")
    sub = parser.add_subparsers(dest="command", required=True)
    p_set = sub.add_parser("set", help="set or remove the understanding flag on a note")
    p_set.add_argument("note", help="absolute path, or path relative to the vault")
    p_set.add_argument("level", choices=(*LEVELS, "none"))
    p_find = sub.add_parser("find", help="locate a note by recorded path, then by title")
    p_find.add_argument("recorded", help="vault-relative path recorded earlier")
    p_find.add_argument("title")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        vault = _vault_from_config()
        if args.command == "set":
            level = None if args.level == "none" else args.level
            print(set_flag(vault / args.note, level, vault, home() / "data" / "flag_backups"))
        else:
            for path in find_note(vault, args.recorded, args.title):
                print(path)
    except FlagError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
