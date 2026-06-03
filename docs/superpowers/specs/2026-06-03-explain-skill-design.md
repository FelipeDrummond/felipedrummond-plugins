# `/explain` — agent-PR explainer & simplifier

**Date:** 2026-06-03
**Status:** Design approved, pending implementation plan
**Plugin:** `linear-planning` (4th skill)

## Problem

Felipe's code is agent-written; he doesn't hand-write it. Agentic PRs share recurring
failure modes that a human reviewer has to catch by hand:

- **They're hard to *understand*.** A 1700-line PR (e.g. `swarm-moments#31`) buries its
  actual change under noise. What did this PR *really* do?
- **They drift from the project.** The building agent often lacks the sense of where the
  project is heading, so it solves a non-problem or over-reaches scope.
- **Over-documentation.** Verbose docs/comments nobody reads, which clutter the repo and
  pollute the context of future agents that *do* read it.
- **Over-engineering.** Speculative configurability and flexibility for a project that is
  actually narrow and straight — the `_maybe_add_arm_a` smell.
- **Bad naming.** Names that made sense to the agent's transient context but communicate
  nothing to a later reader (e.g. `_maybe_add_arm_a`).

The need is a **sense-checking explainer**, not a bug-hunting reviewer: something Felipe
reads to quickly understand and judge what the agent produced, biased hard toward *less
code* (mirrors the global CLAUDE.md §2 "Simplicity First").

## What this is — and is not

- **Is:** an explainer + simplifier. Tells you the core, situates it in the project, and
  flags what to cut/rename.
- **Is not:** a bug-hunting code reviewer. It does not chase correctness bugs, security, or
  style nits. It does not praise the diff.

## Placement & identity

- 4th skill in the `linear-planning` plugin: `ticket → project → implement → explain`
  (author → plan → execute → make-sense-of).
- Invoked as `/linear-planning:explain` (or `/explain`), `argument-hint: "[PR number or url]"`.
- Invoked from **inside a checkout of the PR's repo** (e.g. `swarm-moments`) so it can read
  the surrounding code and `docs/` for real project grounding — not just the diff.
- **Read-only on code until the user approves a change.** It explains first; only after the
  Verdict, and only on explicit approval, does it ever write (see §5).

## Architecture — thin orchestrator

Consistent with the plugin's prose-first, delegation-heavy style (mirrors `implement`):

| Concern | Owner |
|---|---|
| Fetch PR title/body/diff/files (`gh pr view`, `gh pr diff`) | **this skill** (Bash) |
| Find linked Linear ticket → project, pull the *why* | **this skill** (extract `JEV-xx` from PR title/branch/body → `get_issue` → `get_project`; ask if not found) |
| Read surrounding code/docs to situate the change | `Task`/Explore subagents (like `implement` step 4) |
| Hold the YAGNI/simplicity stance powering Cuts & Names | **this skill** (prose) |
| Materialize approved cuts as a follow-up | sibling **`ticket`** skill |
| Apply approved cuts/renames on the PR branch (if chosen) | **this skill** (Edit/Write + Bash) |

## Workflow

1. **Resolve the PR.** Take PR number/url from the argument; if absent, ask — don't guess
   from the current branch. Use `gh pr view` / `gh pr diff` for title, body, diff, files.
2. **Establish the two reference frames** that *Fit* is judged against — they are distinct:
   - **Where the project *is*** (present/past): what's merged on `main` / `develop` — the code
     the PR builds on.
   - **Where the project is *heading*** (future): the end goal and milestones, usually in the
     linked Linear **project's description and milestones**, the originating ticket, and `docs/`.
     Extract the ticket id from the PR title/branch/body, `get_issue` → `get_project`. If no
     link is discoverable, ask the user for the ticket rather than inventing project intent.
3. **Situate.** Dispatch Explore/`Task` subagents to gather both frames from the real repo, not
   the diff alone: merged code around the touched modules (where it *is*) and the project's
   prose context in `docs/` (the *why* behind where it's *heading*). Agent-heavy repos tend to
   carry verbose docs; read enough to judge, don't drown.
4. **Produce the 5-section explanation** (§4).
5. **Offer the handoff** (§5).

## §4. Output contract — Core → Fit → Cuts → Names → Verdict

Delivered in the **terminal only**. Five fixed sections:

1. **Core** — what this PR actually *does*, plain English, ≤1 short paragraph, plus the
   handful of changes that *are* the change (signal, not the full diff dump).
2. **Fit** — measured against both frames: does it build coherently on where the project *is*
   (merged code), and does it serve where it's *heading* (end goal + milestones)? Names it
   plainly when the agent over-reached scope or solved a non-problem.
3. **Cuts** — over-documentation and speculative config/flexibility, each with `file:line`
   and a one-line "why this is noise."
4. **Names** — confusing names (the `_maybe_add_arm_a` smell) → concrete rename suggestions
   with rationale tied to what a context-less reader needs.
5. **Verdict** — the recommended simplification in one breath: what to keep, cut, rename —
   then the offer in §5.

## §5. The handoff (offered, never automatic)

After the Verdict, offer the user a choice for the approved cuts/renames:

- **Follow-up Linear ticket** (or a plain plan) — materialized via the sibling `ticket`
  skill, linked to the PR's ticket. Good when the PR is already merged or the cleanup is
  larger work.
- **Fix in the current PR** — apply the approved cuts/renames directly on the PR branch
  (Edit/Write + commit). Good for an in-review PR where deferring is silly.

The user picks which findings survive and which path to take; the skill materializes only
what was approved. Nothing is written without that approval.

## Keep it light (anti-patterns)

| Don't | Do |
|---|---|
| Re-implement review discipline in prose | Stay a focused explainer |
| Hunt correctness bugs / security / style nits | That's not this skill's job |
| Dump the full diff | Surface only the changes that *are* the change |
| Praise the diff | Bias toward less code (CLAUDE.md §2) |
| Guess the PR from the current branch | Take the arg; if absent, ask |
| Invent project intent when no ticket links | Ask for the ticket |
| Edit code before the Verdict + approval | Read-only until approved |
| Auto-create tickets or auto-apply fixes | Offer both paths; act only on approval |

## Dependencies

- `gh` CLI authenticated for the PR's repo.
- A Linear MCP server named `linear-server` (plugin convention).
- Sibling `ticket` skill for the follow-up-ticket path.

## Open questions

None blocking. Name `explain` confirmed; both handoff paths confirmed.
