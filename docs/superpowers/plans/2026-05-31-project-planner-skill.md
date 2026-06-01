# `/project` Research Planner Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/project` skill that turns an ML research idea + hypothesis + why into a developable Linear project — off-ramped success criteria, a gated milestone arc (day 0 → publication), and rolling-wave tickets authored by delegating to the `ticket` skill.

**Architecture:** A single prose orchestrator skill at `.claude/skills/project/SKILL.md`, in the same lightweight house style as `.claude/skills/ticket/SKILL.md`. The orchestrator runs an interactive planning dialogue, then for the near-term (pre-first-gate) wave it spawns `Task` subagents that draft tickets by applying the `ticket` skill with injected context; the orchestrator itself owns all Linear writes so ordering and relations stay consistent. A committed golden fixture (Swarm-Moments) + rubric serve as the eval harness.

**Tech Stack:** Claude Code skill (Markdown + YAML frontmatter), `Task` tool for subagents, Linear MCP (`mcp__linear-server`) for writes. No code, no build step — verification is a dry-run of the skill against the fixture, checked against the rubric.

**Spec:** `docs/superpowers/specs/2026-05-28-linear-project-generator-design.md`

---

## File structure

- Create `.claude/skills/project/SKILL.md` — the orchestrator skill (the deliverable).
- Create `.claude/skills/project/eval/swarm-moments-input.md` — golden fixture: the idea + hypothesis + why a user would bring (no milestones/tickets — those are what the skill must produce).
- Create `.claude/skills/project/eval/rubric.md` — checkable acceptance criteria for a good generated plan; the "test" the skill must pass.
- Modify `README.md` — move `/project` from "in progress" to "Skills"; add the eval note.

Each task below produces a self-contained, committable change.

---

## Task 1: Golden fixture + acceptance rubric (the "test")

Defines what a good output is *before* writing the skill, so the dry-run in Task 6 has a target.

**Files:**
- Create: `.claude/skills/project/eval/swarm-moments-input.md`
- Create: `.claude/skills/project/eval/rubric.md`

- [ ] **Step 1: Write the fixture input** — the *inputs only* (idea + hypothesis + why), reverse-engineered from the real Swarm-Moments project description with all the *how* (milestones, gates, tickets, dates) stripped out. Content to write into `swarm-moments-input.md`:

```markdown
# Fixture input — Swarm-Moments (idea + hypothesis + why)

**Idea.** Each agent in a decentralized swarm predicts the (mean, covariance) of its local
k-neighborhood latent state — a decoder-free (JEPA-style) distributional generalization of
Mean-Field MARL (Σ=0 recovers mean-field). Loss: Bures-Wasserstein (closed-form W2 between
Gaussians).

**Hypothesis.** An action-conditioned predictor g(z_i, a_i) → (μ̂, Σ̂) (arm D) improves a
decentralized cohesion-conditional-on-survival metric over MAPPO and MF-MAPPO at N=16 on a
predator-avoidance task; a representation-shaping auxiliary Bures loss (arm A) at minimum
improves probe-readout representation quality with no RL-return regression.

**Why.** Mean-field MARL collapses the neighborhood to its mean and loses the spread that
matters under a predator; modeling covariance should capture it. Decoder-free avoids
reconstruction. If the action-conditioned arm is too low-SNR, there is still a publishable
representation-shaping result.

**Known constraints.** Solo researcher, ~12 weeks, ~$300 compute. Simulator: VMAS. Baselines
available via BenchMARL/TorchRL. Target: a workshop/main-track submission.
```

- [ ] **Step 2: Write the rubric** — the checkable properties a good generated plan MUST have. Content to write into `rubric.md`:

