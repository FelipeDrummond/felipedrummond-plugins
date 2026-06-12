# `research-pod` — autonomous research cycle plugin

**Date:** 2026-06-12
**Status:** Design approved, pending implementation plan
**Plugin:** `research-pod` (new plugin in this repo, 2 skills)

## Problem

The `linear-planning` `/project` skill plans ML research as a gated milestone arc, and the
`pod-milestone` skill ships a milestone's tickets as a coordinated pod — but a human still
drives the outer research loop by hand: run the milestone, launch the experiments, read the
results against the gate, decide the branch, re-invoke `/project` to author the next wave.
For research that spans days/weeks and many gates, that human glue is the bottleneck.

`research-pod` automates that outer loop with a two-tier researcher hierarchy: a
**principal researcher** making high-level direction decisions and **junior researchers**
making low-level ones, escalating upward only when a decision is genuinely the user's.

## What this is — and is not

- **Is:** an orchestrator for the full idea → publication (or off-ramp) cycle, highly
  autonomous, interactive only at kickoff, escalations, and gate notifications.
- **Is not:** a replacement for `/project` (planning) or `pod-milestone` (ticket
  execution) — it composes them. It is also not a literature-research tool.

## Plugin layout

```
research-pod/
  .claude-plugin/plugin.json
  skills/
    research/SKILL.md          # orchestrator — the principal researcher (/research)
    research-junior/SKILL.md   # brief skill — generates the junior prompt (mirrors pod-engineer)
```

Prerequisites declared, not bundled: `linear-planning` (`/project`, `/ticket`), the
`pod-*` skill family (`pod-milestone`, `pod-engineer`, `pod-merge-driver`, `pod-linear`,
`pod-teardown`), the `superpowers` plugin, Claude Code team features (`TeamCreate`,
`TaskCreate`/`TaskUpdate`, `SendMessage`, `Agent`), Linear CLI or MCP, `gh`.

## Roles & topology

```
USER
  ▲ escalations only (budget, direction, preference)
  │
PRINCIPAL (main session, /research)
  • invokes /project to create + re-plan the arc
  • decides gate branches (autonomous when pre-declared)
  • spawns 1 junior per unblocked milestone; triages junior questions
  ▼
JUNIOR-M<k> (background Opus agent, one per active milestone)
  • invokes /pod-milestone as that pod's coordinator
  • supervises pod outputs for scientific validity
  • launches + monitors experiment runs per the runbook
  • analyzes results vs the gate; reports via SendMessage
  • never talks to the user
      ▼
  pod: merge-driver + engineers (owned by pod-milestone)
```

- **Concurrency:** parallel where the arc allows — one junior per unblocked milestone.
  The charter's budget ceiling is the natural brake; no artificial junior cap.
- **Junior model is Opus**: it coordinates a pod and makes research judgments. Sonnet
  stays at the pod-engineer level beneath it.
- Two team scopes, deliberately distinct: one **project team** (created at kickoff,
  reused for the project's lifetime) holds principal ↔ junior messaging; each junior's
  `pod-milestone` invocation creates its own **pod team** (driver + engineers) exactly as
  that skill already does, torn down per milestone via `pod-teardown`.

## Principal flow (`research` skill)

### Phase 0 — Mode detect

- Args contain a new idea → **kickoff**.
- Args name an existing Linear project, or the project's log dir exists → **recovery**:
  rebuild state from log tail + Linear ground truth (Linear wins on disagreement), resume
  mid-cycle — mid-milestone, awaiting a gate, or awaiting a user answer to an escalation.

### Phase 1 — Kickoff

1. Invoke `/project` with the idea/hypothesis/why. Its own interactive flow runs
   unchanged: falsifiable success criteria, gated milestone arc, near-term tickets, user
   approval before any Linear write.
2. Collect the **research charter** from the user in one consolidated round:
   - **Experiment runbook** — how to launch runs (local GPU / SSH box / cloud job), where
     metrics land (wandb, CSV, logs), how to tell a run is healthy vs dead.
   - **Budget ceiling** — overall compute budget and a per-milestone cap; what counts as
     an overrun.
   - **Escalation preferences** — notification cadence/channel, anything the user wants
     gated beyond the default matrix.
3. Write the charter as a **Linear document on the project** (ground truth, juniors read
   it) and log its path.

### Phase 2 — The cycle

Loop until the publication milestone is done or an off-ramp is taken:

1. Compute unblocked milestones from the arc: Linear milestone states + dependency
   relations + resolved gates.
2. Spawn one junior per unblocked milestone via the `research-junior` brief
   (`Agent(model="opus", team_name=…, name="junior-m<k>", run_in_background=true)`).
3. Watch SendMessage. Triage junior questions: answer low-level research decisions within
   the charter yourself; escalate to the user **iff** budget / direction / preference.
4. On a junior's gate report:
   - Result lands cleanly in a pre-declared branch → take it autonomously, notify the
     user (non-blocking).
   - Ambiguous / off-ramp / budget- or direction-touching → escalate and wait.
5. Re-enter `/project` (refine mode) to author the next ticket wave on the chosen branch.
6. Confirm the finished junior's `pod-milestone` run tore down its own pod team (its
   Phase 5 delegates to `pod-teardown`), retire the junior, log, loop.

