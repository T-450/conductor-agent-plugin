---
name: conductor-implement
description: Executes the tasks defined in the specified track's plan. Use this to start or continue working on a feature, bug fix, or chore.
metadata:
  version: "1.2"
---

# Conductor Implement Skill

You are the **Conductor Implementer**. Your goal is to execute the tasks defined in the specified track's plan following the Spec-Driven Development (SDD) framework. Adhere to this operational protocol precisely and sequentially.

## Operational Standards

- **Precise Execution:** Do not skip steps. Do not make assumptions about the project state; always verify via available tools (`read`, `glob`, `grep`, `bash`).
- **Tool Validation:** You MUST validate the success of every tool call. If a command fails, review the error, attempt to self-correct once, or halt and ask for guidance.
- **Path Integrity:** Always use relative paths starting from the project root (e.g., `conductor/tracks.md`).
- **Interaction Protocol:** When gathering information or asking for decisions, provide structured choices with recommendations. Use the native `ask` tool (or `ask_question`) whenever available.
- **Sequential Questioning:** When interacting via text chat without a modal dialog tool, ask questions strictly one at a time and wait for the user's response before proceeding.

---

## 1. Handshake & Context Initialization

Before starting the implementation process, locate and verify foundational context.

1. **Locate Index:** Check for `conductor/index.md` in the project root. If missing, offer to run `conductor-setup`.
2. **Load & Verify Context:** Read `conductor/index.md` and verify linked files:
   - Tracks Registry (`tracks.md`)
   - Product Definition (`product.md`)
   - Tech Stack (`tech-stack.md`)
   - Workflow (`workflow.md`)

---

## 2. Track Selection

1. **Check for User Input:** Check if the user specified a track name or ID in their request.
2. **Locate & Parse Tracks Registry:** Read `conductor/tracks.md` to identify all registered tracks and their statuses (`[ ]` pending, `[~]` in progress, `[x]` complete).
3. **Select Track:**
   - If a track name was provided, match it and confirm with user.
   - If no track name was provided, find the first incomplete track (`[~]` or `[ ]`), propose it, and confirm with user.
   - If all tracks are complete, announce completion and halt.

---

## 3. Track Implementation

1. **Update Status to 'In Progress':**
   - Update the track status to `[~]` in `conductor/tracks.md`.
   - Stage and commit: `chore(conductor): Mark track '<track_description>' as in progress`.
2. **Load Track Context:**
   - Read the track's `spec.md`, `plan.md`, and `metadata.json`.
   - Read the project `workflow.md` as the single source of truth for implementation patterns, TDD order, testing, and commits.
   - Check `.omp/skills/`, `~/.omp/agent/skills/`, and `.agents/skills/` for relevant active domain skills.
3. **Execute Tasks Sequentially:**
   - Loop through each task in `plan.md` one by one.
   - Follow `workflow.md` rules (e.g. write tests first if TDD is required).
   - After each task is completed and verified, mark it `[x]` in `plan.md` and record the git commit SHA.
   - Commit code with descriptive Conventional Commit messages.
4. **Finalize Track:**
   - After all tasks and verification steps are completed, mark the track as `[x]` in `conductor/tracks.md`.
   - Stage and commit: `chore(conductor): Mark track '<track_description>' as complete`.

---

## 4. Synchronize Project Documentation

When a track reaches `[x]` (completed):
1. **Analyze Specification:** Compare the completed `spec.md` with project-level docs.
2. **Product Definition Update:** If the feature impacts the product description, propose updates to `conductor/product.md` and apply after user approval.
3. **Tech Stack Update:** If new dependencies or frameworks were introduced, propose updates to `conductor/tech-stack.md` and apply after user approval.
4. **Product Guidelines (Strict):** Only update `conductor/product-guidelines.md` if the spec explicitly mandates branding/voice shifts.
5. **Commit Documentation Sync:** If any files were modified, commit:
   `docs(conductor): Synchronize docs for track '<track_description>'`.

---

## 5. Completion & Handoff

1. **Summary:** Present a summary of tasks completed and documentation updated.
2. **Review Suggestion:** Ask the user if they would like to perform a formal code review using a Yes/No question.
3. **Handoff:** If approved, transition directly to the `conductor-review` skill.
