---
name: agent-execute
description: "SDD Phase 3 — Execute one task from TASKS.md in fresh context (Ralph loop pattern). Writes code, commits atomically, marks task [x]. Argument: task id (e.g., T-001)."
---

# /agent-execute <task-id> — Task Execution

## Arguments

`$ARGUMENTS` = task id (e.g., `T-001`). Required.

## Prerequisite

`TASKS.md` exists and contains `[ ] <task-id>` entry (unchecked).

## Process — Ralph Loop Pattern

1. **Read only what's needed**: `SPEC.md` + the single task entry. Skip unrelated tasks.
2. **Implement** following spec. Write code. Run tests locally.
3. **Verify acceptance criteria** listed in the task. If any fail, abort — do NOT commit. Create `FIX_PLAN.md` describing what's broken.
4. **Commit atomically** — one task = one commit:
   ```
   git add <files> && git commit -m "feat(<task-id>): <title>"
   ```
5. **Mark task complete** — update `TASKS.md`: `[ ]` → `[x]` for this task id. Commit the TASKS.md update in a separate commit: `chore(tasks): mark <task-id> done`.

## Hard rules (SDD non-negotiable)

- Never exceed 200k tokens of context — if you approach limit, stop and report
- Never skip verification
- Never accumulate context across tasks — each `/agent-execute` call is fresh
- SPEC.md is source of truth — if implementation diverges, update spec FIRST via `/agent-spec`

## Output

Print: `✓ T-NNN done — <commit sha>` or `✗ T-NNN blocked — see FIX_PLAN.md`.

Next: `/agent-execute <next-task>` or `/agent-verify` when batch complete.
