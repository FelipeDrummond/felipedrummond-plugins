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

## Design notes

- `/project` design + eval live in [`docs/superpowers/specs`](./docs/superpowers/specs) and [`linear-planning/skills/project/eval`](./linear-planning/skills/project/eval).

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
docs/superpowers/specs/                      # design specs
docs/superpowers/plans/                      # implementation plans
```
