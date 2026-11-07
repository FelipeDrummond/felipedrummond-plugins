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

A one-to-one tutor for M.Sc. coursework, built around one worry: thinking I understand something I don't. It tests before it teaches, gives blunt verdicts and counterexamples, and counts nothing as understood until I pass again days later without notice. One skill, `/tutor` (or `/studium:tutor`), which picks its mode from what I say and what is due.

| Mode | Description |
|------|-------------|
| Setup | First run: collects the review block's day and time, the end goal and exam dates, and proposes a roadmap built backward from the goal, with a value tier and reason for each topic. |
| Session | One 1-hour block on a topic: overdue retests first, a prerequisite quiz, the motivation, then one question per message, with the full mathematics on a notes page beside the chat. |
| Review | The weekly retest block: explain from memory, then new questions on an unseen system aimed at past weak spots. |
| Repair | A separate block on a deep gap found during a session, such as linear systems. |
| Exam | Practice in the style of the course's exams, logged separately so it can't raise a flag by itself. |

Two scripts, standard library only:
- `scripts/tutorlog.py` keeps the evidence log: dated test results with kind, confidence and hints, the understanding level the evidence supports, retest due dates, the weekly block's plan, and a session clock.
- `scripts/flag.py` is the only code that touches the vault. It sets or removes one frontmatter property, `understanding: moderate | good | deep`, and confirms everything else in the note is byte-for-byte unchanged. It also finds a note by title when it has moved.

Everything personal lives in a private home folder, `~/Documents/tutor` (or `$TUTOR_HOME`), never in this repo: the log, roadmap, settings, notes pages, a Python environment for checking the mathematics, and the local server that shows the pages in the app's browser pane. The vault is read, never written, apart from the flag.

## Design notes

- `/project` design + eval live in [`docs/superpowers/specs`](./docs/superpowers/specs) and [`linear-planning/skills/project/eval`](./linear-planning/skills/project/eval).
- `/tutor` replaced `/study` in November 2026. The earlier `/study` spec is kept for its research notes in [`docs/superpowers/specs/2026-10-01-study-skill-design.md`](./docs/superpowers/specs/2026-10-01-study-skill-design.md).

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
