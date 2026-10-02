# Lecture intake

Turns one lecture into: a source note in `sources/`, a list of gaps, and a handful of concept
stubs for the user to write. It has two halves, and either can be run alone.

## Before the lecture — prime (about ten minutes)

Guessing at questions before being taught the answers improves what is retained from the
teaching, even when the guesses are wrong. It also tells them what to listen for.

1. Find the course hub (create it if missing; see SKILL.md) and the slides or script section
   for the coming lecture.
2. Send a subagent to read the PDF and return:
   - the 5–8 core ideas of the lecture, each with slide numbers;
   - the concepts the lecture assumes are already known;
   - 3–5 pretest questions aimed at the core ideas, phrased so that someone who has not seen
     the lecture can still reason toward a guess (predict, estimate, "what would you expect
     if…"), not vocabulary questions.
3. Check the assumed concepts against the profile. Any that are missing, unwritten, or sitting
   in box 1–2 are worth five minutes now; say which, and offer a quick review of those. Also
   say which of their solid notes this lecture builds on, so they walk in knowing where the new
   material attaches.
4. Ask the pretest questions one at a time. Take the guess and move on. Do not give the answers:
   the lecture is the feedback, and telling them now removes the reason to listen for it.
5. Create the lecture note `sources/<Course> L<NN> — <Title>.md` from `assets/Lecture.md`.
   Put the questions under `## Pretest` with their guesses recorded verbatim. Set `link` to the
   PDF and add the note to the hub's `## Lectures`.

## After the lecture — process (same day if possible)

Most forgetting happens in the first day, so the first retrieval is worth the most.

1. **Recall dump first.** Before they reopen the slides, ask them to write down everything they
   remember: main ideas, a derivation or two, anything that confused them. Five to ten minutes,
   in the note's `## Recall dump` or pasted into chat (you save it verbatim). If they arrive
   with the dump already written, go straight on. If they have typed or handwritten notes from
   the lecture, those go under `## Notes`; they are a second input, not a substitute for the
   dump.
2. **Compare.** Read the PDF against the dump and any lecture notes (delegate a long deck).
   Sort each core idea of the lecture into: recalled correctly, recalled with an error, or
   missing — with slide numbers and, for errors, the exact sentence that is wrong. Read each
   wrong sentence for everything wrong with it; one sentence can carry two faults. Check the
   profile too: an error that matches a past miss or a weak prerequisite is a pattern, and you
   say so by name ("this is the complex-eigenvalue slip from your 27 Sept review again").
3. **Open with the map.** Tell them the result before the first question: what they got, how
   many errors, and the missing topics **by name and slide number** ("missing: stability
   definitions, slide 4; marginal stability, slide 6; Routh–Hurwitz, slide 8"). The names tell
   them where the holes are; the content is still theirs to retrieve. Where a new idea extends
   a note they already have, say which.
4. **Errors first.** A misconception left alone gets rehearsed. For each, ask the pointed
   question that exposes it ("you wrote that the system is stable when the poles are real —
   what about a real pole at +2?"). One retry, then correct it plainly in the conversation with
   the slide reference.
5. **Then what is missing**, one topic at a time. Give a cue, not the content: "slides 12–15
   introduce a condition on the controllability matrix — what was it?" One retry. If it does
   not come back, they reread those slides and tell you; if it still does not make sense, that
   is a teaching moment (see `teach.md`), not a reason to recite the lecture.
6. **Revisit the pretest.** Re-ask any question they guessed wrong beforehand.
7. **Write the gaps.** Under `## Gaps` in the lecture note, list what stayed unrecalled, as
   pointers: `- Slides 12–15: rank condition for controllability`. These are a to-do list, not
   explanations.
8. **Extract concepts.** Propose 3–6 atomic concept titles, the ideas from this lecture worth
   owning in five years. Prefer a title that states the idea ("A subspace is closed under
   linear combination") or names one concept, not a chapter heading. Search `concepts/` first:
   if a note already exists, add this lecture to its `sources` rather than making a duplicate.
   When they approve the list, create each stub from `meta/templates/Permanent.md` with:
   - `topics`: the course hub and the relevant subject map;
   - `prereqs`: links to concepts it depends on;
   - `sources`: this lecture note;
   - tag `s/gap`, the title as heading, and an empty body.
   Then fill the lecture note's `covers` and `## Extracted To`.
9. **Muddiest point.** Ask what they understood least. Teach it now if there is time
   (`teach.md`); otherwise add it as a question to the hub's `## Open questions`, a candidate
   for the tutorial or office hours.
10. **Close.** Set the lecture note's `status` to `done`. Tell them the next step: write the
    stubs from memory within a day, then run examine on them.

## What good looks like

The lecture note contains their words and your pointers. A reader could not learn the lecture
from it, and that is intended: the understanding lives in the concept notes they are about to
write.
