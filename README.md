# Conductor

Conductor is an AI agent plugin that provides Spec-Driven Development (SDD). It helps software teams specify, plan, implement, and review code changes systematically.

Conductor works with Pi / Oh-My-Pi, GitHub Copilot CLI, Claude Code, and Gemini CLI.

---

## What Conductor Does

Conductor divides development into five sequential phases:

1. **Setup**: Creates baseline documents for product goals, technology stack choices, and coding rules.
2. **Specify and Plan**: Writes a functional specification (`spec.md`) and a step-by-step task list (`plan.md`) before implementation starts.
3. **Implement**: Executes tasks in order, writes tests first, and records Git commit hashes.
4. **Review**: Audits new code against the specification, plan, and style guides.
5. **Revert**: Rolls back changes safely with Git when a task fails.

All state stays in plain Markdown and JSON files inside the `conductor/` directory in your project root.

---

## Supported Agents

- **Pi / Oh-My-Pi**: Uses the native modal `ask` tool to gather user choices, with text fallback.
- **GitHub Copilot CLI & VS Code**: Includes repository instructions and prompt templates in `.github/`.
- **Claude Code**: Uses standard plugin manifests in `.claude-plugin/`.
- **Gemini CLI / Antigravity**: Uses `gemini-extension.json` and view layer adapters.

---

## Design Decisions & Trade-offs

- **Spec-driven over free-form prompting.** Free-form prompting optimizes for how fast the first line of code appears; Conductor optimizes for the correctness of the final diff. Writing `spec.md` and `plan.md` before implementation costs minutes up front but gives the implementing agent an unambiguous target and gives `conductor-review` an objective baseline to audit against. The trade-off is ceremony: trivial tracks pay a fixed overhead, so every phase is deliberately skippable.
- **Plain Markdown/JSON state instead of a database.** All state lives in `conductor/` as diffable text files, chosen over SQLite or a daemon: it reviews naturally in PRs, is hand-editable when an agent gets stuck, works identically across all four supported agents with zero runtime dependencies. The cost is no locking — Conductor assumes a single operator per track rather than solving concurrent writes.
- **Review and revert as first-class phases.** Implementation isn't done when the code compiles: `conductor-review` audits the change against spec, plan, and style guides, and `conductor-revert` uses Git to roll back failed tasks cleanly. Making failure cheap and visible matters more than making agents look infallible.

---

## Installation

### 1. Pi / Oh-My-Pi

To install globally:

```bash
# Copy to the Pi plugin cache
cp -r conductor-agent-plugin ~/.omp/plugins/cache/plugins/conductor-marketplace___conductor___1.2.0
```

Add this block to `~/.omp/plugins/installed_plugins.json`:

```json
"conductor@conductor-marketplace": [
  {
    "scope": "user",
    "installPath": "~/.omp/plugins/cache/plugins/conductor-marketplace___conductor___1.2.0",
    "version": "1.2.0"
  }
]
```

To install in a single project only:

```bash
mkdir -p .omp/skills
cp -r conductor-agent-plugin/skills/* .omp/skills/
```

### 2. GitHub Copilot CLI

Conductor includes instructions for GitHub Copilot in `.github/copilot-instructions.md`.

To run from your terminal:

```bash
# Run CLI directly
./bin/conductor status
./bin/conductor setup
```

To ask Copilot in terminal:

```bash
gh copilot suggest "Plan a new authentication feature using Conductor"
```

### 3. Claude Code

```bash
claude plugin marketplace add /path/to/conductor-agent-plugin
claude plugin install conductor
```

### 4. Gemini CLI / Antigravity

```bash
agy plugins install https://github.com/T-450/conductor-agent-plugin
```

---

## Commands and Skills

| Skill | Description | Main Output Files |
|---|---|---|
| `conductor-setup` | Audits the project and creates baseline context | `conductor/product.md`<br>`conductor/tech-stack.md`<br>`conductor/workflow.md`<br>`conductor/index.md` |
| `conductor-new-track` | Gathers requirements and writes a task plan | `conductor/tracks/<id>/spec.md`<br>`conductor/tracks/<id>/plan.md`<br>`conductor/tracks.md` |
| `conductor-implement` | Executes planned tasks step by step | Updates `conductor/tracks/<id>/plan.md`<br>Updates `conductor/tracks.md` |
| `conductor-review` | Audits completed code against standards | Review report with pass/fail findings |
| `conductor-status` | Shows project progress and task counts | Status summary in terminal |
| `conductor-revert` | Reverts a track, phase, or task safely | Git revert commits and plan resets |
| `conductor-orchestrate` | Orchestrates planning, implement, and review subagents per phase with TDD and pause points | Updates `conductor/tracks/<id>/plan.md`<br>Updates `conductor/tracks.md` |

---

## Directory Structure

```
conductor-agent-plugin/
├── plugin.json                 # Manifest for Pi and general plugin loaders
├── package.json                # npm package definition and binary entrypoint
├── gemini-extension.json       # Gemini CLI and Antigravity manifest
├── LICENSE                     # Apache 2.0 license
├── README.md                   # Project documentation
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy and reporting
├── .gitignore                  # Git ignore rules
├── .editorconfig               # Editor formatting configuration
├── .claude-plugin/
│   └── plugin.json             # Claude Code manifest
├── .github/
│   ├── copilot-instructions.md # Instructions for GitHub Copilot
│   ├── prompts/                # Copilot prompt templates
│   └── workflows/
│       ├── ci.yml              # CI test workflow
│       └── release.yml         # Release workflow
├── bin/
│   └── conductor               # Node.js CLI entrypoint
├── rules/
│   ├── conductor_pi.md                     # Pi interaction rules
│   ├── conductor_antigravity.md            # Antigravity interaction rules
│   ├── conductor_orchestrate_pi.md         # Pi/Oh-My-Pi subagent dispatch
│   ├── conductor_orchestrate_copilot.md    # Copilot CLI subagent dispatch
│   └── conductor_orchestrate_agy.md        # Antigravity CLI subagent dispatch
├── skills/
│   ├── conductor-setup/        # Project setup skill and style guides
│   ├── conductor-new-track/    # Track planning skill
│   ├── conductor-implement/    # Task execution skill
│   ├── conductor-review/       # Code review skill
│   ├── conductor-status/       # Progress report skill
│   ├── conductor-revert/       # Git revert skill
│   └── conductor-orchestrate/  # Subagent-driven development skill
└── evals/
    └── run_evals.py            # Automated test suite
```

---

## Testing

Run the automated test suite with Python 3:

```bash
python evals/run_evals.py
```

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
