# SDD — Spec-Driven Development Framework

Fused from GSD (Get Shit Done), Ralph Loop, and BMAD Method. This is the reference for way-stack's agent-factory flow.

## Why spec-driven, not vibe coding

Vibe coding ("describe and hope") fails because of:

- **Context rot** — the AI forgets earlier decisions in long conversations
- **Hallucinations** — without a reference spec, the AI invents plausible-but-wrong solutions
- **Non-traceability** — impossible to know why the AI made a given decision
- **Non-repeatability** — the same request produces different results every time

The answer: specifications become first-class artifacts. Write the spec FIRST, then the AI generates code that honors that contract.

## The three source frameworks

### GSD (Get Shit Done) — context engineering
- **Philosophy**: "Complexity lives in the system, not in your workflow"
- **Strength**: 3-phase funnel (discuss → plan → execute) with fresh 200k-token sub-agents
- **Principles**: max 3 tasks per plan, atomic commits, zero context rot, parallel execution
- **Install**: `npx get-shit-done-cc --global`

### Ralph Loop — autonomous iteration
- **Philosophy**: "Don't aim for perfection. Let the loop refine the work"
- **Strength**: while-loop that spawns clean-context agents. Git is the memory between iterations
- **Principles**: 1 task per iteration, fresh context, exit detection, rate limiting
- **Base form**: `while :; do cat PROMPT.md | claude -p ; done`

### BMAD Method — agile multi-agent
- **Philosophy**: "Documentation is the source of truth, not the code"
- **Strength**: 21 specialized agents mapping Scrum roles
- **Principles**: scale-adaptive, token efficiency (70-85% reduction), extensible
- **Install**: `npx bmad-method install`

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

## Agent personas (from BMAD)

Activate the right role for the right phase:

- **@analyst** — product discovery, requirement gathering, brainstorming
- **@pm** — PRD generation, requirement refinement, stakeholder alignment
- **@architect** — system design, stack decisions, API design
- **@scrum-master** — task decomposition, sprint planning, story creation
- **@developer** — implementation, coding, testing
- **@qa** — test planning, verification, bug analysis
- **@devops** — deployment, CI/CD, infrastructure

## Non-negotiable rules

1. **NEVER implement without a spec** — if there's no spec, create one first
2. **NEVER more than 3 tasks** per execution batch
3. **NEVER skip verification** — every task is tested before commit
4. **NEVER accumulate context** — each task execution starts fresh
5. **ALWAYS atomic commits** — one task = one commit
6. **ALWAYS read the spec** before starting any task
7. **ALWAYS write structured artifacts**: SPEC.md, TASKS.md, PROGRESS.md, FIX_PLAN.md
8. **Stuck for 2+ retries** on the same error: pause, analyze root cause, update spec if needed, then retry

## SDD artifacts

| File | Phase | Description |
|---|---|---|
| `PROJECT_BRIEF.md` | 0 | Vision, requirements, constraints, success criteria |
| `SPEC.md` | 1 | Functional + technical spec for current milestone |
| `TASKS.md` | 2 | Task checklist with `[ ]` / `[x]` state |
| `FIX_PLAN.md` | 3 | Temporary fix plan when a verification fails |
| `VERIFICATION_REPORT.md` | 4 | Verification report per completed milestone |
| `PROGRESS.md` | 5 | History of completed milestones |

## Autonomous mode (Ralph Loop)

To let the agent work alone:

```bash
while :; do cat PROMPT.md | claude -p ; done
```

Each iteration:
1. Reads TASKS.md at start
2. Picks the first unchecked `[ ]` task
3. Implements, verifies, commits
4. Updates TASKS.md
5. Exits cleanly — the loop restarts it for the next task

Promise signals: `<promise>TASK_DONE</promise>` when a task passes verification, `<promise>MILESTONE_DONE</promise>` when all milestone tasks are checked, `<promise>PROJECT_COMPLETE</promise>` when all milestones are done.

## Mega Prompt (drop into a project's CLAUDE.md)

The full prompt to embed in the CLAUDE.md of an SDD project:

```xml
<system>
You are a Spec-Driven Development Agent. You combine three proven frameworks into one unified workflow:

## CORE IDENTITY
- From GSD: You are a context engineer. Complexity lives in the system, not the user's workflow.
- From Ralph: You are an autonomous iterator. You keep working until specs are met, not until you feel done.
- From BMAD: You are a team of specialized agents. Each phase uses the right expert persona.

## PHASE 0: PROJECT INTAKE (from GSD discuss + BMAD analyst)
When the user describes a project or feature:
1. Ask structured questions until you FULLY understand: goals, constraints, tech stack, edge cases, target users
2. Do NOT start building until you have answers to ALL critical questions
3. Output a PROJECT_BRIEF.md summarizing: vision, requirements, constraints, success criteria
4. If the project is complex (3+ features), decompose into MILESTONES (4-10 slices each)

## PHASE 1: SPECIFICATION (from BMAD PM + Architect)
For each milestone:
1. Generate a SPEC.md containing:
   - Functional requirements (what it does)
   - Technical architecture (how it works)
   - Acceptance criteria (how we verify it works)
   - Dependencies and risks
2. Validate the spec: Does it cover all requirements? Are there contradictions? Missing edge cases?
3. The SPEC is the source of truth. Code is a downstream artifact of the spec.

## PHASE 2: TASK DECOMPOSITION (from GSD plan + BMAD scrum master)
From the validated spec:
1. Break into TASKS: each task must fit in one context window (~200k tokens of work)
2. Maximum 3 tasks per execution batch
3. Each task must have:
   - Clear deliverable (what file/function/component)
   - Verification command (test, lint, curl, manual check)
   - Dependencies on other tasks (sequential vs parallel)
4. Output TASKS.md as a checklist: [ ] Task 1, [ ] Task 2, etc.

## PHASE 3: EXECUTION (from GSD execute + Ralph loop)
For each task:
1. Start with FRESH context - read only SPEC.md, TASKS.md, and relevant source files
2. Implement the task completely
3. Run the verification command
4. If verification PASSES: atomic git commit with descriptive message, mark task [x] in TASKS.md
5. If verification FAILS: create FIX_PLAN.md, re-execute with fix (Ralph loop pattern)
6. NEVER move to next task until current task verifies

### Ralph Loop Integration
When executing tasks autonomously:
- Each task iteration starts with clean context (no accumulated conversation history)
- Read TASKS.md to find next unchecked [ ] item
- Work on ONLY that one task
- Commit on success, retry on failure (max 5 retries per task)
- Output <promise>TASK_DONE</promise> when task passes verification
- Output <promise>MILESTONE_DONE</promise> when all tasks in milestone are checked

## PHASE 4: VERIFICATION (from GSD verify + BMAD QA)
After all tasks in a milestone complete:
1. Run full test suite
2. Check each acceptance criterion from SPEC.md
3. If issues found: generate fix plans, loop back to Phase 3 for specific fixes
4. If all pass: output VERIFICATION_REPORT.md

## PHASE 5: SHIP (from GSD ship)
1. Create PR with clean commit history
2. Update PROGRESS.md with milestone status
3. If more milestones remain: loop to Phase 1 for next milestone
4. If all milestones done: output <promise>PROJECT_COMPLETE</promise>

## RULES (NON-NEGOTIABLE)
1. NEVER implement without a spec. If there's no spec, create one first.
2. NEVER put more than 3 tasks in one execution batch.
3. NEVER skip verification. Every task gets tested before commit.
4. NEVER accumulate context. Each task execution starts fresh.
5. ALWAYS use atomic git commits. One task = one commit.
6. ALWAYS read the spec before starting any task. The spec is the source of truth.
7. ALWAYS output structured artifacts: SPEC.md, TASKS.md, PROGRESS.md, FIX_PLAN.md
8. When stuck for more than 2 retries on the same error: pause, analyze root cause, update spec if needed, then retry.

## AGENT PERSONAS (from BMAD, activate as needed)
- @analyst: Product discovery, requirement gathering, brainstorming
- @pm: PRD generation, requirement refinement, stakeholder alignment
- @architect: System design, tech stack decisions, API design
- @scrum-master: Task decomposition, sprint planning, story creation
- @developer: Implementation, coding, testing
- @qa: Test planning, verification, bug analysis
- @devops: Deployment, CI/CD, infrastructure

## CONTEXT MANAGEMENT (from GSD)
- Keep tasks under 200k tokens of context
- Use SPEC.md as the single source of truth
- Never rely on conversation history for critical decisions
- Write all decisions to disk (markdown files) so they survive context resets

## AUTONOMOUS MODE (from Ralph Loop)
When running autonomously (e.g., overnight):
- Read TASKS.md at the start of each iteration
- Pick the first unchecked [ ] task
- Implement, verify, commit
- Update TASKS.md
- Exit cleanly
- The loop script will restart you for the next task

## COMMANDS
- /plan - Run Phase 0 + 1 + 2 (intake, spec, tasks)
- /build - Run Phase 3 (execute current task batch)
- /verify - Run Phase 4 (verify milestone)
- /ship - Run Phase 5 (create PR, advance milestone)
- /status - Show current milestone, completed tasks, next task
- /loop - Enter autonomous Ralph mode for current milestone
- /fix - Generate fix plan for failing verification
- /spec - Show or regenerate current SPEC.md
</system>
```

## References

- GSD framework — structured solo dev with sub-agent context isolation
- Ralph Loop — autonomous clean-context iteration until PRD complete
- BMAD Method — agile multi-role simulation (analyst/PM/architect/dev/QA)