```markdown
# Acceptance rubric — a good `/project` output

A dry-run against `swarm-moments-input.md` passes if the generated plan satisfies all of:

## Success criteria
- [ ] At least one `headline` criterion stated as a falsifiable claim with a threshold + a metric.
- [ ] At least one `off_ramp` criterion (what ships if the headline dies).
- [ ] A `floor` and a `generalization` criterion present (or an explicit, reasoned omission).

## Milestone arc (day 0 → publication)
- [ ] Ordered milestones spanning setup → de-risking pilot(s) → core experiments → generalization → writeup/submit.
- [ ] At least one milestone carries a real gate: a measurable exit criterion + ≥2 branches, at least one non-proceed (pivot/off-ramp).
- [ ] Gates sit on genuine go/no-go points (e.g. the D-arm viability pilot), not on every milestone.
- [ ] Each milestone has a target date inside the stated ~12-week window; dates increase; dependencies form a chain (no cycle).

## Rolling wave
- [ ] Only milestones up to the FIRST unresolved gate have fully-authored tickets.
- [ ] Milestones downstream of an unresolved gate are left as gate + one-line intent (NOT fully authored), because their content is contingent on the gate outcome.

## Style / anti-ceremony
- [ ] Description + milestones read as prose; no YAML schema dump, no `SPECIFIED/AGENT_DECIDES/ASK_FIRST`, no LoC estimates.
- [ ] Priority and due dates are NOT invented (left for the human).

## Pushback
- [ ] If the input's hypothesis or success metric were vague, the run surfaced it (asked or flagged) rather than silently inventing thresholds.
```

