# `/study` — a private tutor who knows what you know

**Date:** 2026-10-01
**Status:** v0.1 implemented, three evaluation rounds
**Plugin:** `studium` (new, one skill)

## Problem

Felipe starts an M.Sc. in Mechatronics, Robotics and Biomechanical Engineering at TUM in the
winter semester 2026/27. He wants excellent grades, but the real goal is to understand the
material deeply, keep it, and go beyond the syllabus. He keeps a second brain in Obsidian at
`~/Documents/Obsidian Vault`.

The vault already has the right schema and almost none of it is in use: concept notes carry
`confidence`, `last_tested`, `prereqs` and `sources`, but no note has ever been tested, and
nothing schedules a review. His own note "Math is a meta-skill" describes a sound study loop
(review → active read → exercises → consolidate) with nothing to run it.

The obvious way to use an agent here is the harmful one. An assistant that summarises lectures,
writes the notes and shows the solutions makes every study session feel better and leaves less
behind. In a field experiment with high-school maths students, unrestricted access to GPT-4
improved practice scores and then *lowered* exam scores once access was removed; a version with
tutor guardrails (hints, not answers) largely removed the harm (Bastani et al., 2025).

## What this is — and is not

- **Is:** a private tutor with a one-to-one understanding of the student, built from the vault.
  It reads what he knows before it teaches, explains from his own notes, aims at his weak
  points, and remembers how he learns.
- **Is not:** a rewriter of notes, a lecture summariser or an answer key.

Tutoring's advantage over a lecture is adaptation: the tutor knows this student (Bloom, 1984;
VanLehn, 2011). The vault makes that possible to a degree no human tutor has: every concept in
his own words, how each has held up under testing, each mistake and open question.

**Design history.** The first draft was framed around what the agent must not write, which
produced a careful examiner. Felipe's correction: "The idea is not to be a re-writer, but to be
a private tutor with a 1-1 understanding of my knowledge based on my vault." The second draft
puts the learner model first and adds a teaching loop; the no-ghostwriting rule survives as a
consequence (the notes are only a model of his knowledge if he wrote them), not as the headline.

A second evaluation round then showed the opposite failure. Asked "I still don't get how BIBO
differs", the skill read his confidence levels back to him and replied with a quiz, while the
no-skill baseline simply taught it well. The rule that came out of that: **generous when
teaching, demanding when he practises.** A request to understand gets the answer in the first
line and a full explanation pitched from his notes; recall, problems and note examinations are
where the work is handed back to him. In both, small things are told outright and only the one
idea that matters most is put as a question.

## Decisions taken with Felipe

| Question | Decision |
|---|---|
| What is the agent's role? | Private tutor grounded in the vault, not a rewriter. |
| Who writes concept-note prose? | He writes; the tutor teaches in conversation and examines. |
| Which loops in v1? | Teach, intake, examine, review, drill. |
| Where does spaced repetition live? | In the vault's own frontmatter; no Anki, no plugin. |
| What inputs? | Lecture PDFs, typed notes, handwritten notes, exercise sheets and old exams. |

## The learner model

Every session starts by building a picture of what he knows about the topic at hand:

| Source | What it tells the tutor |
|---|---|
| `vault.py profile --topic` | Each concept note weakest first: stub, untested or box; prerequisites and their levels; open questions; the last two review results. |
| The concept notes themselves | How he explains the idea, his notation and examples, what is absent. |
| `meta/Tutor notes.md` | What cuts across concepts: which explanations land, recurring error patterns, background the vault does not show. Written by the tutor, correctable by him. |
| The course hub | Error log, open questions, redo queue. |

The tutor then starts where he is, uses his notation and names his notes, aims at known weak
points, skips what is solid, and treats the vault as evidence, not the whole truth: where it is
silent, it asks one diagnostic question instead of assuming.

The picture is used, not recited: it shows in where an explanation starts and which example it
picks, and the vault is mentioned only where that does work. Every session ends with him
producing something (an explain-back, a redone step, later the note).

## Visual explanations

Felipe learns best from pictures. Every visual is **computed, never image-generated**: a
generated figure looks plausible and is often wrong; a plot produced by code that implements
the mathematics can be checked.

