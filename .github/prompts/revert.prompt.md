---
name: conductor-revert
description: Git-aware assistant for reverting tracks, phases, or tasks.
---

Safely revert a unit of work within the Conductor framework:
1. Identify the target track, phase, or task to revert.
2. Find associated implementation commit SHAs and plan update commit SHAs from `git log`.
3. Confirm revert strategy with the user: Safe Revert (`git revert`) or Hard Reset (`git reset --hard`).
4. Execute the revert, update `plan.md` to reset tasks to pending `[ ]`, and commit the state reset.
