# Exam mode

Exam practice in the style of the course's exams, separate from normal tutoring. In exam mode this file governs where it differs from the general rules: in particular, a right answer is followed by the next exam problem, not by the "right immediately, move to an unseen system" rule in `SKILL.md`. Exam mode doesn't change what is valued: a topic's tier stays what the roadmap says, and a low-tier topic that is on the exam is still practiced, with its tier said aloud. Load `references/session.md` for the reply shape, clock, recording, correctness and closing. `T` means `python3 S/scripts/tutorlog.py`.

## When

- When he asks for exam practice, past papers or timed problems.
- From about four weeks before `target_date` in config (or the first exam date in `HOME/data/roadmap.md`, if earlier), mention exam practice once in a closing message. Don't start it unasked.
- Retests due come first, as in any session.

## Problems

- **Past papers first.** If he has the course's past exams or exam-style exercises, use them, and read each problem from the source. Ask where they are if you don't know.
- **Otherwise write problems in the course's exam style:** its notation, its typical length and mix (compute, prove, interpret). Say they are yours, not past exam problems. Check every problem and its answer with code before setting it.
- One problem per message. A multi-part exam problem is given one part at a time, as one question each.
- **Timed if he wants it.** State the time for the problem before he starts (from the exam's minutes per point, if known), and write the time he took in the record's `note`.

## His answers

- He may solve on paper and type the key steps. Judge the steps he typed: a right result without the step that justifies it is "Incomplete.", and you ask for that step. This way of answering is still being tried; at the end of the first exam block, ask him once whether it works.
- Verdict first, as always. Full worked solutions go on the page (`HOME/pages/<course>/exam-<n>.html`, as in `references/notes-page.md`), and only after his attempt.

## Recording

Exam results are marked separately from teaching evidence, and a correct exam problem counts as mechanical evidence only. By the level rules, a mechanical answer raises nothing by itself: it counts only together with a correct `state` answer on the same day.

**Say so in the record line, plainly, every time:** the result counts as exam practice, kept apart from the learning record, and can't raise a flag on its own. For example: `[Recorded as exam practice, kept apart from your learning record: correct, counted as mechanical only; it can't raise a flag on its own.]`

- Record every problem with `"exam": true` and `"kind": "mechanical"`, whatever it asked, and with `surprise`, `unseen_system` and `new_variant` all `false`:

```bash
T record SLUG --json '{"date": "2027-01-08", "kind": "mechanical", "result": "partial", "confidence": 4, "exam": true, "note": "exam-style, 18 of 25 min; sign error in the Jacobian"}'
```

- If a topic has no topic file yet, create it first, with every field (`references/session.md`, Recording).
- One problem touching several topics: record it in each topic file it tests.
- Flags follow `tutorlog.py level` as in any session (Flags in `references/session.md`).
- **Slips count here, and only here.** An exam grades the final answer, so a slip is recorded with the result it produced (`wrong` or `partial`), `"error": "slip"`, and what slipped in `note`. It sets no retest and no repair: it comes back in exam practice. At the start of an exam block run `T slips` and aim problems at the kinds of slip recorded (signs, matrix arithmetic, units).
- **A wrong or partial exam answer that is not a slip** goes in the topic's `mistakes`, in his words where useful. Set `"retest_without_notice": true` on that topic, with `next_due` within a week, so it comes back by surprise in a normal session. A deep gap it reveals goes to `repairs` in `open.json`, as in any session.

## Closing

As in `references/session.md`, plus: which problems were right, how the time compared with the exam's, and which topics now owe a retest. Its step 4 (due dates) keeps the weekly block in step (`references/review.md`).
