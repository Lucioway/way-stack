---
name: dream
description: >
  Memory consolidation for Claude Code auto-memory (claude-mem). Merges duplicate memory files, resolves
  contradictions, converts relative dates to absolute, prunes stale entries, and shrinks
  MEMORY.md index under the 24.4KB load limit. Replicates Anthropic's Dream feature.
  Use when user says "/dream", "consolidate memory", "clean memory", "memory bloated",
  or when MEMORY.md is truncated / over the load limit.
---

# Dream — Memory consolidation

Replicate Anthropic's **Dream** feature. Consolidate the auto-memory so Claude gets *smarter* the longer it runs, not noisier.

## Scope

```
DEFAULT  → current project's memory dir
all      → every project memory dir under ~/.claude/projects/*/memory/
<slug>   → a specific project, e.g. /dream -Users-you-Code-myproject
```

Memory lives **per-project** (no user-global memory.md in this setup):
```
MEMDIR="$HOME/.claude/projects/<project-slug>/memory"
```
Resolve current project slug from cwd: replace `/` with `-` in the absolute path
(e.g. `/Users/you/Code/myproject` → `-Users-you-Code-myproject`).

## The hard constraint

`MEMORY.md` is loaded into context **every session**. The harness truncates it past a
**~24.4KB byte limit** (NOT a line count).

> Truncation already observed: "MEMORY.md is 34.3KB (limit: 24.4KB) — only part of it was loaded."

Primary win = get `MEMORY.md` **under 24KB** by shortening over-long index lines and moving
detail into topic files. Each index entry: **one line, under ~150 chars.**

## Procedure — 4 steps

### 1. Read existing memory
- Read `$MEMDIR/MEMORY.md` (the index)
- List `$MEMDIR/*.md` topic files; read any whose index line is suspect (duplicate/stale/contradiction candidates) — don't blind-read all if the dir is huge

### 2. Ground-truth against recent sessions
- Read the **last ~5** session transcripts: `~/.claude/projects/<slug>/*.jsonl` (newest by mtime)
- Skim for: facts that changed, decisions reversed, projects gone dormant, paths that moved
- Goal: does memory match what the user *actually does now*?

### 3. Identify issues (report before changing)
Classify every problem found:

| Type | Example | Action |
|------|---------|--------|
| **Near-duplicate** | two files same topic | merge into one, keep richest |
| **Contradiction** | "use X" vs "never X" | keep the newer (check transcript dates), delete old |
| **Stale** | project marked active but dormant 60d+ | prune or mark paused |
| **Relative date** | "by next Friday" | convert to absolute (e.g. 2026-06-26) |
| **Wrong-bucket** | code convention / path in memory | remove (derivable from repo) |
| **Verbose index line** | >150 chars in MEMORY.md | trim; push detail to topic file |
| **Dead pointer** | index points to missing file | fix or remove |

### 4. Consolidate
- **Merge** duplicate topic files; update/remove their index lines
- **Resolve** contradictions (newer wins; cite transcript evidence in the kept file)
- **Fix** all relative dates → absolute (today = run date)
- **Prune** stale/wrong-bucket files (delete file + index line)
- **Trim** MEMORY.md index: every line one-liner <150 chars, detail lives in topic `.md`
- **Re-check byte size**: `wc -c "$MEMDIR/MEMORY.md"` must be **< 24400 bytes**. If still over, keep trimming the longest index lines.

## Safety

- **Self-edit prompt**: editing files inside `.claude/` triggers a settings-edit permission ask even on bypass — expected, allow it.
- **Never** invent facts to "fill gaps" — consolidate only what exists.
- **Never** delete a topic file whose fact is still live just to save bytes — trim the index line instead.
- Show the issue list (step 3) to the user **before** destructive merges/prunes if running interactively. In autonomous/cron runs, proceed and report.
- Back up first: `cp -r "$MEMDIR" "$MEMDIR.bak-$(date +%Y%m%d-%H%M)"` then prune the .bak after the user confirms.

## Output (terse)

```
Dream — <project-slug>
MEMORY.md: 34.3KB → 22.1KB (under 24.4KB limit ✓)
- merged: N files
- contradictions resolved: N
- dates fixed: N
- pruned: N
- index lines trimmed: N
Backup: memory.bak-YYYYMMDD-HHMM
```

## Frequency

On-the-margin play — run when MEMORY.md nears the limit, or monthly. Optional cron:
```bash
0 9 1 * * cd <your-main-project> && claude --no-interactive "/dream"
```