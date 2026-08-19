---
name: conductor-implement
description: Executes tasks defined in the active track plan.
---

Execute the active Conductor track implementation:
1. Parse `conductor/tracks.md` and select the active (`[~]`) or next pending (`[ ]`) track.
2. Mark the track `[~]` in `conductor/tracks.md` and commit.
3. Sequentially execute tasks from `conductor/tracks/<track_id>/plan.md` following `conductor/workflow.md`.
4. Run tests for each task, mark `[x]` in `plan.md`, and record commit SHAs.
5. Synchronize changes back to `product.md` and `tech-stack.md`.
6. Mark the track `[x]` in `tracks.md` and commit.
