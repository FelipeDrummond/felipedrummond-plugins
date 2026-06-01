# felipedrummond-plugins

My personal Claude Code plugin marketplace.

## Install

```bash
/plugin marketplace add FelipeDrummond/felipedrummond-plugins
/plugin install linear-planning@felipedrummond-plugins
```

Then use `/linear-planning:ticket` and `/linear-planning:project` (or just `/ticket` / `/project` when unambiguous).

## Plugins

### `linear-planning`

Lightweight, prose-first Linear skills. Two skills, one altitude apart:

| Skill | Description |
|-------|-------------|
| `ticket` | Turn a rough request into a well-placed, right-sized Linear ticket written for a staff engineer. Based on the upstream `sonuml` skill, extended with two optional agent-execution constraints (off-limits boundary + stop-and-ask fork). |
| `project` | Turn an ML research idea + hypothesis into a developable Linear project: off-ramped success criteria, a gated milestone arc (day 0 → publication), and rolling-wave tickets authored by delegating to the `ticket` skill. |

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
docs/superpowers/specs/                      # design specs
docs/superpowers/plans/                      # implementation plans
```
