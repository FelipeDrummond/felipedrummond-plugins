# felipedrummond-plugins

My personal Claude Code plugin marketplace.

## Install

```bash
/plugin marketplace add FelipeDrummond/felipedrummond-plugins
/plugin install linear-planning@felipedrummond-plugins
```

Then use `/linear-planning:ticket`, `/linear-planning:project`, `/linear-planning:implement`, and `/linear-planning:explain` (or just `/ticket` / `/project` / `/implement` / `/explain` when unambiguous).

## Plugins

### `linear-planning`

Lightweight, prose-first Linear skills. Author → plan → execute:

| Skill | Description |
|-------|-------------|
| `ticket` | Turn a rough request into a well-placed, right-sized Linear ticket written for a staff engineer. Based on the upstream `sonuml` skill, extended with two optional agent-execution constraints (off-limits boundary + stop-and-ask fork). |
| `project` | Turn an ML research idea + hypothesis into a developable Linear project: off-ramped success criteria, a gated milestone arc (day 0 → publication), and rolling-wave tickets authored by delegating to the `ticket` skill. |
| `implement` | Read a ticket the `ticket` skill authored and carry it to a verified PR — thin orchestrator over the superpowers implementation skills (plan, TDD, verify, finish), then write status + a handoff comment back to Linear. Invoke in plan mode. |
| `explain` | Make sense of an agent-written PR: explain what it actually does, situate it in the project's direction, and flag over-documentation, over-engineering, and bad names to cut or rename. An explainer/simplifier, not a bug-hunting reviewer. Run from inside the PR's repo; approved cuts become a follow-up ticket or in-PR fixes. |

Requires a Linear MCP server named `linear-server` in the environment that runs the skills.

### `studium`

```bash
/plugin install studium@felipedrummond-plugins
```

A private tutor for M.Sc. coursework that knows what I know. Before it teaches, it reads the Obsidian vault: my notes in my own words, how each has held up under testing, my past mistakes. One skill, `/study`, with five loops. The notes stay mine to write.

| Loop | Description |
|------|-------------|
| `/study teach` | Explain a concept I don't understand, starting from the notes I already have solid, finding the missing prerequisite, and checking by having me explain it back. |
| `/study intake` | Before a lecture: pretest questions from the slides. After: free-recall dump compared against the slides, the misconception first, missing topics by slide number, and concept stubs to write. |
| `/study examine` | Oral exam on a concept note I wrote: correctness, depth probes aimed at my weak points, prerequisites and links. Never edits the prose. |
| `/study review` | Spaced retrieval of whatever is due, interleaved across courses, graded and written back to the note's frontmatter. |
| `/study drill` | Exercise sheets and old exams: attempt first, a hint ladder, independently verified solutions, and an error log whose patterns it watches for. |

`scripts/vault.py` reads and updates the knowledge state: `profile` (what I know, weakest first, with prerequisites and recent results), `status` (what is due) and `record` (write a result). Scheduling is a Leitner system stored in each concept note's own `confidence` / `last_tested` frontmatter. `meta/Tutor notes.md` in the vault is the tutor's memory of how I learn between sessions.

Explanations are visual where the idea has a shape or moves: computed matplotlib figures, or small interactive pages with sliders built from `assets/explorable.html`. They are computed from the mathematics, never image-generated, checked by the tutor before I see them, and saved outside the vault next to the course PDFs.

## Design notes

- `/project` design + eval live in [`docs/superpowers/specs`](./docs/superpowers/specs) and [`linear-planning/skills/project/eval`](./linear-planning/skills/project/eval).
- `/study` design, with the learning research behind each choice, lives in [`docs/superpowers/specs/2026-10-01-study-skill-design.md`](./docs/superpowers/specs/2026-10-01-study-skill-design.md).

## Layout

```
.claude-plugin/marketplace.json              # marketplace manifest
linear-planning/                             # the plugin
  .claude-plugin/plugin.json
  skills/ticket/SKILL.md
  skills/project/SKILL.md
  skills/project/eval/                       # golden fixture + acceptance rubric
  skills/implement/SKILL.md
  skills/explain/SKILL.md
studium/                                     # the plugin
  .claude-plugin/plugin.json
  skills/study/SKILL.md                      # the tutor: learner model, vault map, loop router
  skills/study/references/                   # one file per loop, plus visuals.md
  skills/study/scripts/vault.py              # knowledge state (profile / status / record) + tests
  skills/study/assets/                       # course hub, lecture note, tutor notes; explorable page template
  skills/study/evals/                        # test prompts + assertions
docs/superpowers/specs/                      # design specs
docs/superpowers/plans/                      # implementation plans
```
