# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Test-Driven Development:** Write unit tests before implementing functionality
4. **High Code Coverage:** Aim for >80% code coverage for all modules
5. **User Experience First:** Every decision should prioritize user experience
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools (tests, linters) to ensure single execution.

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order
2. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`
3. **Write Failing Tests (Red Phase):**
   - Create a new test file for the feature or bug fix.
   - Write unit tests that define expected behavior.
   - Confirm tests fail before writing implementation code.
4. **Implement to Pass Tests (Green Phase):**
   - Write the minimum amount of code necessary to make the failing tests pass.
   - Confirm all tests pass.
5. **Refactor (Optional but Recommended):**
   - Clean up code without altering behavior. Ensure tests remain passing.
6. **Verify Coverage:** Run coverage reports. Target: >80% coverage for new code.
7. **Document Deviations:** If implementation differs from tech stack, update `tech-stack.md`.
8. **Commit Code Changes:**
   - Stage code changes. Commit with Conventional Commit message (e.g., `feat(auth): add login validation`).
9. **Record Task Commit SHA:** Update `plan.md` task line to `[x]` with commit SHA.
10. **Commit Plan Update:** Stage `plan.md` and commit: `conductor(plan): Mark task '<task_name>' as complete`.

### Task Correction & Plan Amendment Workflows

1. **In-Flight Refinements:** Adjust active `[~]` task directly and verify tests before committing.
2. **Code Review Corrections (`conductor-review`):** The review agent automatically appends a `Review Fixes` phase to `plan.md` for tracked corrections.
3. **Logical State Reversions (`conductor-revert`):** Safely rolls back associated git commits and resets `plan.md` task state back to pending `[ ]`.

### Phase Completion Verification and Checkpointing Protocol

1. **Phase Scope Determination:** Check git diff against previous phase checkpoint.
2. **Automated Test Run:** Run test suite with non-interactive flags (`CI=true npm test`, `pytest`, `cargo test`, `go test`).
3. **Manual Verification Steps:** Present clear manual verification steps to user.
4. **User Confirmation:** Await user confirmation before closing phase.
5. **Checkpoint Commit:** Update `plan.md` with phase checkpoint SHA and commit: `conductor(plan): Mark phase '<PHASE NAME>' as complete`.

### Quality Gates

- [ ] All tests pass
- [ ] Code coverage meets requirements (>80%)
- [ ] Code follows project style guidelines in `conductor/code_styleguides/`
- [ ] Type safety is enforced
- [ ] No linting errors
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced
