---
name: agent-spec
description: "SDD Phase 1 — Turn a user's workflow description into SPEC.md (functional + technical requirements, architecture, acceptance criteria). Prerequisite for /agent-tasks."
---

# /agent-spec — Specification Phase

Part of the SDD (Spec-Driven Development) flow: GSD + Ralph Loop + BMAD fused.

## Prerequisite

`PROJECT_BRIEF.md` must exist. If missing, invoke the `create-agent` skill to run Phase 0 (intake) first.

## Process

Read `PROJECT_BRIEF.md`. Generate `SPEC.md` containing:

1. **Functional requirements** — what the agent does, as numbered list
2. **Non-functional requirements** — perf, reliability, cost, security constraints
3. **Technical architecture** — diagram (ASCII or mermaid), components, data flow
4. **Dependencies** — external APIs, libraries, services required
5. **Acceptance criteria** — testable assertions (one per requirement)
6. **Risks** — ranked list with mitigation
7. **Out of scope** — explicit non-goals

## Gate

Before writing `SPEC.md`, print the draft in chat and ask user to confirm. Only write file after approval. Commit atomically:

```
git add SPEC.md && git commit -m "spec(phase-1): define <agent-name> requirements"
```

Next: `/agent-tasks`.
