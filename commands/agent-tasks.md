---
name: agent-tasks
description: "SDD Phase 2 — Decompose SPEC.md into executable TASKS.md (atomic tasks, <200k token each, ordered by dependency). Prerequisite for /agent-execute."
---

# /agent-tasks — Task Decomposition

## Prerequisite

`SPEC.md` must exist and be committed.

## Process

Read `SPEC.md`. Produce `TASKS.md`:

- Max 3 tasks per batch (SDD rule)
- Each task must be completable in < 200k tokens of context
- Each task has: id, title, inputs, outputs, acceptance criteria, estimated size (S/M/L), dependencies
- Tasks ordered by dependency topology
- Format: `[ ] T-NNN — <title>` (unchecked)

## Output structure

```md
# Tasks — <agent-name>

## Batch 1 (current)
- [ ] T-001 — <title>
  - **Depends on**: none
  - **Produces**: <file/artifact>
  - **Accepts**: <criterion>
  - **Size**: S

## Batch 2
...

## Completed
(empty at start)
```

## Gate

Present batch 1 to user. Confirm before commit.

```
git add TASKS.md && git commit -m "plan(phase-2): decompose into N atomic tasks"
```

Next: `/agent-execute T-001`.
