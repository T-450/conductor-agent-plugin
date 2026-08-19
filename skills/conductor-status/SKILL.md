---
name: conductor-status
description: Displays the current progress of the project by parsing the Tracks Registry and individual track plans.
metadata:
  version: "1.2"
---

# Conductor Status Skill

You are an AI agent. Your primary function is to provide a status overview of the project by parsing the Tracks Registry and individual track plans.

## Operational Standards

- **Precise Execution:** Do not skip steps. Always verify facts via `read` and `glob`.
- **Path Integrity:** Always use relative paths starting from the project root (e.g., `conductor/tracks.md`).

---

## 1. Handshake & Context Initialization

1. **Locate Index:** Check for `conductor/index.md` in the project root. If missing, inform the user and offer to run `conductor-setup`.
2. **Load Tracks Registry:** Read `conductor/tracks.md` (or the path linked in `conductor/index.md`). If missing or empty, announce that no tracks exist.

---

## 2. Status Overview Protocol

### 2.1 Read Project Plan
1. Parse `conductor/tracks.md` to identify all tracks and their statuses (`[ ]`, `[~]`, `[x]`).
2. For each active or registered track, read its `plan.md` file (`conductor/tracks/<track_id>/plan.md`).

### 2.2 Parse & Summarize Progress
1. Parse major phases and individual tasks marked with checkboxes:
   - `[x]` = completed
   - `[~]` = in-progress
   - `[ ]` = pending
2. Calculate aggregate statistics:
   - Total major phases across tracks.
   - Total tasks across tracks.
   - Tasks completed, in progress, and pending.
   - Percentage completion ($$ \text{Progress} = \frac{\text{Completed}}{\text{Total}} \times 100\% $$).

### 2.3 Present Status Report
Present the status report to the user:
- **Timestamp:** Current date and time.
- **Project Status:** High-level status (e.g., "On Track", "In Progress", "Blocked").
- **Current Active Track & Task:** The track and task currently marked as `[~]`.
- **Next Pending Action:** The next task marked as `[ ]`.
- **Blockers:** Any items explicitly flagged as blockers.
- **Phases:** Total major phases.
- **Tasks Summary:** Total tasks, completed ($N$), in-progress ($N$), pending ($N$).
- **Overall Progress:** Percentage completed.
