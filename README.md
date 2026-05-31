# felipedrummond-plugins

My personal collection of Claude Code skills and plugins.

## Skills

| Skill | Location | Description |
|-------|----------|-------------|
| `ticket` | [`.claude/skills/ticket`](./.claude/skills/ticket) | Turn a rough request into a well-placed, right-sized Linear ticket written for a staff engineer. Based on the upstream `sonuml` skill, extended with two optional agent-execution constraints (off-limits boundary + stop-and-ask fork). |
| `project` | [`.claude/skills/project`](./.claude/skills/project) | Turn an ML research idea + hypothesis into a developable Linear project: off-ramped success criteria, a gated milestone arc (day 0 → publication), and rolling-wave tickets authored via the `ticket` skill. |

## In progress

- `/project` design + eval live in [`docs/superpowers/specs`](./docs/superpowers/specs) and [`.claude/skills/project/eval`](./.claude/skills/project/eval).

## Layout

```
.claude/skills/ticket/SKILL.md     # the ticket skill (bare, mirrors upstream)
.claude-plugin/marketplace.json    # marketplace manifest (no plugins yet)
docs/superpowers/specs/            # design specs
```
