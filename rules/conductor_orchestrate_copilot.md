---
trigger: model_decision
description: Subagent dispatch adapter for the conductor-orchestrate skill when operating inside GitHub Copilot CLI. Maps planning, implement, and review subagent roles to custom agents defined in .github/agents/.
---

# Conductor Orchestrate Dispatch Adapter: GitHub Copilot CLI

These rules govern how the `conductor-orchestrate` skill spawns subagents inside GitHub Copilot CLI. The subagent role prompts live in `skills/conductor-orchestrate/subagents/`; the Copilot custom agent wrappers live in `.github/agents/`.

## 1. Custom Agent Inventory

| Orchestrate Role | Copilot Agent File | Dispatch Name |
|---|---|---|
| Planning subagent | `.github/agents/orchestra-planning.agent.md` | `orchestra-planning` |
| Implement subagent | `.github/agents/orchestra-implement.agent.md` | `orchestra-implement` |
| Code review subagent | `.github/agents/orchestra-code-review.agent.md` | `orchestra-code-review` |
| Verify runner subagent | (uses `orchestra-implement` agent file with the verify-runner role prompt) | `orchestra-implement` + verify-runner prompt |

Each agent file loads its shared role prompt from `skills/conductor-orchestrate/subagents/<role>.md` so the content has a single source of truth.

## 2. Dispatch Primitive

Use the `task` tool with `subagent_type` set to the dispatch name:

| Role | Dispatch call |
|---|---|
| Planning | `task` with `subagent_type: "orchestra-planning"`, prompt = user request + track spec, instruction to return findings only |
| Implement | `task` with `subagent_type: "orchestra-implement"`, prompt = phase objective, files, tests, steps; no completion files or commit messages |
| Review | `task` with `subagent_type: "orchestra-code-review"`, prompt = phase objective, acceptance criteria, modified files; review only, no fixes |
| Verify run | `task` with `subagent_type: "orchestra-implement"`, prompt = verify-runner role prompt + parent-named harness command; never `--holdout`; evidence only |

## 3. Programmatic Alternative

To run a role directly from the shell:

```bash
copilot --agent orchestra-planning --prompt "<research request>"
copilot --agent orchestra-implement --prompt "<phase brief>"
copilot --agent orchestra-code-review --prompt "<review brief>"
```

The agent name is the file name without the `.agent.md` extension.

## 4. Notes

- Copilot custom agents get their own context window; large research or implementation passes stay out of the parent context.
- The review agent reviews uncommitted changes (`git diff`); instruct the user to leave the phase's changes uncommitted until the review completes.
- Verification of subagent claims remains the parent's job per the orchestrate protocol.
