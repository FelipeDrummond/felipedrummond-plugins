# Design — `/project`: research project planner

**Date:** 2026-05-31 (revised; supersedes the 2026-05-28 council/schema design)
**Status:** Design in review
**Form:** a bare skill at `.claude/skills/project/SKILL.md`, matching the repo's `ticket` skill
(no plugin packaging, no council agents).

## Why this was revised

The first version mirrored the *old* ticket pipeline — a 5-agent council, a rigid YAML
schema, linter checks, LoC estimates. Upstream then replaced that ticket skill with a
lightweight prose skill ("write for a staff engineer… trust them to decide *how*"). The
project skill should inherit that **philosophy**, not the machinery it rejected.

## Philosophy: light form, rigorous thinking

A ticket and a research plan are different artifacts:

- A **ticket** specifies one unit of work for an executor. Light wins because you trust the
  executor on *how*; over-specifying the path is brittle.
- A **research plan** specifies *a sequence of bets under uncertainty, from day 0 to
  publication*. Its load-bearing content is the **falsification logic** (what would prove the
  idea wrong, and what you do then) and the **de-risking order** (cheap experiments kill bad
  ideas before expensive ones).

So: follow the ticket philosophy (prose, signal-over-ceremony, lead-with-context, trust),
but accept that a research plan needs a richer *spine* than a ticket. That spine — gates and
off-ramps — is the intellectual substance, not ceremony. Swarm-Moments is the proof: it
reads as prose, yet its milestones are gates (G1/G2/G3 → proceed / pivot / off-ramp) and its
success criteria carry an explicit off-ramp ("if D is dead, ship the A-only paper").

Drop, relative to v1: the mandatory council, the fill-in YAML schema, linter rejection, LoC,
forced-empty fields. Keep: gated milestones, off-ramped success criteria, dependencies, and
the `/ticket` handoff — now via subagents and rolling-wave authoring.

## Inputs and outputs

**You bring** (diligence already done): the idea, the hypothesis, and the why — roughly the
top of a Swarm-Moments description.

**The skill produces the *how*:**
1. **Falsifiable success criteria with off-ramps** — formalize the hypothesis into measurable
   claims (headline / floor / generalization / off-ramp), each with a threshold. The off-ramp
   is non-negotiable.
2. **A gated milestone arc, day 0 → publication** — a cheap→expensive de-risking sequence.
   Each gate is a measurable go/no-go with branches (proceed / pivot / off-ramp). Gates only
   where there's a real decision, not on every milestone. A canonical research backbone
   (setup → de-risking pilots → core experiments → generalization → writeup/submit) is an
   *adaptable* default, not a template.
3. **Tickets**, authored by delegating to `/ticket` — see rolling wave.
4. Everything written to Linear: project (description + success criteria), milestones (gate,
   target date, dependencies), and near-term tickets.

## Flow (lightweight, conversational)

1. **Intake** — restate idea / hypothesis / why; confirm before spending tokens.
2. **Pressure-test the claim** — is the hypothesis falsifiable as stated? are success criteria
   measurable and off-ramped? Quick comparability check on the baselines/metric the user
   brought ("will this convince a reviewer?"). This is *light* — it does not go discover the
   literature. It pushes back here because gates can't exist without a falsifiable claim.
3. **Design the milestone arc** — the gated de-risking sequence to publication. Place gates
   where there's a genuine go/no-go.
4. **Identify tickets per milestone**; author the near-term wave via `/ticket` subagents (see
   below).
5. **Human review** — priority and due dates are human-set (never invented); approve the gate
   structure; approve before any write to Linear.
6. **Write to Linear** — project, then milestones in order, then near-term tickets; downstream
   milestones remain gate + intent. Set dependency relations last.
7. **Re-entry** — when a gate resolves, re-invoke to author the next wave on the branch taken.

## The spine: gated milestones + off-ramped success criteria

- **Success criteria** are typed (`headline | floor | generalization | off_ramp`), each with a
  threshold and a date. At least one headline and one off-ramp.
- **A gate** is a measurable exit decision on a milestone: criteria (e.g. "R²(N=16) ≥ 0.3")
  plus ≥2 branches, at least one non-proceed (a pivot or off-ramp must exist where the
  research can fail). Expressed in prose in the milestone body, not a schema.
- **Milestones** carry deliverables, an optional gate, a target date across the timeline,
  optional resource/compute cost, and dependencies on prior milestones.

These are guidance the skill applies, not a form it validates. No linter rejects a draft;
the skill simply writes good structure and the human approves.

## Rolling-wave authoring + `/ticket` orchestration

Gated research means downstream tickets are **contingent** — you cannot author the M5 main
sweep at day 0 because which arm gets swept isn't decided until G2/G3. So:

- Build the **full milestone arc** at the gate altitude up front (cheap, and it's the real
  plan).
- Fully author tickets — via `/ticket` subagents — **only up to the first unresolved gate**
  (the certain work: setup, first pilot).
- Leave gated-downstream milestones as **gate + one-line intent**. Author their tickets on
  re-entry, once the gate resolves and the branch is known.

**Orchestration:** the skill front-loads clarification *once* at the project level (the
planning dialogue), then spawns `/ticket` subagents for the near-term wave with the project
description, the target milestone, and sibling tickets injected as context — so the subagents
author from shared context instead of each interrogating the user. Any genuine per-ticket
question is batched back to the user in one consolidated round, not per-subagent chatter.

*Mechanics to settle in the plan:* invoking the ticket skill from a subagent likely means a
thin author-agent that runs the ticket workflow with milestone context injected (the ticket
skill is `disable-model-invocation: true` and interactive by default). Parallel subagents
must not each block on user questions.

## Pushback scope (flag for review)

The skill interrogates the **plan** ("this milestone sequence doesn't de-risk the expensive
step first"; "this gate doesn't measure the headline claim") and the **falsifiability /
comparability** of the criteria ("your headline isn't falsifiable as written"; "no off-ramp";
"that baseline won't convince a reviewer"). It does **not** re-litigate the idea itself —
diligence is assumed done. Open question for review: is this the right amount of challenge?

## Linear write strategy

1. Create (or, in refine mode, update with explicit approval) the project: name, summary,
   rendered description + success criteria, team, lead, start/target dates, priority.
2. Create milestones in dependency order, each with target date and a body that includes its
   gate (criteria + branches) when it has one.
3. Author + create near-term tickets in their milestone via `/ticket` subagents.
4. Set milestone/ticket dependency relations last, so referenced ids resolve.
- Refine mode never deletes; renames/moves only with explicit human approval. Return the
  project URL + milestone summary.

## Validation (skill artifacts → evals)

- **Dry-run:** stop before writing to Linear and render the full plan (milestone arc + gates +
  near-term tickets) locally. Fast inner loop.
- **Golden eval:** run against the Swarm-Moments idea/hypothesis/why into a throwaway team;
  check the generated arc against the real M0–M7 (gate placement, off-ramps, the day-0→pub
  shape).

## Out of scope (YAGNI)

- Multi-agent council, YAML schema, linter checks, LoC estimates (all dropped from v1).
- Literature discovery / citation hunting (the related-work step only pressure-tests what you
  bring).
- Authoring all tickets up front (rolling wave instead).
- Auto-setting priority or due dates (human-only).
- Cycles, initiative authoring beyond linking an existing one.