- [ ] **Step 3: Verify the fixture/rubric are self-consistent** — re-read both. Confirm every rubric checkbox is judgable from the fixture alone (e.g. the rubric never demands info the fixture doesn't imply). Expected: every checkbox maps to something the fixture asks the skill to produce.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/project/eval/swarm-moments-input.md .claude/skills/project/eval/rubric.md
git commit -m "test: add /project golden fixture and acceptance rubric"
```

---

## Task 2: Skill scaffold — frontmatter + intro + flow outline

**Files:**
- Create: `.claude/skills/project/SKILL.md`

- [ ] **Step 1: Write frontmatter + intro + the numbered flow outline.** Mirror the `ticket` skill's frontmatter conventions (`name`, `description`, `argument-hint`, `allowed-tools`, `disable-model-invocation`). Write exactly:

```markdown
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
```

- [ ] **Step 2: Verify frontmatter parses and matches conventions.** Run:

```bash
head -7 .claude/skills/project/SKILL.md
diff <(sed -n '1,7p' .claude/skills/ticket/SKILL.md | grep -oE '^[a-z-]+:') <(sed -n '1,7p' .claude/skills/project/SKILL.md | grep -oE '^[a-z-]+:')
```

Expected: the same frontmatter keys appear in both skills (`name`, `description`, `argument-hint`, `allowed-tools`, `disable-model-invocation`), in the same order.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/project/SKILL.md
git commit -m "feat: scaffold /project skill (frontmatter + flow outline)"
```

---

## Task 3: Sections 1–2 — intake + make the claim falsifiable

**Files:**
- Modify: `.claude/skills/project/SKILL.md` (append after the flow outline)

- [ ] **Step 1: Append the intake + falsifiability guidance.** Write:

```markdown
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
```

- [ ] **Step 2: Verify the section reads in-style.** Re-read it against `.claude/skills/ticket/SKILL.md`. Expected: prose + tight lists, no YAML schema, no banned jargon (`SPECIFIED`, `Scope fences`, `Estimated LoC`), pushback scoped to plan/claim not the idea.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/project/SKILL.md
git commit -m "feat: /project intake + falsifiability sections"
```

---

## Task 4: Section 3 — the gated milestone arc

**Files:**
- Modify: `.claude/skills/project/SKILL.md`

- [ ] **Step 1: Append the milestone-arc guidance.** Write:

```markdown
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
```

- [ ] **Step 2: Verify against the rubric's "Milestone arc" section.** Re-read Task 1's rubric. Expected: the guidance, if followed, would produce milestones satisfying every "Milestone arc" checkbox (ordered arc, real gate with ≥2 branches incl. non-proceed, gates only on go/no-go points, increasing dates, dependency chain).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/project/SKILL.md
git commit -m "feat: /project gated milestone arc section"
```

---

## Task 5: Sections 4–6 — rolling wave, ticket subagents, Linear write, re-entry

**Files:**
- Modify: `.claude/skills/project/SKILL.md`

- [ ] **Step 1: Append the rolling-wave + orchestration + write + re-entry guidance.** Write:

```markdown
## 4 · Author the near-term wave

Gated research means most downstream tickets are **contingent** — you cannot author the main
sweep before the pilot gate tells you which arm to sweep. So plan in a rolling wave:

- Build the **full milestone arc** now (cheap, and it's the real plan).
- Fully author tickets **only up to the first unresolved gate** — the work that is certain to
  happen (setup, the first pilot).
- Leave gated-downstream milestones as **gate + a one-line intent**. Their tickets get authored
  later, on re-entry, once the gate resolves and the branch is known.

**Delegate ticket authoring to the `ticket` skill.** Front-load all clarification here at the
project level so the subagents never need to stop and ask. For each near-term ticket, spawn a
`Task` subagent that:

- is told to author the ticket by applying `.claude/skills/ticket/SKILL.md`;
- receives the project description, its milestone, the sibling ticket titles, and the ticket's
  intent as context;
- runs **non-interactively** — it returns a ticket draft; if it hits a genuine blocking
  ambiguity it returns that as a flagged question instead of asking the user.

Spawn the wave's subagents in parallel (one message, multiple `Task` calls). Collect the drafts;
batch any flagged questions back to the user in **one** consolidated round.

## 5 · Review with the human

Present the project description, success criteria, the milestone arc, and the near-term ticket
drafts. The human resolves any flagged questions, **sets priority, and sets due dates** — never
invent either. Confirm the gate structure. Get explicit approval before any write to Linear.
In refine mode (an existing project), get explicit approval for anything that renames, moves, or
removes existing milestones/issues — never clobber silently.

## 6 · Write to Linear

You — the orchestrator — own every Linear write, so ordering and relations stay consistent. In
order:

1. Create the project (or, in refine mode, update its description only with approval): name,
   summary, rendered description + success criteria, team, lead, start/target dates, priority.
2. Create milestones in dependency order, each with its target date and a body that includes its
   gate (criterion + branches) when it has one.
3. Create the near-term tickets in their milestone from the approved drafts.
4. Set milestone/ticket `blocked_by` / `blocks` and parent/child relations **last**, so
   referenced ids resolve.

Render everything as clean Markdown. Never paste the planning Q&A into descriptions. Return the
project URL and a one-line-per-milestone summary.

## 7 · Re-entry

When a gate resolves, the user returns with the outcome. Load the existing project + milestones
(refine mode), pick the branch the gate selected, and author the next wave of tickets for the
now-unblocked milestone(s) — same delegation, same review, same write order. The downstream that
the gate ruled out stays unbuilt.
```

- [ ] **Step 2: Verify against the rubric's "Rolling wave" section.** Re-read Task 1's rubric. Expected: following this guidance yields fully-authored tickets only up to the first gate and gate+intent downstream — both "Rolling wave" checkboxes covered. Confirm all Linear writes live in the orchestrator (subagents draft only).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/project/SKILL.md
git commit -m "feat: /project rolling-wave authoring, ticket delegation, Linear write, re-entry"
```

---

## Task 6: Anti-ceremony guardrails + README wiring

**Files:**
- Modify: `.claude/skills/project/SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: Append the altitude / common-mistakes guardrail to the skill.** This keeps the skill from drifting back toward the v1 ceremony. Write:

```markdown
## Keep it light

The structure that earns its place is gates and off-ramps. Everything else is prose. Avoid the
ceremony this skill exists to replace:

| Don't | Do |
|---|---|
| A YAML schema the plan must fill | Prose description + a tight milestone list |
| A gate on every milestone | Gates only on real go/no-go points |
| Authoring the whole project into tickets up front | Rolling wave — near-term only, gate + intent downstream |
| Inventing priority or due dates | Leave them for the human |
| `SPECIFIED / AGENT_DECIDES`, LoC estimates, scope-fence headings | Plain prose; trust the ticket skill for ticket-level detail |
| Re-arguing the idea | Pressure-test the plan and the claim's testability |
```

- [ ] **Step 2: Update `README.md`.** Move `/project` from "In progress" into the Skills table and drop the now-stale "in progress" bullet. Apply this change — replace the Skills table body and the In-progress bullet:

Skills table — add the row:

```markdown
| `project` | [`.claude/skills/project`](./.claude/skills/project) | Turn an ML research idea + hypothesis into a developable Linear project: off-ramped success criteria, a gated milestone arc (day 0 → publication), and rolling-wave tickets authored via the `ticket` skill. |
```

In-progress section — replace the `/project` bullet with a pointer to the design + eval:

```markdown
- `/project` design + eval live in [`docs/superpowers/specs`](./docs/superpowers/specs) and [`.claude/skills/project/eval`](./.claude/skills/project/eval).
```

- [ ] **Step 3: Verify.** Run:

```bash
grep -c "^| \`" README.md          # expect ≥ 2 skill rows (ticket + project)
test -f .claude/skills/project/SKILL.md && echo "skill present"
```

Expected: ≥2 skill rows; "skill present".

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/project/SKILL.md README.md
git commit -m "feat: /project anti-ceremony guardrails + README wiring"
```

---

## Task 7: Dry-run the skill against the fixture (the "run")

Validates the finished skill end-to-end without touching Linear.

**Files:**
- Read: `.claude/skills/project/SKILL.md`, `.claude/skills/project/eval/swarm-moments-input.md`, `.claude/skills/project/eval/rubric.md`

- [ ] **Step 1: Dry-run.** In a scratch session, invoke the skill on the fixture input but **stop before any Linear write** (treat Phase 6 as "render the plan locally"). Feed it `swarm-moments-input.md` as the idea+hypothesis+why. Produce: the project description + success criteria, the full milestone arc with gates, and the near-term ticket drafts — as local Markdown.

- [ ] **Step 2: Score against the rubric.** Go through `rubric.md` checkbox by checkbox against the rendered output. Expected: every checkbox passes. In particular confirm — at least one headline + one off_ramp criterion; a real gate with a non-proceed branch on the D-arm pilot; tickets authored ONLY up to that first gate, with later milestones left as gate+intent.

- [ ] **Step 3: Fix gaps.** For any failed checkbox, edit `.claude/skills/project/SKILL.md` to address the root cause (e.g. if the dry-run authored all milestones' tickets, strengthen the Section-4 rolling-wave instruction). Re-run Steps 1–2 until the rubric passes.

- [ ] **Step 4: Commit any fixes.**

```bash
git add .claude/skills/project/SKILL.md
git commit -m "fix: /project skill passes golden-fixture rubric"
```

---

## Self-review notes (author)

- **Spec coverage:** intake, falsifiability/off-ramps (Task 3), gated arc (Task 4), rolling wave + ticket subagent delegation + Linear write + re-entry (Task 5), light related-work/comparability (Task 3), pushback scope (Task 3), dry-run + golden eval (Tasks 1, 7), bare-skill form + README (Tasks 2, 6). Refine-mode safety covered in Task 5 §5–6. All spec sections map to a task.
- **No fabricated tests:** verification is rubric-vs-dry-run, appropriate for a prose artifact.
- **Naming consistency:** the skill file is `.claude/skills/project/SKILL.md` throughout; eval files under `.claude/skills/project/eval/`; success-criteria kinds `headline | floor | off_ramp | generalization` used identically in fixture, rubric, and skill Section 2.
```
