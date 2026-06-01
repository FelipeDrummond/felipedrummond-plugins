# Design — `/implement`: the ticket executor skill

**Date:** 2026-06-01
**Status:** Design in review
**Form:** a third skill in the `linear-planning` plugin at
`linear-planning/skills/implement/SKILL.md`, matching the `ticket` and `project` skills
(prose-first, `disable-model-invocation: true`, Linear MCP).

## Why this skill

The plugin has an author (`ticket`) and a planner (`project`). This is the **executor** that
closes the loop: read the Linear ticket the `ticket` skill produced and implement it. It *is*
the staff engineer the ticket is written for — it reads the goal, constraints, and acceptance
criteria, then decides *how*, trusting its own judgment exactly as the ticket intends. It does
not need the ticket to over-specify the path, because over-specifying is the thing the `ticket`
skill deliberately avoids.

Intended to be invoked **in plan mode**: it researches the code, presents an implementation
plan for approval, then executes on approval.

## Philosophy: thin orchestrator over a trusted toolkit

The user runs superpowers, which already owns rigorous implementation discipline (plans, TDD,
verification, branch/PR finishing). This skill does **not** restate that discipline. It is
self-contained only on the **ticket-specific seam** — reading the ticket, guarding parents,
mapping acceptance criteria to a success contract, and writing back to Linear — and delegates
everything generic to the superpowers skills it already trusts. Same anti-ceremony stance as
the sibling skills: don't re-implement what a trusted skill already encodes.

## Shape & placement

- Path: `linear-planning/skills/implement/SKILL.md`.
- Name: `implement` (a verb completing author → plan → **execute**). Alternatives considered:
  `execute`, `ship`.
- Frontmatter, matching siblings:
  - `disable-model-invocation: true` — explicitly user-invoked.
  - `argument-hint: "[Linear issue id or url]"`.
  - `allowed-tools` broadened beyond the read-only siblings because this skill writes code:
    `Read, Glob, Grep, Task, Bash, Edit, Write, mcp__linear-server`.
- **MCP name:** `linear-server`, matching the `ticket`/`project` skills (even though this
  environment also exposes `linear-personal` / `claude_ai_Linear`).

## Flow (built around plan-mode invocation)

1. **Resolve the ticket.** Read the id/url argument; if absent, ask. Fetch via
   `mcp__linear-server` `get_issue`.
2. **Parent guard.** If the issue has sub-issues, refuse — a parent is shared context, not a
   single PR — and list the children in blocked-by / dependency order for the user to pick
   one. This preserves the `ticket` skill's **one ticket = one PR** invariant. (Single-ticket
   only; no auto-advancing or batch-sequencing through children.)
3. **Build the mental model.** Parse Context / Goal / Acceptance criteria. The
   acceptance-criteria checklist becomes the literal **success contract**. Honor any agent
   constraints the ticket carries ("leave X untouched", "stop and ask if Y").
4. **Research (in plan mode).** Explore the real code with `Task`/Explore subagents to ground
   the plan in what exists, not guesses.
5. **Plan.** Delegate to superpowers **`writing-plans`** to turn the acceptance criteria into
   an implementation plan; present it via **ExitPlanMode** for approval. ← the plan-mode
   handoff.
6. **Implement (on approval).** Branch first, then drive the work through
   **`subagent-driven-development`** / **`executing-plans`**, with
   **`test-driven-development`** for the red/green loop.
7. **Verify.** Run **`verification-before-completion`**, checking every acceptance-criteria
   box. Use **`systematic-debugging`** on failures. Never claim done on a partial pass.
8. **Finish.** Use **`finishing-a-development-branch`** to commit and open the PR linked to
   the ticket.
9. **Close the loop in Linear.** See below.

## Step 9 — close the loop in Linear

- **Status:** move Todo → In Progress (at step 6) → In Review (at PR). Any transition beyond
  this default path is confirmed first, matching the siblings' ask-before-non-default stance.
- **PR link:** attach / reference the PR on the issue.
- **Closing comment** — the engineer's handoff note, because implementation surfaces what the
  author couldn't know:
  - **Outcome** — what was built; which acceptance criteria are met vs. any deliberately
    deferred.
  - **Consequences** — notable decisions, scope that shifted, anything downstream this touches.
  - **What follows** — concrete next steps, expressed as native Linear relations wherever
    possible rather than prose:
    - discovered follow-up work → **offer** to create a new ticket (delegating to the sibling
      `ticket` skill) and link it `blocks` / `related`;
    - affects an **existing** ticket → link the relation and note it;
    - nothing follows → say so explicitly.
  - Stays prose + native relations, no fictional ticket references — consistent with the
    `ticket` skill's "express every dependency as a real blocked-by / blocks relation" rule.
    Creating a follow-up ticket is **offered, not automatic** (ask-before-write).

## Delegation map (the thin-orchestrator core)

| Concern | Owner |
|---|---|
| Read ticket, parent guard, map criteria → success contract, Linear write-back | **this skill** (self-contained) |
| Plan from acceptance criteria | `writing-plans` |
| Implement | `subagent-driven-development` / `executing-plans` |
| Red / green loop | `test-driven-development` |
| Verify against criteria | `verification-before-completion` |
| Debug failures | `systematic-debugging` |
| Branch + PR | `finishing-a-development-branch` |

## Keep it light (anti-ceremony, mirroring the siblings)

| Don't | Do |
|---|---|
| Re-implement TDD / planning / PR discipline in prose | Delegate to the superpowers skill that owns it |
| Implement a parent issue as one PR | Refuse and list children to pick from |
| Auto-advance or batch-sequence through sub-issues | One ticket = one PR per invocation |
| Invent Linear status transitions | Default path only; confirm anything else |
| Claim done on a partial acceptance-criteria pass | Verify every box; debug failures first |
| Auto-create follow-up tickets | Offer; create via the `ticket` skill on approval |
| Fictional "see the follow-up" prose | Native blocked-by / blocks / related relations |
| Sprawl past what the ticket scopes | Honor the ticket's off-limits / stop-and-ask lines |

## Out of scope (YAGNI)

- Batch-implementing a whole parent's sub-issues in one run (single ticket per invocation).
- Inferring the ticket from the git branch or listing assigned tickets (explicit arg, else ask).
- A self-contained TDD / plan / PR engine (delegated to superpowers).
- Auto-setting priority or due dates (human-only, as in the siblings).

## Build note

Because the artifact is itself a skill, the implementation step uses superpowers'
**`writing-skills`** discipline (not `writing-plans`).
