# Implementation Plan: resume.py Content-Aware Completion

## Overview

`determine_resumption()` in `skills/conductor-setup/scripts/resume.py` equates
"artifact exists" with "step complete" (`os.path.exists`, no content check), so
an empty `product.md` marks Product Definition done and misroutes `next_step`.
Fix: an artifact counts as complete only if it exists **and** carries content.
Eval-first: a failing e2e case lands before the fix, and the two e2e references
built on empty (`touch`) fixtures are regenerated after it.

## Architecture Decisions

- Content rule for `.md` artifacts: file exists and holds non-whitespace text
  (read with `errors="replace"`; unreadable file counts as incomplete, never a
  crash). Rationale: matches the skill's intent - a stub file is not a step done
  - and stays stdlib-only per CONTRIBUTING.
- `code_styleguides` (a directory): complete iff it contains at least one file.
  Keeps the `os.path.exists` shape, extends it minimally.
- `setup_complete` gate: decided in Open Questions (index.md content vs exists).
- Output schema unchanged (`setup_complete`, `checklist`, `next_step`); only
  boolean values can flip. `bin/conductor doctor` and `run_evals.py` assert
  shape only, so they are unaffected by construction.

## Task List

### Phase 1: Red (failing eval first)
- [ ] Task 1: add `evals/cases_e2e/resume_e2e_empty_file.json`, prove it FAILS pre-fix
- [ ] Task 2: fix `determine_resumption`, prove the new case PASSES (green)

### Checkpoint: Red-Green
- [ ] New eval red pre-fix, green post-fix; no other file touched yet
- [ ] Review with human before proceeding

### Phase 2: Re-baseline and verify
- [ ] Task 3: regenerate `resume_e2e_partial` / `resume_e2e_complete` references
  with non-empty fixtures; discrimination probe + validator clean
- [ ] Task 4: full gates green (`run_evals.py`, `edd.py run`, regression gate,
  `doctor`); confirm `tasks/todo.md` all checked

### Checkpoint: Complete
- [ ] All acceptance criteria met; ready for review

## Risks and Mitigations

- Existing setups with stub artifacts flip back to incomplete (intended, but
  visible). Mitigation: call it out in the commit message (`fix:`); no data is
  touched, only reported status.
- E2E references built on empty fixtures go stale the moment behavior changes.
  Mitigation: Task 3 regenerates them from live runs; probe asserts equality.
- Weird encodings/permissions could crash the check. Mitigation: Task 2
  acceptance criteria require fail-closed (incomplete, valid JSON, exit 0).

## Decisions (approved by user)

1. `index.md` goes content-aware too: `setup_complete` requires non-whitespace
   content in `index.md`, consistent with all chain artifacts.
2. `code_styleguides/` is complete iff it contains at least one file
   (emptiness of individual style files is not checked).
