# Acceptance rubric — a good `/project` output

A dry-run against `swarm-moments-input.md` passes if the generated plan satisfies all of:

## Success criteria
- [ ] At least one `headline` criterion stated as a falsifiable claim with a threshold + a metric.
- [ ] At least one `off_ramp` criterion (what ships if the headline dies).
- [ ] A `floor` and a `generalization` criterion present (or an explicit, reasoned omission).

## Milestone arc (day 0 → publication)
- [ ] Ordered milestones spanning setup → de-risking pilot(s) → core experiments → generalization → writeup/submit.
- [ ] At least one milestone carries a real gate: a measurable exit criterion + ≥2 branches, at least one non-proceed (pivot/off-ramp).
- [ ] Gates sit on genuine go/no-go points (e.g. the D-arm viability pilot), not on every milestone.
- [ ] Each milestone has a target date inside the stated ~12-week window; dates increase; dependencies form a chain (no cycle).

## Rolling wave
- [ ] Only milestones up to the FIRST unresolved gate have fully-authored tickets.
- [ ] Milestones downstream of an unresolved gate are left as gate + one-line intent (NOT fully authored), because their content is contingent on the gate outcome.

## Style / anti-ceremony
- [ ] Description + milestones read as prose; no YAML schema dump, no `SPECIFIED/AGENT_DECIDES/ASK_FIRST`, no LoC estimates.
- [ ] Priority and due dates are NOT invented (left for the human).

## Pushback
- [ ] If the input's hypothesis or success metric were vague, the run surfaced it (asked or flagged) rather than silently inventing thresholds.
