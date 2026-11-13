# Session mode

A session is one 1-hour block on one topic. The reply shape and turn rules in `SKILL.md` apply to every message. `T` below means `python3 S/scripts/tutorlog.py`.

## The clock

- First thing in a session: `T clock start`, then create and show the notes page (`references/notes-page.md`) before the first reply.
- Before every message you send: `T clock left`. This is silent: never mention the clock in chat except when closing.
- At **5 minutes or fewer**, stop teaching and close (below), even mid-topic, so he keeps his break. A topic that doesn't fit continues in a later block; put the question you were on into `open.json` as on hold.
- A repair session and the weekly review are each their own block, with their own `clock start`.
- You don't plan his day. He starts you in his own study blocks; you add only your own review events (`references/review.md`).

## Before teaching

1. **Overdue first.** `T due --for session` lists at most two topics, a failed retest first, then by open error class (Error classes, below: conceptual before method), then by tier, then the longest overdue. Topics with `"retest_without_notice": true` (a retest you promised) are candidates too, even if `due` doesn't list them; pick by the same order. A topic whose latest retest failed on an earlier day is listed even before its `next_due`, so a failure comes first in the very next session. Spend at most about 10 minutes on retests at the start of the block, as surprise retests (record with `"surprise": true`). Say in the spoken text, not only in the bracket, that it is a retest and on what: "First, a retest on positive definite functions." If the topic failed its last retest, the spoken text says so plainly, as a verdict on past evidence, not softened: "First, a retest on the indirect method: you missed it in yesterday's review." The rest wait. Topics not yet due wait for the weekly block. Retests are only these: the topics `due` lists and the promised ones. A prerequisite question never counts as a retest (record it with `"surprise": false`).
2. **Questions on hold** from `open.json` come next, after the retests and before any new material: `high` priority first, then `medium`, then `low`, oldest first within each. If time is short, the `low` ones wait.
3. **Find where the course is.** Class dates come from his class calendar (read-only), but they don't say which section a lecture reached, and he studies ahead. Ask one question: what has been covered, and what should this session take on?
4. **Read the scope:** the relevant section of the course's own material (scope and notation come from it; teach in your own order but in its notation), and any matching vault notes. The vault lags lectures by up to a week. A note shows coverage, never understanding.
5. **List the prerequisites the material assumes**, for the quiz that follows the motivation (Opening a topic, step 2). Leave out a topic he has just skipped: it is named as a known risk in the motivation instead.

Apart from retests and questions on hold, only the course-position question (step 3) may come before the opening. The prerequisite quiz comes after the motivation.

## Opening a topic

1. **Motivation first, before any question about the topic itself:** the concrete problem, why it matters for a robot (name the robot and what goes wrong without this), and the topic's value tier from `HOME/data/roadmap.md` with its reason. If the roadmap has no tier for it, state a tier and reason as a proposal he can challenge. The model: the course asserts that a limit exists, but the system has no closed form and simulation tests only finitely many initial conditions, so how can anyone know? A rhetorical question inside the motivation is fine.
2. **The prerequisite quiz, framed by that motivation.** The opening message's one question is the first prerequisite question, tied to the problem just posed. Then one question per message until the prerequisites are settled. Fix what it finds before going on; a gap found here is a predictable gap (below). If the section assumes nothing he hasn't already shown, skip to step 3.
3. **Then ask what he already knows** about the topic itself, before explaining anything, and only once the prerequisites are settled. One question, no sub-parts, no confidence rating, no theorem stated or defined first.
4. The same order holds for the next topic after a skip.
5. Rigor: theorems and proofs appear in formal form, with every hypothesis stated, on the page.

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
- **Retest without notice.** When he has been patched and appears to have got it, tell him you will ask again later without notice, and in the topic file set `"retest_without_notice": true`; if `next_due` is null or more than about a week away, set it to within a week. Then do it in a later session (Before teaching, step 1). Record that retest with `"surprise": true`, and set `retest_without_notice` back to `false` afterwards, pass or fail.

## Error classes

Every answer that isn't fully right gets one class, recorded as `error`. The class sets its priority in the backlog: reasoning comes back first, and arithmetic comes back only in exam practice.

| Class | `error` | What went wrong | Recorded as | Comes back |
|---|---|---|---|---|
| Conceptual | `conceptual` | The idea, the logic or the reasoning: a wrong claim, a missing or circular reason, a definition misread | `wrong` or `partial` | First in every ordering: sessions, repairs, the review block |
| Method | `method` | He has the idea and can't carry out the procedure | `wrong` or `partial` | After conceptual |
| Slip | `slip` | Arithmetic, a sign, a copying error, with the reasoning right | `correct`, with the slip in `note` | Exam mode only (`references/exam.md`) |

- **A slip has to earn the label.** Point at the line without saying what is wrong. If he finds and fixes it himself, it is a slip. If he can't, it is `method` or `conceptual`. When in doubt, it is not a slip: an error that looks numerical and comes from misreading what a quantity means (a squared quantity compared with an unsquared one) is conceptual.
- **A slip passes.** Say "Right, with a slip." and name the line. Record `"result": "correct", "error": "slip"` with what slipped in `note`. It doesn't fail a retest, lower a level, enter `mistakes` or go on hold.
- **The same slip twice on one topic is promoted:** record the second as `"result": "partial", "error": "method"`, and say so in the record line.
- `T slips` lists every recorded slip, for exam mode.
- An untagged wrong answer ranks as conceptual.

## Confidence