| The idea is about | The tutor shows |
|---|---|
| A shape, configuration or position | A computed matplotlib figure |
| Change with a parameter or over time | An explorable: one HTML page with sliders, built from `assets/explorable.html` (Plotly from a CDN, light and dark mode) |
| Two cases that get confused | Side-by-side panels |
| Pure algebra | Nothing |

Decisions taken with Felipe: visuals whenever one fits; made by the tutor only (no
"you draw, tutor checks" loop); saved outside the vault in `<materials>/visuals/`. The tutor
looks at every figure before showing it (reads the PNG, or a headless-Chrome screenshot of the
page) and checks an explorable's numbers against numpy. Explorables open with a prediction
question, because committing to an answer before moving the slider is what makes it stick.

## The evidence behind each loop

| Loop | Technique | Why |
|---|---|---|
| teach | Diagnose, teach to the gap, explain-back | One-to-one tutoring with mastery checks is the strongest instructional effect on record (Bloom, 1984). Instruction lands best after an attempt and when followed by the learner producing it. |
| intake (before) | Pretesting | Attempting questions before instruction improves retention of the instruction, even when the attempts fail (Richland, Kornell & Kao, 2009). |
| intake (after) | Free recall, then feedback | Retrieval beats restudy for long-term retention (Roediger & Karpicke, 2006). First retrieval the same day, when forgetting is fastest. |
| examine | Self-explanation, elaborative interrogation | Students who explain steps to themselves learn more from the same material (Chi et al., 1989). Producing an explanation beats reading one (generation effect; Slamecka & Graf, 1978). |
| review | Practice testing + distributed practice | The two techniques rated "high utility" in the Dunlosky et al. (2013) review. Spacing: Cepeda et al. (2006). |
| review | Interleaving | Mixing problem types forces identifying the type, which blocked practice hides (Rohrer & Taylor, 2007). |
| review | Predict before answering | Fluency produces illusions of competence (Koriat & Bjork, 2005); comparing prediction to outcome trains calibration. |
| drill | Attempt first, graded hints | Step-level tutoring with hints approaches human tutoring in effect (VanLehn, 2011). Worked solutions help novices and stop helping as expertise grows (Kalyuga et al., 2003). |
| drill | Name the principle first | Experts sort problems by underlying principle, novices by surface features (Chi, Feltovich & Glaser, 1981). |
| all | Desirable difficulties | Conditions that slow apparent progress often improve long-term learning (Bjork & Bjork, 2011). |

Rereading, highlighting and summarising, the things an assistant makes effortless, are the
techniques the same review rates lowest.

## Shape: one skill, five loops

`linear-planning` uses one skill per verb. Here one skill with five reference files is the
better fit, because every loop needs the same learner model and vault map in context, and
`/study <loop>` avoids claiming generic names like `/review`.

```
studium/skills/study/
  SKILL.md                 the tutor: learner model, teaching beats, vault map, loop router
  references/teach.md      explain a concept from what he already knows
  references/intake.md     before / after a lecture
  references/examine.md    oral exam on a note he wrote
  references/review.md     spaced retrieval session
  references/drill.md      sheets and old exams
  scripts/vault.py         profile / status / record (+ test_vault.py)
  assets/Course.md         course hub template
  assets/Lecture.md        lecture source-note template
  assets/Tutor notes.md    the tutor's cross-session memory of the student
  assets/explorable.html   working interactive page to copy and adapt
  references/visuals.md    which visual, how to build it, how to check it
```

The skill is model-invocable (unlike the Linear skills), since "quiz me" or "I just got out of
the control lecture" should be enough.

## Who writes what

| The agent writes | The agent never writes |
|---|---|
| Frontmatter (`confidence`, `last_tested`, `prereqs`, `sources`, `covers`, `topics`, tags) | Explanation prose in a concept note |
| Stubs: title + frontmatter, empty body, `s/gap` | A lecture summary |
| Questions and pointers (pretest, open questions, "slides 12–15") | A map's or hub's narrative paragraph |
| Logs (review log, error log, redo queue, tutor notes) | Edits to his sentences, including spelling |
| His words verbatim when dictated in chat | A full solution before an attempt |

