# Implementation Plan: conductor-verify track

## Goal

Build the `conductor-verify` track specified in `specs/SPEC-verify-lifecycle.md`, `specs/SPEC-verify-harness.md`, `specs/SPEC-verify-evals.md`, and `specs/CAPABILITY-MAP-conductor-verify.md`: verification environments built as a track BEFORE implementation, with mandatory user participation, advisory-first gates, and evals proving the machinery enforces its own rules.

## Success Criteria

- A scratch track can walk `VERIFY_DRAFT` → `USER_TRIAL` → `REFINING` → `VERIFY_APPROVED`, with implement refusing (or demanding logged override) before approval and proceeding after.
- A seeded-but-untouched harness cannot satisfy any gate; agent-only edits never confirm the seed (authorship ledger).
- Every approved harness has a hash-bound `RED-DEMO` record; harness revision orphans it and demotes the track.
- New eval cases discriminate 3/3-vs-0/3; full gates green (`run_evals.py`, `edd.py run`, regression, `doctor`).
- No existing skill behavior changes beyond the spec-enumerated edits.

## Context And Current Facts

- Specs reconciled against 27 omp + 22 solo adversarial findings; combined fix pass applied this session. Key mechanisms: `verify/edits.log` authorship ledger, modal transcription of full `verdict X` form, hash-bound `RED-DEMO` in `approvals.log`, proportional re-demo on demotion, REGRESSED exits, uppercase `OVERRIDE` only, separate scoped revision cap.
- Repo conventions (verified by read): skills are `skills/<name>/SKILL.md` + `commands/<name>.md` one-line wrapper + `plugin.json` `skills`/`commands` path arrays; eval cases are `evals/cases/*.json` with `rule` graders matching substrings on `mock_output`; e2e cases live in `evals/cases_e2e/`; gates are `python3 evals/run_evals.py`, `python3 evals/edd.py run`, `python3 evals/engine/regression.py --baseline evals/baselines/baseline_v1.2.0.json`, `bin/conductor doctor`.
- `run_evals.py` currently hardcodes 7 skills / 7 commands and 3 subagents; adding `conductor-verify` requires updating those counts, then (per evals spec) replacing hardcoding with plugin.json derivation.
- `tasks/plan.md` + `tasks/todo.md` are the completed resume.py record and are left untouched; this plan carries its own task list.
- Pilot-dependent work (case 5 `verify_tier_recommendation`, `profile.py`, gold fixtures) is specified PENDING-PILOT in the evals spec and stays deferred.

## Constraints And Non-goals

- Additive-only; enumerated cross-file edits only (new-track prompt, implement matrix branch, orchestrate §6 pause + §4B step + verify-runner role + 3 dispatch-rule mappings, review REGRESSED rule).
- Gates stay advisory-first in v1 (logged override); no hardening to blocking.
- No new binaries: `--status` and harness operations are skill-protocol, stdlib-only where scripts exist.
- Non-goals: remote-backend execution (contract schema only), blocking gates, gold fixtures before a pilot track exists, touching the resume.py record.

## Key Decisions

