---
trigger: model_decision
description: Subagent dispatch adapter for the conductor-orchestrate skill when operating inside Antigravity CLI (agy). Maps planning, implement, and review subagent roles to custom agents invoked via invoke_subagent.
---

# Conductor Orchestrate Dispatch Adapter: Antigravity CLI (agy)

These rules govern how the `conductor-orchestrate` skill spawns subagents inside Antigravity CLI. The subagent role prompts live in `skills/conductor-orchestrate/subagents/`.

## 1. Custom Agent Discovery

Antigravity CLI discovers custom subagents as markdown files with YAML frontmatter:

- **Workspace:** `.agents/agents/orchestra-<role>.md` (or `.agents/agents/<name>/agent.md`)
- **Global:** `~/.gemini/config/agents/`

A custom agent is invocable by the primary agent only when its frontmatter sets `subagent: true`.

## 2. Agent Inventory

| Orchestrate Role | Agent File | Frontmatter |
|---|---|---|
| Planning subagent | `.agents/agents/orchestra-planning.md` | `subagent: true`, read-only role |
| Implement subagent | `.agents/agents/orchestra-implement.md` | `subagent: true` |
| Code review subagent | `.agents/agents/orchestra-code-review.md` | `subagent: true`, read-only role |

## 3. First-Use Materialization

If the `.agents/agents/orchestra-<role>.md` files do not exist in the workspace, materialize them before the first dispatch:

1. Read the shared role prompt `skills/conductor-orchestrate/subagents/<role>.md`.
2. Write `.agents/agents/orchestra-<role>.md` with YAML frontmatter:

```yaml
---
name: orchestra-<role>
description: <one-line role description>
subagent: true
---
```

3. Paste the shared role prompt content below the frontmatter.

This keeps the agent content in sync with the plugin's single source of truth.

## 4. Dispatch Primitive

Use the `invoke_subagent` tool once per role:

| Role | Invocation |
|---|---|
| Planning | `invoke_subagent` for `orchestra-planning` with the user request + track spec; instruct: return findings only |
| Implement | `invoke_subagent` for `orchestra-implement` with phase objective, files, tests, steps; no completion files or commit messages |
| Review | `invoke_subagent` for `orchestra-code-review` with phase objective, acceptance criteria, modified files; review only, no fixes |

## 5. Monitoring

- Watch spawned subagents in the `/agents` panel (states: running, done, killed, error).
- Use `Alt+J` to teleport into a subagent awaiting approval, or `Ctrl+K` for fast-path confirmations.
- Verify subagent claims per the orchestrate protocol before marking plan tasks complete.