Explaining in the conversation is the tutor's job. If he wants an answer straight, with no
attempt first, he gets it, followed by a quick explain-back.

## Vault changes

Additive only; nothing existing is renamed.

- **New folder `courses/`**, `type: course`: one hub per module with `semester`, `ects`, `exam`,
  `language`, `materials`, and sections for lectures, open questions, redo queue, error log.
  Concept notes join a course by listing the hub in `topics`, next to their subject map.
- **Lecture notes** are ordinary `sources/` notes tagged `src/lecture`, with `## Pretest`,
  `## Notes`, `## Recall dump`, `## Gaps`, `## Extracted To`.
- **New tag `s/examined`**, replacing `s/draft` once a note survives examination.
- **`## Review log`** appended to concept notes by `vault.py record`.
- **`meta/Tutor notes.md`**, the tutor's memory between sessions.
- Lecture PDFs stay outside the vault by default (the vault is a git repo); the hub's
  `materials` field records where.

## Scheduling

A Leitner system in the existing fields, chosen because he can read and override it in Obsidian.

- `confidence` is the box: 0 = never tested; boxes 1–5 are due after 1, 3, 7, 16, 35 days.
- `solid` → up one box; `partial` → stay; `miss` → box 1.
- `vault.py profile [--topic]` prints the learner model described above.
- `vault.py status [--topic]` lists due notes, untested notes and unwritten stubs.
- `vault.py record NOTE GRADE [--predicted] [--comment]` updates the two fields and appends a
  log line. Standard library only, line-based edits, so the rest of the note is untouched.

`confidence` moves only through `record`: it reflects tested performance, never a feeling.

## Subagents

| Role | Why it is separate |
|---|---|
| PDF reader | A slide deck is too large for the tutoring conversation; it returns only core ideas, questions, or a comparison. |
| Independent solver | Solves from the problem statement alone and checks with sympy/numpy, so the reference is not anchored on his mistake. |
| Vault librarian | Finds existing notes, prerequisites and duplicates. |

## Evaluation

Single-turn prompts against a scratch copy of the vault, each run with and without the skill
(`studium/skills/study/evals/evals.json`). The second round's fixture carries a learning
history (review logs, an error log with a repeating mistake, tutor notes), and the assertions
ask whether the reply actually uses it: builds on his notes by name, checks a prerequisite the
vault lacks, connects an error to a past miss. Multi-turn behaviour is judged by reading.

## Deferred

- Exam-period planning: mock exams, compressing intervals as the exam date approaches.
- A "beyond class" loop: primary sources, papers, build-it-yourself mini-projects.
- Anki export for atomic facts.
- Any scheduled or automatic run. For now `/study` with no argument reports status.

## References

- Bastani, H. et al. (2025). Generative AI without guardrails can harm learning. *PNAS*.
- Bloom, B. (1984). The 2 sigma problem. *Educational Researcher*.
- Bjork, E. & Bjork, R. (2011). Making things hard on yourself, but in a good way.
- Cepeda, N. et al. (2006). Distributed practice in verbal recall tasks. *Psychological Bulletin*.
- Chi, M. et al. (1989). Self-explanations. *Cognitive Science*.
- Chi, M., Feltovich, P. & Glaser, R. (1981). Categorization and representation of physics problems by experts and novices. *Cognitive Science*.
- Dunlosky, J. et al. (2013). Improving students' learning with effective learning techniques. *Psychological Science in the Public Interest*.
- Kalyuga, S. et al. (2003). The expertise reversal effect. *Educational Psychologist*.
- Koriat, A. & Bjork, R. (2005). Illusions of competence in monitoring one's knowledge during study. *JEP: LMC*.
- Richland, L., Kornell, N. & Kao, L. (2009). The pretesting effect. *JEP: Applied*.
- Roediger, H. & Karpicke, J. (2006). Test-enhanced learning. *Psychological Science*.
- Rohrer, D. & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*.
- Slamecka, N. & Graf, P. (1978). The generation effect. *JEP: Human Learning and Memory*.
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*.