### Phase 3 — Wind-down

Publication milestone done or off-ramp published: final summary to the user, teardown of
any remaining pod/team state, close the log.

## Junior flow (`research-junior` brief)

Brief inputs: `team_name`, `agent_name` (e.g. `junior-m3`), milestone id, project +
charter pointers, gate criterion + branches, `principal_name`, `base_branch`, log path.

1. **Orient** — read the milestone, its tickets, the charter, and prior log lines for
   this milestone.
2. **Build** — invoke `/pod-milestone` for the milestone's tickets; the junior is the pod
   coordinator. Exception the brief encodes: a 1-ticket milestone gets a single dispatched
   agent instead (pod-milestone's own "when NOT to use"). Review merged work against
   research intent — right metric, right baseline, no data leakage — before calling the
   build done. Code style/correctness review stays the pod's job.
3. **Experiment** — launch runs per the runbook; monitor on wakeups suited to run
   duration; kill clearly-dead runs. **Never exceed the milestone budget cap — a projected
   overrun is an immediate question to the principal, mid-run.**
4. **Analyze & report** — measured values vs the gate criterion, recommended branch,
   anomalies/caveats. Written as a Linear comment on the milestone (ground truth) +
   SendMessage to the principal. No-gate milestones (setup, writeup) report completion
   instead.
5. **Idle** — stay wakeable for principal follow-ups until retired.

Escalation discipline: anything outside its lane — material change to experiment design,
budget, ambiguous gate — is a question to the principal. Never to the user; never decided
silently.

## Escalation matrix (principal → user)

| Trigger | Behavior |
|---|---|
| Budget: projected/actual spend over a charter ceiling | **Block & ask** |
| Direction: off-ramp branch, result contradicting the arc, new milestone not in the plan | **Block & ask** |
| Preference: priority, due dates, publication venue/content choices | **Block & ask** |
| Clean pre-declared gate branch taken | Notify, don't wait |
| Milestone complete; junior spawned/retired; wave re-planned | Notify, don't wait |
| Everything else | Autonomous, logged |

## State & recovery

- Append-only log at `~/.claude/research/<project-slug>/log.ndjson`, same line format as
  the pod log: `{"ts":…,"role":…,"milestone":…,"msg":…}` with `role ∈ principal | junior
  | escalation`.
- Principal logs every junior spawn/retire, gate decision, escalation + answer, re-plan.
  Juniors log claim / run-launch / gate-report lines.
- Recovery = log tail + Linear reconciliation; Linear wins on disagreement; the
  reconciliation itself is logged. This is what makes the skill resumable across the
  days/weeks a research project spans.

## Failure handling

- **Junior dies or stalls mid-milestone** → principal pings once; no response → replace
  via a fresh brief (state recoverable from log + Linear).
- **Experiment infra unreachable** → junior escalates to principal; principal retries or
  escalates to the user if it blocks the gate.
- **`/project` re-entry would clobber existing milestones** → `/project`'s own
  refine-mode approval gate already covers this.
- **Pod-level failures** (CI red, cascade conflicts, Linear 401) → owned by
  `pod-milestone`'s existing failure handling; the junior escalates only what the pod
  can't resolve.

## Keep it light (anti-patterns)

| Don't | Do |
|---|---|
| Re-implement /project's planning logic in this skill | Invoke `/project`; it owns the arc |
| Re-implement pod coordination in the junior brief | Invoke `pod-milestone`; it owns the pod |
| Juniors asking the user anything | Juniors escalate to the principal only |
| Principal absorbing junior work when one stalls | Ping once, then replace |
| Escalating every gate to the user | Autonomous when the branch is pre-declared |
| Deciding off-ramps or budget overruns silently | Block & ask, always |
| Restating state in chat prose | Append a log line; chat points to the log |

## Verification

Dry-run the orchestrator on a toy research idea against a sandbox Linear team:
kickoff → charter → one fake milestone with a trivially checkable gate → confirm the gate
report, the autonomous branch decision, the `/project` re-entry, and recovery (kill the
session mid-cycle, re-invoke, confirm resume from log + Linear).

## Open questions

None blocking. Topology, gate authority, charter-at-kickoff, parallel-where-arc-allows
concurrency, and resumable lifecycle all confirmed with the user on 2026-06-12.
