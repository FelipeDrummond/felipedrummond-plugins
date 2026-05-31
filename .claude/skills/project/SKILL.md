---
name: project
description: Use when the user brings an ML research idea + hypothesis + why and wants it turned into a developable Linear project — off-ramped success criteria, a gated milestone arc from day 0 to publication, and rolling-wave tickets authored via the ticket skill.
argument-hint: "[idea + hypothesis + why]"
allowed-tools: Read, Glob, Grep, Task, mcp__linear-server
disable-model-invocation: true
---

# Planning a research project

Turn an idea you've already done your homework on into a project you can *build*. You bring
the **idea, the hypothesis, and the why**; you decide the *what*. This skill owns the **how** —
the success criteria that make the hypothesis falsifiable, the gated milestone sequence that
takes it from day 0 to publication, and the near-term tickets to start on.

Write it the way a sharp collaborator would plan with you: prose, not a form. The structure
that matters in research is the **falsification logic** (what proves the idea wrong, and what
you do then) and the **de-risking order** (cheap experiments first, gating the expensive
ones). That structure is the substance — everything else is ceremony to avoid.

## Flow

1. **Intake** — restate the idea / hypothesis / why; confirm before spending tokens.
2. **Make the claim falsifiable** — formalize success criteria with thresholds and an off-ramp;
   pressure-test the baselines/metric you brought for comparability.
3. **Design the gated milestone arc** — a cheap→expensive de-risking sequence to publication.
4. **Author the near-term wave** — fully author tickets only up to the first unresolved gate,
   delegating to the `ticket` skill via subagents.
5. **Review with the human** — priority and due dates are the human's; approve the gate
   structure; approve before any write.
6. **Write to Linear** — project, milestones, near-term tickets, relations last.
7. **Re-entry** — when a gate resolves, return to author the next wave on the branch taken.

## 1 · Intake

Restate the idea, the hypothesis, and the why in two or three sentences in your own words, and
ask "Did I get that right?" Proceed only on confirmation. You are not here to second-guess the
idea — the user did the diligence — but you must understand it precisely enough to plan it.

Resolve two placement facts before drafting: the **target Linear team** (list teams and ask if
it isn't obvious — a project needs one), and whether this is a **new project or a refinement of
an existing one**. In refine mode, load the existing project, its milestones, and its issues via
the Linear MCP first, and treat them as a baseline you extend — never silently overwrite.

## 2 · Make the claim falsifiable

A plan you can build needs a claim you can disprove. Turn the hypothesis into success criteria,
each a checkable claim with a threshold and a metric — not "improves performance" but
"beats {baselines} on {metric} by {threshold} at {setting}". Use these kinds:

- **headline** — the result the paper is about. State it so a skeptic could see it fail.
- **floor** — the weaker result that still ships if the headline dies.
- **off_ramp** — what you publish instead if the headline is dead. **Always name one.** Research
  without an off-ramp is a bet with no exit.
- **generalization** — does the effect survive a shift (scale, task) you care about?

Then pressure-test **comparability** on the baselines and metric the user brought — not the
literature at large, just: *will this comparison convince a reviewer?* If a baseline is missing
or the metric won't isolate the effect, say so.

This is where you push back. If the hypothesis isn't falsifiable as written, or a threshold is
hand-wavy, or there's no off-ramp — surface it now and resolve it with the user. Gates in the
next step are impossible without it. Push on the *plan and the claim's testability*; do not
re-litigate the idea.

## 3 · Design the gated milestone arc

Lay out the project as an ordered sequence of milestones from day 0 to publication, ordered so
the **cheapest experiments that could kill the idea come first**. A useful default backbone —
adapt it, don't apply it blindly:

> setup & instrumentation → de-risking pilot(s) → core experiments → generalization / robustness → writeup & submission

**Gates are the spine.** A gate is a milestone's exit decision: a measurable criterion plus the
branches you'll take on the outcome — at least one of which is *not* "proceed". Write them in
prose, e.g.:

> **M3 — D-arm viability (pilot) [G2]** — train g(z,a) from rollouts, measure prediction R²
> across N. **Gate G2:** R²(N=16) ≥ 0.3 → D is alive, proceed to the main sweep; 0.1–0.3 →
> implement the counterfactual-delta variant first; < 0.1 → off-ramp to the A-only paper.

Put a gate only where there's a genuine go/no-go — a pilot, a viability check, a scope lock.
Most milestones ("build the loss", "write the paper") have no gate; don't invent one.

For each milestone, capture in prose: its deliverables, its gate (if any), a target date inside
the project's window, an optional resource/compute cost, and which milestone(s) it depends on.
Dates increase; dependencies form a chain, not a cycle. This is guidance you apply, not a form
you fill — there is no linter, and the human approves the result.
