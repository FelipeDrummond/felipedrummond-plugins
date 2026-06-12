# research-pod Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `research-pod` plugin — a `research` orchestrator skill (the principal researcher) and a `research-junior` brief skill — that automates the idea → publication research cycle on top of `/project` and `pod-milestone`, per the approved spec at `docs/superpowers/specs/2026-06-12-research-pod-design.md`.

**Architecture:** A new plugin directory `research-pod/` registered in the repo-root marketplace manifest. The `research` skill runs in the user's main session as the principal: it composes the existing `linear-planning:project` skill for planning and spawns one background Opus junior per unblocked milestone via a brief rendered from the `research-junior` skill; juniors coordinate their own `pod-milestone` pods and run experiments. All deliverables are prose Markdown skill files plus two small JSON manifests — there is no executable code, so verification is JSON validity, frontmatter correctness, and cross-reference consistency checks.

**Tech Stack:** Claude Code plugin format (`.claude-plugin/plugin.json`, `skills/*/SKILL.md` with YAML frontmatter), repo-root `marketplace.json`, Markdown prose in the repo's prose-first skill style.

---

### Task 1: Plugin scaffolding and marketplace registration

**Files:**
- Create: `research-pod/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create the plugin manifest**

Create `research-pod/.claude-plugin/plugin.json` with exactly:

```json
{
  "name": "research-pod",
  "displayName": "Research Pod",
  "version": "0.1.0",
  "description": "Autonomous research cycle on top of linear-planning and the pod-* skills: a principal researcher plans the gated arc via /project, spawns one junior researcher per unblocked milestone to build via pod-milestone and run the experiments, decides gate branches, and escalates only budget, research direction, and preference to the user.",
  "keywords": ["research", "linear", "milestones", "pods", "experiments", "autonomous", "orchestration"],
  "author": {
    "name": "Felipe Drummond",
    "email": "felipe2002drummond@gmail.com",
    "url": "https://github.com/felipedrummond"
  }
}
```

- [ ] **Step 2: Register the plugin in the marketplace manifest**

In `.claude-plugin/marketplace.json`, append a second entry to the `plugins` array (after the `linear-planning` entry, comma-separated):

```json
    {
      "name": "research-pod",
      "source": "./research-pod",
      "description": "Autonomous research cycle on top of linear-planning and the pod-* skills: a principal researcher plans the gated arc via /project, spawns one junior researcher per unblocked milestone to build via pod-milestone and run the experiments, decides gate branches, and escalates only budget, research direction, and preference to the user.",
      "version": "0.1.0"
    }
```

- [ ] **Step 3: Verify both JSON files parse**

Run:
```bash
python3 -m json.tool research-pod/.claude-plugin/plugin.json > /dev/null && python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo OK
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add research-pod/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(research-pod): scaffold plugin and register in marketplace"
```

---

### Task 2: The `research` skill (principal orchestrator)

**Files:**
- Create: `research-pod/skills/research/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `research-pod/skills/research/SKILL.md` with exactly this content:

````markdown
---
name: research
description: Use when the user brings a research idea — or an existing research-pod Linear project to resume — and wants the idea → publication cycle run autonomously. /project plans the gated milestone arc; one junior researcher per unblocked milestone builds via pod-milestone and runs the experiments; this session, as principal researcher, decides gate branches and escalates only budget, research direction, and preference to the user.
argument-hint: "[idea + hypothesis + why | existing Linear project]"
disable-model-invocation: true
---

# Research Principal

You are the **principal researcher** for an ML research project. You own the arc — planning
it with the `linear-planning:project` skill, deciding gate branches when results come in,
re-planning each wave. You do not build tickets or run experiments yourself: one **junior
researcher** per active milestone does that, each coordinating its own `pod-milestone` pod.
The user is your PI for exactly three things — **budget, research direction, preference** —
and is otherwise only notified. Aim to be highly autonomous; interact only at kickoff,
escalations, and gate notifications.

```
USER
  ▲ escalations only (budget, direction, preference)
  │
PRINCIPAL (you, this session)
  • /project: create + re-plan the arc
  • decide gate branches; triage junior questions
  │ one junior per unblocked milestone
  ▼
JUNIOR-M<k> (background Opus agent — brief from `research-junior`)
  • coordinates its own pod-milestone pod
  • supervises pod outputs for scientific validity
  • launches + monitors experiment runs per the charter
  • analyzes results vs the gate; reports up; never talks to the user
      ▼
  pod: merge-driver + engineers (owned by pod-milestone)
```