- Ask for one number, 1 to 5, inside the one question, as part of that sentence. Ask for it most on conclusions (is it stable, does it converge, is the proof valid). Don't ask for it on routine computation, on the opening "what do you know" question, on a request to finish a half answer, or on counterexample work.
- If he omits it: record `"confidence": null` with an empty `note` (it reads as "not given"), answer his content anyway, verdict first, and say in the record line that it was recorded as not given.
- The one mention per session: if the next question is a conclusion, fold the rating into it, and that counts as the mention. If the next question is a routine computation or the completion of a half answer, make the mention one short sentence after the verdict, not part of the question. Never demand a rating before continuing.
- After the one mention, keep including the rating inside later conclusion questions, without comment.
- When the question didn't ask for a rating, record `"confidence": null` with `note` starting "not asked". The summary counts these in their own bucket, apart from "not given".
- A 4 or 5 with a wrong answer: name the mismatch in words and record it (the `note` field can say "5/5, wrong").
- If he still skips ratings after a few sessions, raise it once as a design problem to decide together, and stop asking until he decides.
- On the page, confidence is the short line from `T summary SLUG` ("5: 1 of 2 correct; not given: 1 of 1 correct; not asked: 2 of 3 correct"), never a growing table.

## When a gap appears

| Kind of gap | What happens |
|---|---|
| Predictable | Caught by the prerequisite quiz and fixed first |
| Small surprise | A short patch in place, about 5 minutes: one picture and one example, then back to the topic |
| Deep surprise | A just-enough patch now, plus a separate repair session that week |

For every patch:
1. Say why the topic matters now (for example: the method in this section reads stability from eigenvalues, and the course assumes that from an earlier course).
2. Patch: in chat, one example compressed to the few lines the test question needs; the picture and the full patch go on the page, and chat says they are there.
3. Tell him in the same reply that the next question tests the patch, and make the next question that test.
4. Record it: set `"patched": true` in the topic file (create the topic file for the gap if it has none), and say in the record line "patched, not mastered".
5. For a deep gap, add it to `open.json` under `repairs` and say in the reply that a separate repair session on the gap's subject will be planned this week, naming the subject ("a repair session on linear systems this week"). The course keeps moving; repair runs alongside it.

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
T record SLUG --json '{"date": "2026-11-13", "kind": "conceptual", "result": "wrong", "confidence": 5, "error": "conceptual", "note": "5/5, wrong: stability claim from a partial check"}'
```

Fields: `date`, `kind` (above), `result` (`correct`, `partial`, `wrong`, `not_answered`), `confidence` (1 to 5, or `null` for not given), and the booleans `hinted` (he needed a hint or guided steps), `surprise` (a retest he wasn't told about in advance, including the overdue ones at the start), `unseen_system`, `new_variant`, `exam`, plus `error` (`conceptual`, `method` or `slip`, on every answer that isn't fully right; Error classes above) and a short `note`. "I don't know" is `not_answered`. A half answer completed later is two records: the partial one, then the completion. Only unhinted correct answers earn a level. `record` prints the next due date; a surprise retest sets it from the whole day's outcome (any non-correct surprise item that day fails the retest).

**Skipped at his request:** record no evidence for it (a skip is not a result; existing evidence stays untouched). Add it to `open.json` under `skipped` with the slug, the date and "skipped at the student's request, no credit", and mark the topic in `HOME/data/roadmap.md` as "skipped (YYYY-MM-DD)". No level is credited and no understanding is claimed.

**Open items** go in `HOME/data/open.json`, JSON indented by 2:

```json
{
  "on_hold": [{"topic": "SLUG", "since": "YYYY-MM-DD", "priority": "high", "question": "what was asked, no answer"}],
  "repairs": [{"topic": "SLUG", "since": "YYYY-MM-DD", "priority": "high", "gap": "what is missing"}],
  "skipped": [{"topic": "SLUG", "date": "YYYY-MM-DD", "reason": "skipped at the student's request, no credit"}]
}
```

`priority` is `high` (a conceptual error or an untested patch is behind it, or it opens new material the course needs next), `medium` (a method to carry out) or `low` (routine computation left unfinished). An item without one counts as `high`. Remove an item when it is dealt with. Retests promised without notice are the topics with `retest_without_notice: true`.

## Flags

After recording, update the vault flag only when the evidence changes it:

1. For the topic's note (its `notes` path), collect every topic file listing that same note, and run `T level SLUG` for each.
2. The note's level is the weakest of them, and **no flag** if any of them is `none` (a note with any untested topic shows nothing).
3. Find the note: `python3 S/scripts/flag.py find RECORDED_PATH TITLE`, where `RECORDED_PATH` is the topic's `notes` value and `TITLE` is the note's file name without `.md`. It prints absolute paths. One line: that is the note. No output: tell him it wasn't found and change nothing. Several lines: ask him which, never guess. If found at a new path, store that path relative to the vault in `notes` of every topic file that listed the old one.
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

1. **Every time, one line on what this session covered and the single next step** (the next topic, the question on hold, or the retest owed), even when nothing is due or on hold.
2. A short evidence summary in chat: what is now correct, what is patched, what is open, and how confidence compared with results (from `T summary SLUG`).
3. Make sure every result is recorded, and update any flag the evidence now justifies (Flags above).
4. Set due dates: `record` sets them; check each tested topic has one, and for promised unannounced retests set `retest_without_notice`. Then follow `references/review.md` for the weekly block's calendar event.
5. Point him at any vault note the session suggests he should reconsider and maybe rewrite (path and what to look at; never the rewrite).
6. List the questions on hold, so the next session opens with them; they are in `open.json`.
7. Update the evidence line at the end of the notes page.

## Chat formatting

This is the one place for the chat-math rule (`SKILL.md` points here). Whether the app's chat renders LaTeX is **unverified**. Until it is checked, chat uses Unicode (ẋ, V̇, ≤, ∈, λ, √) and inline code (`x' = Ax`, `V(x) = x1^2 + x2^2`), and full mathematics goes on the notes page with KaTeX.
