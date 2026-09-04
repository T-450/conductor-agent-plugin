## Task 1: Add failing empty-file e2e eval (RED)

**Description:** Author `evals/cases_e2e/resume_e2e_empty_file.json`: fixture
with empty `product.md` plus non-empty `tech-stack.md`; criteria require
`"setup_complete": false` and `"step": "Product Definition"`. Prove it FAILS
against current `resume.py` via a `/tmp` probe.

**Acceptance criteria:**
✓ New case file validates with 0 errors under `validate_case`
✓ Probe shows the case FAILS pre-fix (red) with the empty file counted complete
✓ `evals/cases/` untouched; default `edd.py run` still 10 cases

**Verification:**
✓ Tests pass: `python3 /tmp/probe_empty_file.py` shows red pre-fix
✓ Build succeeds: `python3 -c "import ast; ast.parse(...)"` on touched files
✓ Manual check: `git status` shows only the new case file

**Dependencies:** None

**Files likely touched:**
- `evals/cases_e2e/resume_e2e_empty_file.json` (new)

**Estimated scope:** Small: 1 file

## Task 2: Make determine_resumption content-aware (GREEN)

**Description:** Replace the `os.path.exists` check with exists-and-has-content
for files (non-whitespace text, `errors="replace"`, unreadable counts as
incomplete) and exists-and-non-empty-dir for `code_styleguides`. Schema and
chain order unchanged. Record the Open Questions decisions from `tasks/plan.md`
before coding.

**Acceptance criteria:**
✓ Empty `product.md` yields `checklist["product.md"] is False` and
  `next_step` Product Definition
✓ Full non-empty fixture still yields `setup_complete true`, `next_step null`
✓ Unreadable file yields incomplete, valid JSON, exit 0 (no crash)
✓ Python 3.10+ stdlib only

**Verification:**
✓ Tests pass: Task 1 probe now shows green; `python evals/run_evals.py` green
✓ Build succeeds: `node bin/conductor doctor` exit 0
✓ Manual check: rerun the three `/tmp/e2e_fixtures` scenarios by hand

**Dependencies:** Task 1 (must stay red until this lands)

**Files likely touched:**
- `skills/conductor-setup/scripts/resume.py`

**Estimated scope:** Small: 1-2 files

## Checkpoint: Red-Green

✓ Task 1 eval red pre-fix, green post-fix (probe output quoted)
✓ No files beyond the case + `resume.py` touched
✓ Review with human before proceeding

## Task 3: Regenerate stale e2e references

**Description:** `resume_e2e_partial` and `resume_e2e_complete` references were
captured from empty (`touch`) fixtures and go stale under the new semantics.
Rebuild them from live runs over non-empty fixtures (extend the case builder),
then prove each case still discriminates good vs mutated output.

**Acceptance criteria:**
✓ Both references equal fresh live `resume.py` output byte-for-byte
✓ Discrimination probe: 3/3 pass on good, 0/3 on mutated, for every e2e case
✓ `validate_suite` on `evals/cases_e2e/` reports 0 errors, 0 warnings

**Verification:**
✓ Tests pass: `python3 /tmp/probe_e2e.py` all green
✓ Build succeeds: n/a (data-only change)
✓ Manual check: `git diff evals/cases_e2e/` shows only reference/output churn

**Dependencies:** Task 2

**Files likely touched:**
- `evals/cases_e2e/resume_e2e_partial.json`
- `evals/cases_e2e/resume_e2e_complete.json`

**Estimated scope:** Small: 2 files

## Task 4: Full gates and close-out

**Description:** Run every repo gate and confirm the behavior change trips none
of them; check off this list.

**Acceptance criteria:**
✓ `python evals/run_evals.py` 7/7
✓ `python evals/edd.py run --trials 3` 10/10 with zero validator noise
✓ `python evals/edd.py regression --baseline evals/baselines/baseline_v1.2.0.json` PASS
✓ `node bin/conductor doctor` exit 0

**Verification:**
✓ Tests pass: all four commands above, outputs quoted in final report
✓ Build succeeds: same as above
✓ Manual check: `git status` shows only intended files

**Dependencies:** Task 3

**Files likely touched:** none (verification only)

**Estimated scope:** XS

## Checkpoint: Complete

✓ All acceptance criteria met
✓ Ready for review
