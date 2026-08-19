# Conductor GitHub Copilot Instructions

You are operating within a repository managed by the **Conductor Spec-Driven Development (SDD)** framework.
Follow these rules and operational standards whenever assisting with planning, coding, reviewing, or debugging tasks.

---

## 1. Conductor Architecture & State

All project context and task tracking are stored in relative markdown files under the `conductor/` directory:

- `conductor/index.md` — The central project handshake mapping definition, tech stack, workflow, and skills.
- `conductor/product.md` — Core product vision, goals, and target personas.
- `conductor/product-guidelines.md` — Tone, branding, UX principles, and design standards.
- `conductor/tech-stack.md` — Confirmed language, framework, database, and library selections.
- `conductor/workflow.md` — Operational development rules (TDD order, commit conventions, quality gates).
- `conductor/code_styleguides/` — Language-specific coding standards.
- `conductor/tracks.md` — The central Tracks Registry listing all features, bug fixes, and chores.
- `conductor/tracks/<track_id>/spec.md` — Detailed requirements, acceptance criteria, and out-of-scope bounds for a track.
- `conductor/tracks/<track_id>/plan.md` — Hierarchical execution plan with checkbox tasks (`[ ]` pending, `[~]` in progress, `[x]` complete).

---

## 2. Core SDD Commands & Protocols

When the user requests any of the following operations, execute the corresponding Conductor protocol:

### A. `/conductor-setup` or "Initialize Conductor"
1. Check if `conductor/index.md` exists. If not, inspect the repository (Greenfield vs. Brownfield).
2. Help the user establish `product.md`, `product-guidelines.md`, `tech-stack.md`, style guides, and `workflow.md`.
3. Generate `conductor/index.md` and commit: `chore(conductor): Initialize project context and standards`.

### B. `/conductor-new-track` or "Plan a feature/bug fix"
1. Acquire the track description and classify the type (Feature, Bug, Chore, MVP).
2. Interactively draft `conductor/tracks/<track_id>/spec.md`.
3. Generate hierarchical `conductor/tracks/<track_id>/plan.md` using `[ ]` task checkboxes.
4. Create `metadata.json` and `index.md` inside `conductor/tracks/<track_id>/`.
5. Register the track in `conductor/tracks.md` and link in `conductor/index.md`.
6. Commit: `chore(conductor): initialize track '<track_id>'`.

### C. `/conductor-implement` or "Implement active plan"
1. Read `conductor/tracks.md` and locate the active or next pending track.
2. Mark the track status `[~]` in `conductor/tracks.md` and commit.
3. Work through `plan.md` tasks sequentially following `workflow.md` (TDD test-first, minimal implementation, passing tests).
4. Mark each task `[x]` in `plan.md` with commit SHA upon completion.
5. Synchronize any changes to `product.md` or `tech-stack.md`.
6. Mark track complete `[x]` in `conductor/tracks.md` and commit.

### D. `/conductor-review` or "Review completed track"
1. Perform principal code review against `spec.md`, `plan.md`, `tech-stack.md`, and `conductor/code_styleguides/`.
2. Run the test suite and verify coverage (>80%).
3. Present findings grouped by severity (Critical / High / Medium / Low).
4. Propose fixes and record fix commit SHAs in `plan.md`.

### E. `/conductor-status` or "Show project status"
1. Parse `conductor/tracks.md` and track plans.
2. Report total phases, total tasks, completed, in-progress, pending, and completion percentage ($$ \frac{\text{Completed}}{\text{Total}} \times 100\% $$).

### F. `/conductor-revert` or "Revert a task/track"
1. Identify target track or task and find associated git commit SHAs.
2. Confirm strategy: Safe Revert (`git revert`) or Hard Reset (`git reset --hard`).
3. Reset task checkboxes in `plan.md` back to pending `[ ]` and commit status reset.

---

## 3. General Conventions

- Never bypass `plan.md` or write speculative code outside an active track.
- Always use relative paths starting from the project root.
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`).
