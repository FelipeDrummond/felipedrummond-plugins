# Design — `/project`: agent-driven Linear project generator

**Date:** 2026-05-28
**Status:** Approved (design), pending implementation plan
**Plugin:** `linear-agent-planning` (renamed from `linear-agent-tickets`)

## Goal

Turn a large free-form project description (the *what / why / goal* of an ML research
project) into a fully structured Linear project: a source-of-truth description, a sequence
of gated milestones laid across a timeline, and milestone-assigned issue stubs — critiqued
by a parallel multi-agent council and approved by the human before anything is written to
Linear.

This sits one altitude above the existing `/ticket` skill. `/project` produces the
skeleton and lightweight issue stubs; `/ticket` later promotes any stub into a fully
authored, council-reviewed ticket.

## Scope decisions (locked)

- **Depth:** project + milestones + lightweight issue stubs (title + one-line intent).
  Full issue authoring stays with `/ticket`.
- **Domain:** ML / research projects, modeled on the user's existing Swarm-Moments project
  (hypotheses, typed success criteria with off-ramps, compute budget, gated pilot
  milestones, target venues).
- **Linear features in scope:** milestones + target dates; project metadata (priority,
  lead, team, start/target date, summary, description doc); issue↔milestone assignment +
  blocking dependencies; labels.
- **Review:** full parallel council (5 specialists) + deterministic aggregation + human
  review, mirroring the ticket council's coverage-ensemble design.
- **Modes:** create-new **and** refine-existing.
- **Architecture:** new `/project` skill inside the existing plugin (not a separate plugin,
  not an overload of `/ticket`).

## Architecture & components

