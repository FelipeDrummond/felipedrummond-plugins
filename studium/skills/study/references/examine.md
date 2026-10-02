# Examining a concept note

They have written a concept note from memory. Your job is the oral exam: find what is wrong,
find how deep the understanding goes, and leave the note better **by their hand**. Explaining
something and being questioned on the explanation is one of the few study techniques that
improves understanding and not only recall.

If asked to "examine today's notes" or similar, run `status` and work through the untested
notes for that course, one at a time.

## Steps

1. **Read the note.** If the body is empty (a stub), there is nothing to examine. Offer the
   oral route instead: they explain the concept in chat, you probe, then they write it up.
2. **Get ground truth and context.** Follow the note's `sources` to the lecture note and its
   PDF for the definitions, conditions and notation. Search the vault for related notes:
   prerequisites, neighbours, anything that says the same thing under another name. Fill
   `prereqs` and `sources` with the links you find straight away; they are bookkeeping and do
   not depend on the examination. From the profile and tutor notes, see which prerequisites are
   weak and what they have got wrong before: that is where to probe.
3. **Correctness pass.** Read as a strict grader and sort what you find:
   - **wrong** — a false statement, an invalid proof step, a missing condition that makes the
     claim false;
   - **imprecise** — true in spirit but would lose marks (undefined symbol, "any" for "all",
     wrong units, notation that differs from the lecturer's);
   - **missing** — a core part of the concept that is absent.

4. **Give the verdict in the first reply.** They asked whether the note is right; answer that.
   In this order, most important first:
   - The overall verdict in the first line ("The definitions need tightening; the proof does
     not hold"), and in a sentence what is right, so they know what to keep. Do not call a part
     right if you have a point to make about it.
   - The one **wrong** thing that matters most — usually a broken proof step or a false claim.
     It comes straight after the verdict, not buried under the small points. Put it to them as
     a real question: a counterexample to run their own argument on, a limiting case, "which
     step uses linear independence?". If you have already quoted the faulty sentence, the
     question is why it fails and what would make it true, not which sentence it is. This is
     the single ask of the turn; say that they can ask for the reason if they get stuck.
   - Then the **imprecise** and **missing** items, each stated outright in one line with the
     fix direction: "'two or more elements' leaves out the single-vector set {0}". These are
     not worth a guessing game; they are worth knowing. Order them by how much they matter and
     leave out pure grammar.

   If they cannot find the main error after one pointed question, say plainly what is wrong and
   why. They then repair it themselves; do not write the corrected proof or paragraph for them,
   but do confirm or correct the idea they propose for the repair.
5. **Depth probes.** Pick three or four that suit the concept and this student; do not run the
   whole menu. Favour probes that lean on a weak prerequisite or revisit a past miss.

   | Probe | Asks |
   |---|---|
   | Why | Derive it, or justify the step. Where is each assumption used? |
   | Limits | What happens at zero, at infinity, in the symmetric case? Do the units work? |
   | Example and non-example | Give one that satisfies it and a near miss that does not. |
   | What-if | Drop or change one assumption. What breaks? |
   | Connect | How does this relate to `[[another note]]`, ideally from a different course? |
   | Apply | A three-minute problem that needs it. |
   | In the machine | Where does this show up in a real robot or mechanism, and what goes wrong in practice? |
   | Teach | Explain it to a first-year in two sentences. |

   Prefer probes that cross course boundaries. Seeing that the Jacobian in kinematics and the
   linearisation in control are the same object is the kind of understanding that lasts.
6. **They revise.** They edit the note in Obsidian; you wait, then re-read it. You do not touch
   the body.
7. **Write the wrap-up.**
   - For a prerequisite with no note, propose a stub rather than linking to nothing.
   - `## Open questions` in the note: anything unresolved, written as questions.
   - Tag: replace `s/draft` with `s/examined` once no known error is left in the note. If errors
     remain unfixed, leave `s/draft`.
   - Record the result (`record <note> <grade>`). Grade their performance on the probes, not
     the polish of the prose: `solid` if they handled them unaided, `partial` if they needed
     cues or one real error surfaced, `miss` if the core idea was wrong. Whatever the grade, a
     first examination puts the note in box 1, due tomorrow.
   - Offer to add the note's link to the relevant map's core-concepts list; they write the
     line of context.
8. **Report** in a few lines: what is solid, what they fixed, what is still open, and that the
   first review is due tomorrow.

## When there is no time for a dialogue

If they want everything in one reply, give step 4 in full and add the probes as questions to
answer in their own time. Do not record a grade until they have actually answered something.
