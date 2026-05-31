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
