---
name: agent-ship
description: "SDD Phase 5 — Ship the milestone. Update PROGRESS.md, tag release, open PR (if applicable), advance to next milestone."
---

# /agent-ship — Ship Phase

## Prerequisite

`VERIFICATION_REPORT.md` exists with all criteria ✓ (no blockers).

## Process

1. Append entry to `PROGRESS.md`:
   ```md
   ## <milestone> — YYYY-MM-DD
   - Tasks: T-001, T-002, T-003
   - Outcome: <one-line result>
   - Artifacts: <links>
   ```
2. Tag release: `git tag -a v<n>.<m> -m "<milestone>"` (if semver relevant)
3. If repo has remote: `git push && git push --tags`
4. If PR workflow: `gh pr create --title "..." --body-file VERIFICATION_REPORT.md`
5. Archive milestone artifacts: move `SPEC.md`, `TASKS.md`, `VERIFICATION_REPORT.md` → `docs/milestones/<milestone>/`
6. Reset working files for next milestone: fresh `SPEC.md`, `TASKS.md`

## Output

```
✓ Milestone <name> shipped.
  Commit: <sha>
  Tag: v1.0
  PR: <url> (if remote)
  Next: /agent-spec <next-milestone>
```

## Rules

- Never ship with failing criteria
- Never skip PROGRESS.md update
- Never delete milestone artifacts — archive, don't destroy
