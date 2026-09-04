---
name: conductor-world
description: Reusable eval-engineering knowledge for the conductor-agent-plugin repo (EDD conventions, fixture design, executor contracts, gates).
---

# Conductor World Knowledge

Project-specific eval facts. Task-specific requests, focal records, expected
results, and scoring stay in the Task, never here.

## Eval paradigm

EDD-native (no Harbor): `evals/cases/*.json` fixtures with `rule` graders
(substring/regex on `mock_output`), live cases in `evals/cases_e2e/` via
`executor_contract`, runner `evals/edd.py`, validator
`evals/engine/validate.py`.

## Fixture design (proven)

- Mock = transcript + gate-decision line (`GATE: ...`, `LOG-CHECK: ...`,
  `EVENT: ...`). Transcript vocabulary (`USER:`/`AGENT:`/`EVENT:`
  /`EDIT[user-owned]:`/`ACK:`) is owned by `specs/SPEC-verify-evals.md`.
- Every static case discriminates 3/3-vs-0/3: shipped mock passes,
  decision-flipped mutant fails. Prove with a `/tmp` probe before landing.
- Per-case mutation pairs live in the probe (flip the decision line), not in
  the repo. Throwaway probes stay under `/tmp`, never committed.

## Executor contracts

- JSON string: `{"shell", "cwd" ("$TMP" | dir), "timeout_s", "skip_reason"?}`.
  `$REPO` expands to the repo root. Free-text contracts skip with a stated
  reason. Hermetic: `$TMP` workdirs, no network.
- Multi-leg pattern (gate walk): chain legs with `|| true` on expected-red
  legs so one leg never aborts the run; grade concatenated stdout on leg
  markers + summaries. Retarget repo paths via env (`HARNESS_ROOT`), never
  mutate the live track.

## Bars and gates

- `edd.py validate`: 0 errors, 0 warnings over `cases/` + `cases_e2e/`.
- Full gates: `run_evals.py`, `edd.py run`, `edd.py run --e2e`, regression
  vs `baseline_v1.2.0.json` (new cases surface as improvements), `doctor`.
- `plugin.json` is the source of truth bidirectionally: unregistered files
  and missing files both fail loudly (`run_evals.py`, `doctor`).