Two team scopes, deliberately distinct: the **project team** (created here, lives for the
whole project) carries principal ↔ junior messaging; each junior's `pod-milestone`
invocation creates its own **pod team** (driver + engineers), torn down per milestone via
`pod-teardown`.

## Prerequisites

- `linear-planning` plugin — `project` and `ticket` skills
- `pod-milestone`, `pod-engineer`, `pod-merge-driver`, `pod-linear`, `pod-teardown` skills
- `superpowers` plugin
- Claude Code team features: `TeamCreate`, `TaskCreate`, `TaskUpdate`, `SendMessage`, `Agent`
- Linear CLI or Linear MCP; `gh` and `git` on `$PATH`

## Phase 0 — Mode detect

- Args contain a **new idea** (hypothesis + why) → kickoff (Phase 1).
- Args name an **existing Linear project**, or `~/.claude/research/<project-slug>/` already
  exists → recovery: run the recovery steps in *State & recovery*, then resume the cycle
  wherever it left off — mid-milestone, awaiting a gate, or awaiting a user answer to an
  escalation. Never re-kickoff a project that already has a log.

## Phase 1 — Kickoff

1. **Plan the arc.** Invoke `Skill("linear-planning:project", args=<idea + hypothesis + why>)`.
   Its interactive flow runs unchanged — falsifiable success criteria, gated milestone arc,
   near-term tickets, user approval before any Linear write. Do not re-implement or
   second-guess its planning; you consume its output (the project, milestones, gates).
2. **Collect the research charter** from the user in **one** consolidated round:
   - **Experiment runbook** — how to launch runs (local GPU / SSH box / cloud job), where
     metrics land (wandb, CSV, logs), how to tell a run is healthy vs dead.
   - **Budget ceiling** — overall compute budget and a per-milestone cap; what counts as an
     overrun.
   - **Escalation preferences** — notification cadence/channel, anything the user wants
     gated beyond the default matrix below.
3. **Write the charter as a Linear document on the project** (juniors read it from there —
   it is ground truth, not session state). Log its URL.
4. **Create the project team**: `TeamCreate(team_name=research-<project-slug>,
   agent_type="orchestrator", description="<one-line project summary>")`.
5. **Initialize the log** at `~/.claude/research/<project-slug>/log.ndjson` (see *State &
   recovery*) with a kickoff line recording the project URL, charter doc URL, and team name.

## Phase 2 — The cycle

Loop until the publication milestone is done or an off-ramp is taken:

1. **Compute unblocked milestones** from Linear: milestone states + dependency relations +
   resolved gates. Run every unblocked milestone concurrently — one junior each. The
   charter's budget ceiling is the brake, not an artificial junior cap.
2. **Spawn juniors.** For each unblocked milestone without a live junior, render a brief by
   invoking the `research-junior` skill with that milestone's inputs, then:

   ```
   Agent(
     subagent_type="general-purpose",
     model="opus",
     team_name=<project_team>,
     name="junior-m<k>",
     run_in_background=true,
     prompt=<rendered junior brief>,
   )
   ```

   Log every spawn.
3. **Watch SendMessage and triage junior questions.** Answer low-level research decisions
   within the charter yourself — that is your job, not the user's. Escalate to the user
   **iff** the question touches budget, research direction, or preference.
