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

## Log mining (repeated asks → enforcement)

Run alongside the steps above. Scan user messages from the last ~30 days and count repeats:

```python
import collections, glob, json, os, re, time
cut, c = time.time() - 30 * 86400, collections.Counter()
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    if os.path.getmtime(f) < cut:
        continue
    for ln in open(f, errors="ignore"):
        try:
            m = json.loads(ln)
        except Exception:
            continue
        msg = m.get("message") or {}
        t = msg.get("content") if msg.get("role") == "user" else None
        if isinstance(t, list):
            t = " ".join(x.get("text", "") for x in t if isinstance(x, dict))
        if isinstance(t, str) and 3 < len(t) < 200:
            c[re.sub(r"\W+", " ", t.lower()).strip()[:60]] += 1
print(c.most_common(40))
```

Cluster near-duplicates by hand (same intent, different words: "go", "proceed", "continue" = one cluster). For every cluster with ≥10 hits propose the cheapest enforcement that actually works:

1. **Hook** if the rule is mechanical (a pattern in the prompt or in the closing text can detect it) — e.g. `prompt-reflex`, `closing-guard`.
2. **Skill** if it is a procedure with steps.
3. **Memory line** only if neither fits. A rule that was already in memory and still got repeated is proof memory alone does not enforce it.

## Rules

- Existing-skill check is mandatory — a mature setup has ~100 skills; false "missing skill" proposals are noise.
- Cadence: monthly. If last report in 00_INBOX is <3 weeks old, say so and stop.
