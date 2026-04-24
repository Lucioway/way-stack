---
name: agent-verify
description: "SDD Phase 4 — Run acceptance-criteria verification for all [x] tasks in current batch. Produce VERIFICATION_REPORT.md. Prerequisite for /agent-ship."
---

# /agent-verify — Verification Phase

## Prerequisite

At least one task in `TASKS.md` is `[x]` completed.

## Process

1. Read `SPEC.md` → extract all acceptance criteria
2. For each completed task, run its acceptance checks:
   - Unit tests pass
   - Integration tests pass (if any)
   - Manual checks documented in spec
3. Generate `VERIFICATION_REPORT.md`:

```md
# Verification Report — <milestone>

Date: YYYY-MM-DD
Tasks verified: T-001, T-002, T-003

## Criteria

| Criterion | Status | Evidence |
|---|---|---|
| <criterion text> | ✓ | test output / log / screenshot path |
| <criterion text> | ✗ | reason for failure |

## Summary

- N/M criteria pass
- Blockers: <list>
- Ready to ship: yes / no
```

## Gate

If any criterion fails → write `FIX_PLAN.md` with actionable remediation. Do NOT proceed to ship.

```
git add VERIFICATION_REPORT.md && git commit -m "verify(phase-4): M criteria (N pass)"
```

Next: `/agent-ship` (if all pass) or `/agent-execute` (fix failures).