4. **On a gate report**, decide:
   - The measured result lands **cleanly in a pre-declared branch** (written into the
     milestone's gate at /project time) → take that branch autonomously; notify the user
     without blocking.
   - The result is **ambiguous / between branches**, the branch is an **off-ramp**, or
     taking it **changes budget or direction** → escalate per the matrix and wait.
   Log the decision either way.
5. **Re-plan the wave.** Re-invoke `Skill("linear-planning:project", ...)` in refine mode
   on the existing project to author the next ticket wave on the chosen branch. Its
   refine-mode approval gate covers any change to existing milestones.
6. **Retire the junior.** The finishing junior runs `pod-teardown` for its own pod team;
   confirm, log the retirement, then shut the junior down. Loop.

## Phase 3 — Wind-down

When the publication milestone completes or an off-ramp is published: send the user a final
summary (headline result or off-ramp taken, milestones run, budget spent vs ceiling), have
any remaining juniors run `pod-teardown`, delete the project team, and append a closing log
line.

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

Research spans days or weeks — longer than any session. State lives in two places only:

- **Linear is ground truth**: milestone states, gate outcomes (junior comments on
  milestones), the charter document, ticket states.
- **The log** is the decision trail: `~/.claude/research/<project-slug>/log.ndjson`, one
  JSON object per line: `{"ts":"2026-06-12T18:05Z","role":"principal","milestone":"M3",
  "msg":"..."}`. `role` ∈ `principal | junior | escalation`. `milestone` optional. `msg`
  ≤120 chars. Append with `printf '%s\n' '<json>' >> <log>` — atomic, no locking.

**What you log**: kickoff facts, every junior spawn/retire, every gate decision and which
rule made it autonomous or escalated, every escalation and the user's answer, every
re-plan. Juniors log their own claim / run-launch / gate-report lines. After appending,
stop restating the fact in prose — chat points to the log.

**Recovery** (run at Phase 0 in recovery mode, and whenever you suspect compaction):

1. `tail -100 ~/.claude/research/<project-slug>/log.ndjson`
2. Reconcile against Linear: project, milestone states, latest gate comments.
3. Linear wins on disagreement. Append a reconciliation line, then resume the cycle step
   the state implies (spawn missing juniors, decide a reported-but-undecided gate, or
   re-ask an unanswered escalation).

## Hard rules

- **Juniors never talk to the user.** Everything routes through you; you apply the matrix.
- **Don't absorb junior work.** If a junior stalls, ping once; no response in 10 minutes →
  replace it via a fresh `research-junior` brief (state is recoverable from log + Linear).
- **Don't re-implement planning or pod coordination.** `/project` owns the arc and all
  arc-level Linear writes; `pod-milestone` owns the pod. You compose them.
- **Never decide off-ramps or budget overruns silently.** Block & ask, always.
- **One junior per milestone, one milestone per junior.** No junior owns two milestones;
  replace, don't reassign.

## Failure handling

- **Junior dies or stalls mid-milestone** → ping once, then replace via a fresh brief; the
  replacement recovers from the log + Linear.
- **Experiment infra unreachable** → junior escalates to you; retry/reschedule yourself;
  escalate to the user only if it blocks a gate.
- **`/project` re-entry would rename/move/remove existing milestones** → its refine-mode
  approval gate handles it; never bypass that gate.
- **Pod-level failures** (CI red, cascade conflicts, Linear 401) → owned by
  `pod-milestone`'s failure handling inside the junior's pod; the junior escalates only
  what the pod can't resolve.

## How to invoke

`/research <idea + hypothesis + why>` for a new project, or `/research <Linear project
name or URL>` to resume one. Kickoff surfaces `/project`'s own clarifications plus the
single charter round; after that, expect contact only at escalations and notifications.
````

- [ ] **Step 2: Verify frontmatter and structure**

Run:
```bash
head -7 research-pod/skills/research/SKILL.md
grep -c '^## ' research-pod/skills/research/SKILL.md
```
Expected: frontmatter shows `name: research`, an `argument-hint`, and `disable-model-invocation: true` between `---` fences; the section count is 10 (`Prerequisites`, `Phase 0`, `Phase 1`, `Phase 2`, `Phase 3`, `Escalation matrix`, `State & recovery`, `Hard rules`, `Failure handling`, `How to invoke`).

- [ ] **Step 3: Commit**

```bash
git add research-pod/skills/research/SKILL.md
git commit -m "feat(research-pod): add research skill — principal orchestrator"
```

---

### Task 3: The `research-junior` skill (junior brief generator)

**Files:**
- Create: `research-pod/skills/research-junior/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `research-pod/skills/research-junior/SKILL.md` with exactly this content:

````markdown
---
name: research-junior
description: Generate a self-contained brief for an Opus junior-researcher agent that owns one research milestone end-to-end — coordinates its own pod-milestone build, supervises outputs for scientific validity, launches and monitors experiment runs per the project charter, analyzes results against the milestone gate, and reports to the research principal. Use when the research principal spawns a junior per unblocked milestone.
---

# Research Junior Brief

## What this skill produces

A complete prompt block to pass to:

```
Agent(
  subagent_type: "general-purpose",
  model: "opus",
  team_name: "<project_team>",
  name: "<agent_name>",
  run_in_background: true,
  prompt: <brief>,
)
```

The brief encodes the junior half of the principal/junior research design: own one
milestone end-to-end, coordinate its `pod-milestone` pod, run the experiments, judge the
gate, report up. The brief explicitly bans talking to the user and exceeding the budget cap.

## When to use

- The `research` principal spawns a junior for a newly unblocked milestone.
- Replacing a junior mid-milestone (stalled, died, lost state) — the replacement recovers
  from the log + Linear.

## When NOT to use

- Outside a `research`-orchestrated project — without a principal there is nobody to
  escalate to, and the brief depends on the charter document and project log existing.
- For ticket-level engineering work — that is `pod-engineer`'s brief, one level down.

## Inputs the caller collects before generating the brief

- `team_name` — the project team (NOT a pod team; the junior creates its own pod team).
- `agent_name` — e.g. `junior-m3`.
- `milestone_id` — the Linear milestone this junior owns.
- `project_url` — the Linear project.
- `charter_doc` — URL of the charter document on the project (runbook, budget caps,
  escalation preferences).
- `gate` — the milestone's gate criterion + pre-declared branches, verbatim from the
  milestone body; or `none` for gateless milestones (setup, writeup).
- `principal_name` — SendMessage target for questions and reports. Default: the team
  coordinator.
- `base_branch` — repo base branch for the pod. Default: `develop`.
- `repo_root` — absolute path to the repo checkout.
- `log_path` — `~/.claude/research/<project-slug>/log.ndjson`.
- `linear_interface` — `cli` (default) or `mcp` (see `pod-linear` for the mapping).

## The brief template

Render with the inputs above; pass the result as the agent prompt verbatim.

```
You are {agent_name}, a junior researcher on team {team_name}. You own ONE milestone:
{milestone_id} of {project_url}. You report to {principal_name} via SendMessage. You never
talk to the user — every escalation goes to {principal_name}, and anything outside your
lane (material change to experiment design, budget, an ambiguous gate) IS an escalation.
Never decide those silently.

Append one log line to {log_path} at each lifecycle step (claim, build done, each run
launch, gate report), format {"ts":"...","role":"junior","milestone":"{milestone_id}",
"msg":"<=120 chars"}: printf '%s\n' '<json>' >> {log_path}

## 1 · Orient
- Read the milestone {milestone_id} and its tickets in Linear ({linear_interface}).
- Read the charter document: {charter_doc}. It defines how to launch experiment runs,
  where metrics land, what a healthy vs dead run looks like, and your budget cap. The
  charter is binding.
- Read prior log lines for this milestone in {log_path} — if a previous junior worked it,
  resume from their last logged step; do not redo finished work.
- Your gate: {gate}

## 2 · Build
- cd {repo_root}. Invoke Skill("pod-milestone", args="tickets=<this milestone's ticket
  selector> base_branch={base_branch}") — YOU are that pod's coordinator; follow that
  skill's procedure end-to-end, including its Phase 5 teardown via pod-teardown.
- Exception: a 1-ticket milestone is pod-milestone's own "when NOT to use" — dispatch a
  single general-purpose Sonnet agent for the ticket instead.
- Before calling the build done, review the merged work against RESEARCH intent: right
  metric, right baselines, no data leakage, seeds/dtype handling per the repo's standards.
  Code style and correctness review is the pod's job, not yours — you check the science.

## 3 · Experiment
- Launch runs exactly per the charter's runbook. Log each launch.
- Monitor on wakeups suited to the run duration; kill clearly-dead runs (per the charter's
  health definition) rather than letting them burn budget.
- NEVER exceed your milestone budget cap. A projected overrun is an immediate SendMessage
  question to {principal_name}, mid-run — do not wait for the run to finish.

## 4 · Analyze & report
- Compare measured results against the gate criterion. Write a gate report as a Linear
  comment on milestone {milestone_id}: measured values vs criterion, recommended branch,
  anomalies/caveats. Linear is ground truth — the comment exists even if your session dies.
- SendMessage the gate report to {principal_name}: measured values, recommendation, link
  to the Linear comment. If your gate is `none`, report completion instead.
- You RECOMMEND a branch; {principal_name} decides. Do not start work on the next wave.

## 5 · Idle
- Stay wakeable for follow-ups from {principal_name} until retired. Do not emit "exiting"
  prose; do not pick up other milestones.
```

## Hard rules baked into the brief

- **Never talks to the user** — principal-only escalation, no silent decisions outside its
  lane.
- **Budget cap is hard** — projected overruns escalate mid-run.
- **Recommends, never decides, the gate branch.**
- **One milestone, then idle** — no scope creep into other milestones.
- **Science review ≠ code review** — the junior checks metric/baseline/leakage; the pod's
  own review machinery owns code quality.
````

- [ ] **Step 2: Verify frontmatter and template placeholders**

Run:
```bash
head -4 research-pod/skills/research-junior/SKILL.md
grep -o '{[a-z_]*}' research-pod/skills/research-junior/SKILL.md | sort -u
```
Expected: frontmatter has `name: research-junior` and a `description`, and **no**
`disable-model-invocation` line (the principal invokes this skill). The placeholder list is
exactly: `{agent_name}`, `{base_branch}`, `{charter_doc}`, `{gate}`, `{linear_interface}`,
`{log_path}`, `{milestone_id}`, `{principal_name}`, `{project_url}`, `{repo_root}`,
`{team_name}` — each one also appears in the Inputs section.

- [ ] **Step 3: Commit**

```bash
git add research-pod/skills/research-junior/SKILL.md
git commit -m "feat(research-pod): add research-junior skill — junior brief generator"
```

---

### Task 4: Cross-reference consistency check

**Files:**
- Modify (only if a check fails): `research-pod/skills/research/SKILL.md`, `research-pod/skills/research-junior/SKILL.md`, `research-pod/.claude-plugin/plugin.json`

- [ ] **Step 1: Check skill names match directories and cross-references resolve**

Run:
```bash
grep '^name:' research-pod/skills/research/SKILL.md research-pod/skills/research-junior/SKILL.md
grep -n 'research-junior' research-pod/skills/research/SKILL.md
grep -n 'linear-planning:project\|pod-milestone\|pod-teardown' research-pod/skills/research/SKILL.md | head
grep -n 'pod-milestone\|pod-engineer\|pod-linear' research-pod/skills/research-junior/SKILL.md | head
```
Expected: `name:` equals the directory name in both files; the `research` skill references
`research-junior` (spawn step) and the external skills it composes; the junior brief
references `pod-milestone`. Fix any mismatch by editing the offending file — the skill
`name:` field and directory name are the contract.

- [ ] **Step 2: Check the two skills agree on shared facts**

Verify by reading (no command): log path format `~/.claude/research/<project-slug>/log.ndjson`,
log line fields (`ts`/`role`/`milestone`/`msg`, junior role value `junior`), junior agent
naming `junior-m<k>`, junior model `opus`, and the rule "junior recommends / principal
decides" appear consistently in both SKILL.md files. Fix inline if they drift.

- [ ] **Step 3: Commit (only if fixes were made)**

```bash
git add -A research-pod && git commit -m "fix(research-pod): align cross-references between skills"
```
If no fixes were needed, skip the commit.

---

### Task 5: Manual dry-run (interactive — requires the user)

**Files:** none (verification only)

This is the spec's verification section; it cannot run unattended because kickoff and the
charter round are interactive and it needs a sandbox Linear team.

- [ ] **Step 1: Install the plugin locally and confirm both skills load**

Add the marketplace and install (or restart the session if already added):
```bash
claude plugin marketplace add /Users/felipedrummond/Documents/personal_projects/felipedrummond-plugins 2>/dev/null || true
claude plugin install research-pod@felipedrummond-plugins
```
Expected: in a fresh session, `/research` appears as an invocable skill and
`research-junior` is listed as model-invocable.

- [ ] **Step 2: Dry-run kickoff on a toy idea against a sandbox Linear team**

With the user present: `/research <toy idea with one trivially checkable gate>` on a
sandbox Linear team. Confirm in order: `/project` runs and writes the toy arc; the charter
round happens once and the document lands on the Linear project; one junior spawns for the
first milestone; the junior's gate report lands as a Linear comment + SendMessage; the
principal takes the pre-declared branch autonomously and notifies; `/project` re-entry
authors the next wave.

- [ ] **Step 3: Dry-run recovery**

Kill the session mid-cycle, re-invoke `/research <toy project name>`, and confirm the
principal reconstructs state from `log.ndjson` + Linear and resumes at the right step
without re-running kickoff.

- [ ] **Step 4: Record findings**

Any gap found in the dry-run becomes an edit to the relevant SKILL.md, committed as
`fix(research-pod): <finding>`.
