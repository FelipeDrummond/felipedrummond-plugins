---
name: ticket
description: Use when the user wants to create or refine a Linear ticket for a staff engineer or an autonomous coding agent to execute — turning a rough request into a well-placed, right-sized ticket.
argument-hint: "[rough description of the work]"
allowed-tools: Read, Glob, Grep, Task, mcp__linear-server
disable-model-invocation: true
---

# Writing a Linear ticket

Write the ticket a **staff engineer** would be glad to receive: enough **context** to build
the right mental model, the **goal** as an outcome, and the **constraints** that genuinely
matter — then trust them to decide *how*. You are writing for a peer, not programming a robot.

**One ticket = one PR**, roughly half a day of work (~0.5–0.7 day). Bigger than that → split.

## Workflow

1. **Clarify — never assume.** Restate the request in one or two sentences and ask the
   refining questions that actually change the ticket (what the terms mean, which behaviours
   are in scope, where state lives, what "done" looks like). Ask them in one batch; stop when
   the picture is clear or the user says "good enough". A rough request almost always hides a
   branch point — find it before drafting.
2. **Gather context only when you need it, and say so first.** Before reading code or pulling
   from Linear, tell the user what you're about to look at and why. Use `Task` (Explore agents)
   to read the real code so the ticket's references are true, not guessed. Pull the project and
   sibling issues from Linear so the ticket lands in the right place.
3. **Size and split.** If the work is more than ~0.5–0.7 day, make a parent issue that holds
   the shared context and a **flat** list of sub-issues (no nesting), each one PR. When several
   tickets form distinct streams of work, group them with Linear **projects and milestones** —
   not prose labels.
4. **Write it** in the house style below.
5. **Place and submit.** Defaults, chosen for the user: an educated-guess **project** and
   **milestone**, the **current cycle**, status **Todo**, and assignee = the requesting user
   when the work doesn't name an obvious owner. **Ask permission before** creating a ticket
   with *no* project or *no* milestone, in any status other than Todo, or in any cycle other
   than the current one. **Priority and due date are the human's to set** — never invent them.
   Create via the Linear MCP, then **sweep every live ticket**: replace any placeholder
   reference (`sub-issue 1`, `stream A`, a draft id) with the real Linear ticket number, and
   express every dependency as a native **blocked-by / blocks** or **parent / child** relation.
   A live ticket must contain no fictional ticket, stream, or lane references.

## Write like this

> **Add status observability across the V2 batch → job → patch-batch hierarchy**
>
> **Context**
> The V2 API decomposes work into a hierarchy: a batch has many jobs; a job has many
> patch-batches. Jobs still map 1:1 to a COG. Today there's no way to see where work stands
> across these levels.
>
> **Goal**
> Give clients full visibility into the status of batches, jobs, and patch-batches, and the
> mapping between levels:
> - list batches, jobs, and patch-batches
> - `get_batch_status` — a batch's status and its jobs
> - `get_job_status` — a job's status and its patch-batches; **must return the job's COG**
> - `get_patch_batch_status` — a patch-batch's status
>
> **Acceptance criteria**
> - [ ] All routes behind auth; status read from Firestore
> - [ ] Responses are narrowly typed
> - [ ] List responses are paginated with a cursor — never unbounded
> - [ ] Unknown batch / job / patch-batch id → 404
> - [ ] 100% unit coverage via positive and negative tests
> - [ ] Prefer routes split by concern over one large file

**Why this works:** it leads with the domain model so the reader understands the *why*; the
goal is an outcome plus the few constraints that matter (`must return the COG`); the acceptance
criteria are a checklist of real, checkable constraints (auth, typing, pagination, 404s,
coverage) that bound the solution without dictating internals. *How* to lay out the routes,
name the models, or shape each response is left to the engineer.

## Not like this

> **Delta from parent** — Add two GET routes under `/batch/{id}/jobs/{job_id}`… **/patches** →
> 200 with a bare array ordered by `patch_batch_idx`; each element has `patch_batch_idx`
> (int, always), `status` (always), `point_count` (int|null)… **Spec partitioning** —
> SPECIFIED: exact route paths…; AGENT_DECIDES: model names…; ASK_FIRST: None.
> **Scope fences** — Do not wire OTel… **Estimated LoC** — impl 130 · tests 150.

**Why this fails:** it specifies the *how* byte-for-byte (every field, nullability, ordering),
enumerates every route × status case, and buries the goal under jargon scaffolding. It leaves
the engineer no room to think. **Banned:** `Delta from parent`, `Spec partitioning`,
`SPECIFIED / AGENT_DECIDES / ASK_FIRST`, `Scope fences`, `Context anchors`, `Estimated LoC`,
and exhaustive per-case enumeration.

**Altitude:** use only the sections that add signal — Context almost always, Goal, Acceptance
criteria, and a one-line user story when it sharpens intent. Drop any heading you'd leave
empty. Prefer prose and a tight checklist over nested taxonomies.

## When an autonomous agent will execute it

A staff engineer supplies judgment an agent doesn't: they won't quietly refactor half the
module, and they stop to ask when a request forks. When the executor is a coding agent, add
the two constraints you'd otherwise trust a human to bring — as plain prose woven into the
goal or criteria, never as headings or taxonomy:

- **Name what's off-limits** when the change could sprawl — one line: *"Leave the existing
  auth middleware and the batch schema untouched."* It bounds the blast radius without
  dictating the design.
- **Flag the fork the agent can't resolve alone** — *"If the status field isn't on the job
  document, stop and ask rather than adding it."* It turns a silent guess into a question.

Use them only where the risk is real. A ticket with no sprawl risk and no live ambiguity
needs neither — don't add them as ceremony.

## Common mistakes

| Mistake | Instead |
|---|---|
| Specifying response shapes / field layouts / internal layering | State the constraint that matters; leave the design to the engineer |
| Enumerating every route × status × case | Give representative criteria; trust the engineer to cover the rest |
| Adding empty ceremony headings | Keep only sections that carry signal |
| Jargon scaffolding (`Scope fences`, `Estimated LoC`, …) | Plain Context / Goal / Acceptance criteria |
| Guessing meaning instead of asking | Ask the refining question first |
| One giant ticket that's really three PRs | Split into a parent + flat sub-issues |
| Prose like "see the patches ticket" | A real blocked-by / parent-child relation |
| Letting an agent sprawl into adjacent code or guess at a fork | Name what's off-limits and the stop-and-ask branch point (only when the risk is real) |

## Linear notes

- Sub-issues are flat (no nesting). The parent holds shared context; each sub-issue holds its
  own acceptance criteria.
- Render the ticket as clean Markdown. Never paste the clarifying Q&A into the description.
- Set `blocked_by` / `blocks` and parent/child relations *after* all tickets exist, so the
  referenced ids resolve.
