# Exam mode

Exam practice in the style of the course's exams, separate from normal tutoring. It doesn't change what is valued: a topic's tier stays what the roadmap says, and a low-tier topic that is on the exam is still practiced, with its tier said aloud. Load `references/session.md` for the reply shape, clock, recording, correctness and closing. `T` means `python3 S/scripts/tutorlog.py`.

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

Exam results are logged separately from teaching evidence, and a correct exam problem counts as mechanical evidence only, so exam practice can never raise a flag by itself.

- Record every problem with `"exam": true` and `"kind": "mechanical"`, whatever it asked, and with `surprise`, `unseen_system` and `new_variant` all `false`:

```bash
T record SLUG --json '{"date": "2027-01-08", "kind": "mechanical", "result": "partial", "confidence": 4, "exam": true, "note": "exam-style, 18 of 25 min; sign error in the Jacobian"}'
```

- One problem touching several topics: record it in each topic file it tests.
- Exam mode doesn't run the flag update (Flags in `references/session.md`). The flag changes only through teaching and review evidence.
- **A wrong or partial exam answer** goes in the topic's `mistakes`, in his words where useful. Set `"retest_without_notice": true` on that topic, with `next_due` within a week, so it comes back by surprise in a normal session. A deep gap it reveals goes to `repairs` in `open.json`, as in any session.

## Closing

As in `references/session.md`, without the flag update, plus: which problems were right, how the time compared with the exam's, and which topics now owe a retest. Its step 3 keeps the weekly block in step (`references/review.md`).
