---
name: session-audit
description: Monthly audit of recent Claude Code sessions — cluster repeated manual tasks, propose new skills/automations. Diagnosis-only, writes report. Trigger: /session-audit, "audit my sessions", "what skills am I missing".
---

# Session Audit (Chase — Agentic OS 2.0 workflow audit)

Diagnosis-only. NEVER create skills/automations in this run — only propose.

## Steps

1. List recent session transcripts: `ls -t ~/.claude/projects/*/  | head` — take last ~30 sessions across projects (use the recall archive index if available, see `recall` skill).
2. Spawn 3-4 parallel subagents (model: sonnet), each reads a slice of sessions and returns: repeated user-requested tasks (task, frequency, output produced, manual back-and-forth involved).
3. Cluster results yourself: merge duplicates, drop one-offs (<3 occurrences), drop tasks already covered by an existing skill/agent (check `~/.claude/skills/` and `~/.claude/agents/` names first).
4. Per cluster decide: **new skill** / **automation (cron/loop)** / **fix existing skill** / **nothing**. One line of rationale each.
5. Write report to `<vault>/00_INBOX/session-audit-YYYY-MM-DD.md`: table cluster · freq · verdict · proposed skill name. Show the user the table, ask which to build.

## Rules

- Existing-skill check is mandatory — a mature setup has ~100 skills; false "missing skill" proposals are noise.
- Cadence: monthly. If last report in 00_INBOX is <3 weeks old, say so and stop.
