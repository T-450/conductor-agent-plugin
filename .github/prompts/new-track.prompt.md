---
name: conductor-new-track
description: Creates a new feature or bug fix track with specification and plan.
---

Plan a new track within the Conductor SDD framework:
1. Load `conductor/index.md` and read the project definition and tech stack.
2. Interactively gather requirements and write `conductor/tracks/<track_id>/spec.md`.
3. Generate a hierarchical implementation plan `conductor/tracks/<track_id>/plan.md` using `[ ]` checkboxes.
4. Create `conductor/tracks/<track_id>/metadata.json` and `index.md`.
5. Register the track in `conductor/tracks.md`.
6. Stage and commit: `chore(conductor): initialize track '<track_id>'`.
