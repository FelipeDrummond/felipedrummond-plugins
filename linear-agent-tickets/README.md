# linear-agent-tickets

Claude Code plugin for authoring agent-ready Linear tickets through a structured pipeline with multi-agent council critique.

## What it does

`/linear-agent-tickets:ticket [rough description]` (or just `/ticket` when the name is unambiguous) runs:

1. **Intake** — restate intent, confirm
2. **Context** — pull project, milestone, siblings from Linear
3. **Q/A** — confidence-gated, ephemeral, max 2 rounds
4. **Draft** — schema-validated, with hard linter checks
5. **Council** — 4 specialists in parallel (project, decomposition, test-strategy, critic)
6. **Aggregate** — deterministic merge by ticket region: corroborated regions first, then blockers, then suggestions
7. **Human review** — resolve blockers, set priority + due date
8. **Revise** — re-invoke council max once
9. **Submit** — create ticket(s) in Linear

## Design invariants

- 1 ticket = 1 PR (or 1 subissue = 1 PR when parent has subissues)
- Subissues are flat, no nesting
- Project description in Linear is the architectural source of truth
- Priority and due date are required, **human-set only**
- Q/A is ephemeral; never persisted to ticket descriptions
- Council specialists run independently in parallel
- Aggregation is deterministic, human is tie-breaker

## Requirements

- Claude Code
- Linear MCP (auto-configured via `.mcp.json`)
- A populated Linear project description (acts as the source-of-truth doc)

## Install

```bash
claude plugin install ./linear-agent-tickets --scope user
```

## Usage

```
/ticket Add Redis cache to the user-lookup endpoint to reduce p99 latency
```

The orchestrator will ask follow-ups if needed, run the council, present a report, and submit on your approval.

## Files

- `skills/ticket/SKILL.md` — orchestrator
- `agents/ticket-project-specialist.md` — architectural fit
- `agents/ticket-decomposition-specialist.md` — shape and size
- `agents/ticket-test-strategy-specialist.md` — testability
- `agents/ticket-critic.md` — adversarial review (Opus)

## Cost notes

Critic is on Opus, others on Sonnet. A full pipeline run with 1 council pass is ~5 LLM turns:
intake → draft → 4 parallel specialists → aggregation. Expect ~30–90 seconds wall-clock.

## Known limits

- No post-execution feedback loop yet (you can't tell the plugin which tickets succeeded)
- Council re-invocation capped at 1 per ticket
- Q/A capped at 2 rounds; remaining unknowns go to `ASK_FIRST`