- Single new `conductor-verify` skill (map's ranked winner) instead of bloating `conductor-new-track`: lowest regression risk to the modal protocol.
- Authorship ledger (`verify/edits.log`) over session write logs: persists across sessions, closes the cross-session ripening attack, keeps confirmation sticky under mixed-author edits.
- `RED-DEMO` lines co-located in `approvals.log` (not a separate file) so `--report` derives observed-red from the same record the gate reads.
- Eval fixtures before skill-prose finalization for gate-adjacent behavior (cases 1a/1b, 2, 9, 11 pin the implement matrix and override rule), mirroring the repo's eval-first habit.
- Build order follows the map: lifecycle skill → harness contract support → strategy/profiler stub (pilot-gated) → evals, with full gates after each phase.

## Recommended Approach

Implement in vertical slices that each leave a walkable track state, proving each slice against the specs' own eval cases as they land. Skill prose first (gates readable via `--status`), then the verdict/sign-off core, then the cross-skill handoffs, then the eval suite that locks behavior, deferring only pilot-bound items.

## Work Plan

### Phase 1: Foundation (gates readable)

## Task 1: Skill skeleton, command, registration

**Description:** Create `skills/conductor-verify/SKILL.md` (frontmatter + Objective/Scope/Files/Commands shell, protocol sections stubbed), `commands/conductor-verify.md` wrapper, append `plugin.json` entries, update hardcoded 7→8 counts in `run_evals.py` and doctor lists.

**Acceptance criteria:**
- [x] `conductor-verify` appears in skill and command listings
- [x] `run_evals.py` green with updated counts; `doctor` exit 0

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` (8/8 skills+commands, 7/7 suites)
- [x] Build succeeds: `bin/conductor doctor` (38 passed, 0 failures)
- [x] Manual check: `git status` shows only intended files (plus pre-existing untracked dirs)

**Dependencies:** None

**Files likely touched:**
- `skills/conductor-verify/SKILL.md` (new)
- `commands/conductor-verify.md` (new)
- `plugin.json`
- `evals/run_evals.py`

**Estimated scope:** Medium: 3-5 files

## Task 2: `--status` op, metadata init, track bootstrap

**Description:** Specify the `--status` protocol block (`VERIFY_STATUS <state> seed=<bool> red=<bound|orphaned|absent> override=<none|moves>`), `metadata.json` field init (`VERIFY_DRAFT`/`false`) and migration defaults, `verify/` layout creation incl. `seed.json` + `edits.log`, plan.md mirror rule (existing checkboxes only, never gate-read).

**Acceptance criteria:**
- [x] Scratch track in /tmp reports exact `--status` block pre- and post-edit
- [x] Missing `verify/` dir reads as `VERIFY_DRAFT` per spec

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` green (7/7)
- [x] Manual check: /tmp dry-walk printed `VERIFY_STATUS VERIFY_DRAFT seed=true red=absent override=none` after simulated user edit

**Dependencies:** Task 1

**Files likely touched:**
- `skills/conductor-verify/SKILL.md`

**Estimated scope:** Small: 1-2 files

## Checkpoint: Foundation

- [ ] `run_evals.py` green, `doctor` exit 0
- [ ] Scratch track bootstraps and reports status correctly
- [ ] Review with human before proceeding

### Phase 2: Core gate flow

## Task 3: Touchpoints 1-3 protocol (interview, traceability, trial)

**Description:** Write the ideation interview (Recommended-first + Other, modal-first), traceability review with NOT-COVERED convention, trial scope picker + modal bridging (verbatim verdict labels transcribing full form with `author=user`), prerequisites refusal, RED-DEMO grammar with domain-hash binding, user-visible evidence rule.

**Acceptance criteria:**
- [x] Modal click path yields gate-satisfying entry without typed incantation (per transcription rule)
- [x] Trial refuses while traceability unconfirmed unless move-(a) override logged
- [x] RED-DEMO names domain hash; revised harness orphans it

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` green (7/7)
- [x] Manual check: /tmp grammar probe validates RED-DEMO + modal transcription lines against spec grammar

**Dependencies:** Task 2

**Files likely touched:**
- `skills/conductor-verify/SKILL.md`

**Estimated scope:** Small: 1 file

## Task 4: Sign-off grammar, override, counters, demotion, REGRESSED

**Description:** Verdict grammar with legal scopes, objection bodies on following lines, invalid-APPROVED → NEEDS_REVISION transition, uppercase `OVERRIDE` with move-(a)/(b) hooks and FAILED/REGRESSED exclusions, separate full-scope/scoped caps with fresh-direction-only resets, author-blind proportional demotion with changed-checks rule, REGRESSED exits.

**Acceptance criteria:**
- [x] Every transition in the spec's state diagram has a specified trigger, including invalid APPROVED and scoped-cap exhaustion
- [x] Counters reset only on fresh-direction re-entry (matches case 10)

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` green (7/7)
- [x] Manual check: keyword coverage probe hits all 9 transition terms in SKILL.md (10k chars)

**Dependencies:** Task 3

**Files likely touched:**
- `skills/conductor-verify/SKILL.md`

**Estimated scope:** Small: 1 file

## Task 5: Cross-skill handoff edits

**Description:** Apply the enumerated edits: new-track offer prompt before implement Yes/No, implement status-matrix branch (incl. missing-dir rule and REGRESSED exits), orchestrate §6 pause + §4B confirmation step, `subagents/verify-runner.md` + 3 dispatch-rule mappings, review REGRESSED no-pass + overridden-class pass rule.

**Acceptance criteria:**
- [x] Each edit matches the map's enumerated list exactly; nothing else in those files changes
- [x] `verify-runner` runs `--all` only, never `--holdout`, never interprets results

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` (7/7), `python3 evals/edd.py run` all PASS
- [x] Manual check: `git diff --stat` shows hunk-scoped insertions only (install.ps1 modification pre-existing, untouched)

**Dependencies:** Task 4

**Files likely touched:**
- `skills/conductor-new-track/SKILL.md`
- `skills/conductor-implement/SKILL.md`
- `skills/conductor-orchestrate/SKILL.md`
- `skills/conductor-orchestrate/subagents/verify-runner.md` (new)
- `rules/conductor_orchestrate_pi.md`, `_copilot.md`, `_agy.md`
- `skills/conductor-review/SKILL.md`

**Estimated scope:** Large: 5+ files (hunks bounded to enumerated edits; split by file if review needs it)

## Checkpoint: Core flow

- [ ] Scratch track walks DRAFT → APPROVED; seeded-untouched and agent-only tracks cannot pass
- [ ] Demotion, REGRESSED round-trip, and override paths behave per spec
- [ ] Full gates green; review with human before proceeding

### Phase 3: Eval lock-in

## Task 6: Gate-adjacent eval cases

**Description:** Author fixtures 1a/1b (gate pause), 2 (vocabulary/authorship), 4 (self-approval/ACK), 9 (seed+override pair), 10 (revision cap incl. escalation-no-reset), 11 (FAILED refusal + fresh-direction re-entry), 12 (provenance incl. modal exception). Validate clean; prove 3/3-vs-0/3 discrimination via /tmp probes.

**Acceptance criteria:**
- [x] Each case passes good transcript 3/3 and fails mutated variant 0/3
- [x] `validate` reports 0 errors, 0 warnings on new cases

**Verification:**
- [x] Tests pass: `/tmp/probe_verify_cases.py` ALL DISCRIMINATE (8/8); `edd.py run` green
- [x] Manual check: `git status` shows only new case files

**Dependencies:** Task 4 (grammar frozen)

**Files likely touched:**
- `evals/cases/verify_*.json` (7 new files)

**Estimated scope:** Medium: 3-5 files (one per case; land as a group)

## Task 7: Coverage, seam, scope, report cases + e2e runner

**Description:** Author fixtures 3 (traceability counting), 6a/6b (seam), 7 (scope picker narrowing), 8a/8b (prereq refusal, report shape); implement `edd.py run --e2e` + `validate` subcommand and the `verify_e2e_observed_red` case; update `--report` metrics derivation note if code-adjacent.

**Acceptance criteria:**
- [x] Same 3/3-vs-0/3 bar for each new case; e2e executes live commands and grades stdout
- [x] Non-hermetic skips carry stated reasons

**Verification:**
- [x] Tests pass: probe2 ALL DISCRIMINATE (6/6); `edd.py run` 24 PASS 0 FAIL; `--e2e` 3/3 live; `validate` 0 errors 0 warnings
- [x] Manual check: executor output confirmed live (temp fixture harness, not reference comparison)

**Dependencies:** Task 6

**Files likely touched:**
- `evals/cases/verify_*.json` (4 new files)
- `evals/cases_e2e/verify_e2e_observed_red.json` (new)
- `evals/edd.py`

**Estimated scope:** Medium: 3-5 files

## Task 8: Derive expected skills/commands from plugin.json

**Description:** Replace hardcoded skill/command lists in `run_evals.py` and `doctor` with plugin.json derivation so a missing registration fails loudly (evals spec Implementation section).

**Acceptance criteria:**
- [x] Removing a plugin.json entry (probe, not committed) makes gates fail loudly
- [x] Full gates green with the entry present

**Verification:**
- [x] Tests pass: `python3 evals/run_evals.py` (7/7), `bin/conductor doctor` (38/0)
- [x] Manual check: removal probe fails loudly in both (`AssertionError: ... not registered`, doctor `FAIL ... Exists but is not registered`); green after restore. Bidirectional check added after first probe passed silently.

**Dependencies:** Task 1

**Files likely touched:**
- `evals/run_evals.py`
- `bin/conductor` (doctor path)

**Estimated scope:** Small: 1-2 files

## Checkpoint: Eval lock-in

- [ ] All new cases discriminate 3/3-vs-0/3; `edd.py run` (incl. e2e) green
- [ ] Regression PASS against `baseline_v1.2.0.json` (new cases surface as improvements)
- [ ] Review with human before proceeding

### Phase 4: Pilot and close-out (pilot-gated)

## Task 9: Profiler, gold fixtures, first pilot run [PILOT ACTIVE: verify_runner_parity_20260904; awaiting user sign-off verdict]

**Description:** Run only with a real pilot track: implement `skills/conductor-verify/assets/profile.py` (stdlib-only pure function), co-author the 4 gold fixtures at the pilot selection interview, land case 5, execute the full verify flow on the pilot and record deviations.

**Acceptance criteria:**
- [x] Case 5 asserts exact tier match on the profiler (not on mock strings)
- [x] Pilot deviations feed back into specs before close-out

**Verification:**
- [x] Tests pass: case 5 green 3/3 live (`TIER-MATCH: 4/4`); full gates green (run_evals 7/7, edd 100%, --e2e 100%, validate 0/0, regression 0, doctor green)
- [x] Manual check: pilot `approvals.log` shows user verdicts at interview (NOTE), traceability (scoped), sign-off (full-scope); invalid first approval correctly reclassified per spec

**Dependencies:** Tasks 5, 7 (flow + runner complete)

**Files likely touched:**
- `skills/conductor-verify/assets/profile.py` (new)
- `evals/cases/verify_tier_recommendation.json` (new)
- Pilot track under `conductor/tracks/` (real data, not fixtures)

**Estimated scope:** Medium: 3-5 files

## Task 10: Full gates and close-out

**Description:** Run every repo gate, confirm the task list, update the map status line if human-approved.

**Acceptance criteria:**
- [x] `python3 evals/run_evals.py` all-pass
- [x] `python3 evals/edd.py run` (incl. `--e2e`) all-pass
- [x] Regression PASS; `bin/conductor doctor` exit 0

**Verification:**
- [x] Tests pass: run_evals 7/7; edd run 100% (24 cases); --e2e 100% (1 live + 7 stated skips); validate 0/0; regression exit 0; doctor 38/0
- [x] Manual check: `git status` shows only intended files (install.ps1 modification pre-existing, untouched; map status line left for human approval)

**Dependencies:** Task 9 (or Task 8 if pilot deferred — close-out then excludes case 5)

**Files likely touched:** none (verification only)

**Estimated scope:** XS

## Checkpoint: Complete

- [ ] All acceptance criteria met (minus explicitly deferred pilot items, if any)
- [ ] Ready for review

## Next (after spec implementation): full-cycle gate walk on the live pilot track

- [x] DONE: `evals/cases_e2e/verify_e2e_gate_walk.json` runs the real pilot
  harness on a throwaway copy (real track untouched — zero WALK lines,
  still VERIFY_APPROVED): baseline-red → green → mutant-red →
  restore-green → report-bound, 3/3 live. `HARNESS_ROOT` override added to
  the pilot harness; `$REPO` expansion added to the e2e executor.
  validate 0/0; all gates green (edd 100%, --e2e 100%, run_evals 7/7,
  regression 0, doctor 38/0).
- [x] DONE: World Skill seed written to
  `.agents/skills/conductor-world/SKILL.md` (EDD conventions, probe method,
  executor schema, bars, bidirectional derivation, multi-leg pattern).
  Treat as unreviewed until the user reviews it.
- [ ] OPEN (needs your words): commit. Staged for it: specs/, plan file,
  conductor-verify skill + assets, verify-runner role, 17 eval cases,
  edd/run_evals/doctor derivation, handoff hunks, pilot track, parity agent
  files, world skill. Left out: install.ps1 (pre-existing), kimi/log/
  wireless files (yours), agents/ (pre-existing untracked).

## Parallelization Opportunities

- Tasks 6 and 7 fixtures can split across sessions once Task 4 freezes the grammar (shared contract: evals transcript schema).
- Task 8 is independent of Tasks 2-7 (depends only on Task 1).
- Task 5 file-hunks are independent per skill but must land as one reviewed unit (shared protocol surface).
- Never parallelize: Tasks 3→4 (same file, stacked semantics), Task 9 pilot (needs the whole flow live).

## Validation Plan

- After every task: `python3 evals/run_evals.py` green (registration/shape guard).
- After Tasks 5, 7: `python3 evals/edd.py run` green (behavior guard).
- After Task 7: `python3 evals/edd.py run --e2e` green (execution guard).
- Before close-out: `python3 evals/engine/regression.py --baseline evals/baselines/baseline_v1.2.0.json` PASS + `bin/conductor doctor` exit 0.
- Highest-risk validation: Task 5's cross-skill hunks (a wrong §6/§4B edit silently changes the orchestrate loop) — mitigated by the hunk-scoped manual check plus the existing orchestrate cases staying green.
- E2E proof: Task 9's pilot run is the only true end-to-end (user verdicts at four touchpoints); everything before it is fixture-graded.

## Risks / Rollback

| Risk | Impact | Mitigation |
|------|--------|------------|
| `run_evals.py` hardcodes counts that Task 1 must bump | Med | Bump in the same task; Task 8 removes the hardcoding permanently |
| Fixture schema drift between lifecycle prose and evals cases | Med | Task 6 first (gate-adjacent cases pin shared vocabulary); single transcript schema owned by evals spec |
| Task 5 hunk bleeds into orchestrate loop behavior | High | Hunk-scoped diff review + existing orchestrate cases green before/after |
| No pilot track available → Task 9 blocked | Low | Case 5 stays PENDING-PILOT per spec; close-out proceeds without it, explicitly noted |
| Advisory-gate scope creep into blocking | Med | Non-goal stated; any hardening needs a new spec decision, not an implementation improvisation |

Rollback: every phase is additive files plus bounded hunks; revert is per-task (`git revert` / checkout of listed files). No migrations, no shared-state changes, no data to repair.

## Open Questions

- Which real track becomes the pilot (blocks Task 9 only)?
- Does the human approve flipping the map status line at close-out (Task 10)?

## Sources

None — no external claims; all decisions trace to the four spec files and repo conventions inspected during this session.
