---
name: token-budget
description: Measure and cut Claude Code token spend - daily tracker (Ctx/turn, % turns >200k), per-turn context line, empty-chat baseline, context diet, API MAP generator. Use on "token usage", "why is my quota gone", "sessions are expensive", "check consumption".
---

# token-budget — the token management system

**Premise, measured on the reference machine:** the bill is the context, not the model. Every turn re-pays the entire context, and cache reads count toward the quota. Before the diet: average context 283k, 30-42% of turns above 200k, a fresh chat paying ~88k before the first word. After: 78k per turn, 0% above 200k, fresh chat 69k. Same models, same work.

So the system has one job: **keep Ctx/turn low and prove it with a number.** `context-budget` (sibling skill) audits *what* is heavy; this skill *measures over time* and holds the line.

All scripts live in `${CLAUDE_PLUGIN_ROOT}/skills/token-budget/scripts/` (installed to `~/.claude/token-budget/bin/` by `/stack-bootstrap`). State goes to `~/.claude/token-budget/`.

## 1. Measure

| Tool | Command | Tells you |
|---|---|---|
| Daily tracker | `token_tracker.py --days 14` | Per day and model: turns, total, cache read/write, output, **Ctx/turn**, **% turns >200k**. Reads `~/.claude/projects/**/*.jsonl`, dedupes by message id, also books Codex CLI sessions. Writes `token_usage.md` + a merged `db.json` that never loses old days. `--summary` → today + 7 days as JSON for a status bar. |
| Context line | `ctx_guard.py` as a `Stop` hook | After every turn: `🟢 ctx 78k (39%)`. 🟡 from 50%, 🔴 from 80%. Above `CC_CTX_WARN` (140k) it adds "hand off now". Instant: reads only the last usage record. |
| Baseline | `baseline.sh` | Cost of an empty chat = what every new session pays before doing anything. |
| Attribution | `/usage` (built in) | Which skill / MCP / subagent eats ≥10%. `npx ccusage daily` for a second opinion. |

**The two numbers to watch:** Ctx/turn (target < 100k) and % turns >200k (target 0). If >200k climbs past 5%, someone picked a `[1m]` model or skipped a handoff.

Schedule the tracker daily (23:55). macOS: a LaunchAgent running `python3 ~/.claude/token-budget/bin/token_tracker.py`. Linux: `55 23 * * * python3 ~/.claude/token-budget/bin/token_tracker.py >/dev/null`.

## 2. Settings (`~/.claude/settings.json` → `env`)

| Var | Value | Why |
|---|---|---|
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | `1` | Removes `[1m]` variants. The single biggest lever. |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `sonnet` | Generic subagents on Sonnet. No `_FORCE`: agents with `model:` keep it. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `75` | Compaction safety net earlier; the real rule is still handoff at ~150k. |
| `CLAUDE_CODE_PROMPT_CACHE_TTL` | `1h` | Fewer cache re-writes when you pause between turns. |
| `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` | `1h` | Same for subagents. |
| `BASH_MAX_OUTPUT_LENGTH` | `12000` | A runaway command cannot dump 30k chars into context. |

Check the tracker two days after enabling the 1h TTLs: if **Cache write** jumps, remove them — 1h writes cost more than 5-minute ones and only pay off if you actually come back within the hour.

Back up `settings.json` before editing. Merge, never replace.

## 3. Context diet (run `baseline.sh` before and after)

Everything below loads into every prompt. Cut in this order:

1. **`MEMORY.md` → pure index.** One line per memory; detail in `index_<topic>.md` sub-files opened per task.
2. **`~/.claude/CLAUDE.md` → operational only.** Inventories and cheatsheets go to an on-demand reference (way-stack ships it that way since v2.5.0). Target ≤ 8 KB.
3. **Agents:** move unused ones to `~/.claude/agents_archive/`; every `description` ≤ 130 chars. Descriptions load every session, bodies do not.
4. **Skills:** unused → `~/.claude/skills_archive/`. Same logic: the description is the cost.
5. **Global MCP servers:** each one's tool schemas are paid per prompt. Keep global only what you need in *every* session; the rest goes project-scoped (`.mcp.json`) or on demand (`claude --mcp-config`). Save the removed config blocks to a file so re-enabling is a paste.
6. **Plugins:** disable the ones whose skills/hooks you never trigger.
7. **Hooks that echo text every turn:** each echo is context. Remove the decorative ones.

Keep dated backups (`*.bak-YYYY-MM-DD-tokens`). Archive, never delete.

## 4. Right-size agents

Custom agents that only report or do mechanical work: `model: sonnet`, `effort: medium`. Standard dev: `opus`. Only judges/verifiers: top model. No agent on `effort: max` by default. In workflows and `claude -p` loops always pass an explicit cheap `--model`, plus `--strict-mcp-config --mcp-config <empty.json> --setting-sources ""` for headless jobs so they skip the whole baseline.

## 5. Grounding for cheap models — `api_map.py`

Cheap models say "that API doesn't exist" when they lack grounding. `api_map.py <projects-root> [max]` appends a `## API MAP` table (API | File | Entry point | Auth | Notes) to each project `CLAUDE.md`, built by a headless Sonnet call from **grep evidence only**. Append-only, skips projects that already have the section, three hard stops (max runs, 5 consecutive failures, 180s per run). Tables are a first draft: correct them by hand when you touch the project.

## 6. Habits the tooling cannot enforce

- Hand off at ~150k (`/handoff` → `/reboot`). Mega-sessions are the top residual waste.
- Never switch model mid-task (cache is lost).
- No wide subagent fan-out for small jobs (200-500% overhead).
- Headless jobs that call the model once per item → batch them.
- Never `/fast`, never external routers/proxies.

## Playbook: "check my token usage"

1. `token_tracker.py --days 7` → read Ctx/turn and >200k for the last days.
2. Both healthy → report the numbers, stop.
3. Ctx/turn high → `baseline.sh`; if baseline > ~75k run the diet (section 3) via `context-budget`; else it is session length → habits (section 6).
4. One model dominating with many turns → `/usage` attribution → right-size that agent (section 4).
5. Report before/after numbers. No number, no claim.
