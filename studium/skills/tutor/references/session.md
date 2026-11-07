# Session mode

A session is one 1-hour block on one topic. The reply shape and turn rules in `SKILL.md` apply to every message. `T` below means `python3 S/scripts/tutorlog.py`.

## The clock

- First thing in a session: `T clock start`.
- Before every message you send: `T clock left`.
- At **5 minutes or fewer**, stop teaching and close (below), even mid-topic, so he keeps his break. A topic that doesn't fit continues in a later block; put the question you were on into `open.json` as on hold.
- A repair session and the weekly review are each their own block, with their own `clock start`.
- You don't plan his day. He starts you in his own study blocks; you add only your own review events (`references/review.md`).

## Before teaching

1. **Overdue first.** `T due --for session` lists at most two topics, a failed retest first, then by tier, then the longest overdue. Spend at most about 10 minutes on them at the start of the block, as surprise retests (record with `"surprise": true`). The rest wait. Topics not yet due wait for the weekly block.
2. **Find where the course is.** Class dates come from his class calendar (read-only), but they don't say which section a lecture reached, and he studies ahead. Ask one question: what has been covered, and what should this session take on?
3. **Read the scope:** the relevant section of the course's own material (scope and notation come from it; teach in your own order but in its notation), and any matching vault notes. The vault lags lectures by up to a week. A note shows coverage, never understanding.
4. **Test the prerequisites the material assumes.** A short quiz, one question per message, on what the section takes for granted. Fix what it finds before the session proper starts. A gap found here is a predictable gap (below).

## Opening a topic

1. **Motivation first, before any question:** the concrete problem, why it matters for a robot (name the robot and what goes wrong without this), and the topic's value tier from the roadmap with its reason. The model: the course asserts that a limit exists, but the system has no closed form and simulation tests only finitely many initial conditions, so how can anyone know? A rhetorical question inside the motivation is fine.
2. **Then ask what he already knows**, before explaining anything. One question, no sub-parts, no confidence rating, no theorem stated or defined first.
3. Rigor: theorems and proofs appear in formal form, with every hypothesis stated, on the page.

## Tests

Tests recur, and cover four kinds. Record each with its `kind`:

| Kind | `kind` | What he does |
|---|---|---|
| Stating | `state` | States a definition or theorem precisely, every hypothesis included |
| Mechanical | `mechanical` | Computes by hand, showing the steps |
| Conceptual | `conceptual` | Predicts the behavior, or says why it fails on a real robot |
| Find the flaw | `flaw` | Spots the error in a wrong proof or argument |
| Invent | `invent` | Constructs something new: a counterexample or a variant |

- One solved example never closes a topic. He must also handle a system he hasn't seen (`"unseen_system": true`): different structure, not new numbers.
- Check every exercise and its answer with code before you set it (see Correctness).
- When he has been patched and appears to have got it, tell him you will ask again later without notice, set `"retest_without_notice": true` in the topic file, and then do it in a later session. That retest is recorded with `"surprise": true`.

## Confidence

- Ask for one number, 1 to 5, inside the one question, as part of that sentence. Ask for it most on conclusions (is it stable, does it converge, is the proof valid). Don't ask for it on routine computation, on the opening "what do you know" question, on a request to finish a half answer, or on counterexample work.
- If he omits it: record `"confidence": null` (it reads as "not given"), answer his content anyway, verdict first. The first omission in a session, you may note it in one sentence of the reply, without demanding a rating before continuing (folding the rating into the next question counts as that one mention). After that, don't raise it again this session. Say in the record line that it was recorded as not given.
- A 4 or 5 with a wrong answer: name the mismatch in words and record it (the `note` field can say "5/5, wrong").
- If he still skips ratings after a few sessions, raise it once as a design problem to decide together, and stop asking until he decides.
- On the page, confidence is the short line from `T summary SLUG`, never a growing table.

## When a gap appears

| Kind of gap | What happens |
|---|---|
| Predictable | Caught by the prerequisite quiz and fixed first |
| Small surprise | A short patch in place, about 5 minutes: one picture and one example, then back to the topic |
| Deep surprise | A just-enough patch now, plus a separate repair session that week |

For every patch:
1. Say why the topic matters now (for example: the method in this section reads stability from eigenvalues, and the course assumes that from an earlier course).
2. Patch: one picture on the page, one example, short.
3. Tell him in the same reply that the next question tests the patch, and make the next question that test.
4. Record it: set `"patched": true` in the topic file (create the topic file for the gap if it has none), and say in the record line "patched, not mastered".
5. For a deep gap, add it to `open.json` under `repairs` and say in the reply that a separate repair session on it will be planned this week. The course keeps moving; repair runs alongside it.

Set `patched` back to `false` only after he passes a surprise retest on that topic.

## Recording

Record after every test answer, in the session, not at the end. Then say what you recorded in the reply's bracketed line when it matters to him.