### Plugin changes
- Rename `linear-agent-tickets` → `linear-agent-planning` (`displayName` "Linear Agent
  Planning"). Update `plugin.json` description/keywords, `.claude-plugin/marketplace.json`,
  and both READMEs. The `/ticket` skill is unchanged.
- Add `skills/project/SKILL.md` — the project orchestrator (command `/project`).
- Add 5 project-council agents under `agents/`.

### Council roster (coverage ensemble — disjoint slices, not a voting panel)
| Agent | Owns (target_region) | Bundle | Tools |
|---|---|---|---|
| `project-milestone-architect` | `milestone_sequence`, `gates`, `dependencies` | milestone plan + dependency graph + start/target dates | reasoning |
| `project-methodology-critic` | `success_criteria` (internal validity) | description (what/approach/success_criteria) + gate criteria | reasoning |
| `project-risk-budget-analyst` | `budget_timeline` | constraints, compute_budget, per-milestone costs, risks, timeline | reasoning |
| `project-related-work-specialist` | `related_work` (external positioning, baseline completeness, citation validity, defensive citations) | description (what/approach/success_criteria) + venues + cited works | WebSearch, WebFetch (time-boxed; degrades to reasoning-only + lowered confidence if web unavailable) |
| `project-critic` | cross-cutting (`scope`, contradictions, ambiguity, over-ambition) | full description + full milestone plan | reasoning |

Each specialist returns the same structured JSON contract the ticket specialists use
(verified against `agents/ticket-critic.md`):
`{ specialist, verdict, confidence, issues[{ severity, category, target_region, description, suggested_fix }] }`.
`category` is a per-specialist enum (each agent defines its own); the aggregator only keys
on `verdict`, `severity`, and `target_region`, so its logic is reused unchanged. Agent
frontmatter mirrors the ticket council (`model: opus`, `effort: high`, `maxTurns: 3`),
except the related-work specialist which also needs web tools.

## Pipeline (9 phases, mirroring `/ticket`)

1. **Intake** — restate the project intent in 1–2 sentences; confirm before spending tokens.
2. **Mode + context resolution** — determine create-new vs refine-existing.
   - *create:* resolve target team (required) + optional initiative.
   - *refine:* resolve the existing project; load its description, milestones, and issues as
     a **no-clobber baseline**.
   - Optionally resolve repo root(s) for a code-area map.
3. **Context gather** — team conventions (recent projects as style templates, label
   taxonomy, milestone naming), an optional local design-doc the user points to, optional
   repo code-map. Held in context, not dumped back.
4. **Q/A** — confidence-gated (high → skip; medium → 1–3; low → 3–5), ephemeral, ≤2 rounds.
   Project-level ambiguities: success thresholds, off-ramp criteria, compute budget,
   deadline, milestone/gate count. User may short-circuit with "good enough, draft it."
5. **Draft** — produce the draft (schema below), then run hard linter checks.
6. **Council** — invoke all 5 specialists in parallel (single message, multiple Task calls),
   each with its role slice.
7. **Aggregation** — deterministic merge by region (algorithm below).
8. **Human review** — resolve blockers + escalated ties; **human sets priority + confirms
   target_date/deadline** (never auto-filled); approve milestone/gate structure; in refine
   mode, explicitly approve any destructive change. Re-invoke council ≤1 time.
9. **Submit to Linear** — write in dependency order (below).

## Draft schema

### (a) Project description (source-of-truth markdown)
```yaml
project:
  name: string
  summary: string                 # one-liner (Linear "summary")
  team: string                    # required
  initiative: string | none       # optional
  description:
    what: string
    approach: string | none        # optional: arms / mechanisms / method
    success_criteria:              # numbered, each typed
      - { claim, threshold, date, type: headline|floor|generalization|off_ramp }
    scope_locked: [string]
    risks: [ { risk, mitigation } ]
    constraints: string
    compute_budget: string | none  # optional, research
    venues: [string] | none        # optional, research
  metadata:
    priority: TBD                  # HUMAN-set only
    lead: string
    start_date: date
    target_date: TBD               # HUMAN-confirmed deadline
    labels_to_create: [string]
```

### (b) Milestone plan (gate is first-class)
```yaml
milestones:
  - id: M0
    title: string                  # rendered "M0 — <title>" (+ " [G1]" if gated)
    deliverables: [string]
    gate:                          # optional
      id: G1
      criteria: string             # MEASURABLE, e.g. "R²(N=16) ≥ 0.3"
      branches:                    # ≥2; at least one non-proceed
        - { condition, action }    # proceed | fix | pivot | off_ramp
    target_date: date
    compute_cost: string | none
    depends_on: [milestone_id]     # DAG edges
    issue_stubs:
      - { title, intent, labels: [string] }   # intent = one line; promote via /ticket
```

### (c) Hard linter checks (re-draft if any fail)
- Milestone `target_date`s strictly increase; last ≤ `project.target_date`.
- `depends_on` forms a DAG (no cycles); every non-M0 milestone has ≥1 predecessor or is
  explicitly marked parallel.
- Every `gate` has measurable `criteria` and ≥2 `branches`, at least one non-`proceed`
  (a failure/off-ramp branch must exist).
- Success criteria include ≥1 `headline` and ≥1 `off_ramp`.
- Every issue stub maps to exactly one milestone.
- `priority` and `target_date` remain `TBD` — never auto-filled.
- **Refine mode:** diff against baseline; any milestone/issue the draft would delete or
  rename is flagged for explicit human confirmation in Phase 8.

## Aggregation (Phase 7, deterministic)

`target_region` enum: `description`, `success_criteria`, `milestone_sequence`, `gates`,
`dependencies`, `budget_timeline`, `related_work`, `scope`, `issue_stubs`.

- `overall_verdict`: any `block` → block; else any `suggest` → suggest; else approve.
- Group issues by `target_region`. **Corroborated** = ≥2 specialists flag the same region
  (lead with these); **Single** = one specialist.
- Conflict resolution by domain owner: `milestone_sequence`/`gates`/`dependencies` →
  architect; `success_criteria` → methodology-critic; `budget_timeline` →
  risk-budget-analyst; `related_work` → related-work-specialist; critic is cross-cutting and
  never overrides an owner on its turf. Mutually-exclusive equal-severity ties with no clear
  owner escalate to the human.
- Output order: Decisions-needed → Corroborated → Blockers → Suggestions.

## Submit to Linear (Phase 9 — strict order so relations resolve)

1. *create:* create project (name, summary, rendered description markdown, team, lead,
   start/target dates, priority).
   *refine:* update the existing project's description **only if the human approved it** in
   Phase 8 — never recreate.
2. Create any `labels_to_create` that don't already exist.
3. Create milestones in topological order, each with target date + description (gate
   rendered into the milestone body as a "Gate Gn: criteria / branches" section).
4. Create issue stubs assigned to their milestone, with labels; each stub body carries a
   `Promote with /ticket` marker.
5. Set milestone/issue dependency relations last (all IDs now exist).

**Refine safety:** never delete; renames/moves only with explicit Phase-8 confirmation.
Return the project URL + milestone summary.

## Escape hatches
- Stop/cancel at any phase → no writes to Linear.
- Linear MCP fails at Phase 9 → dump the rendered plan to `./project-plan-<timestamp>.md`.
- Council re-invocation cap: 1. Q/A round cap: 2.

## Handoff seam
- `/project` emits milestone-assigned issue *stubs*; `/ticket` promotes any stub to a full
  ticket (each stub body carries the promotion marker).
- The ticket skill's existing `escalate_to_milestone_split` verdict documents `/project` as
  the doorway up.

## Validation (skill artifacts → evals, not unit tests)
- **Dry-run:** stop after Phase 8 and render the full plan locally without writing to
  Linear. Fast inner loop.
- **Golden eval:** run create-mode against the Swarm-Moments description into a throwaway
  test team; diff the generated structure (milestone count, gate placement, dates,
  off-ramps, baseline roster) against the real Swarm-Moments project as the reference answer.

## Out of scope (YAGNI)
- Cycles, sub-projects/initiative authoring beyond linking an existing one.
- Domain profiles beyond ML/research (the pipeline is research-specialized by intent).
- Auto-authoring full issue bodies (that is `/ticket`'s job).
- Auto-setting priority or due dates (human-only, by design).
