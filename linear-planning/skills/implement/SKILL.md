---
name: implement
description: Use when the user wants to implement an existing Linear ticket — reading a ticket authored for a staff engineer and carrying it through to a verified, merged-ready PR with a status and handoff written back to Linear. Typically invoked in plan mode.
argument-hint: "[Linear issue id or url]"
allowed-tools: Read, Glob, Grep, Task, Bash, Edit, Write, mcp__linear-server
disable-model-invocation: true
---

# Implementing a Linear ticket

You are the **staff engineer** the ticket was written for. It hands you the **context**, the
**goal** as an outcome, and the **constraints** that matter — and trusts you to decide *how*.
So decide. Don't wait for the ticket to spell out the path; the `ticket` skill deliberately
leaves that to you. Bring the judgment a ticket assumes: don't sprawl into adjacent code, and
stop to ask when a request genuinely forks.

**One ticket = one PR.** This skill implements a single ticket per invocation.

You will usually be invoked **in plan mode**: research the code, present a plan for approval,
then implement on approval. The steps below are built around that.

## You orchestrate; trusted skills do the work

This skill owns only the **ticket-specific seam** — reading the ticket, guarding parents,
turning acceptance criteria into a success contract, and writing back to Linear. Everything
generic is delegated to the superpowers skills that already own it. Don't restate their
discipline here; invoke them.

| Concern | Owner |
|---|---|
| Read ticket · parent guard · criteria → contract · Linear write-back | **this skill** |
| Turn criteria into a plan | **REQUIRED:** `superpowers:writing-plans` |
| Implement the plan | **REQUIRED:** `superpowers:subagent-driven-development` (or `superpowers:executing-plans`) |
| Red / green loop | **REQUIRED:** `superpowers:test-driven-development` |
| Verify against criteria | **REQUIRED:** `superpowers:verification-before-completion` |
| Debug failures | `superpowers:systematic-debugging` |
| Commit + open the PR | **REQUIRED:** `superpowers:finishing-a-development-branch` |

## Workflow

1. **Resolve the ticket.** Take the id/url from the argument; if none was given, ask for one —
   don't guess from the branch or pick from a list. Fetch it with the Linear MCP (`get_issue`).
2. **Parent guard.** If the issue has sub-issues, it's shared context, not a PR. Stop, say so,
   and list the children in blocked-by / dependency order for the user to pick one. Do not
   auto-advance through them or implement them as a batch.
3. **Build the mental model.** Read Context, Goal, and Acceptance criteria. The
   acceptance-criteria checklist is your **success contract** — every box must be checkable and
   checked before you call it done. Honor any constraints the ticket carries verbatim ("leave X
   untouched", "stop and ask if Y").
4. **Research (in plan mode).** Ground the plan in what actually exists. Use `Task`/Explore
   subagents to read the real code. Read the project's prose context too — a `docs/` directory
   (design specs, plans, architecture notes) often carries the *why* behind the code; consult it
   alongside the source so your plan respects decisions already made.
5. **Plan and present.** Use `superpowers:writing-plans` to turn the acceptance criteria into an
   implementation plan, then present it via **ExitPlanMode** for approval.
6. **Implement (on approval).** Branch first. Drive the work through
   `superpowers:subagent-driven-development` (or `superpowers:executing-plans`), with
   `superpowers:test-driven-development` for the red/green loop.
7. **Verify.** Run `superpowers:verification-before-completion` against the success contract —
   tick off every acceptance-criteria box. On a failure, use `superpowers:systematic-debugging`;
   never claim done on a partial pass.
8. **Finish.** Use `superpowers:finishing-a-development-branch` to commit and open the PR,
   linked to the ticket.
9. **Close the loop in Linear.** See below.

## Closing the loop in Linear

Move the status along the default path — **Todo → In Progress** once the plan is approved and
you actually start implementing (step 6), **→ In Review** at the PR. Don't touch status during
plan-mode research; if the plan is never approved, nothing moves. Read the team's real statuses
first; if those names don't exist, use the nearest equivalent. Any transition off this path (closing, blocking, a custom state) is the user's call —
ask first. Reference the PR on the issue.

Then post a **closing comment** — the handoff note, because implementing surfaces what the
author couldn't know:

- **Outcome** — what you built; which acceptance criteria are met, and any you deliberately
  deferred (and why).
- **Consequences** — decisions worth knowing, scope that shifted, anything downstream this
  touched.
- **What follows** — concrete next steps, as **native Linear relations**, not prose:
  - discovered follow-up work → **offer** to author a new ticket (delegating to the sibling
    `ticket` skill) and link it `blocks` / `related`;
  - it affects an **existing** ticket → link the relation and name it;
  - nothing follows → say so plainly.

Express every dependency as a real blocked-by / blocks / related relation — never a prose "see
the follow-up ticket". Creating a follow-up is **offered, not automatic**.

## Keep it light

| Don't | Do |
|---|---|
| Re-implement TDD / planning / PR discipline in prose | Delegate to the superpowers skill that owns it |
| Implement a parent issue as one PR | Refuse; list the children to pick from |
| Auto-advance or batch-sequence sub-issues | One ticket = one PR per invocation |
| Guess the ticket from the branch or a list | Take the arg; if absent, ask |
| Invent Linear status transitions | Default path only; ask before anything else |
| Claim done on a partial acceptance-criteria pass | Verify every box; debug failures first |
| Auto-create follow-up tickets | Offer; author via the `ticket` skill on approval |
| Prose like "see the follow-up ticket" | A real blocked-by / blocks / related relation |
| Sprawl into adjacent code, or silently resolve a fork | Honor the ticket's off-limits and stop-and-ask lines |
