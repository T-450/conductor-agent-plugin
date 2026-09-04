---
trigger: model_decision
description: Subagent dispatch adapter for the conductor-orchestrate skill when operating inside Pi, Oh-My-Pi, or compatible harnesses. Maps planning, implement, and review subagent roles to the native task tool agents.
---

# Conductor Orchestrate Dispatch Adapter: Pi / Oh-My-Pi

These rules govern how the `conductor-orchestrate` skill spawns subagents inside Pi / Oh-My-Pi. The skill protocol references these mappings; the subagent role prompts live in `skills/conductor-orchestrate/subagents/`.

## 1. Dispatch Primitive

Use the native `task` tool. One dispatch per subagent role; pass the role prompt file content in the task string.

| Orchestrate Role | `task` tool agent | Rationale |
|---|---|---|
| Planning subagent | `agent: "scout"` | Read-only research specialist; faster model, no edit permissions |
| Implement subagent | default worker (omit `agent`) | Full edit/test capabilities for TDD execution |
| Code review subagent | `agent: "code-reviewer"` | Read-only review specialist |
| Verify runner subagent | default worker (omit `agent`) | Boots env, runs named harness command, reports evidence only |

## 2. Planning Subagent Dispatch

```json
{
  "tasks": [
    {
      "name": "OrchestraPlanning",
      "agent": "scout",
      "task": "<paste skills/conductor-orchestrate/subagents/planning.md content>\n\n# Task\nResearch the following request and return findings only:\n<user request + track spec context>"
    }
  ]
}
```

Collect the returned findings before drafting the plan.

## 3. Implement Subagent Dispatch

```json
{
  "tasks": [
    {
      "name": "OrchestraImplement",
      "task": "<paste skills/conductor-orchestrate/subagents/implement.md content>\n\n# Task\nExecute Phase <N>: <objective>\nFiles: <list>\nTests to write: <list>\nSteps: <ordered steps>\nTrack spec: conductor/tracks/<track_id>/spec.md\nDo not write completion files, review records, or commit messages. Report back with summary, files changed, tests, and test confirmation."
    }
  ]
}
```

## 4. Code Review Subagent Dispatch

```json
{
  "tasks": [
    {
      "name": "OrchestraReview",
      "agent": "code-reviewer",
      "task": "<paste skills/conductor-orchestrate/subagents/code-review.md content>\n\n# Task\nReview Phase <N>: <objective>\nAcceptance criteria: <criteria>\nFiles modified/created: <list>\nReview uncommitted changes via git diff. Return the structured review with Status APPROVED | NEEDS_REVISION | FAILED. Do not implement fixes."
    }
  ]
}
```

## 5. Verify Runner Subagent Dispatch

```json
{
  "tasks": [
    {
      "name": "OrchestraVerify",
      "task": "<paste skills/conductor-orchestrate/subagents/verify-runner.md content>\n\n# Task\nRun: <parent-named harness.sh --all or --check invocation>\nTrack verify dir: conductor/tracks/<track_id>/verify/\nNever run --holdout. Report evidence only; do not interpret results."
    }
  ]
}
```

## 6. Coordination Notes

- Steering: if the parent needs to send follow-up context mid-run, use `hub` send addressed to the spawned agent by its task name.
- Results deliver automatically when the job settles; verify claimed changes before marking plan tasks complete.
- A settled `completed` status means the subagent yielded, not that artifacts are correct. The parent still runs the verification pass defined in the orchestrate protocol.
