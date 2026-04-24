# SDD — Spec-Driven Development Framework

Fused from GSD (Get Shit Done), Ralph Loop, and BMAD Method. This is the reference for way-stack's agent-factory flow.

## Core principles

1. **Spec is source of truth** — code is derived from spec. If implementation diverges, update spec FIRST.
2. **Atomic commits** — one task = one commit.
3. **Fresh context per task** — never accumulate conversation across tasks. Ralph loop pattern.
4. **Max 200k token context budget per task** — if approaching limit, decompose further.
5. **Verification before ship** — every acceptance criterion tested.
6. **Max 3 tasks per execution batch** — keeps scope tight.

## The 6 phases

### Phase 0 — Project Intake
- Skill: `create-agent`
- Output: `PROJECT_BRIEF.md`
- Goal: capture vision, requirements, constraints, success criteria via ≤5 targeted questions
- Split into milestones if 3+ features

### Phase 1 — Specification
- Command: `/agent-spec`
- Output: `SPEC.md`
- Goal: functional + non-functional requirements, architecture, dependencies, acceptance criteria, risks, out-of-scope
- Gate: user approval before commit

### Phase 2 — Task Decomposition
- Command: `/agent-tasks`
- Output: `TASKS.md`
- Goal: atomic tasks ordered by dependency, each <200k token, batched (max 3 per batch)
- Format: `[ ] T-NNN — <title>` with inputs/outputs/criteria/size

### Phase 3 — Execution (Ralph Loop)
- Command: `/agent-execute T-NNN`
- Goal: implement ONE task in fresh context, commit atomically, mark done
- Rule: fail fast — if acceptance criteria fail, write `FIX_PLAN.md`, do NOT commit

### Phase 4 — Verification
- Command: `/agent-verify`
- Output: `VERIFICATION_REPORT.md`
- Goal: run every acceptance criterion from SPEC.md, tabulate pass/fail with evidence
- Gate: if any ✗ → FIX_PLAN + back to Phase 3

### Phase 5 — Ship
- Command: `/agent-ship`
- Output: `PROGRESS.md` updated, git tag, archive milestone artifacts
- Goal: formalize completion, prep next milestone

## Anti-patterns

| Don't | Do |
|---|---|
| Implement without spec | Run `/agent-spec` first |
| Batch 10 tasks at once | Max 3 per batch |
| Skip verification | Every criterion tested |
| Carry context across tasks | Fresh session per `/agent-execute` |
| Multiple things in one commit | Atomic: one task = one commit |
| Live run before dry-run | `--dry-run` / `--once` first |
| Selenium when OpenCLI covers the site | `opencli list` first |
| Scatter config across files | Single `config.py` / `config.ts` |

## Stack decision matrix (for agent-factory outputs)

| Need | Choice | Why |
|---|---|---|
| Email I/O | `imaplib` or Gmail API | built-in / official |
| WhatsApp | Selenium + WhatsApp Web | persistent session, no official API |
| Reddit / TikTok / YouTube / HN / GitHub / IG / Twitter / Yahoo Finance | OpenCLI | zero-token, structured JSON |
| Custom web (Amazon, Meta Ads, Trustpilot) | Selenium + browser | centralized CSS selectors |
| Text analysis | Claude API (Sonnet simple / Opus complex) | cost-weighted routing |
| Storage | SQLite / Notion API / Drive / local files | pick by access pattern |

## References

- GSD framework — structured solo dev with sub-agent context isolation
- Ralph Loop — autonomous clean-context iteration until PRD complete
- BMAD Method — agile multi-role simulation (analyst/PM/architect/dev/QA)
