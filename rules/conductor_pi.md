---
trigger: model_decision
description: Interaction standards and view-layer adapter for Conductor skills when operating inside Pi, Oh-My-Pi, or compatible harnesses.
---

# Conductor Pi / Oh-My-Pi UX Adapter (View Layer)

These operational rules govern the user interface, dialog rendering, and execution workflows when Conductor skills are active in Pi / Oh-My-Pi environments.

## 1. Native Interactive Dialogs (`ask`)

- **Interactive Tool Check:** Whenever a Conductor skill needs to gather user choices, single-select decisions, multiple-choice options, or conduct interactive scaffolding loops, the agent MUST check if the native `ask` tool is available.
- **Strict `ask` Schema Usage:** When `ask` is present, the agent MUST format structured questions using Pi's `ask` tool parameters:
  ```json
  {
    "questions": [
      {
        "id": "decision_id",
        "question": "What would you like to configure?",
        "options": [
          {
            "label": "Interactive Mode",
            "description": "Guided question-and-answer interview"
          },
          {
            "label": "Autogenerate Mode",
            "description": "Infer best practices automatically from codebase"
          }
        ],
        "recommended": 0,
        "multi": false
      }
    ]
  }
  ```
- **Text Fallback:** If `ask` is NOT available (e.g. non-interactive batch or text-only streaming sessions), the agent MUST fall back to structured text menus using numbered choices (`[1] Option A`, `[2] Option B`) and ask strictly one question at a time.

## 2. Natural Language Triggers

When Conductor is installed in the project, the agent SHOULD automatically route natural language requests to the appropriate Conductor skill:

| Intent | Example Request | Conductor Skill |
|---|---|---|
| Initialize project context | "Let's create a new conductor project" / "Run setup for Conductor" | `conductor-setup` |
| Plan a feature or bug fix | "Let's start a new track to add X" / "Create a plan for track Y" | `conductor-new-track` |
| Execute implementation | "Start implementing the active plan" / "Proceed with implementation" | `conductor-implement` |
| Check project status | "How is our track progress going?" / "Show current project status" | `conductor-status` |
| Code review & audit | "Review completed work" / "Audit code against track plan" | `conductor-review` |
| Revert track or task | "Revert the last completed task" / "Undo track changes" | `conductor-revert` |

## 3. Skill & File Path Discovery

- **Local Project State:** All Conductor project artifacts reside strictly in relative paths under `conductor/` (`conductor/index.md`, `conductor/tracks.md`, `conductor/tracks/<track_id>/`).
- **Domain Skills:** When discovering installed domain skills, check `.omp/skills/`, `~/.omp/agent/skills/`, and `.agents/skills/`.
