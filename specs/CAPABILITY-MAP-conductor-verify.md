# Capability Map: conductor-verify (approved)

Verification environments built as a track BEFORE implementation, with
mandatory user participation. Status: map approved by human; T4 in v1 scope;
gates advisory-first with logged override.
Implementation: complete per `tasks/plan-conductor-verify.md` (pilot track
`verify_runner_parity_20260904` VERIFY_APPROVED; case 5 TIER-MATCH 4/4).

| Module id | Responsibility | Depends on |
|---|---|---|
| verify-lifecycle | Skill protocol, track states, user gates, seeded-vs-owned rules | — |
| verify-harness | contract.json, harness.sh, baseline, evidence, re-run, T0–T4 backends | verify-lifecycle |
| verify-strategy | Tier catalog, complexity profiler, selection interview, escalation | verify-lifecycle |
| verify-evals | edd.py cases, red-green e2e, approval metrics | verify-lifecycle, verify-harness |

Build order: lifecycle → harness + strategy (parallelizable) → evals.
Specs: `specs/SPEC-verify-<id>.md` (kept in `specs/` to leave root clean).

## Sources (Junie `/demo` docs, read firsthand)

Borrowed mechanics and the doc sections backing them: first-run seeding +
untouched-seed nag + fill-in choice (First-run setup); never rewrite existing
files (First-run setup); scope picker before expensive runs (Basic usage);
visible milestone plan as interruptible contract (What happens: Plan);
upfront prereq checks (Prerequisites); per-run artifact folder + clean
teardown (Finish, Stopping, Output artifacts); multi-VM
layout (Multiple VM templates). Deliberately NOT claimed from Junie: any
no-double-launch rule (our design choice in the trial section) and the
untouched-seed nag as a repeating prompt (docs say setup is re-checked and
un-edited seeds don't count; the nag loop is our enforcement of that).
Anything beyond this list is our design, not
Junie's — do not cite Junie for it.

## Cross-module contracts

- Track workspace: `conductor/tracks/<id>/verify/` (contract, harness,
  traceability, approvals log, authorship ledger, seed, mounts, images,
  metrics, holdout, baseline, evidence).
- Verdict vocabulary in two layers: user verdicts `APPROVED | NEEDS_REVISION |
  FAILED` (plus authorship-marked `OVERRIDE`, which is a marker, not a
  verdict); execution payload `{passed, failed, skipped}` mapping to report
  `pass / fail / partial` per SPEC-verify-harness.
- State lives in `conductor/tracks/<id>/metadata.json` (`verify_status` +
  `seed_confirmed` — the file itself is an existing new-track convention,
  only the two fields are new) plus
  `plan.md` checkbox/marker conventions the status skill already parses.
  Implement/orchestrator read gate state via `conductor-verify --status`,
  never by parsing state files.
- Gates are advisory in v1: override allowed only with a USER-authored reason
  string logged to `verify/approvals.log`; override covers timing/order only,
  never seed confirmation or FAILED; hardening to blocking is a later version.
- Registration: `plugin.json` skills+commands arrays, `commands/` file, skill
  frontmatter `version: "1.3.0"` era conventions. Handoffs are enumerated
  structural edits, stated honestly: `conductor-new-track` completion step
  gains the verify-track offer prompt (ordered before the implement Yes/No);
  `conductor-implement` gains a status-matrix refusal branch (missing
  `verify/` reads as `VERIFY_DRAFT`); `conductor-orchestrate` gains a §6
  verify-gate pause, a §4B user-confirmation step for verify tracks, a fourth
  `verify-runner` dispatch role with
  `skills/conductor-orchestrate/subagents/verify-runner.md` plus
  `rules/conductor_orchestrate_{pi,copilot,agy}.md` mapping entries;
  `conductor-review` gains a REGRESSED no-pass rule. Each covered by eval.
