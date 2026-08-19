---
name: conductor-review
description: Conducts code review against track spec, plan, and style guides.
---

Review the completed Conductor track work:
1. Identify the target track from `conductor/tracks.md`.
2. Inspect `git diff` against the track revision range.
3. Check intent against `spec.md` and `plan.md`, verify style compliance against `code_styleguides/`, and ensure test coverage.
4. Output structured findings (Critical / High / Medium / Low).
5. Apply approved fixes and commit with `fix(conductor): apply review suggestions`.