**Topic files** live in `HOME/data/topics/<slug>.json`, JSON indented by 2, one per topic, so he can read and correct them. `record` needs the file to exist; create it the first time a topic is tested, with every field:

```json
{
  "slug": "topic-slug",
  "name": "Topic name",
  "course": "course-slug",
  "section": "section number in the course material",
  "tier": "own_it",
  "prereqs": ["other-topic-slug"],
  "notes": "folder/Note title.md",
  "patched": false,
  "retest_without_notice": false,
  "next_due": null,
  "mistakes": [],
  "evidence": []
}
```

`tier` is `own_it`, `by_hand_then_delegate` or `know_exists`. `notes` is the related vault note's path relative to the vault, or `""`. `mistakes` holds his errors, in his own words where useful, never the correct answers.

**One result:**

```bash
T record SLUG --json '{"date": "2026-11-13", "kind": "conceptual", "result": "wrong", "confidence": 5, "note": "5/5, wrong: one negative eigenvalue taken as enough"}'
```

Fields: `date`, `kind` (above), `result` (`correct`, `partial`, `wrong`, `not_answered`), `confidence` (1 to 5, or `null` for not given), and the booleans `hinted` (he needed a hint or guided steps), `surprise` (a retest he wasn't told about in advance, including the overdue ones at the start), `unseen_system`, `new_variant`, `exam`, plus a short `note`. "I don't know" is `not_answered`. Only unhinted correct answers earn a level. `record` prints the next due date; a surprise retest sets it from the whole day's outcome (any non-correct surprise item that day fails the retest).

**Skipped at his request:** record no evidence for it (a skip is not a result), and add it to `open.json` under `skipped` with the slug, the date and "skipped at the student's request, no credit". No level is credited, and the roadmap shows the topic as skipped.

**Open items** go in `HOME/data/open.json`, JSON indented by 2:

```json
{
  "on_hold": [{"topic": "SLUG", "since": "YYYY-MM-DD", "question": "what was asked, no answer"}],
  "repairs": [{"topic": "SLUG", "since": "YYYY-MM-DD", "gap": "what is missing"}],
  "skipped": [{"topic": "SLUG", "date": "YYYY-MM-DD", "reason": "skipped at the student's request, no credit"}]
}
```

Remove an item when it is dealt with. Retests promised without notice are the topics with `retest_without_notice: true`.

## Flags

After recording, update the vault flag only when the evidence changes it:

1. For the topic's note (its `notes` path), collect every topic file listing that same note, and run `T level SLUG` for each.
2. The note's level is the weakest of them, and **no flag** if any of them is `none` (a note with any untested topic shows nothing).
3. Find the note: `python3 S/scripts/flag.py find RECORDED_PATH TITLE`. One line: that is the note. No output: tell him it wasn't found and change nothing. Several lines: ask him which, never guess. If found at a new path, update `notes` in the topic files.
4. Read the note's current `understanding` property. If it equals the computed level (or both are absent), do nothing.
5. Otherwise: `python3 S/scripts/flag.py set NOTE LEVEL` (or `none` to remove it). Report the change in the reply.

Never flag an empty note (he hasn't written it yet; you may point it out). No note means no flag: never create one. Flags can go down: a failed retest lowers the level, and `level` already accounts for it.

| Level | Evidence the log must show |
|---|---|
| none | Untested, or below moderate |
| moderate | Stated it precisely and solved a standard problem, same day, unhinted |
| good | Passed a surprise retest at least two days later, on an unseen system |
| deep | After that, passed again by surprise, found the flaw in a wrong proof, and handled a new variant |

## Correctness

- Before asserting a numeric or symbolic result, or setting an exercise, check it by running code: `HOME/.venv/bin/python` has SymPy and NumPy. If it can't be checked by code, say so.
- Page references and quotations are read from the source, never recalled. A book recalled from memory is labeled "from memory".
- If a check shows you were wrong, tell him plainly, in chat and on the page.

## Closing (at 5 minutes left, or when the topic ends)

1. A short evidence summary in chat: what is now correct, what is patched, what is open, and how confidence compared with results (from `T summary SLUG`).
2. Make sure every result is recorded, and update any flag the evidence now justifies (Flags above).
3. Set due dates: `record` sets them; check each tested topic has one, and for promised unannounced retests set `retest_without_notice`. Then follow `references/review.md` for the weekly block's calendar event.
4. Point him at any vault note the session suggests he should reconsider and maybe rewrite (path and what to look at; never the rewrite).
5. List the questions on hold, so the next session opens with them; they are in `open.json`.
6. Update the evidence line at the end of the notes page.

## Chat formatting

Whether the app's chat renders LaTeX is **unverified**. Until it is checked, chat uses Unicode (ẋ, V̇, ≤, ∈, λ, √) and inline code (`x' = Ax`, `V(x) = x1^2 + x2^2`), and full mathematics goes on the notes page with KaTeX.
