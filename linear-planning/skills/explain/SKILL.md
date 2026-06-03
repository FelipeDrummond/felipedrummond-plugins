---
name: explain
description: Use when the user wants to make sense of an agent-written PR — explaining what it actually does, situating it in the project's direction, and flagging over-documentation, over-engineering, and bad names to cut or rename. An explainer and simplifier, not a bug-hunting reviewer. Invoked from inside a checkout of the PR's repo.
argument-hint: "[PR number or url]"
allowed-tools: Read, Glob, Grep, Task, Bash, Edit, Write, AskUserQuestion, mcp__linear-server
disable-model-invocation: true
---

# Explaining an agent-written PR

The code under this PR was written by an agent, not by hand. That means the diff carries the
agent's transient context but not its judgment: the *actual* change is buried under noise, the
work may have drifted from where the project is heading, and you get over-documentation,
speculative flexibility, and names that meant something to the agent and nothing to a later
reader (`_maybe_add_arm_a`).

You are the reader who has to make sense of it. Your job is to **explain and simplify**, not to
review for bugs. Tell the user what the PR really does, whether it fits the project, and what to
cut or rename — biased hard toward *less code*. Don't chase correctness, security, or style
nits. Don't praise the diff.

**Read-only on code until the user approves a change.** You explain first. Only after the
Verdict, and only on explicit approval, do you ever write (see *The handoff*).

## You orchestrate; trusted skills do the work

This skill owns the **explain-and-judge seam** — reading the PR, finding the project's
intent, and holding the simplicity stance. Generic work is delegated.

| Concern | Owner |
|---|---|
| Fetch PR title / body / diff / files | **this skill** (`gh pr view`, `gh pr diff`) |
| Find the linked Linear ticket → project, pull the *why* | **this skill** + `mcp__linear-server` |
| Read the surrounding code and `docs/` to situate the change | `Task` / Explore subagents |
| Hold the YAGNI / simplicity stance powering Cuts & Names | **this skill** (your judgment) |
| Materialize approved cuts as a follow-up ticket | sibling **`ticket`** skill |
| Apply approved cuts / renames on the PR branch (if chosen) | **this skill** (Edit/Write + Bash) |

## Workflow

1. **Resolve the PR.** Take the PR number/url from the argument; if none was given, ask —
   don't guess from the current branch. Use `gh pr view` and `gh pr diff` for the title, body,
   changed files, and diff. You are expected to be inside a checkout of the PR's repo.
2. **Establish the two reference frames** that *Fit* is judged against — don't conflate them:
   - **Where the project *is*** (the present, the past): what's already merged on `main` /
     `develop`. This is the code the PR builds on.
   - **Where the project is *heading*** (the future): the end goal and milestones — usually the
     linked Linear **project's description and milestones**, the originating ticket, and the
     repo's `docs/`. Get this from Linear: extract the ticket id from the PR title, branch, or
     body and fetch it (`get_issue` → `get_project`). If no link is discoverable, ask the user
     for the ticket rather than inventing project intent.
3. **Situate.** Dispatch `Task`/Explore subagents to gather both frames from the real repo, not
   the diff alone: the merged code around the touched modules (where the project *is*) and the
   project's prose context in `docs/` (often the *why* behind where it's *heading*). Agent-heavy
   repos tend to carry verbose docs — read enough to judge, don't drown in them.
4. **Produce the explanation.** The five-section contract below, in the terminal.
5. **Offer the handoff.** See below. Nothing is written without explicit approval.

## The explanation — Core → Fit → Cuts → Names → Verdict

Deliver these five sections, in order, in the terminal:

1. **Core** — what this PR actually *does*, in plain English (≤1 short paragraph), plus the
   handful of changes that *are* the change. Signal, not the full diff dump.
2. **Fit** — measured against both frames: does it build coherently on where the project *is*
   (the merged code), and does it serve where the project is *heading* (its end goal and
   milestones)? Say so plainly when the agent over-reached scope or solved a problem nobody has.
3. **Cuts** — over-documentation and speculative config/flexibility. Each item: a `file:line`
   and one line on why it's noise.
4. **Names** — confusing names (the `_maybe_add_arm_a` smell) → a concrete rename, with a
   rationale tied to what a reader *without* the agent's context needs to understand.
5. **Verdict** — the recommended simplification in one breath: what to keep, what to cut, what
   to rename — then the offer below.

## The handoff (offered, never automatic)

After the Verdict, let the user pick which findings survive, then offer two paths for them:

- **Follow-up Linear ticket** (or a plain plan) — author it via the sibling `ticket` skill and
  link it to the PR's ticket. Right when the PR is already merged or the cleanup is larger work.
- **Fix in the current PR** — apply the approved cuts/renames directly on the PR branch
  (Edit/Write, then commit). Right for an in-review PR where deferring the cleanup is silly.

Materialize only what was approved. Creating a ticket and editing the branch are both offered,
never automatic.

## Keep it light

| Don't | Do |
|---|---|
| Hunt correctness bugs, security, or style nits | Stay a focused explainer |
| Dump the full diff | Surface only the changes that *are* the change |
| Praise the diff | Bias toward less code |
| Guess the PR from the current branch | Take the arg; if absent, ask |
| Invent project intent when no ticket links | Ask for the ticket |
| Edit code before the Verdict and approval | Read-only until approved |
| Auto-create a ticket or auto-apply fixes | Offer both paths; act only on approval |
