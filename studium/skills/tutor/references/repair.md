# Repair mode

A repair is one 1-hour block on one deep gap: a prerequisite the course assumes and he doesn't have, found during a session and patched just enough to go on (`references/session.md`, When a gap appears). The course keeps moving; repair runs alongside it, never instead of it. Load `references/session.md` too: the reply shape, clock, tests, confidence, recording, flags, correctness, page and closing all apply.

## Which gap

- Repairs waiting are in `HOME/data/open.json` under `repairs`. If he names one, take it; otherwise the highest `priority`, and the oldest within it.
- The tutor adds no calendar event for a repair; he starts it in one of his own study blocks. Until it is done, a waiting repair counts as an unclear mode when you pick the mode at the start of a run (`SKILL.md`): ask the one question, whether this block is the repair. If it has waited more than a week, say how long in that question.
- One gap per block. If the gap is wider than an hour, cut it at a point he can be tested on, and leave the rest in `repairs`.

## The block

1. `T clock start` (`T` is `python3 S/scripts/tutorlog.py`). Retests due come first, as in any session.
2. **Open with why it matters now:** which topic exposed the gap, and what the course is about to do that needs it, in concrete terms (the section that uses it, and what goes wrong on a robot without it). Then one question asking what he already knows about it. Same shape as opening a topic.
3. **Scope from what the course uses.** Read the course section that exposed the gap and list what it takes for granted. Teach that, from the ground up, and no further than the course needs. Formal statements with every hypothesis, on the page.
4. **Test it as any topic**: stating, mechanical, conceptual, find the flaw, invent, and an unseen system before the block ends. The patch test from the session that found the gap is not enough.
5. **Record** in the gap's topic file (created when the patch was made; create it now if missing). Its `tier` is the gap's own tier, stated with a reason like any topic's.
6. **Closing:** as in `references/session.md`. If he passed the block's tests unhinted, remove the item from `repairs`, set `"retest_without_notice": true`, and tell him it will come back without notice. `patched` stays `true` until he passes that surprise retest. If the gap isn't closed, keep it in `repairs` and rewrite its `gap` text to say what is still missing.

## No source to lean on

Assume there is no source for a repair: no notes from the earlier course and no reference books on hand, unless he names one and it can be read.

- **Derive the content yourself**, and check every result with code before you assert it (`HOME/.venv/bin/python`, SymPy and NumPy): eigenvalues, matrix exponentials, a closed-form solution against a numerical one.
- **A book named from memory is labeled "from memory"**, with no page or theorem numbers. Never quote it.
- If something can't be checked by code, say so.

## The first case: stability of linear systems

The typical gap is reading the stability of `x' = Ax` from the eigenvalues of `A`, which a nonlinear-control course assumes for linearization (the indirect method). Take from this list only what the course section uses:

- Eigenvalues and eigenvectors as directions `A` only stretches; `x(t) = e^(λt) v` solves `x' = Ax`.
- The solution `x(t) = e^(At) x0`, and its modal form when `A` is diagonalizable.
- Stability from the real parts; complex eigenvalues as rotation with growth or decay.
- Repeated eigenvalues without enough eigenvectors: the `t e^(λt)` term, and why "all real parts negative" still decides.
- Phase portraits in the plane (node, saddle, focus, center), each drawn from computed trajectories (`references/figures.md`).
- The bridge back: what linearization tells you about a nonlinear equilibrium, and when it tells you nothing (a zero real part).

Good unseen systems here: a defective matrix, a saddle disguised by off-diagonal terms, a center whose linearization says nothing about the nonlinear system.

## Red flags

| About to | Instead |
|---|---|
| Teach the whole earlier course | Only what the exposing section takes for granted |
| Cite a page or theorem number from a book you haven't read here | "From memory", no numbers |
| Assert an eigenvalue or solution without running it | Check with code first |
| Close the repair after the patch test | Test all kinds, including an unseen system |
| Call the gap fixed at the end of the block | Retest without notice; `patched` stays until it passes |
